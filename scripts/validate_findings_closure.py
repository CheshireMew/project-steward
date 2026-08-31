#!/usr/bin/env python3
"""Validate and render a fail-closed findings closure ledger."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


INPUT_SCHEMA = "project-steward-findings-closure/v1"
RESULT_SCHEMA = "project-steward-findings-closure-result/v1"
CLAIM = "all-findings-resolved"
STATES = {
    "resolved",
    "reclassified",
    "withdrawn",
    "blocked",
    "unverified",
    "open",
}
TERMINAL_STATES = {"resolved", "reclassified", "withdrawn", "blocked"}
SUPPORTED_CLOSED_STATES = {"resolved", "reclassified", "withdrawn"}
RESOLVED_STATES = {"resolved"}
EVIDENCE_KINDS = {
    "automated-test",
    "user-chain",
    "static-check",
    "runtime",
    "manual-review",
    "authorization",
    "diagnosis",
}
STATUSES = {"pass", "fail", "blocked", "unknown", "not-run"}
CLASSIFICATIONS = {"product", "verifier", "environment", "scope", "other"}
VALIDATION_KINDS = EVIDENCE_KINDS - {"authorization"}


class ContractError(ValueError):
    pass


def _mapping(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractError(f"{label} must be an object")
    return value


def _list(value: object, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise ContractError(f"{label} must be an array")
    return value


def _string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{label} must be a non-empty string")
    return value.strip()


def _boolean(value: object, label: str) -> bool:
    if not isinstance(value, bool):
        raise ContractError(f"{label} must be a boolean")
    return value


def _only_keys(value: dict[str, Any], allowed: set[str], label: str) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise ContractError(f"{label} has unknown fields: {', '.join(unknown)}")


def _string_list(value: object, label: str) -> list[str]:
    items = _list(value, label)
    result = [_string(item, f"{label}[{index}]") for index, item in enumerate(items)]
    if len(result) != len(set(result)):
        raise ContractError(f"{label} must not contain duplicates")
    return result


def _evidence(value: object, label: str) -> dict[str, Any]:
    item = _mapping(value, label)
    _only_keys(
        item,
        {
            "id",
            "kind",
            "status",
            "scope",
            "expected_test_identity",
            "collected_test_identity",
        },
        label,
    )
    evidence_id = _string(item.get("id"), f"{label}.id")
    kind = _string(item.get("kind"), f"{label}.kind")
    if kind not in EVIDENCE_KINDS:
        raise ContractError(f"{label}.kind is unsupported: {kind}")
    status = _string(item.get("status"), f"{label}.status")
    if status not in STATUSES:
        raise ContractError(f"{label}.status is unsupported: {status}")
    scope = _string(item.get("scope"), f"{label}.scope")
    expected = item.get("expected_test_identity")
    collected = item.get("collected_test_identity")
    if kind == "automated-test":
        expected_identity = _string(expected, f"{label}.expected_test_identity")
        collected_identity = _string(collected, f"{label}.collected_test_identity")
        if expected_identity != collected_identity:
            raise ContractError(
                f"{label} expected and collected test identities must match exactly"
            )
    elif expected is not None or collected is not None:
        raise ContractError(
            f"{label} may carry test identities only when kind is automated-test"
        )
    return {
        "id": evidence_id,
        "kind": kind,
        "status": status,
        "scope": scope,
        **(
            {
                "expected_test_identity": expected_identity,
                "collected_test_identity": collected_identity,
            }
            if kind == "automated-test"
            else {}
        ),
    }


def _finding(value: object, index: int) -> dict[str, Any]:
    label = f"findings[{index}]"
    item = _mapping(value, label)
    _only_keys(
        item,
        {
            "id",
            "title",
            "state",
            "last_evidence",
            "unverified_boundaries",
            "disposition",
            "claims_automated_regression",
        },
        label,
    )
    finding_id = _string(item.get("id"), f"{label}.id")
    title = _string(item.get("title"), f"{label}.title")
    state = _string(item.get("state"), f"{label}.state")
    if state not in STATES:
        raise ContractError(f"{label}.state is unsupported: {state}")
    evidence = [
        _evidence(entry, f"{label}.last_evidence[{evidence_index}]")
        for evidence_index, entry in enumerate(
            _list(item.get("last_evidence"), f"{label}.last_evidence")
        )
    ]
    evidence_ids = [entry["id"] for entry in evidence]
    if len(evidence_ids) != len(set(evidence_ids)):
        raise ContractError(f"{label}.last_evidence has duplicate evidence IDs")
    boundaries = _string_list(
        item.get("unverified_boundaries"),
        f"{label}.unverified_boundaries",
    )
    regression_claimed = _boolean(
        item.get("claims_automated_regression"),
        f"{label}.claims_automated_regression",
    )
    disposition_value = item.get("disposition")
    disposition = (
        _string(disposition_value, f"{label}.disposition")
        if disposition_value is not None
        else None
    )

    if state in TERMINAL_STATES and not evidence:
        raise ContractError(f"{label} terminal state requires last_evidence")
    if state in SUPPORTED_CLOSED_STATES and any(
        entry["status"] != "pass" for entry in evidence
    ):
        raise ContractError(f"{label} resolved state may use only passing last evidence")
    if state in {"reclassified", "withdrawn", "blocked"} and disposition is None:
        raise ContractError(f"{label}.{state} requires disposition")
    if state == "withdrawn" and not any(
        entry["kind"] == "authorization" and entry["status"] == "pass"
        for entry in evidence
    ):
        raise ContractError(f"{label}.withdrawn requires passing authorization evidence")
    if state in {"blocked", "unverified", "open"} and not boundaries:
        raise ContractError(f"{label}.{state} requires an unverified boundary")

    regression_evidence = [
        entry
        for entry in evidence
        if entry["kind"] == "automated-test" and entry["status"] == "pass"
    ]
    if regression_claimed and not regression_evidence:
        raise ContractError(
            f"{label} claims automated regression without passing collected test evidence"
        )

    return {
        "id": finding_id,
        "title": title,
        "state": state,
        "last_evidence": evidence,
        "unverified_boundaries": boundaries,
        "disposition": disposition,
        "claims_automated_regression": regression_claimed,
        "automated_regression_proven": bool(regression_evidence),
    }


def _validation_event(value: object, index: int) -> dict[str, Any]:
    label = f"validation_events[{index}]"
    item = _mapping(value, label)
    _only_keys(
        item,
        {"id", "status", "scope", "classification", "blocking", "relevance"},
        label,
    )
    event_id = _string(item.get("id"), f"{label}.id")
    status = _string(item.get("status"), f"{label}.status")
    if status not in STATUSES:
        raise ContractError(f"{label}.status is unsupported: {status}")
    classification = _string(item.get("classification"), f"{label}.classification")
    if classification not in CLASSIFICATIONS:
        raise ContractError(
            f"{label}.classification is unsupported: {classification}"
        )
    return {
        "id": event_id,
        "status": status,
        "scope": _string(item.get("scope"), f"{label}.scope"),
        "classification": classification,
        "blocking": _boolean(item.get("blocking"), f"{label}.blocking"),
        "relevance": _string(item.get("relevance"), f"{label}.relevance"),
    }


def close_ledger(payload: object) -> dict[str, Any]:
    root = _mapping(payload, "root")
    _only_keys(
        root,
        {"schema", "claim", "original_finding_ids", "findings", "validation_events"},
        "root",
    )
    schema = _string(root.get("schema"), "schema")
    if schema != INPUT_SCHEMA:
        raise ContractError(f"schema must be {INPUT_SCHEMA}")
    claim = _string(root.get("claim"), "claim")
    if claim != CLAIM:
        raise ContractError(f"claim must be {CLAIM}")
    original_ids = _string_list(root.get("original_finding_ids"), "original_finding_ids")
    if not original_ids:
        raise ContractError("original_finding_ids must not be empty")

    findings = [
        _finding(item, index)
        for index, item in enumerate(_list(root.get("findings"), "findings"))
    ]
    if not findings:
        raise ContractError("findings must contain at least one item")
    finding_ids = [item["id"] for item in findings]
    if len(finding_ids) != len(set(finding_ids)):
        raise ContractError("findings must use unique stable IDs")
    if set(finding_ids) != set(original_ids):
        raise ContractError("findings must match original_finding_ids exactly")
    findings_by_id = {item["id"]: item for item in findings}
    findings = [findings_by_id[finding_id] for finding_id in original_ids]

    events = [
        _validation_event(item, index)
        for index, item in enumerate(
            _list(root.get("validation_events"), "validation_events")
        )
    ]
    event_ids = [item["id"] for item in events]
    if len(event_ids) != len(set(event_ids)):
        raise ContractError("validation_events must use unique IDs")
    events_by_id = {item["id"]: item for item in events}
    evidence_by_id: dict[str, dict[str, Any]] = {}
    for finding in findings:
        for evidence in finding["last_evidence"]:
            evidence_id = evidence["id"]
            if evidence_id in evidence_by_id and evidence_by_id[evidence_id] != evidence:
                raise ContractError(f"evidence ID {evidence_id} has conflicting records")
            evidence_by_id[evidence_id] = evidence
            if evidence["kind"] not in VALIDATION_KINDS:
                continue
            recorded = events_by_id.get(evidence_id)
            if recorded is None:
                raise ContractError(f"evidence {evidence_id} has no validation event")
            if (recorded["status"], recorded["scope"]) != (
                evidence["status"], evidence["scope"]
            ):
                raise ContractError(f"evidence {evidence_id} contradicts its validation event")

    non_pass_events = [item for item in events if item["status"] != "pass"]
    blockers = [
        f"{item['id']}: state is {item['state']}"
        for item in findings
        if item["state"] not in RESOLVED_STATES
    ]
    blockers.extend(
        f"{item['id']}: blocking validation event is {item['status']}"
        for item in non_pass_events
        if item["blocking"]
    )
    closure_complete = all(item["state"] in TERMINAL_STATES for item in findings)
    all_findings_resolved = not blockers and all(
        item["state"] in RESOLVED_STATES for item in findings
    )
    all_checks_passed = bool(events) and not non_pass_events

    result = {
        "schema": RESULT_SCHEMA,
        "status": "eligible" if all_findings_resolved else "blocked",
        "claim": claim,
        "original_finding_ids": original_ids,
        "verification_scope": "supplied-ledger-consistency-only",
        "closure_complete": closure_complete,
        "all_findings_resolved": all_findings_resolved,
        "validation_events_recorded": len(events),
        "all_checks_passed": all_checks_passed,
        "findings": findings,
        "non_pass_validation_events": non_pass_events,
        "blockers": blockers,
    }
    result["markdown"] = render_markdown(result)
    return result


def _cell(value: object) -> str:
    text = str(value).replace("\r", " ").replace("\n", " ").replace("|", "\\|")
    return " ".join(text.split())


def render_markdown(result: dict[str, Any]) -> str:
    eligibility = "允许" if result["all_findings_resolved"] else "不允许"
    closure = "完整" if result["closure_complete"] else "未闭环"
    if not result["validation_events_recorded"]:
        checks = "无验证事件记录"
    else:
        checks = "是" if result["all_checks_passed"] else "否"
    lines = [
        "# 发现结项",
        "",
        f"- 全称结论资格：{eligibility}",
        f"- 逐项闭环：{closure}",
        f"- 所有已执行检查均通过：{checks}",
        "",
        "本结果只校验输入账本的一致性，不独立证明原始记录完整、证据真实或新鲜。",
        "",
        "| 稳定发现 ID | 标题 | 最终状态 | 最后一次有效证据 | 未验证边界 | 自动回归保护 | 处置说明 |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for finding in result["findings"]:
        evidence = "; ".join(
            f"{item['id']} [{item['kind']}/{item['status']}]"
            for item in finding["last_evidence"]
        ) or "无"
        boundaries = "; ".join(finding["unverified_boundaries"]) or "无"
        regression = (
            "已证明"
            if finding["claims_automated_regression"]
            else "未声明"
        )
        lines.append(
            "| "
            + " | ".join(
                _cell(value)
                for value in (
                    finding["id"],
                    finding["title"],
                    finding["state"],
                    evidence,
                    boundaries,
                    regression,
                    finding["disposition"] or "无",
                )
            )
            + " |"
        )
    lines.extend(["", "## 非通过验证事件", ""])
    if result["non_pass_validation_events"]:
        lines.extend(
            [
                "| 身份 | 状态 | 范围 | 分类 | 是否阻塞 | 相关性 |",
                "| --- | --- | --- | --- | --- | --- |",
            ]
        )
        for event in result["non_pass_validation_events"]:
            lines.append(
                "| "
                + " | ".join(
                    _cell(value)
                    for value in (
                        event["id"],
                        event["status"],
                        event["scope"],
                        event["classification"],
                        "是" if event["blocking"] else "否",
                        event["relevance"],
                    )
                )
                + " |"
            )
    else:
        lines.append("无。")
    if result["blockers"]:
        lines.extend(["", "## 阻塞", ""])
        lines.extend(f"- {_cell(item)}" for item in result["blockers"])
    return "\n".join(lines) + "\n"


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ContractError(f"duplicate JSON field: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ContractError(f"non-finite JSON constant: {value}")


def _read_payload(input_path: str) -> object:
    text = sys.stdin.read() if input_path == "-" else Path(input_path).read_text(encoding="utf-8")
    try:
        return json.loads(
            text, object_pairs_hook=_unique_object, parse_constant=_reject_constant
        )
    except json.JSONDecodeError as error:
        raise ContractError(f"input is not valid JSON: {error.msg}") from error


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="-", help="JSON ledger path, or - for stdin")
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument("--compact", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = close_ledger(_read_payload(args.input))
    except (OSError, UnicodeError, ContractError) as error:
        payload = {
            "schema": RESULT_SCHEMA,
            "status": "invalid",
            "error": {"code": "ledger_contract_invalid", "message": str(error)},
        }
        print(json.dumps(payload, ensure_ascii=False), file=sys.stderr)
        return 2

    if args.format == "markdown":
        print(result["markdown"], end="")
    else:
        print(
            json.dumps(
                result,
                ensure_ascii=False,
                indent=None if args.compact else 2,
            )
        )
    return 0 if result["all_findings_resolved"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
