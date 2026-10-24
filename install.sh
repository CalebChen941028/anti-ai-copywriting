#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Liangliang Chen
# Unified installer for anti-ai-copywriting with multi-target manifest tracking
set -euo pipefail

TARGET="zcode"
LANG_OPT="zh"
DRY_RUN=false
DEST=""
VERSION="0.8.0"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target)
      TARGET="$2"
      shift 2
      ;;
    --lang)
      LANG_OPT="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --dest)
      DEST="$2"
      shift 2
      ;;
    -h|--help)
      echo "Usage: $0 [--target zcode|claude|codex|opencode|deepseek|workbuddy|cursor|windsurf|cline|aider|antigravity|harness2|generic] [--lang zh|en] [--dry-run] [--dest <path>]"
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_HOME="${ANTI_AI_HOME:-$HOME}"
MANIFEST_DIR="${ANTI_AI_MANIFEST_DIR:-$BASE_HOME/.local/share/anti-ai-copywriting}"
MANIFEST_FILE="$MANIFEST_DIR/install-manifest.json"

if [[ -n "$DEST" ]]; then
  DEST="$(python3 -c 'import os, sys; print(os.path.abspath(os.path.expanduser(sys.argv[1])))' "$DEST")"
fi

case "$TARGET" in
  zcode)
    if [[ -n "$DEST" ]]; then
      if [[ "$DEST" == *.md ]]; then
        SKILL_DEST="$(dirname "$DEST")/skills/anti-ai-copywriting"
        RULE_FILE="$DEST"
      else
        SKILL_DEST="$DEST/.zcode/skills/anti-ai-copywriting"
        RULE_FILE="$DEST/.zcode/AGENTS.md"
      fi
    else
      SKILL_DEST="$BASE_HOME/.zcode/skills/anti-ai-copywriting"
      RULE_FILE="$BASE_HOME/.zcode/AGENTS.md"
    fi
    ;;
  claude)
    if [[ -n "$DEST" ]]; then
      if [[ "$DEST" == *.md ]]; then
        SKILL_DEST="$(dirname "$DEST")/skills/anti-ai-copywriting"
        RULE_FILE="$DEST"
      else
        SKILL_DEST="$DEST/.claude/skills/anti-ai-copywriting"
        RULE_FILE="$DEST/CLAUDE.md"
      fi
    else
      SKILL_DEST="$BASE_HOME/.claude/skills/anti-ai-copywriting"
      RULE_FILE="$BASE_HOME/.claude/CLAUDE.md"
    fi
    ;;
  codex)
    if [[ -n "$DEST" ]]; then
      if [[ "$DEST" == *.md ]]; then
        SKILL_DEST="$(dirname "$DEST")/skills/anti-ai-copywriting"
        RULE_FILE="$DEST"
      else
        SKILL_DEST="$DEST/.codex/skills/anti-ai-copywriting"
        RULE_FILE="$DEST/AGENTS.md"
      fi
    else
      SKILL_DEST="$BASE_HOME/.codex/skills/anti-ai-copywriting"
      RULE_FILE="$BASE_HOME/.codex/AGENTS.md"
    fi
    ;;
  opencode)
    if [[ -n "$DEST" ]]; then
      if [[ "$DEST" == *.md ]]; then
        SKILL_DEST="$(dirname "$DEST")/skills/anti-ai-copywriting"
        RULE_FILE="$DEST"
      else
        SKILL_DEST="$DEST/.opencode/skills/anti-ai-copywriting"
        RULE_FILE="$DEST/AGENTS.md"
      fi
    else
      SKILL_DEST="$BASE_HOME/.opencode/skills/anti-ai-copywriting"
      RULE_FILE="$BASE_HOME/.opencode/AGENTS.md"
    fi
    ;;
  deepseek)
    if [[ -n "$DEST" ]]; then
      if [[ "$DEST" == *.md ]]; then
        SKILL_DEST="$(dirname "$DEST")/skills/anti-ai-copywriting"
        RULE_FILE="$DEST"
      else
        SKILL_DEST="$DEST/skills/anti-ai-copywriting"
        RULE_FILE="$DEST/AGENTS.md"
      fi
    else
      SKILL_DEST="$BASE_HOME/.deepseek/skills/anti-ai-copywriting"
      RULE_FILE="$BASE_HOME/.deepseek/AGENTS.md"
    fi
    ;;
  workbuddy)
    if [[ -z "$DEST" ]]; then
      SKILL_DEST="$BASE_HOME/.workbuddy/skills/anti-ai-copywriting"
      RULE_FILE="$BASE_HOME/.workbuddy/prompts/anti-ai-rules.md"
    else
      if [[ "$DEST" == *.md ]]; then
        SKILL_DEST="$(dirname "$DEST")/skills/anti-ai-copywriting"
        RULE_FILE="$DEST"
      else
        SKILL_DEST="$DEST/skills/anti-ai-copywriting"
        RULE_FILE="$DEST/anti-ai-rules.md"
      fi
    fi
    ;;
  cursor)
    if [[ -z "$DEST" ]]; then
      SKILL_DEST="$BASE_HOME/.cursor/skills/anti-ai-copywriting"
      RULE_FILE="$BASE_HOME/.cursorrules"
    else
      if [[ "$DEST" == *.cursorrules ]] || [[ "$DEST" == *.md ]] || [[ "$DEST" == *.mdc ]]; then
        SKILL_DEST="$(dirname "$DEST")/.cursor/skills/anti-ai-copywriting"
        RULE_FILE="$DEST"
      else
        SKILL_DEST="$DEST/.cursor/skills/anti-ai-copywriting"
        RULE_FILE="$DEST/.cursorrules"
      fi
    fi
    ;;
  windsurf)
    if [[ -z "$DEST" ]]; then
      SKILL_DEST="$BASE_HOME/.windsurf/skills/anti-ai-copywriting"
      RULE_FILE="$BASE_HOME/.windsurfrules"
    else
      if [[ "$DEST" == *.windsurfrules ]] || [[ "$DEST" == *.md ]]; then
        SKILL_DEST="$(dirname "$DEST")/.windsurf/skills/anti-ai-copywriting"
        RULE_FILE="$DEST"
      else
        SKILL_DEST="$DEST/.windsurf/skills/anti-ai-copywriting"
        RULE_FILE="$DEST/.windsurfrules"
      fi
    fi
    ;;
  cline)
    if [[ -z "$DEST" ]]; then
      SKILL_DEST="$BASE_HOME/.cline/skills/anti-ai-copywriting"
      RULE_FILE="$BASE_HOME/.clinerules"
    else
      if [[ "$DEST" == *.clinerules ]] || [[ "$DEST" == *.md ]]; then
        SKILL_DEST="$(dirname "$DEST")/skills/anti-ai-copywriting"
        RULE_FILE="$DEST"
      else
        SKILL_DEST="$DEST/skills/anti-ai-copywriting"
        RULE_FILE="$DEST/.clinerules"
      fi
    fi
    ;;
  aider)
    if [[ -z "$DEST" ]]; then
      SKILL_DEST="$BASE_HOME/.aider/skills/anti-ai-copywriting"
      RULE_FILE="$BASE_HOME/.aider.conventions.md"
    else
      if [[ "$DEST" == *.md ]]; then
        SKILL_DEST="$(dirname "$DEST")/skills/anti-ai-copywriting"
        RULE_FILE="$DEST"
      else
        SKILL_DEST="$DEST/skills/anti-ai-copywriting"
        RULE_FILE="$DEST/CONVENTIONS.md"
      fi
    fi
    ;;
  antigravity)
    if [[ -z "$DEST" ]]; then
      SKILL_DEST="$BASE_HOME/.antigravity/skills/anti-ai-copywriting"
      RULE_FILE="$BASE_HOME/.antigravity/AGENTS.md"
    else
      if [[ "$DEST" == *.md ]]; then
        SKILL_DEST="$(dirname "$DEST")/skills/anti-ai-copywriting"
        RULE_FILE="$DEST"
      else
        SKILL_DEST="$DEST/skills/anti-ai-copywriting"
        RULE_FILE="$DEST/AGENTS.md"
      fi
    fi
    ;;
  harness2)
    if [[ -z "$DEST" ]]; then
      SKILL_DEST="$BASE_HOME/.harness2/skills/anti-ai-copywriting"
      RULE_FILE="$BASE_HOME/.harness2/AGENTS.md"
    else
      if [[ "$DEST" == *.md ]]; then
        SKILL_DEST="$(dirname "$DEST")/skills/anti-ai-copywriting"
        RULE_FILE="$DEST"
      else
        SKILL_DEST="$DEST/.harness2/skills/anti-ai-copywriting"
        RULE_FILE="$DEST/AGENTS.md"
      fi
    fi
    ;;
  generic)
    if [[ -z "$DEST" ]]; then
      SKILL_DEST="$BASE_HOME/.anti-ai-copywriting/skill/anti-ai-copywriting"
      RULE_FILE="$BASE_HOME/.anti-ai-copywriting/AGENTS.md"
    else
      if [[ "$DEST" == *.md ]]; then
        SKILL_DEST="$(dirname "$DEST")/skill/anti-ai-copywriting"
        RULE_FILE="$DEST"
      else
        SKILL_DEST="$DEST/skill/anti-ai-copywriting"
        RULE_FILE="$DEST/AGENTS.md"
      fi
    fi
    ;;
  *)
    echo "Unsupported target: $TARGET" >&2
    exit 1
    ;;
esac

# Choose language-tailored snippet
if [[ "$LANG_OPT" == "en" ]] && [[ -f "$SCRIPT_DIR/rules/AGENTS.snippet.en.md" ]]; then
  SNIPPET_FILE="$SCRIPT_DIR/rules/AGENTS.snippet.en.md"
elif [[ "$LANG_OPT" == "zh" ]] && [[ -f "$SCRIPT_DIR/rules/AGENTS.snippet.zh.md" ]]; then
  SNIPPET_FILE="$SCRIPT_DIR/rules/AGENTS.snippet.zh.md"
else
  SNIPPET_FILE="$SCRIPT_DIR/rules/AGENTS.snippet.md"
fi

echo "Target platform: $TARGET"
echo "Language:        $LANG_OPT (Snippet: $(basename "$SNIPPET_FILE"))"
echo "Skill directory: $SKILL_DEST"
echo "Rules file:      $RULE_FILE"

if [[ "$DRY_RUN" == true ]]; then
  echo "[Dry-Run] Would copy $SCRIPT_DIR/skill/anti-ai-copywriting/SKILL.md -> $SKILL_DEST/SKILL.md"
  echo "[Dry-Run] Would inject snippet from $SNIPPET_FILE into $RULE_FILE"
  exit 0
fi

TIMESTAMP="$(date +%Y%m%d%H%M%S)"
RULE_BACKUP=""
SKILL_BACKUP=""

mkdir -p "$SKILL_DEST"
if [[ -f "$SKILL_DEST/SKILL.md" ]]; then
  SKILL_BACKUP="$SKILL_DEST/SKILL.md.bak-$TIMESTAMP"
  cp "$SKILL_DEST/SKILL.md" "$SKILL_BACKUP"
fi
cp "$SCRIPT_DIR/skill/anti-ai-copywriting/SKILL.md" "$SKILL_DEST/SKILL.md"
echo "Installed skill to $SKILL_DEST/SKILL.md"

# Bounded marker block update in RULE_FILE
mkdir -p "$(dirname "$RULE_FILE")"
if [[ -f "$RULE_FILE" ]]; then
  RULE_BACKUP="$RULE_FILE.bak-$TIMESTAMP"
  cp "$RULE_FILE" "$RULE_BACKUP"
fi

python3 - "$RULE_FILE" "$SNIPPET_FILE" <<'EOF'
import re
import sys
from pathlib import Path

rule_path = Path(sys.argv[1])
snippet_path = Path(sys.argv[2])
content = rule_path.read_text(encoding="utf-8") if rule_path.exists() else ""
pattern = r"<!-- BEGIN anti-ai-copywriting.*?<!-- END anti-ai-copywriting -->"
new_snippet = snippet_path.read_text(encoding="utf-8").strip()

if re.search(pattern, content, flags=re.DOTALL):
    parts = re.split(pattern, content, flags=re.DOTALL)
    prefix = parts[0].rstrip()
    remainder = "".join(parts[1:]).strip()
    if prefix:
        updated = prefix + "\n\n" + new_snippet
    else:
        updated = new_snippet
    if remainder:
        updated += "\n\n" + remainder
    updated += "\n"
else:
    if content.strip():
        updated = content.rstrip() + "\n\n" + new_snippet + "\n"
    else:
        updated = new_snippet + "\n"

rule_path.write_text(updated, encoding="utf-8")
EOF
echo "Injected rules block into $RULE_FILE"

# Record in multi-target manifest
mkdir -p "$MANIFEST_DIR"
python3 - "$MANIFEST_FILE" "$TARGET" "$DEST" "$VERSION" "$LANG_OPT" "$SKILL_DEST/SKILL.md" "$RULE_FILE" "$SKILL_BACKUP" "$RULE_BACKUP" <<'EOF'
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

manifest_path = Path(sys.argv[1])
target = sys.argv[2]
dest = sys.argv[3]
version = sys.argv[4]
lang_opt = sys.argv[5]
skill_file = sys.argv[6]
rule_file = sys.argv[7]
skill_backup = sys.argv[8]
rule_backup = sys.argv[9]

if manifest_path.is_file():
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        data = {}
else:
    data = {}

targets = data.get("targets", {})

# Migrate legacy format if present
if "target" in data and data["target"] not in targets:
    legacy_t = data["target"]
    targets[legacy_t] = {
        "version": data.get("version", version),
        "target": legacy_t,
        "lang": "zh",
        "installed_at": data.get("installed_at", ""),
        "files": data.get("files", []),
        "rule_file": data.get("rule_file", ""),
        "backups": data.get("backups", {})
    }

target_key = target
if dest:
    target_key = f"{target}:{dest}"

targets[target_key] = {
    "version": version,
    "target": target,
    "lang": lang_opt,
    "installed_at": datetime.now(timezone.utc).isoformat(),
    "files": [skill_file],
    "rule_file": rule_file,
    "backups": {
        "skill_backup": skill_backup,
        "rule_backup": rule_backup
    }
}

data["version"] = version
data["targets"] = targets

manifest_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
EOF

echo "Installation complete. Manifest updated at $MANIFEST_FILE."
