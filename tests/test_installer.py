# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Liangliang Chen
"""Integration tests for install.sh and uninstall.sh."""

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent


class TestInstaller(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.fake_home = Path(self.temp_dir.name)
        self.env = os.environ.copy()
        self.env["ANTI_AI_HOME"] = str(self.fake_home)
        self.env["ANTI_AI_MANIFEST_DIR"] = str(self.fake_home / ".local" / "share" / "anti-ai-copywriting")
        self.install_sh = str(repo_root / "install.sh")
        self.uninstall_sh = str(repo_root / "uninstall.sh")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_dry_run(self):
        res = subprocess.run(
            [self.install_sh, "--dry-run", "--target", "zcode"],
            cwd=str(repo_root),
            env=self.env,
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("[Dry-Run]", res.stdout)
        # Verify no files were created
        self.assertFalse((self.fake_home / ".zcode").exists())

    def test_install_custom_dest_and_idempotence(self):
        dest_dir = self.fake_home / "custom_project"
        rule_file = dest_dir / "AGENTS.md"

        # First install
        res1 = subprocess.run(
            [self.install_sh, "--target", "generic", "--dest", str(dest_dir), "--lang", "zh"],
            cwd=str(repo_root),
            env=self.env,
            capture_output=True,
            text=True,
        )
        self.assertEqual(res1.returncode, 0)

        skill_file = dest_dir / "skill" / "anti-ai-copywriting" / "SKILL.md"
        self.assertTrue(skill_file.is_file())
        self.assertTrue(rule_file.is_file())

        content1 = rule_file.read_text(encoding="utf-8")
        self.assertEqual(content1.count("<!-- BEGIN anti-ai-copywriting"), 1)

        # Second install (idempotence check)
        res2 = subprocess.run(
            [self.install_sh, "--target", "generic", "--dest", str(dest_dir), "--lang", "zh"],
            cwd=str(repo_root),
            env=self.env,
            capture_output=True,
            text=True,
        )
        self.assertEqual(res2.returncode, 0)

        content2 = rule_file.read_text(encoding="utf-8")
        self.assertEqual(content2.count("<!-- BEGIN anti-ai-copywriting"), 1)

    def test_functional_lang_en_vs_zh(self):
        dest_zh = self.fake_home / "proj_zh"
        dest_en = self.fake_home / "proj_en"

        subprocess.run(
            [self.install_sh, "--target", "generic", "--dest", str(dest_zh), "--lang", "zh"],
            cwd=str(repo_root),
            env=self.env,
            check=True,
        )
        subprocess.run(
            [self.install_sh, "--target", "generic", "--dest", str(dest_en), "--lang", "en"],
            cwd=str(repo_root),
            env=self.env,
            check=True,
        )

        rule_zh = (dest_zh / "AGENTS.md").read_text(encoding="utf-8")
        rule_en = (dest_en / "AGENTS.md").read_text(encoding="utf-8")

        self.assertIn("自然语态与学术专业文案规则", rule_zh)
        self.assertIn("Anti-AI Copywriting & Natural English Voice Rules", rule_en)

    def test_multi_target_manifest_and_selective_uninstall(self):
        # Install zcode
        subprocess.run(
            [self.install_sh, "--target", "zcode"],
            cwd=str(repo_root),
            env=self.env,
            check=True,
        )
        # Install claude
        subprocess.run(
            [self.install_sh, "--target", "claude"],
            cwd=str(repo_root),
            env=self.env,
            check=True,
        )

        manifest_file = Path(self.env["ANTI_AI_MANIFEST_DIR"]) / "install-manifest.json"
        self.assertTrue(manifest_file.is_file())

        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
        targets = manifest.get("targets", {})
        self.assertIn("zcode", targets)
        self.assertIn("claude", targets)

        zcode_skill = self.fake_home / ".zcode" / "skills" / "anti-ai-copywriting" / "SKILL.md"
        claude_skill = self.fake_home / ".claude" / "skills" / "anti-ai-copywriting" / "SKILL.md"
        self.assertTrue(zcode_skill.is_file())
        self.assertTrue(claude_skill.is_file())

        # Uninstall only zcode
        subprocess.run(
            [self.uninstall_sh, "--target", "zcode"],
            cwd=str(repo_root),
            env=self.env,
            check=True,
        )

        # zcode should be gone, claude should remain
        self.assertFalse(zcode_skill.exists())
        self.assertTrue(claude_skill.is_file())

        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
        targets = manifest.get("targets", {})
        self.assertNotIn("zcode", targets)
        self.assertIn("claude", targets)

        # Uninstall all
        subprocess.run(
            [self.uninstall_sh, "--all"],
            cwd=str(repo_root),
            env=self.env,
            check=True,
        )

        self.assertFalse(claude_skill.exists())
        self.assertFalse(manifest_file.exists())

    def test_safe_bounded_marker_cleanup_preserves_user_rules(self):
        claude_dir = self.fake_home / ".claude"
        claude_dir.mkdir(parents=True)
        claude_rule = claude_dir / "CLAUDE.md"
        user_content = "# User Custom Instructions\nAlways be polite and helpful.\n"
        claude_rule.write_text(user_content, encoding="utf-8")

        # Install claude
        subprocess.run(
            [self.install_sh, "--target", "claude"],
            cwd=str(repo_root),
            env=self.env,
            check=True,
        )

        content_after_install = claude_rule.read_text(encoding="utf-8")
        self.assertIn("User Custom Instructions", content_after_install)
        self.assertIn("<!-- BEGIN anti-ai-copywriting", content_after_install)

        # User adds a new rule AFTER installation
        post_install_content = content_after_install + "\n# Post-install User Rule\nNever delete this custom configuration.\n"
        claude_rule.write_text(post_install_content, encoding="utf-8")

        # Uninstall
        subprocess.run(
            [self.uninstall_sh, "--target", "claude"],
            cwd=str(repo_root),
            env=self.env,
            check=True,
        )

        content_after_uninstall = claude_rule.read_text(encoding="utf-8")
        self.assertIn("User Custom Instructions", content_after_uninstall)
        self.assertIn("Post-install User Rule", content_after_uninstall)
        self.assertNotIn("<!-- BEGIN anti-ai-copywriting", content_after_uninstall)

    def test_relative_dest_normalized_to_absolute(self):
        rel_dest = "rel_proj_test"
        subprocess.run(
            [self.install_sh, "--target", "generic", "--dest", rel_dest],
            cwd=str(self.fake_home),
            env=self.env,
            check=True,
        )
        manifest_file = Path(self.env["ANTI_AI_MANIFEST_DIR"]) / "install-manifest.json"
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
        targets = manifest.get("targets", {})
        abs_dest = str((self.fake_home / rel_dest).resolve())
        self.assertIn(f"generic:{abs_dest}", targets)
        record = targets[f"generic:{abs_dest}"]
        self.assertTrue(Path(record["files"][0]).is_absolute())
        self.assertTrue(Path(record["rule_file"]).is_absolute())

    def test_deepseek_and_common_agents_install_and_uninstall(self):
        # 1. Install deepseek
        subprocess.run(
            [self.install_sh, "--target", "deepseek", "--lang", "zh"],
            cwd=str(repo_root),
            env=self.env,
            check=True,
        )
        deepseek_skill = self.fake_home / ".deepseek" / "skills" / "anti-ai-copywriting" / "SKILL.md"
        deepseek_rule = self.fake_home / ".deepseek" / "AGENTS.md"
        self.assertTrue(deepseek_skill.is_file())
        self.assertTrue(deepseek_rule.is_file())

        # 2. Install cursor with custom destination
        cursor_dest = self.fake_home / "cursor_proj"
        subprocess.run(
            [self.install_sh, "--target", "cursor", "--dest", str(cursor_dest), "--lang", "en"],
            cwd=str(repo_root),
            env=self.env,
            check=True,
        )
        cursor_skill = cursor_dest / ".cursor" / "skills" / "anti-ai-copywriting" / "SKILL.md"
        cursor_rule = cursor_dest / ".cursorrules"
        self.assertTrue(cursor_skill.is_file())
        self.assertTrue(cursor_rule.is_file())

        # 3. Install workbuddy
        subprocess.run(
            [self.install_sh, "--target", "workbuddy", "--lang", "zh"],
            cwd=str(repo_root),
            env=self.env,
            check=True,
        )
        workbuddy_rule = self.fake_home / ".workbuddy" / "prompts" / "anti-ai-rules.md"
        self.assertTrue(workbuddy_rule.is_file())

        manifest_file = Path(self.env["ANTI_AI_MANIFEST_DIR"]) / "install-manifest.json"
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
        targets = manifest.get("targets", {})
        self.assertIn("deepseek", targets)
        self.assertIn(f"cursor:{cursor_dest}", targets)
        self.assertIn("workbuddy", targets)

        # Uninstall only deepseek
        subprocess.run(
            [self.uninstall_sh, "--target", "deepseek"],
            cwd=str(repo_root),
            env=self.env,
            check=True,
        )
        self.assertFalse(deepseek_skill.exists())
        self.assertFalse(deepseek_rule.exists())
        self.assertTrue(cursor_rule.is_file())
        self.assertTrue(workbuddy_rule.is_file())

        # Uninstall all remaining
        subprocess.run(
            [self.uninstall_sh, "--all"],
            cwd=str(repo_root),
            env=self.env,
            check=True,
        )
        self.assertFalse(cursor_rule.exists())
        self.assertFalse(workbuddy_rule.exists())
        self.assertFalse(manifest_file.exists())


if __name__ == "__main__":
    unittest.main()

