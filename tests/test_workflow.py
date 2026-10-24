# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Liangliang Chen
"""Tests for polishing/translation information conservation, warm-tone cases, and workflow documentation contracts."""

import json
import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
lint_dir = repo_root / "lint"
if str(lint_dir) not in sys.path:
    sys.path.insert(0, str(lint_dir))

from anti_ai_lint.cli import main
from anti_ai_lint.detector import analyze_text
from anti_ai_lint.fidelity import check_fidelity
from anti_ai_lint.mcp_server import handle_tool_call

CASES = Path(__file__).resolve().parent / "workflow_cases"


def read(*parts: str) -> str:
    return CASES.joinpath(*parts).read_text(encoding="utf-8")


def run_cli(argv):
    old_out, old_err = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = StringIO(), StringIO()
    try:
        try:
            code = main(argv)
        except SystemExit as exc:
            code = exc.code
        return code, sys.stdout.getvalue(), sys.stderr.getvalue()
    finally:
        sys.stdout, sys.stderr = old_out, old_err


class TestFidelityCheck(unittest.TestCase):
    def test_faithful_polish_has_no_issues(self):
        self.assertEqual(check_fidelity(read("polish", "source.md"), read("polish", "faithful.md")), [])
        report = analyze_text(read("polish", "faithful.md"), source_text=read("polish", "source.md"))
        self.assertTrue(report.passed)
        self.assertEqual(report.score, 0.0)

    def test_fabricated_polish_is_caught(self):
        issues = check_fidelity(read("polish", "source.md"), read("polish", "fabricated.md"))
        added = {i.token for i in issues if i.kind == "added"}
        self.assertEqual(added, {"3", "36"})
        self.assertFalse([i for i in issues if i.kind == "dropped"])

    def test_added_number_matching_another_source_number_is_still_caught(self):
        # The source already contains "3"; a second "3" (as in "3 weeks") must still be flagged.
        issues = check_fidelity("3 项需求延期。", "连续加班 3 周，3 项需求延期。")
        self.assertEqual([(i.kind, i.token) for i in issues], [("added", "3")])

    def test_faithful_translation_has_no_issues(self):
        src = read("translate", "source.en.md")
        self.assertEqual(check_fidelity(src, read("translate", "faithful.zh.md")), [])

    def test_fabricated_translation_is_caught(self):
        src = read("translate", "source.en.md")
        issues = check_fidelity(src, read("translate", "fabricated.zh.md"))
        self.assertEqual([(i.kind, i.token) for i in issues], [("added", "87")])

    def test_normalization_avoids_false_positives(self):
        src = "预算 1,200 元，温度 2700 K，型号 H100，样本 48 例。"
        out = "预算 1200 元，色温 2700K，型号 H100，共 48 例。"
        self.assertEqual(check_fidelity(src, out), [])
        # Fullwidth digits are normalized.
        self.assertEqual(check_fidelity("共 12 次", "共１２次"), [])

    def test_list_numbering_headings_and_footnotes_are_ignored(self):
        src = "# 标题\n\n1. 样本 48 例\n2. 随访 6 个月[^1]\n"
        out = "## 小标题\n\n- 样本 48 例\n- 随访 6 个月\n"
        self.assertEqual(check_fidelity(src, out), [])

    def test_dropped_number_is_reported_without_hard_failure(self):
        issues = check_fidelity("样本 48 例，随访 6 个月。", "样本 48 例。")
        self.assertEqual([(i.kind, i.token) for i in issues], [("dropped", "6")])
        report = analyze_text("样本 48 例。", source_text="样本 48 例，随访 6 个月。")
        self.assertTrue(report.passed)
        self.assertEqual(report.score, 3.0)

    def test_dropped_acronym_is_ignored_but_added_acronym_is_not(self):
        self.assertEqual(check_fidelity("美国国家航空航天局发布了报告。", "NASA 发布了报告。")[0].kind, "added")
        self.assertEqual(check_fidelity("NASA released a report.", "美国国家航空航天局发布了报告。"), [])

    def test_added_fact_fails_regardless_of_score_threshold(self):
        report = analyze_text("共 93 个样本", source_text="共 92 个样本", max_score=1000.0)
        self.assertFalse(report.passed)
        self.assertEqual(report.score, 8.0)

    def test_without_source_nothing_changes(self):
        text = read("polish", "fabricated.md")
        self.assertEqual(analyze_text(text).score, analyze_text(text, source_text=None).score)
        self.assertFalse([v for v in analyze_text(text).violations if v.category.startswith("fidelity")])

    def test_empty_inputs(self):
        self.assertEqual(check_fidelity("", ""), [])
        self.assertEqual([i.kind for i in check_fidelity("", "共 5 例")], ["added"])

    def test_unit_and_magnitude_equivalence(self):
        src = "峰值时延由850ms降至180ms，节约资金3000万元。"
        out = "峰值时延由0.85秒降至0.18秒，节约资金3千万元。"
        self.assertEqual(check_fidelity(src, out), [])

    def test_unit_equivalence_does_not_mask_fabricated_percentages(self):
        src = "峰值时延由850ms降至180ms，节约资金3000万元。"
        out = "峰值时延由0.85秒降至0.18秒，降低幅度达78.8%，节约资金3千万元。"
        issues = check_fidelity(src, out)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].kind, "added")
        self.assertEqual(issues[0].token, "78.8")


class TestFidelityCli(unittest.TestCase):
    def test_cli_source_flag_pass_and_fail(self):
        good = CASES / "polish" / "faithful.md"
        bad = CASES / "polish" / "fabricated.md"
        src = CASES / "polish" / "source.md"
        code, out, _ = run_cli([str(good), "--source", str(src), "--format", "hook"])
        self.assertEqual(code, 0)
        self.assertIn("PASS", out)
        code, out, _ = run_cli([str(bad), "--source", str(src), "--format", "hook"])
        self.assertEqual(code, 1)
        self.assertIn("fidelity_added", out)

    def test_cli_source_json_and_agent_formats(self):
        bad = CASES / "translate" / "fabricated.zh.md"
        src = CASES / "translate" / "source.en.md"
        code, out, _ = run_cli([str(bad), "--source", str(src), "--format", "json"])
        self.assertEqual(code, 1)
        data = json.loads(out)
        cats = [v["category"] for v in data["reports"][0]["violations"]]
        self.assertIn("fidelity_added", cats)
        code, out, _ = run_cli([str(bad), "--source", str(src), "--format", "agent"])
        self.assertIn("fidelity_added", out)

    def test_cli_source_rejects_missing_file_and_multiple_targets(self):
        good = CASES / "polish" / "faithful.md"
        code, _, err = run_cli([str(good), "--source", str(CASES / "nope.md")])
        self.assertEqual(code, 2)
        self.assertIn("--source file not found", err)
        code, _, err = run_cli([str(good), str(good), "--source", str(CASES / "polish" / "source.md")])
        self.assertEqual(code, 2)
        self.assertIn("single output file", err)
        code, _, err = run_cli([str(CASES / "polish"), "--source", str(CASES / "polish" / "source.md")])
        self.assertEqual(code, 2)

    def test_cli_source_with_stdin(self):
        src = CASES / "polish" / "source.md"
        old_stdin = sys.stdin
        sys.stdin = StringIO(read("polish", "faithful.md"))
        try:
            code, out, _ = run_cli(["--source", str(src), "--format", "hook"])
        finally:
            sys.stdin = old_stdin
        self.assertEqual(code, 0)
        self.assertIn("PASS", out)

    def test_cli_source_non_utf8_does_not_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src.md"
            src.write_bytes("共 5 例 ".encode("utf-8") + b"\xff")
            out_file = Path(tmp) / "out.md"
            out_file.write_text("共 5 例。", encoding="utf-8")
            code, _, _ = run_cli([str(out_file), "--source", str(src), "--format", "hook"])
            self.assertEqual(code, 0)


class TestFidelityMcp(unittest.TestCase):
    def test_lint_prose_accepts_source_text_and_source_path(self):
        res = handle_tool_call("lint_prose", {"text": "共 93 个样本", "source_text": "共 92 个样本"})
        self.assertTrue(res["isError"])
        payload = json.loads(res["content"][0]["text"])
        self.assertIn("fidelity_added", [v["category"] for v in payload["violations"]])

        res = handle_tool_call(
            "lint_prose",
            {"text": read("polish", "faithful.md"), "source_path": str(CASES / "polish" / "source.md")},
        )
        self.assertFalse(res["isError"])

        res = handle_tool_call("lint_prose", {"text": "共 5 例", "source_path": str(CASES / "missing.md")})
        self.assertTrue(res["isError"])
        self.assertIn("source file not found", res["content"][0]["text"])

    def test_style_contracts_for_warm_and_fidelity(self):
        for lang in ("zh", "en"):
            for genre in ("warm", "fidelity"):
                res = handle_tool_call("get_style_contract", {"genre": genre, "lang": lang})
                self.assertFalse(res["isError"])
                text = res["content"][0]["text"]
                self.assertGreater(len(text), 200)
        zh_fid = handle_tool_call("get_style_contract", {"genre": "fidelity", "lang": "zh"})["content"][0]["text"]
        self.assertIn("--source", zh_fid)
        en_warm = handle_tool_call("get_style_contract", {"genre": "warm", "lang": "en"})["content"][0]["text"]
        self.assertIn("Never fabricate", en_warm)

    def test_remediation_for_fidelity_categories(self):
        for cat in ("fidelity_added", "fidelity_dropped"):
            res = handle_tool_call("remediate_violation", {"category": cat, "match_text": "36"})
            self.assertIn("信息守恒", res["content"][0]["text"])


class TestWarmToneCases(unittest.TestCase):
    def test_ai_fake_emotion_fails_gate(self):
        report = analyze_text(read("warm", "ai_fake_emotion.md"))
        self.assertFalse(report.passed)
        self.assertGreater(report.score, 10.0)

    def test_objective_and_warm_versions_both_pass_gate(self):
        for name in ("objective.md", "warm_human_touch.md"):
            report = analyze_text(read("warm", name))
            self.assertTrue(report.passed, name)
            self.assertEqual(report.score, 0.0, name)

    def test_warm_version_is_not_just_a_data_dump(self):
        def prose(name):
            return "\n".join(l for l in read("warm", name).splitlines() if not l.startswith("<!--"))

        warm = prose("warm_human_touch.md")
        objective = prose("objective.md")
        # Sensory and trade-off detail is carried by concrete nouns, with no exclamation marks or mood adjectives.
        self.assertNotIn("！", warm)
        self.assertNotIn("!", warm)
        self.assertIn("代价", warm)
        self.assertNotIn("代价", objective)


class TestWorkflowDocumentation(unittest.TestCase):
    def setUp(self):
        self.skill = (repo_root / "skill" / "anti-ai-copywriting" / "SKILL.md").read_text(encoding="utf-8")

    def test_skill_defines_routing_conservation_and_tone_protocol(self):
        for needle in (
            "## 0. 任务分流、信息守恒与温感交互协议",
            "### 0.2 信息守恒公理",
            "### 0.3 温感交互协议",
            "零新增事实",
            "零误删事实",
            "断言强度不变",
            "只用真实素材",
            "【待补：……】",
            "--source",
            "ISO 17100:2015",
            "ISO 18587:2017",
            "GB/T 19363.1-2008",
        ):
            self.assertIn(needle, self.skill)

    def test_polish_and_translate_never_trigger_tone_question(self):
        section = self.skill.split("### 0.1", 1)[1].split("### 0.2", 1)[0]
        for task in ("润色 Polishing", "翻译 Translation", "评审 Review"):
            row = next(line for line in section.splitlines() if task in line)
            self.assertTrue(row.rstrip().endswith("**否** |"), task)

    def test_rules_snippets_carry_routing_and_no_fabrication(self):
        for name in ("AGENTS.snippet.zh.md", "AGENTS.snippet.en.md", "AGENTS.snippet.md"):
            text = (repo_root / "rules" / name).read_text(encoding="utf-8")
            self.assertIn("--source", text, name)
            self.assertIn("<auto_trigger>", text, name)
            lowered = text.lower()
            self.assertTrue("invent" in lowered or "编造" in text, name)
            self.assertEqual(text.count("BEGIN anti-ai-copywriting"), 1, name)
            self.assertEqual(text.count("END anti-ai-copywriting"), 1, name)

    def test_subagent_declares_modes_and_fidelity_command(self):
        text = (repo_root / "sub_agents" / "copywriting-editor" / "AGENT.md").read_text(encoding="utf-8")
        for needle in ("`polish`", "`translate`", "Never Fabricate", "--source"):
            self.assertIn(needle, text)


if __name__ == "__main__":
    unittest.main()
