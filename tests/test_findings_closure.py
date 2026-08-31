from __future__ import annotations

import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = SKILL_ROOT / "scripts" / "validate_findings_closure.py"
REFERENCE = SKILL_ROOT / "references" / "root-cause-verification-and-closure.md"


def evidence(
    evidence_id: str,
    *,
    kind: str = "user-chain",
    status: str = "pass",
) -> dict[str, object]:
    result: dict[str, object] = {
        "id": evidence_id,
        "kind": kind,
        "status": status,
        "scope": "representative current-host path",
    }
    if kind == "automated-test":
        identity = f"tests.test_product.ProductTests.{evidence_id}"
        result["expected_test_identity"] = identity
        result["collected_test_identity"] = identity
    return result


def finding(
    finding_id: str,
    *,
    state: str = "resolved",
    last_evidence: list[dict[str, object]] | None = None,
    boundaries: list[str] | None = None,
    regression: bool = False,
    disposition: str | None = None,
) -> dict[str, object]:
    result: dict[str, object] = {
        "id": finding_id,
        "title": f"Finding {finding_id}",
        "state": state,
        "last_evidence": (
            last_evidence
            if last_evidence is not None
            else [evidence(f"chain-{finding_id}")]
        ),
        "unverified_boundaries": boundaries if boundaries is not None else [],
        "claims_automated_regression": regression,
    }
    if disposition is not None:
        result["disposition"] = disposition
    return result


def event(
    event_id: str,
    *,
    status: str = "pass",
    classification: str = "product",
    blocking: bool = False,
) -> dict[str, object]:
    return {
        "id": event_id,
        "status": status,
        "scope": "representative current-host path",
        "classification": classification,
        "blocking": blocking,
        "relevance": "supports or qualifies the current result",
    }


def ledger(
    findings: list[dict[str, object]],
    validation_events: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    events = {item["id"]: item for item in (validation_events or [])}
    for item in findings:
        for proof in item["last_evidence"]:
            if proof["kind"] != "authorization" and proof["id"] not in events:
                recorded = event(proof["id"], status=proof["status"])
                recorded["scope"] = proof["scope"]
                events[proof["id"]] = recorded
    return {
        "schema": "project-steward-findings-closure/v1",
        "claim": "all-findings-resolved",
        "original_finding_ids": list(dict.fromkeys(item["id"] for item in findings)),
        "findings": findings,
        "validation_events": list(events.values()),
    }


def run_validator(
    payload: dict[str, object],
    *,
    output_format: str = "json",
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "--format", output_format],
        input=json.dumps(payload),
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
    )


class FindingsClosureTests(unittest.TestCase):
    def test_method_routes_only_prior_all_findings_claims_to_the_validator(self) -> None:
        text = REFERENCE.read_text(encoding="utf-8")
        section = text.split("### 全称结论经过确定性发现账本", 1)[1].split("### ", 1)[0]
        for phrase in (
            "scripts/validate_findings_closure.py",
            "逐项终态、最后有效证据、未验证边界和全部实际验证事件",
            "未承接既有发现账本的单点修复不调用它",
            "预期身份与测试框架实际收集身份完全相同",
            "真实用户链、测试源码存在、测试总数或计划新增测试都不能代替",
            "单列全部非通过验证事件",
            "只有状态 `0` 允许生成“全部发现已解决”",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, section)
        self.assertEqual(text.count("### 全称结论经过确定性发现账本"), 1)
        main_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        route = main_text.split("## 根因治理", 1)[1].split("## 外部工具兼容性", 1)[0]
        self.assertEqual(route.count("`references/root-cause-verification-and-closure.md`"), 1)
        self.assertTrue(VALIDATOR.is_file())

    def test_resolved_ledger_renders_stable_mapping_and_collected_regression(self) -> None:
        payload = ledger(
            [
                finding(
                    "UX-01",
                    last_evidence=[evidence("test_compare", kind="automated-test")],
                    regression=True,
                ),
                finding("UX-02", boundaries=["other operating systems"]),
            ],
            [event("final-user-chain")],
        )

        completed = run_validator(payload)

        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual("eligible", result["status"])
        self.assertTrue(result["all_findings_resolved"])
        self.assertTrue(result["closure_complete"])
        self.assertTrue(result["all_checks_passed"])
        self.assertEqual(["UX-01", "UX-02"], [item["id"] for item in result["findings"]])
        self.assertIn("| UX-01 | Finding UX-01 | resolved |", result["markdown"])
        self.assertIn("other operating systems", result["markdown"])
        self.assertIn("已证明", result["markdown"])

    def test_open_finding_is_valid_but_blocks_the_all_resolved_claim(self) -> None:
        payload = ledger(
            [
                finding("UX-01"),
                finding(
                    "UX-02",
                    state="open",
                    last_evidence=[],
                    boundaries=["current producer has not been verified"],
                ),
            ]
        )

        completed = run_validator(payload)

        self.assertEqual(completed.returncode, 1, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual("blocked", result["status"])
        self.assertFalse(result["closure_complete"])
        self.assertFalse(result["all_findings_resolved"])
        self.assertIn("UX-02: state is open", result["blockers"])

    def test_nonblocking_verifier_failure_is_preserved_without_becoming_product_failure(self) -> None:
        payload = ledger(
            [finding("UX-01")],
            [
                event(
                    "visual-verifier-2",
                    status="fail",
                    classification="verifier",
                    blocking=False,
                ),
                event("real-visible-input-chain"),
            ],
        )

        completed = run_validator(payload)

        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertTrue(result["all_findings_resolved"])
        self.assertFalse(result["all_checks_passed"])
        self.assertEqual(
            ["visual-verifier-2"],
            [item["id"] for item in result["non_pass_validation_events"]],
        )
        self.assertEqual(
            "verifier",
            result["non_pass_validation_events"][0]["classification"],
        )
        self.assertIn("visual-verifier-2", result["markdown"])

    def test_blocking_validation_event_blocks_the_all_resolved_claim(self) -> None:
        payload = ledger(
            [finding("UX-01")],
            [event("final-contract", status="unknown", blocking=True)],
        )

        completed = run_validator(payload)

        self.assertEqual(completed.returncode, 1, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertFalse(result["all_findings_resolved"])
        self.assertIn(
            "final-contract: blocking validation event is unknown",
            result["blockers"],
        )

    def test_reclassified_and_withdrawn_are_legal_closure_but_not_fixed(self) -> None:
        payload = ledger(
            [
                finding(
                    "UX-01",
                    state="reclassified",
                    last_evidence=[evidence("new-diagnosis", kind="diagnosis")],
                    disposition="new evidence disproved the original issue",
                ),
                finding(
                    "UX-02",
                    state="withdrawn",
                    last_evidence=[evidence("user-authority", kind="authorization")],
                    disposition="user explicitly removed this finding from scope",
                ),
            ]
        )

        completed = run_validator(payload)

        self.assertEqual(completed.returncode, 1, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertTrue(result["closure_complete"])
        self.assertFalse(result["all_findings_resolved"])
        self.assertIn("UX-01: state is reclassified", result["blockers"])
        self.assertIn("UX-02: state is withdrawn", result["blockers"])

    def test_user_chain_cannot_prove_a_claimed_automated_regression(self) -> None:
        payload = ledger([finding("UX-01", regression=True)])

        completed = run_validator(payload)

        self.assertEqual(completed.returncode, 2)
        error = json.loads(completed.stderr)["error"]
        self.assertEqual("ledger_contract_invalid", error["code"])
        self.assertIn("claims automated regression", error["message"])

    def test_automated_evidence_requires_the_exact_collected_identity(self) -> None:
        automated = evidence("test_compare", kind="automated-test")
        automated["collected_test_identity"] = "tests.test_product.other_test"
        payload = ledger(
            [finding("UX-01", last_evidence=[automated], regression=True)]
        )

        completed = run_validator(payload)

        self.assertEqual(completed.returncode, 2)
        error = json.loads(completed.stderr)["error"]
        self.assertIn("must match exactly", error["message"])

    def test_duplicate_stable_finding_ids_fail_closed(self) -> None:
        payload = ledger([finding("UX-01"), finding("UX-01")])

        completed = run_validator(payload)

        self.assertEqual(completed.returncode, 2)
        error = json.loads(completed.stderr)["error"]
        self.assertIn("unique stable IDs", error["message"])

    def test_markdown_mode_keeps_nonpass_event_and_eligibility_separate(self) -> None:
        payload = ledger(
            [finding("UX-01")],
            [event("old-infra", status="fail", classification="environment")],
        )

        completed = run_validator(payload, output_format="markdown")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("全称结论资格：允许", completed.stdout)
        self.assertIn("所有已执行检查均通过：否", completed.stdout)
        self.assertIn("old-infra", completed.stdout)
        self.assertIn("environment", completed.stdout)

    def test_missing_or_added_findings_cannot_change_the_original_scope(self) -> None:
        for original_ids in (["UX-01", "UX-02"], ["UX-02"]):
            with self.subTest(original_ids=original_ids):
                payload = ledger([finding("UX-01")])
                payload["original_finding_ids"] = original_ids
                completed = run_validator(payload)
                self.assertEqual(completed.returncode, 2)
                self.assertIn("match original_finding_ids exactly", completed.stderr)

    def test_output_preserves_original_order_and_disposition(self) -> None:
        payload = ledger([
            finding("UX-02"),
            finding("UX-01", state="reclassified", disposition="new evidence changed the diagnosis"),
        ])
        payload["original_finding_ids"] = ["UX-01", "UX-02"]
        completed = run_validator(payload)
        self.assertEqual(completed.returncode, 1, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual(["UX-01", "UX-02"], [item["id"] for item in result["findings"]])
        self.assertIn("new evidence changed the diagnosis", result["markdown"])

    def test_last_evidence_must_match_the_recorded_validation_event(self) -> None:
        for change in ("missing", "status", "scope", "duplicate"):
            with self.subTest(change=change):
                payload = ledger([finding("UX-01")])
                events = payload["validation_events"]
                if change == "missing":
                    events.clear()
                elif change == "duplicate":
                    events.append(copy.deepcopy(events[0]))
                else:
                    events[0][change] = "fail" if change == "status" else "another path"
                self.assertEqual(run_validator(payload).returncode, 2)

    def test_invalid_contract_fields_fail_with_structured_errors(self) -> None:
        base = ledger([finding("UX-01")])
        cases = []
        for key, value in (
            ("schema", "unknown/v2"),
            ("claim", "single-finding-status"),
            ("original_finding_ids", []),
            ("original_finding_ids", ["UX-01", "UX-01"]),
            ("findings", []),
            ("extra_field", True),
        ):
            payload = copy.deepcopy(base)
            payload[key] = value
            cases.append(payload)
        for key, value in (
            ("id", " "),
            ("state", "done"),
            ("last_evidence", []),
            ("unverified_boundaries", "none"),
            ("claims_automated_regression", "false"),
        ):
            payload = copy.deepcopy(base)
            payload["findings"][0][key] = value
            cases.append(payload)
        for index, payload in enumerate(cases):
            with self.subTest(case=index):
                completed = run_validator(payload)
                self.assertEqual(completed.returncode, 2)
                self.assertEqual("", completed.stdout)
                self.assertEqual("invalid", json.loads(completed.stderr)["status"])

    def test_missing_collection_identity_and_failed_evidence_cannot_prove_regression(self) -> None:
        for change in ("missing", "failed"):
            with self.subTest(change=change):
                proof = evidence("regression", kind="automated-test")
                if change == "missing":
                    del proof["collected_test_identity"]
                else:
                    proof["status"] = "fail"
                completed = run_validator(ledger([
                    finding("UX-01", last_evidence=[proof], regression=True)
                ]))
                self.assertEqual(completed.returncode, 2)

    def test_blocked_and_unverified_remain_distinct_from_resolved(self) -> None:
        for state in ("blocked", "unverified"):
            with self.subTest(state=state):
                completed = run_validator(ledger([
                    finding("UX-01", state=state, boundaries=["external condition"],
                            disposition="requires external evidence")
                ]))
                self.assertEqual(completed.returncode, 1, completed.stderr)
                result = json.loads(completed.stdout)
                self.assertFalse(result["all_findings_resolved"])
                self.assertEqual(state == "blocked", result["closure_complete"])

    def test_withdrawal_requires_explicit_authorization_evidence(self) -> None:
        completed = run_validator(ledger([
            finding("UX-01", state="withdrawn", disposition="not currently tested")
        ]))
        self.assertEqual(completed.returncode, 2)
        self.assertIn("requires passing authorization evidence", completed.stderr)

    def test_malformed_or_ambiguous_json_fails_closed(self) -> None:
        for raw in ("{", '{"schema":"first","schema":"second"}', '{"schema": NaN}'):
            with self.subTest(raw=raw):
                completed = subprocess.run(
                    [sys.executable, str(VALIDATOR)], input=raw,
                    capture_output=True, text=True, encoding="utf-8", timeout=30,
                )
                self.assertEqual(completed.returncode, 2)
                self.assertEqual("invalid", json.loads(completed.stderr)["status"])


if __name__ == "__main__":
    unittest.main()
