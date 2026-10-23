# WorkBuddy Adapter Guide

## Overview

WorkBuddy is an enterprise AI assistant / workspace platform. Because WorkBuddy does not offer a publicly documented custom skill SDK or proprietary extension manifest format, `anti-ai-copywriting` integrates with WorkBuddy via the **Generic Rule Adapter**.

## Integration Approach

WorkBuddy bots and workspace assistants allow configuring custom instructions, system prompts, or agent personas.

### Option 1: Direct Prompt Rule Injection (Recommended)

Copy the concise rules from `rules/AGENTS.snippet.md` directly into your WorkBuddy agent's system prompt or global instructions:

```markdown
# Anti-AI Copywriting & Natural Voice Rules (Mandatory & Silent)

All written or rewritten prose across Chinese and English—including academic manuscripts, grant proposals, technical columns, documentation, social media copy, and business memos—must adhere to the Anti-AI Copywriting guidelines:
1. Forbidden Lexicon: Eliminate buzzwords and formulaic AI tropes (Chinese: 赋能, 抓手, 闭环, 底层逻辑, 颗粒度, 全方位, 不仅是...更是...; English: delve into, testament to, beacon of, tapestry of, realm, crucial/paramount, navigating complexities, revolutionize, leverage).
2. Syntax & Rhythm: Avoid nominalizations, excessive passive voice, and redundant hedging ("possibly/perhaps/might tend to"). Control particle '的' density in Chinese; alternate sentence lengths in English.
3. No Fluff Openings / Closings: Begin directly with empirical facts, concrete problems, or immediate actions. Conclude on operational implications rather than repetitive philosophical summaries.
```

### Option 2: Automated Installation via CLI

You can install the rules file into a specific directory monitored by WorkBuddy or export it to a chosen file:

```bash
./install.sh --target generic --dest /path/to/workbuddy/prompts/anti-ai-rules.md
```

### Option 3: Automated Quality Gate (CI / Post-Processing)

If your WorkBuddy workflow invokes external tools or webhooks, you can run the zero-dependency linter `anti-ai-lint` as a deterministic verification gate:

```bash
anti-ai-lint /path/to/generated_output.md --max-score 8.0
```
If the output contains forbidden buzzwords, stacked hedges, or excessive punctuation, the command exits with code `1`, preventing flawed text from being sent.
