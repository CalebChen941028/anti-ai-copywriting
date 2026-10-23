# DeepSeek Adapter Guide

[English](deepseek.md) | [简体中文](deepseek.zh-CN.md)

## Overview

This guide details integration of `anti-ai-copywriting` with DeepSeek models (DeepSeek-V3, DeepSeek-R1) across standalone CLI environments, generic agent harnesses (such as Cursor, Cline, or Aider configured with the DeepSeek API), and automated LLM pipelines.

---

## 1. Automated Installation

Run the unified installer specifying the `deepseek` target:

```bash
# Global user installation
./install.sh --target deepseek --lang en

# Local workspace installation
./install.sh --target deepseek --dest /path/to/project --lang en
```

This setup:
1. Deploys `SKILL.md` to `~/.deepseek/skills/anti-ai-copywriting/SKILL.md` (or workspace directory).
2. Injects bounded rule blocks into `~/.deepseek/AGENTS.md` (or workspace `AGENTS.md`) with explicit `<auto_trigger>` directives.
3. Records all installed files in `~/.local/share/anti-ai-copywriting/install-manifest.json` for rollback.

---

## 2. Using DeepSeek with Generic Agent Harnesses

When using DeepSeek via OpenAI-compatible endpoints (`https://api.deepseek.com`) within development tools:

### Aider with DeepSeek

Launch Aider with the DeepSeek model and load the rule conventions:

```bash
# Export your DeepSeek API key
export DEEPSEEK_API_KEY="your-api-key"

# Run Aider with rules convention
aider --model deepseek/deepseek-chat --read rules/AGENTS.snippet.en.md
```

### Cursor or Cline configured with DeepSeek

1. In Cursor or Cline settings, select DeepSeek (`deepseek-chat` or `deepseek-reasoner`) as your model provider.
2. Install the rules into the repository root:
   ```bash
   ./install.sh --target cursor --dest . --lang en
   ```
3. The agent reads the bounded rules from `.cursorrules` or `.clinerules` during every prompt cycle.

---

## 3. Custom DeepSeek API & Pipeline Integration

When invoking the DeepSeek API directly in Python, TypeScript, or Go:

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# Load the anti-ai rule snippet
with open("rules/AGENTS.snippet.en.md", "r", encoding="utf-8") as f:
    system_rules = f.read()

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": system_rules},
        {"role": "user", "content": "Draft the methodology section for our experimental analysis."}
    ],
    temperature=0.3,
)

print(response.choices[0].message.content)
```

---

## 4. In-Loop Reflection & Verification Gate

DeepSeek reasoning models (`deepseek-reasoner`) excel at self-correction when provided with deterministic structured feedback. You can establish an automated feedback loop:

```bash
# Verify output file with agent reflection format
python3 -m anti_ai_lint generated_report.md --genre academic --format agent --max-score 8.0
```

If the linter flags buzzwords or excessive hedges, pass the emitted `<anti-ai-lint-feedback>` block back into DeepSeek to prompt a clean rewrite:

```markdown
<anti-ai-lint-feedback>
Found 2 violations in generated_report.md:
  - Line 14: Forbidden AI cliché 'delve into' (+3.0) -> Suggestion: explore, examine, study
  - Line 28: Stacked hedging 'could potentially indicate' (+4.0) -> Suggestion: demonstrates, indicates
Please revise the text to remove these markers while retaining all empirical data.
</anti-ai-lint-feedback>
```

---

## 5. Uninstallation

To remove DeepSeek configuration and restore original files:

```bash
./uninstall.sh --target deepseek
```

---

## Trademark & Non-Affiliation Disclaimer

DeepSeek is a trademark of Hangzhou DeepSeek Artificial Intelligence Co., Ltd. `anti-ai-copywriting` is an independent open-source project and is not affiliated with, endorsed by, or sponsored by DeepSeek or Hangzhou DeepSeek Artificial Intelligence Co., Ltd.
