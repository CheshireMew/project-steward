from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "github_about.py"
SPEC = importlib.util.spec_from_file_location("github_about", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load github_about.py")
ABOUT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ABOUT
SPEC.loader.exec_module(ABOUT)

HEAD = "a" * 40


class FixtureClient:
    def __init__(
        self,
        *,
        description="Old description",
        website="",
        head=HEAD,
        after_head=None,
        visibility="public",
        can_push=True,
    ) -> None:
        self.description = description
        self.website = website
        self.head = head
        self.after_head = after_head
        self.visibility = visibility
        self.can_push = can_push
        self.patch_payloads = []

    def request(self, method, endpoint, *, payload=None):
        if endpoint == "repos/Owner/project" and method == "GET":
            return {
                "full_name": "Owner/project",
                "visibility": self.visibility,
                "default_branch": "main",
                "description": self.description or None,
                "homepage": self.website or None,
                "permissions": {"push": self.can_push},
            }
        if endpoint == "repos/Owner/project/commits/main" and method == "GET":
            return {"sha": self.head}
        if endpoint == "repos/Owner/project" and method == "PATCH":
            self.patch_payloads.append(dict(payload))
            self.description = payload["description"]
            self.website = payload["homepage"]
            if self.after_head is not None:
                self.head = self.after_head
            return {
                "full_name": "Owner/project",
                "description": self.description,
                "homepage": self.website or None,
            }
        raise AssertionError("unexpected request: {} {}".format(method, endpoint))


def homepage_with(description, website=""):
    sidebar = {"description": description, "formattedDescription": description}
    if website:
        sidebar["website"] = website
    payload = {"payload": {"sidebarAbout": sidebar}}
    return '<script type="application/json">{}</script>'.format(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    )


class GitHubAboutTests(unittest.TestCase):
    def test_inspect_is_read_only_and_returns_both_about_fields(self) -> None:
        client = FixtureClient(
            description="Public definition",
            website="https://example.com/project",
        )

        snapshot = ABOUT.inspect_repository(client, "Owner/project")

        self.assertEqual("Public definition", snapshot.description)
        self.assertEqual("https://example.com/project", snapshot.website)
        self.assertEqual([], client.patch_payloads)

    def test_description_and_website_validation_preserve_explicit_values(self) -> None:
        self.assertEqual(
            "A public project definition.",
            ABOUT.validate_description("  A public project definition.  "),
        )
        self.assertEqual(
            "https://docs.example.com/project?lang=en",
            ABOUT.validate_website("https://docs.example.com/project?lang=en"),
        )
        for invalid in ("", "line one\nline two", "definition\n", "\tdefinition"):
            with self.subTest(description=invalid):
                with self.assertRaises(ValueError):
                    ABOUT.validate_description(invalid)
        for invalid in (
            "",
            "docs.example.com",
            "ftp://example.com",
            "https://u:p@example.com",
            "https://example.com/a b",
            "https://example.com\n",
        ):
            with self.subTest(website=invalid):
                with self.assertRaises(ValueError):
                    ABOUT.validate_website(invalid)

    def test_homepage_about_is_read_from_the_visible_sidebar_payload(self) -> None:
        self.assertEqual(
            ("Public definition", "https://example.com/project"),
            ABOUT.extract_homepage_about(
                homepage_with("Public definition", "https://example.com/project")
            ),
        )
        self.assertEqual(
            ("Public definition", ""),
            ABOUT.extract_homepage_about(homepage_with("Public definition")),
        )

    def test_apply_verifies_metadata_without_claiming_to_check_the_destination(self) -> None:
        client = FixtureClient()
        result = ABOUT.apply_about(
            client,
            "Owner/project",
            "Public definition",
            "https://example.com/project",
            expected_head=HEAD,
            homepage_attempts=1,
            homepage_delay=0,
            homepage_loader=lambda _: homepage_with(
                "Public definition",
                "https://example.com/project",
            ),
        )

        self.assertEqual(
            [
                {
                    "description": "Public definition",
                    "homepage": "https://example.com/project",
                }
            ],
            client.patch_payloads,
        )
        self.assertTrue(result.changed)
        self.assertTrue(result.api_verified)
        self.assertTrue(result.github_page_verified)
        self.assertTrue(result.metadata_verified)
        self.assertEqual(
            "caller_qualified_not_checked",
            result.website_destination_validation,
        )
        self.assertFalse(hasattr(result, "homepage_verified"))
        self.assertEqual(HEAD, result.head)

    def test_noop_still_verifies_the_api_and_homepage(self) -> None:
        client = FixtureClient(
            description="Public definition",
            website="https://example.com/project",
        )
        result = ABOUT.apply_about(
            client,
            "Owner/project",
            "Public definition",
            "https://example.com/project",
            expected_head=HEAD,
            homepage_attempts=1,
            homepage_delay=0,
            homepage_loader=lambda _: homepage_with(
                "Public definition",
                "https://example.com/project",
            ),
        )

        self.assertEqual([], client.patch_payloads)
        self.assertFalse(result.changed)
        self.assertTrue(result.metadata_verified)

    def test_clear_website_is_an_explicit_atomic_target(self) -> None:
        client = FixtureClient(
            description="Public definition",
            website="https://stale.example.com",
        )
        result = ABOUT.apply_about(
            client,
            "Owner/project",
            "Public definition",
            "",
            expected_head=HEAD,
            homepage_attempts=1,
            homepage_delay=0,
            homepage_loader=lambda _: homepage_with("Public definition"),
        )

        self.assertEqual("", client.patch_payloads[0]["homepage"])
        self.assertEqual("", result.website)
        self.assertEqual("", result.github_page_website)
        self.assertEqual(
            "not_applicable",
            result.website_destination_validation,
        )
        self.assertTrue(result.metadata_verified)

    def test_head_drift_and_write_permission_fail_before_patch(self) -> None:
        cases = (
            (FixtureClient(head="b" * 40), "HEAD changed"),
            (FixtureClient(can_push=False), "lacks repository write permission"),
            (FixtureClient(visibility="private"), "only applies to public repositories"),
        )
        for client, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(ABOUT.AboutError, message):
                    ABOUT.apply_about(
                        client,
                        "Owner/project",
                        "Public definition",
                        "",
                        expected_head=HEAD,
                        homepage_attempts=1,
                        homepage_delay=0,
                        homepage_loader=lambda _: homepage_with("Public definition"),
                    )
                self.assertEqual([], client.patch_payloads)

    def test_head_change_during_update_and_homepage_mismatch_fail_closed(self) -> None:
        client = FixtureClient(after_head="b" * 40)
        with self.assertRaisesRegex(ABOUT.AboutError, "identity changed"):
            ABOUT.apply_about(
                client,
                "Owner/project",
                "Public definition",
                "",
                expected_head=HEAD,
                homepage_attempts=1,
                homepage_delay=0,
                homepage_loader=lambda _: homepage_with("Public definition"),
            )

        client = FixtureClient()
        with self.assertRaisesRegex(ABOUT.AboutError, "homepage About did not match"):
            ABOUT.apply_about(
                client,
                "Owner/project",
                "Public definition",
                "https://example.com/project",
                expected_head=HEAD,
                homepage_attempts=1,
                homepage_delay=0,
                homepage_loader=lambda _: homepage_with("Different description"),
            )

    def test_cli_requires_an_explicit_website_decision(self) -> None:
        parser = ABOUT.build_parser()
        base = [
            "apply",
            "--repository",
            "Owner/project",
            "--expected-head",
            HEAD,
            "--description",
            "Public definition",
        ]
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                parser.parse_args(base)
        self.assertTrue(parser.parse_args(base + ["--clear-website"]).clear_website)
        self.assertEqual(
            "https://example.com",
            parser.parse_args(base + ["--website", "https://example.com"]).website,
        )


if __name__ == "__main__":
    unittest.main()
