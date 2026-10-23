# WorkBuddy Adapter Guide

[English](workbuddy.md) | [简体中文](workbuddy.zh-CN.md)

## Overview

WorkBuddy is an enterprise AI assistant and digital workspace platform. `anti-ai-copywriting` integrates with WorkBuddy through prompt configuration, CLI automation, and external webhook quality gates.

---

## Integration Approaches

### Option 1: Direct Prompt Rule Injection (Recommended)

Copy the concise rules from `rules/AGENTS.snippet.md` (or `rules/AGENTS.snippet.en.md`) directly into your WorkBuddy assistant's system instructions or persona settings:

```markdown
# Anti-AI Copywriting & Natural Voice Rules (Mandatory & Silent)

All written or rewritten prose across Chinese and English—including academic manuscripts, grant proposals, technical columns, documentation, social media copy, and business memos—must adhere to the Anti-AI Copywriting guidelines:
1. Forbidden Lexicon: Eliminate buzzwords and formulaic AI tropes (Chinese: 赋能, 抓手, 闭环, 底层逻辑, 颗粒度, 全方位, 不仅是...更是...; English: delve into, testament to, beacon of, tapestry of, realm, crucial/paramount, navigating complexities, revolutionize, leverage).
2. Syntax & Rhythm: Avoid nominalizations, excessive passive voice, and redundant hedging ("possibly/perhaps/might tend to"). Control particle '的' density in Chinese; alternate sentence lengths in English.
3. No Fluff Openings / Closings: Begin directly with empirical facts, concrete problems, or immediate actions. Conclude on operational implications rather than repetitive philosophical summaries.
```

---

### Option 2: Automated Installation via CLI

Install the rules file directly into your WorkBuddy configuration directory:

```bash
# Global user prompt directory
./install.sh --target workbuddy --lang en

# Custom prompt path
./install.sh --target workbuddy --dest /path/to/workbuddy/prompts/anti-ai-rules.md --lang en
```

---

### Option 3: Automated Quality Gate (CI / Post-Processing / Webhooks)

If your WorkBuddy workflow invokes external tools or webhooks, run the zero-dependency linter `anti-ai-lint` as a deterministic verification gate:

```bash
anti-ai-lint /path/to/generated_output.md --max-score 8.0
```

If the generated prose contains forbidden buzzwords, stacked hedges, or excessive punctuation, the command exits with code `1`, preventing flawed text from reaching users.

---

## Uninstallation

```bash
./uninstall.sh --target workbuddy
```

---

## Trademark & Non-Affiliation Disclaimer

WorkBuddy is an enterprise workspace product. `anti-ai-copywriting` is an independent open-source project and is not affiliated with, endorsed by, or sponsored by WorkBuddy or its parent entities.
