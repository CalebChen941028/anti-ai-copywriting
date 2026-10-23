# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Liangliang Chen
"""Unit tests for anti_ai_lint detector, CLI, genre modes, and regression fixtures."""

import json
import os
import sys
import unittest
from io import StringIO
from pathlib import Path

# Add lint directory to sys.path
repo_root = Path(__file__).resolve().parent.parent
lint_dir = repo_root / "lint"
if str(lint_dir) not in sys.path:
    sys.path.insert(0, str(lint_dir))

from anti_ai_lint import __version__
from anti_ai_lint.cli import main
from anti_ai_lint.detector import analyze_text, split_sentences_spans


class TestAntiAiLinter(unittest.TestCase):
    def setUp(self):
        self.fixtures_dir = Path(__file__).resolve().parent / "fixtures"
        self.repo_root = repo_root

    def test_empty_input(self):
        report = analyze_text("")
        self.assertTrue(report.passed)
        self.assertEqual(report.score, 0.0)
        self.assertEqual(len(report.violations), 0)

    def test_code_blocks_and_headings_ignored(self):
        text = "# 这是一个赋能的标题\n```python\n# 这是一个闭环\nx = 'delve into'\n```\n真实正文内容没有任何套话。"
        report = analyze_text(text)
        self.assertTrue(report.passed)
        self.assertEqual(len(report.violations), 0)

    def test_multiline_code_blocks_with_forbidden_words_ignored(self):
        text = (
            "Here is normal introduction prose without buzzwords.\n"
            "```python\n"
            "# Multi-line code block containing tropes:\n"
            "def empower_pipeline():\n"
            "    buzz = '赋能'\n"
            "    trope = 'delve into'\n"
            "    disclaimer = '虽然本研究还不成熟'\n"
            "```\n"
            "Follow-up prose is also completely clean."
        )
        report = analyze_text(text)
        self.assertTrue(report.passed)
        self.assertEqual(report.score, 0.0)
        self.assertEqual(len(report.violations), 0)

    def test_inline_code_masked(self):
        text = "Use the function `delve_into()` and variable `闭环` in the API. Prose continues cleanly."
        report = analyze_text(text)
        self.assertTrue(report.passed)
        self.assertEqual(report.score, 0.0)

    def test_chinese_buzzwords_detected(self):
        text = "我们要打通底层逻辑，形成完整闭环，为全行业赋能。"
        report = analyze_text(text, max_score=5.0)
        self.assertFalse(report.passed)
        self.assertGreater(report.score, 8.0)
        categories = [v.category for v in report.violations]
        self.assertIn("forbidden_word_zh", categories)

    def test_english_tropes_detected(self):
        text = "In this study, we delve into the intricate tapestry of neural networks as a testament to innovation."
        report = analyze_text(text, max_score=5.0)
        self.assertFalse(report.passed)
        categories = [v.category for v in report.violations]
        self.assertIn("forbidden_word_en", categories)

    def test_stacked_hedging(self):
        text = "该方案可能或许在某种程度上试图去尝试解决这一问题。"
        report = analyze_text(text)
        categories = [v.category for v in report.violations]
        self.assertIn("hedging_overuse", categories)

    def test_defensive_disclaimer(self):
        text = "虽然本研究还不成熟，难免存在不足，但仍具有一定参考意义。"
        report = analyze_text(text)
        categories = [v.category for v in report.violations]
        self.assertIn("defensive_disclaimer", categories)

    def test_sentence_splitting_and_precision(self):
        text = (
            "Speculative decoding improves throughput by 28.6% (95% CI 24.1–33.2; P = 0.003). "
            "It works effectively, e.g. when draft acceptance exceeds 70%. "
            "However, latency was not increased."
        )
        sentences = split_sentences_spans(text)
        # Should split into 3 sentences without breaking on 28.6%, P = 0.003, or e.g.
        self.assertEqual(len(sentences), 3)

    def test_bilingual_word_count_metrics(self):
        text = "Hello world 这是测试文本。"
        report = analyze_text(text)
        # 2 Latin words ('Hello', 'world') + 6 CJK characters ('这是测试文本') = 8 total words
        self.assertEqual(report.metrics.latin_words, 2)
        self.assertEqual(report.metrics.cjk_count, 6)
        self.assertEqual(report.metrics.total_words, 8)

    def test_remediation_suggestions_present(self):
        text = "我们要打通底层逻辑，形成完整闭环，为全行业赋能。本研究可能或许试图尝试分析数据。"
        report = analyze_text(text)
        self.assertGreater(len(report.violations), 0)
        for v in report.violations:
            self.assertIsNotNone(v.suggestion, f"Violation {v.category} missing suggestion")
            self.assertTrue(len(v.suggestion) > 0)

    def test_genre_academic_mode(self):
        text = "实验表明该模型在各项基准上具有极其重要的现实意义与应用价值。"
        rep_gen = analyze_text(text, genre="general")
        rep_acad = analyze_text(text, genre="academic")
        cats_acad = [v.category for v in rep_acad.violations]
        self.assertIn("empty_self_praise_academic", cats_acad)
        self.assertGreater(rep_acad.score, rep_gen.score)

    def test_genre_plain_mode(self):
        long_sentence = (
            "这是一个非常非常非常非常非常非常非常非常长的单句用来测试受控白话层是否能够正确检测出超出三十个字符限制的句子。"
            "此外这里包含若干模糊指标。"
        )
        rep_gen = analyze_text(long_sentence, genre="general")
        rep_plain = analyze_text(long_sentence, genre="plain")
        cats_plain = [v.category for v in rep_plain.violations]
        self.assertIn("sentence_length_plain", cats_plain)
        self.assertIn("vague_quantifier_plain", cats_plain)
        self.assertNotIn("sentence_length_plain", [v.category for v in rep_gen.violations])

    def test_normalized_score_calculation_and_filtering(self):
        text = "我们要打通底层逻辑，形成完整闭环，为全行业赋能。"
        # Score is 12.0 for ~20 words -> normalized score is ~600 per 1k words
        report = analyze_text(text, max_score=100.0, max_normalized_score=50.0)
        self.assertGreater(report.normalized_score, 100.0)
        self.assertFalse(report.passed)

        report_pass = analyze_text(text, max_score=100.0, max_normalized_score=1000.0)
        self.assertTrue(report_pass.passed)

    def test_fixtures_before_vs_after_regression(self):
        scenarios = ["academic", "grant", "popsci", "social", "business", "en_academic"]
        for sc in scenarios:
            before_files = list((self.fixtures_dir / sc).glob("*.before.md"))
            after_files = list((self.fixtures_dir / sc).glob("*.after.md"))
            self.assertTrue(len(before_files) > 0, f"Missing before fixture for {sc}")
            self.assertTrue(len(after_files) > 0, f"Missing after fixture for {sc}")

            before_content = before_files[0].read_text(encoding="utf-8")
            after_content = after_files[0].read_text(encoding="utf-8")

            rep_before = analyze_text(before_content, file_path=str(before_files[0]), max_score=10.0)
            rep_after = analyze_text(after_content, file_path=str(after_files[0]), max_score=10.0)

            # Assert before fails or has high penalty
            self.assertGreater(
                rep_before.score, 12.0,
                f"Scenario {sc} before score should be high, got {rep_before.score}"
            )
            self.assertFalse(
                rep_before.passed,
                f"Scenario {sc} before should fail max-score=10.0"
            )

            # Assert after passes with low score
            self.assertTrue(
                rep_after.passed,
                f"Scenario {sc} after should pass max-score=10.0, got score {rep_after.score}"
            )
            self.assertLessEqual(
                rep_after.score, 5.0,
                f"Scenario {sc} after should have score <= 5.0, got {rep_after.score}"
            )

    def test_cli_json_output(self):
        sample = self.fixtures_dir / "academic" / "paper.after.md"
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            exit_code = main([str(sample), "--format", "json", "--max-score", "10.0"])
            output = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout

        self.assertEqual(exit_code, 0)
        data = json.loads(output)
        self.assertEqual(data["version"], __version__)
        self.assertEqual(data["failed_files"], 0)

    def test_cli_hook_output(self):
        good = self.fixtures_dir / "academic" / "paper.after.md"
        bad = self.fixtures_dir / "academic" / "paper.before.md"

        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            exit_good = main([str(good), "--format", "hook", "--max-score", "10.0"])
            out_good = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout

        self.assertEqual(exit_good, 0)
        self.assertIn("[anti-ai-lint] PASS", out_good)

        sys.stdout = StringIO()
        try:
            exit_bad = main([str(bad), "--format", "hook", "--max-score", "10.0"])
            out_bad = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout

        self.assertEqual(exit_bad, 1)
        self.assertIn("[anti-ai-lint] FAIL", out_bad)
        self.assertIn("->", out_bad)  # Contains actionable remediation suggestion

    def test_cli_agent_output(self):
        bad = self.fixtures_dir / "academic" / "paper.before.md"
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            exit_bad = main([str(bad), "--format", "agent", "--max-score", "10.0"])
            out_bad = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout

        self.assertEqual(exit_bad, 1)
        self.assertIn("<anti-ai-lint-feedback status=\"FAILED\"", out_bad)
        self.assertIn("Remediation:", out_bad)

    def test_version_sync(self):
        version_file = (self.repo_root / "VERSION").read_text(encoding="utf-8").strip()
        self.assertEqual(version_file, __version__)

        pyproject = (self.repo_root / "lint" / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn(f'version = "{version_file}"', pyproject)

        install_sh = (self.repo_root / "install.sh").read_text(encoding="utf-8")
        self.assertIn(f'VERSION="{version_file}"', install_sh)

        snippet = (self.repo_root / "rules" / "AGENTS.snippet.md").read_text(encoding="utf-8")
        self.assertIn(f"v{version_file}", snippet)

        snippet_zh = (self.repo_root / "rules" / "AGENTS.snippet.zh.md").read_text(encoding="utf-8")
        self.assertIn(f"v{version_file}", snippet_zh)

        snippet_en = (self.repo_root / "rules" / "AGENTS.snippet.en.md").read_text(encoding="utf-8")
        self.assertIn(f"v{version_file}", snippet_en)

    def test_wordlists_sync(self):
        root_zh = json.loads((self.repo_root / "wordlists" / "zh.json").read_text(encoding="utf-8"))
        pkg_zh = json.loads((self.repo_root / "lint" / "anti_ai_lint" / "wordlists" / "zh.json").read_text(encoding="utf-8"))
        self.assertEqual(root_zh, pkg_zh)

        root_en = json.loads((self.repo_root / "wordlists" / "en.json").read_text(encoding="utf-8"))
        pkg_en = json.loads((self.repo_root / "lint" / "anti_ai_lint" / "wordlists" / "en.json").read_text(encoding="utf-8"))
        self.assertEqual(root_en, pkg_en)

    def test_code_block_four_backticks_enclosing_three_backticks(self):
        text = '````markdown\n```python\nbuzz = "赋能"\n```\n````\nClean prose follows.'
        report = analyze_text(text)
        self.assertTrue(report.passed)
        self.assertEqual(len(report.violations), 0)

    def test_code_block_inside_blockquote(self):
        text = '> ```python\n> buzz = "赋能"\n> ```\nClean prose.'
        report = analyze_text(text)
        self.assertTrue(report.passed)
        self.assertEqual(len(report.violations), 0)

    def test_double_backtick_inline_code_masked(self):
        text = "Run ``import 赋能`` to execute the module."
        report = analyze_text(text)
        self.assertTrue(report.passed)
        self.assertEqual(len(report.violations), 0)

    def test_chinese_sentence_closing_quote_preserved(self):
        text = "他说：“我们必须提高认识。”然后他离开了。"
        sentences = split_sentences_spans(text)
        self.assertEqual(len(sentences), 2)
        self.assertEqual(sentences[0][0], "他说：“我们必须提高认识。”")
        self.assertEqual(sentences[1][0], "然后他离开了。")

    def test_academic_abbreviations_sentence_splitting(self):
        text = "The U.S. President arrived. In vol. 12, no. 3, pp. 45-67, the results are clear."
        sentences = split_sentences_spans(text)
        self.assertEqual(len(sentences), 2)
        self.assertEqual(sentences[0][0], "The U.S. President arrived.")
        self.assertEqual(sentences[1][0], "In vol. 12, no. 3, pp. 45-67, the results are clear.")

    def test_plain_genre_etc_and_several_detected(self):
        text = "This method handles several tasks such as filtering, sorting, etc. without error."
        rep = analyze_text(text, genre="plain")
        cats = [v.category for v in rep.violations]
        self.assertIn("vague_quantifier_plain", cats)
        matches = [v.context for v in rep.violations if v.category == "vague_quantifier_plain"]
        self.assertTrue(any("several" in m or "etc." in m for m in matches))

    def test_no_duplicate_violations_on_overlapping_phrases(self):
        text_zh = "在当今快速发展的背景下，各行各业都在探索新技术。"
        rep_zh = analyze_text(text_zh)
        # Should report exactly 1 opening cliché violation, not 3 duplicates
        self.assertEqual(len(rep_zh.violations), 1)

        text_en = "It plays a pivotal role in modern deep learning."
        rep_en = analyze_text(text_en)
        # Should report exactly 1 cliché violation, not 3 duplicates
        self.assertEqual(len(rep_en.violations), 1)

    def test_pattern_does_not_cross_sentence_boundaries(self):
        text = "这不仅是个问题。今天天气很好。更多的人来到了现场。"
        rep = analyze_text(text)
        # Should NOT match '不仅...更...' across sentence boundaries
        formulaic_violations = [v for v in rep.violations if v.category == "formulaic_pattern"]
        self.assertEqual(len(formulaic_violations), 0)

    def test_cli_non_existent_file_exits_with_error(self):
        exit_code = main(["non_existent_document_12345.md"])
        self.assertEqual(exit_code, 1)


if __name__ == "__main__":
    unittest.main()
