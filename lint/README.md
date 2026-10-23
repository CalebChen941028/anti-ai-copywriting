# anti-ai-lint

Deterministic zero-dependency linter for detecting AI buzzwords, translationese, stacked hedging, and formulaic rhetorical padding across Chinese and English prose.

---

## Installation

```bash
pip install anti-ai-lint
# or local editable install:
pip install ./lint
```

## Quick Start

```bash
# Check a single markdown file
anti-ai-lint document.md

# Academic mode with in-loop hook output
anti-ai-lint paper.md --genre academic --format hook --max-score 8.0

# Controlled plain layer validation
anti-ai-lint guide.md --genre plain --format agent

# Check multiple files or directories with max allowed score threshold
anti-ai-lint docs/ --max-score 8.0

# Check with normalized score per 1,000 text units
anti-ai-lint docs/ --max-normalized-score 20.0 --format json
```

## Metrics & Detections

- Forbidden buzzwords & clichés (Chinese & English) with actionable replacement suggestions
- Punctuation abuse (excessive em-dashes `——`, exclamation marks `!`, excessive bolding)
- Structural formulaic patterns (e.g., `不仅...更是...`, `随着...飞速发展`, `not only... but also...`)
- High particle density (`的` concentration > 8% or > 4 per clause)
- Stacked hedging & defensive disclaimers in academic writing
- Controlled plain layer constraints (sentence length $\le 30$ chars / $\le 25$ words, zero vague quantifiers)

## License

[MIT](https://github.com/CalebChen941028/anti-ai-copywriting/blob/main/LICENSE) © 2026 Liangliang Chen
