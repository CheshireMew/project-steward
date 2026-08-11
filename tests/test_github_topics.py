from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "github_topics.py"
SPEC = importlib.util.spec_from_file_location("github_topics", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
TOPICS = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = TOPICS
SPEC.loader.exec_module(TOPICS)


HEAD = "a" * 40


class FixtureClient:
    def __init__(self, *, topics=(), after_head=HEAD, can_push=True) -> None:
        self.topics = tuple(topics)
        self.after_head = after_head
        self.can_push = can_push
        self.calls = []
        self.put_count = 0

    def request(self, method, endpoint, *, payload=None):
        self.calls.append((method, endpoint, payload))
        if endpoint == "repos/Owner/project":
            return {
                "full_name": "Owner/project",
                "visibility": "public",
                "default_branch": "main",
                "permissions": {"push": self.can_push},
            }
        if endpoint == "repos/Owner/project/commits/main":
            head = HEAD if self.put_count == 0 else self.after_head
            return {"sha": head}
        if endpoint == "repos/Owner/project/topics":
            if method == "GET":
                return {"names": list(self.topics)}
            if method == "PUT":
                self.put_count += 1
                self.topics = tuple(payload["names"])
                return {"names": list(self.topics)}
        raise AssertionError("unexpected request: {} {}".format(method, endpoint))


def homepage_with(*topics):
    return "".join(
        '<a class="topic-tag" href="/topics/{}">{}</a>'.format(topic, topic)
        for topic in topics
    )


class GitHubTopicsTests(unittest.TestCase):
    def test_final_topics_are_canonical_unique_and_deterministic(self) -> None:
        self.assertEqual(
            ("agent-skill", "learning", "research"),
            TOPICS.validate_topics(("research", "agent-skill", "learning")),
        )
        for invalid in (
            (),
            ("Agent-Skill",),
            ("agent_skill",),
            ("-learning",),
            ("learning-",),
            ("learning", "learning"),
            tuple("topic-{}".format(index) for index in range(21)),
        ):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    TOPICS.validate_topics(invalid)

    def test_apply_replaces_once_then_verifies_api_head_and_homepage(self) -> None:
        client = FixtureClient(topics=("old-topic",))
        result = TOPICS.apply_topics(
            client,
            "Owner/project",
            ("research", "learning", "agent-skill"),
            expected_head=HEAD,
            homepage_attempts=1,
            homepage_delay=0,
            homepage_loader=lambda _: homepage_with(
                "agent-skill", "learning", "research"
            ),
        )

        self.assertTrue(result.changed)
        self.assertTrue(result.verified)
        self.assertTrue(result.api_verified)
        self.assertTrue(result.homepage_verified)
        self.assertEqual(client.put_count, 1)
        self.assertEqual(
            ("agent-skill", "learning", "research"), result.topics
        )

    def test_matching_set_is_read_back_without_a_redundant_write(self) -> None:
        current = ("agent-skill", "learning")
        client = FixtureClient(topics=current)
        result = TOPICS.apply_topics(
            client,
            "Owner/project",
            current,
            expected_head=HEAD,
            homepage_attempts=1,
            homepage_delay=0,
            homepage_loader=lambda _: homepage_with(*current),
        )

        self.assertFalse(result.changed)
        self.assertEqual(client.put_count, 0)
        self.assertTrue(result.verified)

    def test_concurrent_default_branch_change_invalidates_the_result(self) -> None:
        client = FixtureClient(topics=(), after_head="b" * 40)
        with self.assertRaisesRegex(
            TOPICS.TopicsError,
            "default-branch identity changed",
        ):
            TOPICS.apply_topics(
                client,
                "Owner/project",
                ("agent-skill",),
                expected_head=HEAD,
                homepage_attempts=1,
                homepage_delay=0,
                homepage_loader=lambda _: homepage_with("agent-skill"),
            )
        self.assertEqual(client.put_count, 1)

    def test_homepage_requires_the_exact_api_set(self) -> None:
        client = FixtureClient(topics=())
        with self.assertRaisesRegex(
            TOPICS.TopicsError,
            "homepage Topics did not match",
        ):
            TOPICS.apply_topics(
                client,
                "Owner/project",
                ("agent-skill", "learning"),
                expected_head=HEAD,
                homepage_attempts=1,
                homepage_delay=0,
                homepage_loader=lambda _: homepage_with("agent-skill"),
            )

    def test_cli_contract_requires_head_and_explicit_topics(self) -> None:
        parser = TOPICS.build_parser()
        arguments = parser.parse_args(
            [
                "apply",
                "--repository",
                "Owner/project",
                "--expected-head",
                HEAD,
                "--topic",
                "agent-skill",
                "--topic",
                "learning",
            ]
        )
        self.assertEqual(arguments.command, "apply")
        self.assertEqual(arguments.topic, ["agent-skill", "learning"])


if __name__ == "__main__":
    unittest.main()
