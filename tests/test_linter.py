"""Unit tests for anti_ai_lint detector, CLI, and regression fixtures."""

import json
import os
import sys
import unittest
from pathlib import Path

# Add lint directory to sys.path
lint_dir = Path(__file__).resolve().parent.parent / "lint"
if str(lint_dir) not in sys.path:
    sys.path.insert(0, str(lint_dir))

from anti_ai_lint.cli import main
from anti_ai_lint.detector import analyze_text


class TestAntiAiLinter(unittest.TestCase):
    def setUp(self):
        self.fixtures_dir = Path(__file__).resolve().parent / "fixtures"

    def test_empty_input(self):
        report = analyze_text("")
        self.assertTrue(report.passed)
        self.assertEqual(report.score, 0.0)
        self.assertEqual(len(report.violations), 0)

    def test_code_blocks_and_headings_ignored(self):
        text = "# 这是一个赋能的标题\n```python\n# 这是一个闭环\nx = 'delve into'\n```\n真实正文内容没有任何套话。"
        report = analyze_text(text)
        # Heading with buzzword was skipped by clean_line startswith('#')
        self.assertTrue(report.passed)

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
        exit_code = main([str(sample), "--format", "json", "--max-score", "10.0"])
        self.assertEqual(exit_code, 0)


if __name__ == "__main__":
    unittest.main()
