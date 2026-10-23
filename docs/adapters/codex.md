# Codex Adapter Guide

[English](codex.md) | [简体中文](codex.zh-CN.md)

## Overview

Codex CLI and autonomous code agents read instructions and guidelines from `AGENTS.md` in your repository root or home configuration directory (`~/.codex/AGENTS.md`).

---

## 1. Installation

Run the unified installer specifying the `codex` target:

```bash
# Global user installation
./install.sh --target codex --lang en

# Local workspace installation
./install.sh --target codex --dest /path/to/project --lang en
```

This will:
1. Copy `SKILL.md` to `~/.codex/skills/anti-ai-copywriting/SKILL.md` (or workspace directory).
2. Inject bounded rules into `AGENTS.md` with explicit `<auto_trigger>` directives.
3. Track installation in multi-target manifest `~/.local/share/anti-ai-copywriting/install-manifest.json`.

---

## 2. In-Loop Verification Hook (Harness² c8)

Codex supports in-loop execution hooks. You can link or copy `.codex/hooks.json` to enable post-tool prose verification:

```json
{
  "$schema": "https://raw.githubusercontent.com/google-research/harness2/main/schemas/hooks.json",
  "version": "1.0.0",
  "hooks": [
    {
      "id": "anti-ai-prose-verifier",
      "event": "post_tool_execution",
      "tools": ["write_to_file", "replace_file_content", "apply_diff"],
      "file_patterns": ["*.md", "*.txt", "*.markdown"],
      "command": "python3 -m anti_ai_lint.cli \"${file_path}\" --format hook --max-score 10.0",
      "on_failure": "block_and_feedback",
      "feedback_format": "agent"
    }
  ]
}
```

Whenever the agent modifies a markdown file, the hook runs `anti-ai-lint` and automatically reports any AI tropes or defensive hedging back into the agent context for instant remediation.

---

## 3. Quality Gate Integration

In your CI or pre-commit workflow, you can add `anti-ai-lint` as an automated gate:

```bash
anti-ai-lint path/to/deliverable.md --genre academic --format hook --max-score 8.0
```

---

## 4. Uninstallation

```bash
./uninstall.sh --target codex
```

---

## Trademark & Non-Affiliation Disclaimer

Codex and OpenAI are trademarks of OpenAI, Inc. `anti-ai-copywriting` is an independent open-source project and is not affiliated with, endorsed by, or sponsored by OpenAI, Inc.
