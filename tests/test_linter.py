# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Liangliang Chen
"""Unit tests for anti_ai_lint detector, CLI, genre modes, and regression fixtures."""

import json
import os
import re
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
        self.fixtures_dir = Path(__file__).resolve().parent / "fixtures_glm5"
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
        scenarios = ["academic", "grant", "popsci", "social", "business", "en_academic", "polish", "translate"]
        for sc in scenarios:
            before_files = sorted(list((self.fixtures_dir / sc).glob("*before*.md")))
            after_files = sorted(list((self.fixtures_dir / sc).glob("*after*.md")))
            self.assertTrue(len(before_files) > 0, f"Missing before fixture for {sc}")
            self.assertTrue(len(after_files) > 0, f"Missing after fixture for {sc}")

            before_content = before_files[0].read_text(encoding="utf-8")
            after_content = after_files[0].read_text(encoding="utf-8")

            source_content = None
            if sc == "polish":
                source_content = (self.repo_root / "tests" / "workflow_cases" / "polish" / "source.md").read_text(encoding="utf-8")
            elif sc == "translate":
                source_content = (self.repo_root / "tests" / "workflow_cases" / "translate" / "source.en.md").read_text(encoding="utf-8")

            rep_before = analyze_text(before_content, file_path=str(before_files[0]), max_score=10.0, source_text=source_content)
            rep_after = analyze_text(after_content, file_path=str(after_files[0]), max_score=10.0, source_text=source_content)

            # In information conservation scenarios (polish & translate), solo before must fail gate due to fidelity_added
            if sc in ("polish", "translate"):
                self.assertFalse(rep_before.passed, f"Solo {sc} before should fail gate under --source")
                self.assertTrue(any(v.category == "fidelity_added" for v in rep_before.violations))

            # Assert after passes with compliant score (<= 5.0)
            self.assertTrue(
                rep_after.passed,
                f"Scenario {sc} after should pass max-score=10.0, got score {rep_after.score}"
            )
            self.assertLessEqual(
                rep_after.score, 5.0,
                f"Scenario {sc} after should have score <= 5.0, got {rep_after.score}"
            )

    def test_cli_json_output(self):
        sample = self.fixtures_dir / "academic" / "skill_tool_after.md"
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
        good = self.fixtures_dir / "academic" / "skill_tool_after.md"
        bad = self.fixtures_dir / "polish" / "solo_before.md"

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
            exit_bad = main([str(bad), "--format", "hook", "--max-score", "8.0"])
            out_bad = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout

        self.assertEqual(exit_bad, 1)
        self.assertIn("[anti-ai-lint] FAIL", out_bad)
        self.assertIn("->", out_bad)  # Contains actionable remediation suggestion

    def test_cli_agent_output(self):
        bad = self.fixtures_dir / "polish" / "solo_before.md"
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            exit_bad = main([str(bad), "--format", "agent", "--max-score", "8.0"])
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

    def test_latex_math_blocks_masked(self):
        text = (
            "Here is normal introduction prose.\n"
            "$$\n"
            "\\text{utilize} = \\int_{0}^{\\infty} f(x) dx + \\text{delve into}\n"
            "$$\n"
            "The model optimizes $x = \\text{realm}$ without error. Clean prose continues."
        )
        report = analyze_text(text)
        self.assertTrue(report.passed)
        self.assertEqual(len(report.violations), 0)

    def test_html_comments_and_tags_masked(self):
        text = (
            "Prose before comment.\n"
            "<!-- This is an internal comment mentioning 赋能 and delve into -->\n"
            "<!--\n"
            "Multiline comment containing 闭环 and 底层逻辑\n"
            "-->\n"
            '<span class="badge" title="revolutionize">Verified</span>\n'
            "Prose after HTML elements is completely clean."
        )
        report = analyze_text(text)
        self.assertTrue(report.passed)
        self.assertEqual(len(report.violations), 0)

    def test_markdown_table_separator_and_plain_mode(self):
        table_text = (
            "| Column A | Column B | Column C | Column D | Column E | Notes |\n"
            "| :------- | :------- | :------- | :------- | :------- | :---- |\n"
            "| Val 1    | Val 2    | Val 3    | Val 4    | Val 5    | Ok    |\n"
        )
        # In plain mode, table rows must not trigger sentence_length_plain
        rep = analyze_text(table_text, genre="plain")
        categories = [v.category for v in rep.violations]
        self.assertNotIn("sentence_length_plain", categories)

    def test_markdown_footnotes_sentence_splitting(self):
        text = "This empirical result is confirmed.[^1] In addition, latency remained stable.[^2]"
        sentences = split_sentences_spans(text)
        self.assertEqual(len(sentences), 2)
        self.assertEqual(sentences[0][0], "This empirical result is confirmed.[^1]")
        self.assertEqual(sentences[1][0], "In addition, latency remained stable.[^2]")

    def test_multilingual_kana_and_hangul_metrics(self):
        # Japanese Hiragana (5 chars: こんにちは) + Katakana (3 chars: テスト) = 8
        # Korean Hangul (5 chars: 안녕하세요) = 5
        # Total East Asian chars = 13
        # Latin words: Hello (1 word)
        text = "Hello こんにちは テスト 안녕하세요"
        report = analyze_text(text)
        self.assertEqual(report.metrics.latin_words, 1)
        self.assertEqual(report.metrics.cjk_count, 13)
        self.assertEqual(report.metrics.total_words, 14)

    def test_pure_punctuation_and_whitespace_edge_cases(self):
        punct = "!?,.:;——\"'“”《》！？"
        rep_punct = analyze_text(punct)
        self.assertTrue(rep_punct.passed)
        self.assertEqual(rep_punct.score, 0.0)

        whitespace = "   \n\t  \r\n   "
        rep_ws = analyze_text(whitespace)
        self.assertTrue(rep_ws.passed)
        self.assertEqual(rep_ws.score, 0.0)

    def test_genre_case_insensitivity_and_fallback(self):
        text = "实验表明该模型在各项基准上具有极其重要的现实意义与应用价值。"
        rep_upper = analyze_text(text, genre="ACADEMIC")
        self.assertIn("empty_self_praise_academic", [v.category for v in rep_upper.violations])

        rep_invalid = analyze_text(text, genre="non_existent_genre")
        self.assertEqual(rep_invalid.genre, "general")

    def test_boundary_zero_scores(self):
        clean_text = "AlphaFold2 predicts protein structures with high accuracy."
        rep_pass = analyze_text(clean_text, max_score=0.0, max_normalized_score=0.0)
        self.assertTrue(rep_pass.passed)
        self.assertEqual(rep_pass.score, 0.0)

    def test_redos_stress_test_long_prose(self):
        # 10,000 characters of benign repetitive prose without period
        long_prose = "Furthermore moreover Additionally " * 300
        # Must execute within fractions of a second without regex backtracking hang
        report = analyze_text(long_prose)
        self.assertIsNotNone(report)

    def test_wordlist_regexes_compilation_and_keys(self):
        zh_data, en_data = json.loads((self.repo_root / "wordlists" / "zh.json").read_text("utf-8")), json.loads((self.repo_root / "wordlists" / "en.json").read_text("utf-8"))
        for d, name in [(zh_data, "zh.json"), (en_data, "en.json")]:
            self.assertIn("forbidden_words", d, f"{name} missing forbidden_words")
            self.assertIn("formulaic_patterns", d, f"{name} missing formulaic_patterns")
            self.assertIn("hedging_words", d, f"{name} missing hedging_words")
            for pat_info in d["formulaic_patterns"]:
                pat = pat_info["pattern"]
                # Must compile as valid regex
                compiled = re.compile(pat)
                self.assertIsNotNone(compiled)

    def test_cli_stdin_pipe_robustness(self):
        old_stdin = sys.stdin
        old_stdout = sys.stdout
        sys.stdin = StringIO("Clean stdin prose without any clichés.")
        sys.stdout = StringIO()
        try:
            exit_code = main(["--format", "json"])
            output = sys.stdout.getvalue()
        finally:
            sys.stdin = old_stdin
            sys.stdout = old_stdout

        self.assertEqual(exit_code, 0)
        data = json.loads(output)
        self.assertEqual(data["failed_files"], 0)

    def test_math_block_multiline_start_and_end_with_prose(self):
        doc = (
            "公式如下：$$\n"
            "E = mc^2\n"
            "$$ 我们需要赋能业务。\n"
            "后续依然包含闭环。"
        )
        report = analyze_text(doc)
        words = [v.context for v in report.violations]
        self.assertTrue(any("赋能" in w for w in words), f"Failed to detect 赋能 on closing math line: {words}")
        self.assertTrue(any("闭环" in w for w in words), f"Failed to detect 闭环 on subsequent line: {words}")

    def test_html_comments_multiline_closing_with_prose(self):
        doc = (
            "<!-- comment starts\n"
            "still comment --> 这里也需要赋能。\n"
        )
        report = analyze_text(doc)
        words = [v.context for v in report.violations]
        self.assertTrue(any("赋能" in w for w in words), f"Failed to detect 赋能 after closing comment: {words}")

    def test_latex_math_environments_masked(self):
        doc = (
            "Here is an equation environment:\n"
            "\\begin{equation}\n"
            "\\text{utilize} + x = 1\n"
            "\\end{equation}\n"
            "And an align block:\n"
            "\\begin{align*}\n"
            "\\text{leverage} &= 2\n"
            "\\end{align*}\n"
            "And bracket math: \\[ \\text{delve into} \\] and inline: \\( \\text{matrix} \\).\n"
            "Normal clean prose follows."
        )
        report = analyze_text(doc)
        self.assertEqual(len(report.violations), 0, f"Math environment leaked violations: {report.violations}")

    def test_markdown_link_url_and_raw_url_masking(self):
        doc = (
            "Check [documentation](https://github.com/foo/bar/releases/tag/v1.0.0-matrix-utilize).\n"
            "Local file: [architecture](docs/matrix-pipeline.md).\n"
            "Raw URL: https://example.com/api/utilize/foster.\n"
            "[1]: https://example.com/matrix-pipeline\n"
            "Prose itself is completely clean."
        )
        report = analyze_text(doc)
        self.assertEqual(len(report.violations), 0, f"URL path leaked violations: {report.violations}")

    def test_plain_genre_thematic_breaks_and_symbols_not_exceeding_length(self):
        doc = (
            "短句陈述事实。\n"
            "--------------------------------------------------------\n"
            "********************************************************\n"
            "另外一个短句。"
        )
        report = analyze_text(doc, genre="plain")
        categories = [v.category for v in report.violations]
        self.assertNotIn("sentence_length_plain", categories)

    def test_terminal_abbreviation_sentence_splitting(self):
        text = "We brought apples, oranges, etc. In today's fast-paced world, this is a beacon of hope."
        sentences = split_sentences_spans(text)
        self.assertEqual(len(sentences), 2)
        self.assertTrue(sentences[0][0].endswith("etc."))
        self.assertTrue(sentences[1][0].startswith("In today's"))

    def test_cli_genre_case_insensitivity(self):
        old_stdin = sys.stdin
        old_stdout = sys.stdout
        sys.stdin = StringIO("Clean prose for academic testing.")
        sys.stdout = StringIO()
        try:
            code = main(["--genre", "ACADEMIC", "--format", "json"])
            output = sys.stdout.getvalue()
        finally:
            sys.stdin = old_stdin
            sys.stdout = old_stdout
        self.assertEqual(code, 0)
        data = json.loads(output)
        self.assertEqual(data["genre"], "academic")

    def test_table_and_definition_list_bold_not_counted_as_prose_bold_abuse(self):
        rows = ["| Platform | Status |", "|---|---|"]
        for i in range(15):
            rows.append(f"| **Target {i}** | Supported |")
        table_doc = "\n".join(rows) + "\n\n- **Item 1**: Definition\n- **Item 2**: Definition\n"
        report = analyze_text(table_doc)
        categories = [v.category for v in report.violations]
        self.assertNotIn("formatting_abuse", categories)

    def test_burstiness_and_rhythmic_monotony(self):
        # Monotonous text: 8 sentences of identical length (20 characters each)
        mono_text = (
            "这是第一个测试句子长度完全相同的例句。"
            "这是第二个测试句子长度完全相同的例句。"
            "这是第三个测试句子长度完全相同的例句。"
            "这是第四个测试句子长度完全相同的例句。"
            "这是第五个测试句子长度完全相同的例句。"
            "这是第六个测试句子长度完全相同的例句。"
            "这是第七个测试句子长度完全相同的例句。"
            "这是第八个测试句子长度完全相同的例句。"
        )
        rep_mono = analyze_text(mono_text)
        self.assertAlmostEqual(rep_mono.metrics.burstiness_cv, 0.0, places=2)
        categories_mono = [v.category for v in rep_mono.violations]
        self.assertIn("rhythmic_monotony", categories_mono)
        v_mono = [v for v in rep_mono.violations if v.category == "rhythmic_monotony"][0]
        self.assertEqual(v_mono.penalty, 3.5)
        self.assertIn("Monotonous", v_mono.suggestion)

        # Varied text: 7 sentences with significant length variations
        varied_text = (
            "短句斩截。"
            "这是一句比较长的具有丰富观察和复杂论证结构的句子用来测试变异系数是否达标。"
            "再来一句。"
            "然后我们深入探讨各种不同维度，但是句子长度必须有着非常显著的波动与起伏。"
            "是的。"
            "这一段的长度也是专门为了拉开标准差而设计的长句。"
            "完结。"
        )
        rep_var = analyze_text(varied_text)
        self.assertGreater(rep_var.metrics.burstiness_cv, 0.40)
        categories_var = [v.category for v in rep_var.violations]
        self.assertNotIn("rhythmic_monotony", categories_var)

        # Monotonous but fewer than 6 sentences (< 6 should not trigger)
        short_mono = (
            "这是第一个测试句子长度完全相同的例句。"
            "这是第二个测试句子长度完全相同的例句。"
            "这是第三个测试句子长度完全相同的例句。"
            "这是第四个测试句子长度完全相同的例句。"
        )
        rep_short = analyze_text(short_mono)
        categories_short = [v.category for v in rep_short.violations]
        self.assertNotIn("rhythmic_monotony", categories_short)

        # Varied text with fewer than 6 sentences: computes valid CV without triggering rhythmic_monotony
        short_varied = (
            "短句斩截。"
            "这是一个为了拉开句子长度变异系数而专门构造的相对更长一些的测试句子。"
            "第三句中等长度。"
        )
        rep_short_var = analyze_text(short_varied)
        self.assertGreater(rep_short_var.metrics.burstiness_cv, 0.20)
        self.assertNotIn("rhythmic_monotony", [v.category for v in rep_short_var.violations])

    def test_mattr_lexical_richness_metric(self):
        # Empty text
        rep_empty = analyze_text("")
        self.assertEqual(rep_empty.metrics.mattr, 0.0)

        # Repetitive token loop (low MATTR)
        rep_loop = analyze_text("the token " * 60)
        self.assertLess(rep_loop.metrics.mattr, 0.20)

        # Diverse prose (high MATTR)
        diverse_text = (
            "AlphaFold2 couples multiple sequence alignments with axial attention "
            "to predict high-resolution protein coordinate geometry without templates."
        )
        rep_div = analyze_text(diverse_text)
        self.assertGreater(rep_div.metrics.mattr, 0.80)

    def test_kobak_2024_excess_vocabulary_and_tiered_penalties(self):
        # Tier S words (penalty 5.0)
        text_tier_s = "We delve into the meticulous details as a testament to progress."
        rep_s = analyze_text(text_tier_s)
        delve_v = [v for v in rep_s.violations if "delve into" in v.message]
        self.assertEqual(len(delve_v), 1)
        self.assertEqual(delve_v[0].penalty, 5.0)

        testament_v = [v for v in rep_s.violations if "testament to" in v.message]
        self.assertEqual(len(testament_v), 1)
        self.assertEqual(testament_v[0].penalty, 5.0)

        rep_meticulous = analyze_text("The data were meticulously examined.")
        met_v = [v for v in rep_meticulous.violations if "meticulously" in v.message]
        self.assertEqual(len(met_v), 1)
        self.assertEqual(met_v[0].penalty, 5.0)

        # Tier A words (penalty 3.5)
        rep_realm = analyze_text("In this realm of physics, it plays a pivotal role.")
        realm_v = [v for v in rep_realm.violations if "realm" in v.message]
        self.assertEqual(len(realm_v), 1)
        self.assertEqual(realm_v[0].penalty, 3.5)

        # Tier B words (penalty 2.0)
        rep_robust = analyze_text("We utilize a robust framework for comprehensive evaluation.")
        utilize_v = [v for v in rep_robust.violations if "utilize" in v.message]
        self.assertEqual(len(utilize_v), 1)
        self.assertEqual(utilize_v[0].penalty, 2.0)

        robust_v = [v for v in rep_robust.violations if "robust" in v.message]
        self.assertEqual(len(robust_v), 1)
        self.assertEqual(robust_v[0].penalty, 2.0)

    def test_chinese_light_verb_constructions_expanded(self):
        # Test various light verbs and nominalized action targets including proposal examples
        samples = [
            "课题组对该系统开展了深入的分析与对比。",
            "我们展开了全面的调研并提交总结报告。",
            "专家组对该项目予以系统评估。",
            "各部门必须对安全隐患加以科学整改。",
            "针对该系统展开了全面的性能测评。",
            "团队展开了全面的安全排查。",
            "对数据进行了进一步分析。",
            "课题组对数据进行了深入而全面的调研。",
            "专家组给予了充分的评估。",
            "作出了实质性整改。",
            "进行了代码审校并记录日志。",
        ]
        for s in samples:
            rep = analyze_text(s)
            pats = [v for v in rep.violations if "轻动词名物化" in v.message]
            self.assertTrue(len(pats) >= 1, f"Failed to detect expanded LVC in: {s}")
            self.assertEqual(pats[0].penalty, 3.5)
            self.assertIn("还原为直接动作强动词", pats[0].suggestion)

    def test_mattr_stress_100k_words(self):
        # Stress test MATTR calculation on 100k tokens
        tokens = ["word" + str(i % 500) for i in range(100000)]
        big_text = " ".join(tokens)
        rep = analyze_text(big_text)
        self.assertGreater(rep.metrics.mattr, 0.0)
        self.assertLessEqual(rep.metrics.mattr, 1.0)
        # Verify 50 tokens with identical repeating cycle has MATTR 1.0
        self.assertEqual(rep.metrics.mattr, 1.0)

    def test_mcp_server_jsonrpc_protocol(self):
        from anti_ai_lint.mcp_server import process_jsonrpc_message

        # 1. initialize
        init_req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"protocolVersion": "2024-11-05"},
        }
        init_resp = process_jsonrpc_message(init_req)
        self.assertEqual(init_resp["id"], 1)
        self.assertEqual(init_resp["result"]["serverInfo"]["name"], "anti-ai-copywriting")
        self.assertIn("tools", init_resp["result"]["capabilities"])

        # 2. ping
        ping_resp = process_jsonrpc_message({"jsonrpc": "2.0", "id": 2, "method": "ping"})
        self.assertEqual(ping_resp["id"], 2)
        self.assertEqual(ping_resp["result"], {})

        # 3. tools/list
        list_resp = process_jsonrpc_message({"jsonrpc": "2.0", "id": 3, "method": "tools/list"})
        tools = list_resp["result"]["tools"]
        tool_names = [t["name"] for t in tools]
        self.assertIn("lint_prose", tool_names)
        self.assertIn("remediate_violation", tool_names)
        self.assertIn("get_style_contract", tool_names)

        # 4. tools/call -> lint_prose (clean text)
        call_lint = process_jsonrpc_message({
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "lint_prose",
                "arguments": {
                    "text": "AlphaFold2 predicts protein coordinates with high accuracy.",
                    "genre": "academic",
                },
            },
        })
        self.assertFalse(call_lint["result"]["isError"])
        lint_payload = json.loads(call_lint["result"]["content"][0]["text"])
        self.assertTrue(lint_payload["passed"])

        # 5. tools/call -> remediate_violation (Chinese buzzword)
        call_rem = process_jsonrpc_message({
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "remediate_violation",
                "arguments": {
                    "category": "forbidden_word_zh",
                    "match_text": "赋能",
                    "context": "为业务全面赋能",
                },
            },
        })
        self.assertFalse(call_rem["result"]["isError"])
        self.assertIn("支持", call_rem["result"]["content"][0]["text"])

        # 6. tools/call -> remediate_violation (Chinese LVC text)
        call_rem_lvc = process_jsonrpc_message({
            "jsonrpc": "2.0",
            "id": 51,
            "method": "tools/call",
            "params": {
                "name": "remediate_violation",
                "arguments": {
                    "category": "formulaic_pattern",
                    "match_text": "展开了全面的性能测评",
                    "context": "针对该系统展开了全面的性能测评",
                },
            },
        })
        self.assertFalse(call_rem_lvc["result"]["isError"])
        self.assertIn("文字义肢", call_rem_lvc["result"]["content"][0]["text"])
        self.assertIn("全面测评系统性能", call_rem_lvc["result"]["content"][0]["text"])

        # 7. tools/call -> get_style_contract
        call_contract = process_jsonrpc_message({
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "get_style_contract",
                "arguments": {"genre": "academic", "lang": "zh"},
            },
        })
        self.assertIn("学术专业语态公理", call_contract["result"]["content"][0]["text"])

        # 8. Invalid method returns -32601
        err_resp = process_jsonrpc_message({
            "jsonrpc": "2.0",
            "id": 99,
            "method": "non_existent_method",
        })
        self.assertEqual(err_resp["error"]["code"], -32601)

        # 9. Non-dict request returns -32600 without raising unhandled exception
        err_non_dict = process_jsonrpc_message("not a dict request")
        self.assertEqual(err_non_dict["error"]["code"], -32600)

        err_primitive = process_jsonrpc_message(12345)
        self.assertEqual(err_primitive["error"]["code"], -32600)

        # 10. Empty batch returns -32600
        err_empty_batch = process_jsonrpc_message([])
        self.assertEqual(err_empty_batch["error"]["code"], -32600)

        # 11. Valid batch request returns list of responses
        batch_resp = process_jsonrpc_message([
            {"jsonrpc": "2.0", "id": 101, "method": "ping"},
            {"jsonrpc": "2.0", "id": 102, "method": "ping"},
        ])
        self.assertIsInstance(batch_resp, list)
        self.assertEqual(len(batch_resp), 2)
        self.assertEqual(batch_resp[0]["id"], 101)
        self.assertEqual(batch_resp[1]["id"], 102)

        # 12. Tool call with invalid arguments gracefully returns tool error
        err_args_call = process_jsonrpc_message({
            "jsonrpc": "2.0",
            "id": 103,
            "method": "tools/call",
            "params": {
                "name": "lint_prose",
                "arguments": {
                    "text": "sample text",
                    "max_score": "not_a_valid_number",
                },
            },
        })
        self.assertEqual(err_args_call["id"], 103)
        self.assertFalse(err_args_call["result"].get("isError", True) is None)

    def test_cli_github_action_format(self):
        bad = self.fixtures_dir / "polish" / "solo_before.md"
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            exit_code = main([str(bad), "--format", "github", "--max-score", "8.0"])
            out = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout

        self.assertEqual(exit_code, 1)
        self.assertIn("::error file=", out)
        self.assertIn("Remediation:", out)
        self.assertIn("[anti-ai-lint] FAILED:", out)

    def test_dpo_exporter_and_dspy_optimizer_modules(self):
        from scripts.export_dpo_pairs import load_fixture_pairs, export_dpo, validate_pairs
        from scripts.dspy_optimizer import evaluate_lint_metric, load_fixtures_dataset, run_standalone_optimizer

        # Test DPO pairs loading and validation
        pairs = load_fixture_pairs(self.fixtures_dir)
        self.assertEqual(len(pairs), 8)
        valid = validate_pairs(pairs, min_rejected_score=0.0)
        self.assertTrue(valid)

        dpo_records = export_dpo(pairs, fmt="dpo")
        self.assertEqual(len(dpo_records), 8)
        self.assertIn("prompt", dpo_records[0])
        self.assertIn("chosen", dpo_records[0])
        self.assertIn("rejected", dpo_records[0])

        # Test DPO CLI entrypoint with --validate and --verify
        from scripts.export_dpo_pairs import main as dpo_main
        ret_val = dpo_main(["--validate", "--fixtures-dir", str(self.fixtures_dir)])
        self.assertEqual(ret_val, 0)
        ret_verify = dpo_main(["--verify", "--fixtures-dir", str(self.fixtures_dir)])
        self.assertEqual(ret_verify, 0)

        # Test DSPy optimizer evaluation
        dataset = load_fixtures_dataset(self.fixtures_dir)
        self.assertEqual(len(dataset), 8)
        summary = run_standalone_optimizer(dataset, iterations=1, verbose=False)
        self.assertIn("best_candidate", summary)
        self.assertEqual(summary["best_candidate"]["pass_rate"], "8/8")


if __name__ == "__main__":
    unittest.main()
