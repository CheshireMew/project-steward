from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
REVIEW = SKILL_ROOT / "scripts" / "production_storage_review.py"
TEMPLATES = SKILL_ROOT / "scripts" / "project_templates.py"


class ProductionStorageGovernanceTests(unittest.TestCase):
    def test_skill_routes_storage_prevention_to_one_method(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        reference = (SKILL_ROOT / "references" / "production-storage-governance.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("生产存储预防与审查", skill)
        self.assertGreaterEqual(skill.count("references/production-storage-governance.md"), 2)
        directory_route = skill.split("## 项目目录治理", 1)[1].split("## 项目基线与模板", 1)[0]
        self.assertIn("references/production-storage-governance.md", directory_route)
        for phrase in (
            "事先预防必须发生在首个大文件之前",
            "获准实施时必须写进生产项目",
            ".project-steward/storage-contract.json",
            "scripts/production_storage_review.py",
            "不能让 Project Steward 的脚本成为运行时代理",
            "候选归属体积不等于可回收体积",
            "实际回收体积",
            "最后一个写入同一登记根的生产者",
        ):
            self.assertIn(phrase, reference)

    def test_explicit_template_writes_storage_decisions_into_project(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(TEMPLATES), "list", "--compact"],
            cwd=SKILL_ROOT,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        listed = json.loads(completed.stdout)
        template = next(item for item in listed["templates"] if item["id"] == "managed-runtime-artifacts")
        self.assertEqual("explicit-only", template["selection"])

    def test_review_requires_real_enforcement_and_tests(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-steward-storage-") as temporary:
            project = Path(temporary)
            (project / "src").mkdir()
            (project / "tests").mkdir()
            (project / ".project-steward").mkdir()
            (project / "src" / "producer.py").write_text(
                "def require_storage_budget():\n    pass\n\ndef write_storage_inventory():\n    pass\n",
                encoding="utf-8",
            )
            (project / "tests" / "test_storage.py").write_text("def test_budget():\n    pass\n", encoding="utf-8")
            contract = {
                "protocol": "project-steward-production-storage-contract",
                "version": 1,
                "project_id": "fixture",
                "policy": {
                    "unknown_peak": "block",
                    "outside_owned_roots": "block",
                    "over_budget": "block",
                    "cleanup_without_authorization": "report-only",
                },
                "producers": [
                    {
                        "id": "fixture-producer",
                        "root_source": {"kind": "runtime-config", "value": "FIXTURE_STORAGE_ROOT"},
                        "artifact_classes": ["cache", "temporary", "evidence"],
                        "peak_estimate": {"source": "src/producer.py:require_storage_budget", "unknown_behavior": "block"},
                        "budget": {
                            "maximum_managed_bytes_source": "runtime-config:max_bytes",
                            "minimum_free_bytes_source": "runtime-config:min_free_bytes",
                        },
                        "reuse": {"required": True, "identity": "content hash and producer version"},
                        "lifecycle": {
                            "preflight": "require_storage_budget",
                            "finalization": "write_storage_inventory",
                            "interruption": "retain owned manifest and report exact candidates",
                        },
                        "implementation_files": ["src/producer.py"],
                        "test_files": ["tests/test_storage.py"],
                        "enforcement": {
                            "file": "src/producer.py",
                            "tokens": ["require_storage_budget", "write_storage_inventory"],
                        },
                    }
                ],
            }
            contract_path = project / ".project-steward" / "storage-contract.json"
            contract_path.write_text(json.dumps(contract, indent=2), encoding="utf-8")

            passed = subprocess.run(
                [sys.executable, str(REVIEW), str(project), "--compact"],
                cwd=SKILL_ROOT,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(0, passed.returncode, passed.stderr)
            self.assertEqual("passed", json.loads(passed.stdout)["status"])

            contract["producers"][0]["root_source"]["value"] = "D:/unowned"
            contract_path.write_text(json.dumps(contract, indent=2), encoding="utf-8")
            blocked = subprocess.run(
                [sys.executable, str(REVIEW), str(project), "--compact"],
                cwd=SKILL_ROOT,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(2, blocked.returncode)
            self.assertIn("machine drive", blocked.stderr)


if __name__ == "__main__":
    unittest.main()
