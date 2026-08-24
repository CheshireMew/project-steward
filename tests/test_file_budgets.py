from __future__ import annotations

import sys
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
SKILL_ROOT = SCRIPTS.parent
SKILL_TEXT = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
SELF_EVOLUTION_TEXT = (
    SKILL_ROOT / "references" / "skill-self-evolution-governance.md"
).read_text(encoding="utf-8")
sys.path.insert(0, str(SCRIPTS))

from check_file_budgets import (
    BYTES_PER_OUTER_TOOL_TOKEN,
    MAX_OUTER_TOOL_TOKENS,
    MAX_SKILL_CHARACTERS,
    MAX_SKILL_LINES,
    collect_file_budgets,
    estimate_outer_tool_tokens,
    main,
    validate_file_budgets,
)


class FileBudgetTests(unittest.TestCase):
    def test_estimate_rounds_utf8_bytes_up(self) -> None:
        self.assertEqual(estimate_outer_tool_tokens(0), 0)
        self.assertEqual(estimate_outer_tool_tokens(1), 1)
        self.assertEqual(estimate_outer_tool_tokens(4), 1)
        self.assertEqual(estimate_outer_tool_tokens(5), 2)

    def test_exact_limit_passes_and_one_more_byte_fails(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            exact_size = MAX_OUTER_TOOL_TOKENS * BYTES_PER_OUTER_TOOL_TOKEN
            target = root / "reference.md"
            target.write_bytes(b"a" * exact_size)
            self.assertEqual(validate_file_budgets(root), [])

            target.write_bytes(b"a" * (exact_size + 1))
            errors = validate_file_budgets(root)

        self.assertEqual(len(errors), 1)
        self.assertIn("reference.md", errors[0])
        self.assertIn("9001 estimated tokens", errors[0])

    def test_inactive_directories_and_binary_assets_are_excluded(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            for relative_path in (
                "archive/old.md",
                "artifacts/runtime.txt",
                "node_modules/dependency.md",
                "assets/preview.png",
            ):
                path = root / relative_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("inactive", encoding="utf-8")

            records = collect_file_budgets(root)

        self.assertEqual(records, [])

    def test_active_text_and_model_readable_assets_are_budgeted(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            expected = (root / "SKILL.md", root / "assets" / "catalog.json")
            for path in expected:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("active", encoding="utf-8")
            (root / "binary.dat").write_bytes(b"\xff\xfe")

            records = collect_file_budgets(root)

        self.assertEqual(
            [record.path.as_posix() for record in records],
            ["SKILL.md", "assets/catalog.json"],
        )

    def test_skill_router_exact_limits_pass_and_overflow_fails(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            skill = root / "SKILL.md"
            skill.write_text("a" * MAX_SKILL_CHARACTERS, encoding="utf-8")
            self.assertEqual(validate_file_budgets(root), [])

            skill.write_text("a" * (MAX_SKILL_CHARACTERS + 1), encoding="utf-8")
            character_errors = validate_file_budgets(root)

            skill.write_text(
                "\n".join("a" for _ in range(MAX_SKILL_LINES)),
                encoding="utf-8",
            )
            self.assertEqual(validate_file_budgets(root), [])

            skill.write_text(
                "\n".join("a" for _ in range(MAX_SKILL_LINES + 1)),
                encoding="utf-8",
            )
            line_errors = validate_file_budgets(root)

        self.assertEqual(len(character_errors), 1)
        self.assertIn("14001 characters", character_errors[0])
        self.assertEqual(len(line_errors), 1)
        self.assertIn("221 lines", line_errors[0])

    def test_skill_router_limits_do_not_apply_to_references(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "reference.md").write_text(
                "a" * (MAX_SKILL_CHARACTERS + 1),
                encoding="utf-8",
            )

            errors = validate_file_budgets(root)

        self.assertEqual(errors, [])

    def test_cli_reports_skill_usage_and_remaining_headroom(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "SKILL.md").write_text("alpha\nbeta", encoding="utf-8")
            output = StringIO()

            with redirect_stdout(output):
                result = main(["check_file_budgets.py", str(root)])

            (root / "SKILL.md").write_text(
                "a" * (MAX_SKILL_CHARACTERS + 1),
                encoding="utf-8",
            )
            failed_output = StringIO()
            with redirect_stdout(failed_output):
                failed_result = main(["check_file_budgets.py", str(root)])

        self.assertEqual(result, 0)
        self.assertIn("2/220 lines (218 remaining)", output.getvalue())
        self.assertIn("10/14000 characters (13990 remaining)", output.getvalue())
        self.assertEqual(failed_result, 1)
        self.assertIn("FILE BUDGET FAIL", failed_output.getvalue())
        self.assertIn("14001 characters", failed_output.getvalue())

    def test_budget_method_has_one_owner_and_router_only_keeps_its_gate(
        self,
    ) -> None:
        self.assertIn(
            "自我进化写入前后按 `references/skill-self-evolution-governance.md`",
            SKILL_TEXT,
        )
        self.assertIn(
            "预算算法、上限、职责迁移与失败收口由该方法唯一拥有",
            SKILL_TEXT,
        )

        for method_detail in (
            "取得全部活动 UTF-8 文本文件的完整账本",
            "硬上限为 9,000 tokens",
            "不得超过 220 行和 14,000 个字符",
            "迁移完整章节、内聚函数族或测试主题",
            "停止本次写入并重新规划",
        ):
            with self.subTest(method_detail=method_detail):
                self.assertIn(method_detail, SELF_EVOLUTION_TEXT)
                self.assertNotIn(method_detail, SKILL_TEXT)


if __name__ == "__main__":
    unittest.main()
