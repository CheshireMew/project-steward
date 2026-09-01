from __future__ import annotations

import ast
import re
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
MAIN_TEXT = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
AGENT_TEXT = (
    SKILL_ROOT / "agents" / "openai.yaml"
).read_text(encoding="utf-8")
LEARNING_TEXT = (
    SKILL_ROOT
    / "references"
    / "conversation-learning-and-self-evolution.md"
).read_text(encoding="utf-8")
SOURCE_AUTHORITY_TEXT = (
    SKILL_ROOT / "references" / "conversation-source-authority.md"
).read_text(encoding="utf-8")
SOURCE_AUTHORITY_ENTRY = (
    "公开对话、上下文来源、过程事件及其权限归因，固定前置完整读取 "
    "`conversation-source-authority.md`；本文件不维护第二套来源权限规则。"
)
LEARNING_TEXT = LEARNING_TEXT.replace(
    SOURCE_AUTHORITY_ENTRY,
    SOURCE_AUTHORITY_ENTRY + "\n\n" + SOURCE_AUTHORITY_TEXT,
    1,
)
PUBLICATION_TEXT = (
    SKILL_ROOT / "references" / "repository-publication.md"
).read_text(encoding="utf-8")
PREVENTION_TEXT = (
    SKILL_ROOT / "references" / "change-prevention.md"
).read_text(encoding="utf-8")
REMEDIATION_TEXT = (
    SKILL_ROOT / "references" / "root-cause-remediation.md"
).read_text(encoding="utf-8")
DESKTOP_TEXT = (
    SKILL_ROOT / "references" / "desktop-app-governance.md"
).read_text(encoding="utf-8")
IMPLEMENTATION_TEXT = (
    SKILL_ROOT / "references" / "implementation-review.md"
).read_text(encoding="utf-8")
PRODUCT_EXPERIENCE_TEXT = (
    SKILL_ROOT / "references" / "product-experience-governance.md"
).read_text(encoding="utf-8")
DESIGN_METHOD_TEXT = (
    SKILL_ROOT / "references" / "design-method.md"
).read_text(encoding="utf-8")
INTERACTION_MOTION_TEXT = (
    SKILL_ROOT / "references" / "interaction-motion.md"
).read_text(encoding="utf-8")
LAYOUT_RESPONSIVE_TEXT = (
    SKILL_ROOT / "references" / "layout-responsive.md"
).read_text(encoding="utf-8")
INTERFACE_PROBLEM_TEXT = (
    SKILL_ROOT / "references" / "interface-problem-patterns.md"
).read_text(encoding="utf-8")
LOG_TEXT = (
    SKILL_ROOT / "references" / "log-audit-standard.md"
).read_text(encoding="utf-8")
USER_ENVIRONMENT_TEXT = (
    SKILL_ROOT / "references" / "user-environment-governance.md"
).read_text(encoding="utf-8")
HARD_DIAGNOSTIC_TEXT = (
    SKILL_ROOT / "references" / "hard-to-reproduce-diagnostics.md"
).read_text(encoding="utf-8")
PROJECT_AUDIT_TEXT = (
    SKILL_ROOT / "references" / "project-audit.md"
).read_text(encoding="utf-8")
STRUCTURED_DATA_TEXT = (
    SKILL_ROOT / "references" / "structured-data-boundary.md"
).read_text(encoding="utf-8")
MODEL_OPERATION_TEXT = (
    SKILL_ROOT / "references" / "model-mediated-operation-governance.md"
).read_text(encoding="utf-8")
DURABLE_OPERATION_TEXT = (
    SKILL_ROOT / "references" / "durable-operation-governance.md"
).read_text(encoding="utf-8")
PROJECT_RESEARCH_TEXT = (
    SKILL_ROOT / "references" / "project-research.md"
).read_text(encoding="utf-8")
UX_DESIGN_TEXT = (
    SKILL_ROOT / "references" / "ux-design.md"
).read_text(encoding="utf-8")
LOCAL_WORKSPACE_TEXT = (
    SKILL_ROOT / "references" / "local-file-workspace-governance.md"
).read_text(encoding="utf-8")



LEARNING_TEXT += (SKILL_ROOT / "references" / "skill-self-evolution-governance.md").read_text(encoding="utf-8")
PUBLICATION_TEXT += (SKILL_ROOT / "references" / "repository-publication-execution.md").read_text(encoding="utf-8")
DESKTOP_TEXT += (SKILL_ROOT / "references" / "desktop-window-lifecycle-and-verification.md").read_text(encoding="utf-8")
PREVENTION_TEXT += "".join(
    (SKILL_ROOT / "references" / name).read_text(encoding="utf-8")
    for name in (
        "change-prevention-state-and-capability.md",
        "change-prevention-delivery-boundaries.md",
        "change-prevention-verification.md",
    )
)
REMEDIATION_TEXT += (SKILL_ROOT / "references" / "root-cause-verification-and-closure.md").read_text(encoding="utf-8")
IMPLEMENTATION_TEXT += (SKILL_ROOT / "references" / "implementation-review-visual-evidence.md").read_text(encoding="utf-8")
INTERACTION_MOTION_TEXT += (SKILL_ROOT / "references" / "interaction-navigation-and-media-lifecycle.md").read_text(encoding="utf-8")
PROJECT_AUDIT_TEXT += (SKILL_ROOT / "references" / "project-audit-release-and-evidence.md").read_text(encoding="utf-8")
