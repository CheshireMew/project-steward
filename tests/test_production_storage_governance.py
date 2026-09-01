from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
REVIEW = SKILL_ROOT / "scripts" / "production_storage_review.py"
TEMPLATES = SKILL_ROOT / "scripts" / "project_templates.py"


def write_storage_fixture(project: Path) -> dict:
    """Create static declarations, deliberately not a working storage system."""
    (project / "src").mkdir()
    (project / "tests").mkdir()
    (project / ".project-steward").mkdir()
    (project / "src" / "producer.py").write_text(
        "raise AssertionError('Static review must not execute project code')\n"
        "def require_storage_budget():\n    pass\n\n"
        "def list_storage_roots():\n    pass\n\n"
        "def allocated_bytes():\n    pass\n\n"
        "def file_identity():\n    pass\n\n"
        "def consume_artifact():\n    pass\n\n"
        "def write_storage_inventory():\n    pass\n",
        encoding="utf-8",
    )
    (project / "tests" / "test_storage.py").write_text(
        "raise AssertionError('Static review must not run project tests')\n"
        "def test_budget():\n    pass\n", encoding="utf-8"
    )
    contract = {
        "protocol": "project-steward-production-storage-contract",
        "version": 3,
        "project_id": "fixture",
        "policy": {
            "unknown_peak": "block",
            "outside_owned_roots": "block",
            "over_budget": "block",
            "cleanup_without_authorization": "report-only",
        },
        "producers": [{
            "id": "fixture-producer",
            "root_source": {
                "kind": "runtime-config",
                "value": "FIXTURE_STORAGE_ROOT",
                "ownership": {
                    "scope": "project-owned-external",
                    "project_namespace": "fixture",
                    "approved_root_source": "user-environment-policy:tools_root",
                    "fallback": "block",
                },
            },
            "artifact_classes": ["cache", "temporary", "evidence"],
            "peak_estimate": {
                "source": "src/producer.py:require_storage_budget", "unknown_behavior": "block"
            },
            "budget": {
                "maximum_managed_bytes_source": "runtime-config:max_bytes",
                "minimum_free_bytes_source": "runtime-config:min_free_bytes",
                "registered_roots_inventory_source": "src/producer.py:list_storage_roots",
                "filesystem_allocated_bytes_source": "src/producer.py:allocated_bytes",
                "managed_object_identity_source": "src/producer.py:file_identity",
            },
            "reuse": {"required": True, "identity": "content hash and producer version"},
            "lifecycle": {
                "preflight": "require_storage_budget",
                "finalization": "write_storage_inventory",
                "interruption": "retain owned manifest and report exact candidates",
            },
            "consumer_sources": ["src/producer.py:consume_artifact"],
            "manifest": {
                "source": "src/producer.py:write_storage_inventory",
                "terminal_states": ["succeeded", "failed", "interrupted"],
                "cleanup_authorization": "report-only",
            },
            "implementation_files": ["src/producer.py"],
            "test_files": ["tests/test_storage.py"],
            "enforcement": {
                "file": "src/producer.py",
                "tokens": ["require_storage_budget", "write_storage_inventory"],
            },
        }],
    }
    (project / ".project-steward" / "storage-contract.json").write_text(
        json.dumps(contract, indent=2), encoding="utf-8"
    )
    return contract


class ProductionStorageGovernanceTests(unittest.TestCase):
    def test_template_plan_adopt_verify_and_upgrade_keep_runtime_pending(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-steward-storage-lifecycle-") as temporary:
            project = Path(temporary)
            contract = write_storage_fixture(project)
            contract_path = project / ".project-steward" / "storage-contract.json"
            profile_path = project / ".project-steward" / "project.json"

            def call(command: str) -> tuple[subprocess.CompletedProcess, dict]:
                args = [sys.executable, str(TEMPLATES), command, str(project), "--compact"]
                if command in {"plan", "adopt"}:
                    args += ["--template", "managed-runtime-artifacts"]
                completed = subprocess.run(
                    args, cwd=SKILL_ROOT, check=False, capture_output=True, text=True, encoding="utf-8"
                )
                self.assertTrue(completed.stdout, completed.stderr)
                return completed, json.loads(completed.stdout)

            def storage_check(verification: dict) -> dict:
                return next(
                    item for item in verification["checks"]
                    if item["id"] == "runtime-artifact-contract-present"
                )

            planned, plan = call("plan")
            self.assertEqual(0, planned.returncode)
            self.assertEqual("passed", plan["preflight"]["status"])
            self.assertFalse(profile_path.exists())
            adopted, result = call("adopt")
            self.assertEqual(0, adopted.returncode)
            self.assertEqual("adopted", result["status"])
            verified, result = call("verify")
            self.assertEqual(0, verified.returncode)
            verification = result["verification"]
            self.assertEqual("static", verification["verification_level"])
            evidence = storage_check(verification)["evidence"]
            self.assertEqual("static_checks_passed", evidence["status"])
            self.assertEqual("not_run", evidence["runtime_verification"]["status"])
            self.assertTrue(verification["manual_verification_required"])
            self.assertTrue({
                "runtime-artifact-real-producer-chain", "runtime-artifact-interruption-chain"
            }.issubset({item["id"] for item in verification["manual_verification"]}))

            profile = json.loads(profile_path.read_text(encoding="utf-8"))
            pin = next(item for item in profile["templates"] if item["id"] == "managed-runtime-artifacts")
            pin["version"] = "0.9.0"
            pin["sha256"] = "0" * 64
            profile_path.write_text(json.dumps(profile), encoding="utf-8")
            previous_profile = profile_path.read_bytes()
            contract["version"] = 2
            contract_path.write_text(json.dumps(contract), encoding="utf-8")
            previous_contract = contract_path.read_bytes()
            verified, result = call("verify")
            self.assertEqual(1, verified.returncode)
            self.assertIn("version", {item["kind"] for item in result["verification"]["drift"]})
            self.assertEqual(
                "contract_version_mismatch",
                storage_check(result["verification"])["evidence"]["error_code"],
            )
            _, plan = call("plan")
            self.assertEqual("failed", plan["preflight"]["status"])
            blocked, result = call("upgrade")
            self.assertEqual(1, blocked.returncode)
            self.assertEqual("blocked", result["status"])
            self.assertEqual(previous_profile, profile_path.read_bytes())
            self.assertEqual(previous_contract, contract_path.read_bytes())

            contract["version"] = 3
            contract_path.write_text(json.dumps(contract), encoding="utf-8")
            _, plan = call("plan")
            self.assertEqual("passed", plan["preflight"]["status"])
            upgraded, result = call("upgrade")
            self.assertEqual(0, upgraded.returncode)
            self.assertEqual("upgraded", result["status"])
            self.assertTrue(result["verification"]["manual_verification_required"])
            self.assertEqual(
                "not_run",
                storage_check(result["verification"])["evidence"]["runtime_verification"]["status"],
            )
            verified, result = call("verify")
            self.assertEqual(0, verified.returncode)
            self.assertEqual([], result["verification"]["drift"])

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
            "产物归位门槛唯一决定",
            "项目拥有的外部工作根",
            "批准根和稳定项目命名空间下",
            "项目外无所有者的任务产物为零",
            "旧 v2 又缺少外部根所有权、正式消费者与终态清单来源",
            "事先预防必须发生在首个大文件之前",
            "获准实施时必须写进生产项目",
            ".project-steward/storage-contract.json",
            "scripts/production_storage_review.py",
            "不能让 Project Steward 的脚本成为运行时代理",
            "候选归属体积不等于可回收体积",
            "文件系统分配体积",
            "受管唯一对象体积",
            "实际回收结果",
            "最后一个写入同一登记根的生产者",
            "枚举结果不是事务快照",
            "精确返回 not-found",
            "权限、损坏、身份漂移和其它 I/O 错误继续失败",
            "不能统一忽略成临时文件消失",
            "只有新鲜稳定重扫与生产者终态清单一致时才能宣告成功",
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

        with tempfile.TemporaryDirectory(prefix="project-steward-storage-template-") as temporary:
            project = Path(temporary)
            write_storage_fixture(project)
            adopted = subprocess.run(
                [
                    sys.executable,
                    str(TEMPLATES),
                    "adopt",
                    str(project),
                    "--template",
                    "managed-runtime-artifacts",
                    "--compact",
                ],
                cwd=SKILL_ROOT,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(0, adopted.returncode, adopted.stderr)
            profile = json.loads(
                (project / ".project-steward" / "project.json").read_text(encoding="utf-8")
            )
            selected = {item["id"]: item["version"] for item in profile["templates"]}
            self.assertEqual("1.3.0", selected["managed-runtime-artifacts"])
            self.assertEqual("2.6.0", profile["catalog_version"])
            self.assertEqual(
                "required-and-blocking",
                profile["decisions"]["runtime_artifact_preflight"],
            )

    def test_review_reports_static_references_without_running_project(self) -> None:
        with tempfile.TemporaryDirectory(prefix="project-steward-storage-") as temporary:
            project = Path(temporary)
            contract = write_storage_fixture(project)
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
            payload = json.loads(passed.stdout)
            self.assertEqual("project-steward-production-storage-review/v3", payload["schema"])
            self.assertEqual("static_checks_passed", payload["status"])
            self.assertEqual("static", payload["verification_level"])
            self.assertEqual("not_run", payload["runtime_verification"]["status"])
            self.assertEqual(
                {
                    "first-production",
                    "same-input-reuse",
                    "budget-rejection",
                    "interruption-recovery",
                    "external-root-ownership",
                    "manifest-consumer-closure",
                },
                set(payload["runtime_verification"]["required_checks"]),
            )
            self.assertEqual(
                hashlib.sha256(contract_path.read_bytes()).hexdigest(),
                payload["contract_identity"]["sha256"],
            )
            self.assertEqual(
                "src/producer.py:allocated_bytes",
                payload["producers"][0]["capacity_references"]["filesystem_allocated_bytes_source"],
            )
            self.assertEqual(
                "project-owned-external",
                payload["producers"][0]["root_source"]["scope"],
            )
            self.assertEqual(
                "user-environment-policy:tools_root",
                payload["producers"][0]["root_source"]["approved_root_source"],
            )
            self.assertEqual(
                ["src/producer.py:consume_artifact"],
                payload["producers"][0]["consumer_sources"],
            )

            contract["version"] = 2
            contract_path.write_text(json.dumps(contract, indent=2), encoding="utf-8")
            legacy = subprocess.run(
                [sys.executable, str(REVIEW), str(project), "--compact"],
                cwd=SKILL_ROOT,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(2, legacy.returncode)
            legacy_result = json.loads(legacy.stderr)
            self.assertEqual("contract_version_mismatch", legacy_result["error_code"])
            self.assertEqual(2, legacy_result["actual_contract"]["version"])
            self.assertEqual(3, legacy_result["supported_contract"]["version"])
            self.assertEqual(2, json.loads(contract_path.read_text(encoding="utf-8"))["version"])

            contract["version"] = 3
            del contract["producers"][0]["budget"]["filesystem_allocated_bytes_source"]
            contract_path.write_text(json.dumps(contract, indent=2), encoding="utf-8")
            missing_allocation = subprocess.run(
                [sys.executable, str(REVIEW), str(project), "--compact"],
                cwd=SKILL_ROOT,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(2, missing_allocation.returncode)
            self.assertIn("filesystem_allocated_bytes_source", missing_allocation.stderr)

            contract["producers"][0]["budget"]["filesystem_allocated_bytes_source"] = (
                "src/producer.py:allocated_bytes"
            )
            contract["producers"][0]["budget"]["managed_object_identity_source"] = (
                "src/producer.py:missing_identity"
            )
            contract_path.write_text(json.dumps(contract, indent=2), encoding="utf-8")
            missing_identity = subprocess.run(
                [sys.executable, str(REVIEW), str(project), "--compact"],
                cwd=SKILL_ROOT,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(2, missing_identity.returncode)
            self.assertIn("implementation token is absent", missing_identity.stderr)

            contract["producers"][0]["budget"]["managed_object_identity_source"] = (
                "src/producer.py:file_identity"
            )
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
            self.assertIn("stable config token", blocked.stderr)


if __name__ == "__main__":
    unittest.main()
