from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "scripts" / "audit_readme.py"
HEADER_SCRIPT = SKILL_ROOT / "scripts" / "readme_header.py"
HEADER_PROFILE = SKILL_ROOT / "assets" / "readme-profile" / "profile.json"
FIXTURE_IDENTITY_ARGS = [
    "--project-name",
    "Fixture",
    "--tagline",
    "A fixture readers can understand.",
    "--identity-image",
    "assets/readme/logo.svg",
]


def run(
    command: list[str], cwd: Path, *, check: bool = True
) -> subprocess.CompletedProcess:
    return subprocess.run(
        command,
        cwd=cwd,
        check=check,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


class ReadmeAuditTests(unittest.TestCase):
    def test_real_readme_reference_is_resolved_and_svg_is_consumed(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="project-steward-readme-"
        ) as temporary:
            root = Path(temporary)
            assets = root / "assets" / "readme"
            assets.mkdir(parents=True)
            readme = root / "README.md"
            svg = assets / "hero.svg"
            readme.write_text(
                (
                    "# Fixture\n\n"
                    '<img src="./assets/readme/hero.svg" '
                    'alt="Fixture result and workflow">\n'
                ),
                encoding="utf-8",
            )
            svg.write_text(
                (
                    '<svg xmlns="http://www.w3.org/2000/svg" '
                    'viewBox="0 0 1200 320">'
                    "<title>Fixture result</title>"
                    '<rect width="1200" height="320"/>'
                    "</svg>\n"
                ),
                encoding="utf-8",
            )

            completed = run(
                [sys.executable, str(SCRIPT), str(readme)],
                root,
            )
            self.assertIn("Local images checked: 1", completed.stdout)
            self.assertIn("Prose blocks checked: 0", completed.stdout)
            self.assertIn("Scope: structural and prose-density checks", completed.stdout)
            self.assertIn("source currency", completed.stdout)
            self.assertIn("factual accuracy", completed.stdout)
            self.assertIn("visual relevance", completed.stdout)
            self.assertIn("rendered quality are not evaluated", completed.stdout)
            self.assertIn(
                "OK: structural README checks passed",
                completed.stdout,
            )

            svg.write_text(
                '<svg xmlns="http://www.w3.org/2000/svg"></svg>\n',
                encoding="utf-8",
            )
            failed = run(
                [sys.executable, str(SCRIPT), str(readme)],
                root,
                check=False,
            )
            self.assertEqual(1, failed.returncode)
            self.assertIn("missing viewBox", failed.stdout)
            self.assertIn("missing <title>", failed.stdout)

            svg.write_text(
                (
                    '<svg xmlns="http://www.w3.org/2000/svg" '
                    'viewBox="0 0 1200 320">'
                    "<title>Fixture result</title>"
                    "</svg>\n"
                ),
                encoding="utf-8",
            )
            readme.write_text(
                "# Fixture\n\n![](./assets/readme/hero.svg)\n",
                encoding="utf-8",
            )
            missing_alt = run(
                [sys.executable, str(SCRIPT), str(readme)],
                root,
                check=False,
            )
            self.assertEqual(1, missing_alt.returncode)
            self.assertIn(
                "Markdown image missing useful alt text",
                missing_alt.stdout,
            )

    def test_prose_density_rejects_long_paragraphs_and_consecutive_walls(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="project-steward-readme-density-"
        ) as temporary:
            root = Path(temporary)
            readme = root / "README.md"
            readme.write_text(
                (
                    "# Fixture\n\n"
                    + "A" * 361
                    + "\n\n"
                    "First short paragraph.\n\n"
                    "Second short paragraph.\n\n"
                    "Third short paragraph.\n\n"
                    "Fourth short paragraph.\n"
                ),
                encoding="utf-8",
            )

            failed = run(
                [sys.executable, str(SCRIPT), str(readme)],
                root,
                check=False,
            )
            self.assertEqual(1, failed.returncode)
            self.assertIn("has 361 characters", failed.stdout)
            self.assertIn("5 consecutive paragraphs", failed.stdout)

            readme.write_text(
                (
                    "# Fixture\n\n"
                    "A concise introduction.\n\n"
                    "- A list breaks the prose run.\n\n"
                    "A second concise paragraph.\n\n"
                    "```text\n"
                    + "B" * 500
                    + "\n```\n"
                ),
                encoding="utf-8",
            )
            passed = run(
                [sys.executable, str(SCRIPT), str(readme)],
                root,
            )
            self.assertIn("Prose blocks checked: 2", passed.stdout)
            self.assertIn("OK: structural README checks passed", passed.stdout)

    def test_profile_producer_reaches_all_language_readmes_and_auditor(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="project-steward-readme-header-"
        ) as temporary:
            root = Path(temporary)
            (root / "LICENSE").write_text("Fixture license\n", encoding="utf-8")
            (root / "ARCHITECTURE.md").write_text(
                "# Fixture architecture\n", encoding="utf-8"
            )
            (root / "CONTRIBUTING.md").write_text(
                "# Contributing\n", encoding="utf-8"
            )
            logo = root / "assets" / "readme" / "logo.svg"
            logo.parent.mkdir(parents=True)
            logo.write_text(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
                "<title>Fixture logo</title><circle cx=\"50\" cy=\"50\" r=\"40\"/>"
                "</svg>\n",
                encoding="utf-8",
            )
            language_files = {
                "zh-CN": root / "README.md",
                "en": root / "README.en.md",
                "ja": root / "README.ja.md",
            }
            for path in language_files.values():
                path.write_text("# Fixture\n", encoding="utf-8")

            for language, readme in language_files.items():
                produced = run(
                    [
                        sys.executable,
                        str(HEADER_SCRIPT),
                        "render",
                        "--profile",
                        str(HEADER_PROFILE),
                        "--repository",
                        "CheshireMew/fixture",
                        "--language",
                        language,
                        *FIXTURE_IDENTITY_ARGS,
                        "--branch",
                        "main",
                        "--readme-root",
                        str(root),
                        "--navigation-target",
                        "docs=ARCHITECTURE.md",
                    ],
                    root,
                ).stdout.strip()
                readme.write_text(
                    produced + "\n\n# Fixture\n",
                    encoding="utf-8",
                )
                verified = run(
                    [
                        sys.executable,
                        str(HEADER_SCRIPT),
                        "verify",
                        "--profile",
                        str(HEADER_PROFILE),
                        "--repository",
                        "CheshireMew/fixture",
                        "--language",
                        language,
                        *FIXTURE_IDENTITY_ARGS,
                        "--branch",
                        "main",
                        "--readme",
                        str(readme),
                        "--navigation-target",
                        "docs=ARCHITECTURE.md",
                    ],
                    root,
                )
                self.assertIn("OK: README header matches profile", verified.stdout)

            chinese = language_files["zh-CN"].read_text(encoding="utf-8")
            identity_index = chinese.index('./assets/readme/logo.svg')
            name_index = chinese.index('<h1 align="center">Fixture</h1>')
            tagline_index = chinese.index("A fixture readers can understand.")
            language_index = chinese.index("<strong>中文</strong>")
            social_index = chinese.index("img.shields.io/badge/X-")
            repository_index = chinese.index("github/stars/CheshireMew/fixture")
            self.assertLess(identity_index, name_index)
            self.assertLess(name_index, tagline_index)
            self.assertLess(tagline_index, language_index)
            self.assertLess(language_index, social_index)
            self.assertLess(social_index, repository_index)
            self.assertIn("<strong>中文</strong>", chinese)
            self.assertIn('./README.en.md">English</a>', chinese)
            self.assertIn('./README.ja.md">日本語</a>', chinese)
            self.assertIn(
                '日本語</a> | <a href="./ARCHITECTURE.md">文档</a> | '
                '<a href="./CONTRIBUTING.md">贡献</a> | '
                '<a href="https://github.com/CheshireMew/fixture/issues">反馈</a>',
                chinese,
            )
            self.assertIn("https://x.com/0xCheshire", chinese)
            self.assertIn('title="X"', chinese)
            self.assertIn("img.shields.io/badge/X-", chinese)
            self.assertIn("https://t.me/CheshireBTC", chinese)
            self.assertIn("https://blog.blacknico.com/", chinese)
            self.assertIn("https://blacknico.com/", chinese)
            self.assertIn("github/stars/CheshireMew/fixture", chinese)
            self.assertIn("github/forks/CheshireMew/fixture", chinese)
            self.assertIn("github/license/CheshireMew/fixture", chinese)
            self.assertNotIn("官方网站", chinese)

            audited = run(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(language_files["zh-CN"]),
                    "--header-profile",
                    str(HEADER_PROFILE),
                    "--repository",
                    "CheshireMew/fixture",
                    "--language",
                    "zh-CN",
                    *FIXTURE_IDENTITY_ARGS,
                    "--branch",
                    "main",
                    "--navigation-target",
                    "docs=ARCHITECTURE.md",
                ],
                root,
            )
            self.assertIn("Managed header checked: yes", audited.stdout)
            self.assertIn("OK: structural README checks passed", audited.stdout)

            language_files["zh-CN"].write_text(
                chinese.replace(
                    "github/stars/CheshireMew/fixture",
                    "github/stars/AnotherOwner/fixture",
                    1,
                ),
                encoding="utf-8",
            )
            stale = run(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(language_files["zh-CN"]),
                    "--header-profile",
                    str(HEADER_PROFILE),
                    "--repository",
                    "CheshireMew/fixture",
                    "--language",
                    "zh-CN",
                    *FIXTURE_IDENTITY_ARGS,
                    "--navigation-target",
                    "docs=ARCHITECTURE.md",
                ],
                root,
                check=False,
            )
            self.assertEqual(1, stale.returncode)
            self.assertIn("does not match the active profile", stale.stdout)

    def test_unresolved_project_navigation_does_not_remove_universal_links(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="project-steward-readme-optional-navigation-"
        ) as temporary:
            root = Path(temporary)
            for name in ("README.md", "README.en.md", "README.ja.md"):
                (root / name).write_text("# Fixture\n", encoding="utf-8")
            (root / "LICENSE").write_text("Fixture license\n", encoding="utf-8")
            (root / "CONTRIBUTING.md").write_text(
                "# Contributing\n", encoding="utf-8"
            )
            logo = root / "assets" / "readme" / "logo.svg"
            logo.parent.mkdir(parents=True)
            logo.write_text(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
                "<title>Fixture logo</title><circle cx=\"50\" cy=\"50\" r=\"40\"/>"
                "</svg>\n",
                encoding="utf-8",
            )

            rendered = run(
                [
                    sys.executable,
                    str(HEADER_SCRIPT),
                    "render",
                    "--profile",
                    str(HEADER_PROFILE),
                    "--repository",
                    "CheshireMew/fixture",
                    "--language",
                    "zh-CN",
                    *FIXTURE_IDENTITY_ARGS,
                    "--readme-root",
                    str(root),
                ],
                root,
            ).stdout

            self.assertNotIn(">文档</a>", rendered)
            self.assertIn('./CONTRIBUTING.md">贡献</a>', rendered)
            self.assertIn("https://blacknico.com/", rendered)
            self.assertIn("github/stars/CheshireMew/fixture", rendered)

    def test_profile_refuses_missing_translations_and_unowned_repositories(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="project-steward-readme-header-missing-"
        ) as temporary:
            root = Path(temporary)
            (root / "README.md").write_text("# Fixture\n", encoding="utf-8")
            (root / "LICENSE").write_text("Fixture license\n", encoding="utf-8")
            logo = root / "assets" / "readme" / "logo.svg"
            logo.parent.mkdir(parents=True)
            logo.write_text(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
                "<title>Fixture logo</title><circle cx=\"50\" cy=\"50\" r=\"40\"/>"
                "</svg>\n",
                encoding="utf-8",
            )
            base_command = [
                sys.executable,
                str(HEADER_SCRIPT),
                "render",
                "--profile",
                str(HEADER_PROFILE),
                "--language",
                "zh-CN",
                *FIXTURE_IDENTITY_ARGS,
                "--readme-root",
                str(root),
            ]
            missing = run(
                base_command + ["--repository", "CheshireMew/fixture"],
                root,
                check=False,
            )
            self.assertEqual(1, missing.returncode)
            self.assertIn("README.en.md", missing.stderr)
            self.assertIn("README.ja.md", missing.stderr)

            unowned = run(
                base_command
                + [
                    "--repository",
                    "AnotherOwner/fixture",
                    "--allow-missing-languages",
                ],
                root,
                check=False,
            )
            self.assertEqual(1, unowned.returncode)
            self.assertIn("does not apply to GitHub owner", unowned.stderr)

    def test_profile_refuses_a_missing_identity_image(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="project-steward-readme-identity-"
        ) as temporary:
            root = Path(temporary)
            for name in ("README.md", "README.en.md", "README.ja.md"):
                (root / name).write_text("# Fixture\n", encoding="utf-8")
            (root / "LICENSE").write_text("Fixture license\n", encoding="utf-8")
            (root / "CONTRIBUTING.md").write_text(
                "# Contributing\n", encoding="utf-8"
            )

            missing_logo = run(
                [
                    sys.executable,
                    str(HEADER_SCRIPT),
                    "render",
                    "--profile",
                    str(HEADER_PROFILE),
                    "--repository",
                    "CheshireMew/fixture",
                    "--language",
                    "zh-CN",
                    *FIXTURE_IDENTITY_ARGS,
                    "--readme-root",
                    str(root),
                ],
                root,
                check=False,
            )

            self.assertEqual(1, missing_logo.returncode)
            self.assertIn(
                "configured identity image is missing: assets/readme/logo.svg",
                missing_logo.stderr,
            )

    def test_profile_refuses_legacy_schema_and_missing_navigation_targets(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="project-steward-readme-navigation-"
        ) as temporary:
            root = Path(temporary)
            legacy_profile = root / "legacy-profile.json"
            profile = json.loads(HEADER_PROFILE.read_text(encoding="utf-8"))
            profile["schema_version"] = 2
            legacy_profile.write_text(
                json.dumps(profile, ensure_ascii=False),
                encoding="utf-8",
            )
            legacy = run(
                [
                    sys.executable,
                    str(HEADER_SCRIPT),
                    "validate",
                    "--profile",
                    str(legacy_profile),
                ],
                root,
                check=False,
            )
            self.assertEqual(1, legacy.returncode)
            self.assertIn("schema_version must be 3", legacy.stderr)

            for name in ("README.md", "README.en.md", "README.ja.md"):
                (root / name).write_text("# Fixture\n", encoding="utf-8")
            (root / "LICENSE").write_text("Fixture license\n", encoding="utf-8")
            logo = root / "assets" / "readme" / "logo.svg"
            logo.parent.mkdir(parents=True)
            logo.write_text(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
                "<title>Fixture logo</title><circle cx=\"50\" cy=\"50\" r=\"40\"/>"
                "</svg>\n",
                encoding="utf-8",
            )
            missing_project_target = run(
                [
                    sys.executable,
                    str(HEADER_SCRIPT),
                    "render",
                    "--profile",
                    str(HEADER_PROFILE),
                    "--repository",
                    "CheshireMew/fixture",
                    "--language",
                    "zh-CN",
                    *FIXTURE_IDENTITY_ARGS,
                    "--readme-root",
                    str(root),
                    "--navigation-target",
                    "docs=ARCHITECTURE.md",
                ],
                root,
                check=False,
            )
            self.assertEqual(1, missing_project_target.returncode)
            self.assertIn(
                "project navigation target is missing: ARCHITECTURE.md",
                missing_project_target.stderr,
            )

            (root / "ARCHITECTURE.md").write_text(
                "# Fixture architecture\n", encoding="utf-8"
            )
            missing_managed_target = run(
                [
                    sys.executable,
                    str(HEADER_SCRIPT),
                    "render",
                    "--profile",
                    str(HEADER_PROFILE),
                    "--repository",
                    "CheshireMew/fixture",
                    "--language",
                    "zh-CN",
                    *FIXTURE_IDENTITY_ARGS,
                    "--readme-root",
                    str(root),
                    "--navigation-target",
                    "docs=ARCHITECTURE.md",
                ],
                root,
                check=False,
            )
            self.assertEqual(1, missing_managed_target.returncode)
            self.assertIn(
                "configured navigation target is missing: CONTRIBUTING.md",
                missing_managed_target.stderr,
            )

    def test_star_history_must_precede_license_and_attribution(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="project-steward-readme-section-order-"
        ) as temporary:
            root = Path(temporary)
            readme = root / "README.md"
            readme.write_text(
                (
                    "# Fixture\n\n"
                    "## 许可证与第三方致谢\n\n"
                    "Project license and notices.\n\n"
                    "## Star History\n\n"
                    "Repository growth chart.\n"
                ),
                encoding="utf-8",
            )

            failed = run(
                [sys.executable, str(SCRIPT), str(readme)],
                root,
                check=False,
            )
            self.assertEqual(1, failed.returncode)
            self.assertIn(
                "Star History section must appear before license and third-party acknowledgements",
                failed.stdout,
            )

            readme.write_text(
                (
                    "# Fixture\n\n"
                    "## Star History\n\n"
                    "Repository growth chart.\n\n"
                    "## License and third-party acknowledgements\n\n"
                    "Project license and notices.\n"
                ),
                encoding="utf-8",
            )
            passed = run(
                [sys.executable, str(SCRIPT), str(readme)],
                root,
            )
            self.assertIn(
                "OK: structural README checks passed",
                passed.stdout,
            )


if __name__ == "__main__":
    unittest.main()
