# anti-ai-lint

Deterministic zero-dependency linter for detecting AI buzzwords, translationese, stacked hedging, and formulaic rhetorical padding across Chinese and English prose.

## Installation

```bash
pip install anti-ai-lint
```

## Quick Start

```bash
# Check a single markdown file
anti-ai-lint document.md

# Check multiple files or directories with max allowed score threshold
anti-ai-lint docs/ --max-score 8.0

# Output structured JSON for CI quality gates
anti-ai-lint report.md --format json
```

## Metrics & Detections

- Forbidden buzzwords & clichés (Chinese & English)
- Punctuation abuse (consecutive em-dashes `——`, exclamation marks `!`)
- Structural formulaic patterns (e.g., `不仅...更是...`, `not only... but also...`)
- High particle density (`的` concentration > 8% or > 4 per clause)
- Stacked hedging & defensive disclaimers
