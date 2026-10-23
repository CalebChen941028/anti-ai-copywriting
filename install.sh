#!/usr/bin/env bash
# Unified installer for anti-ai-copywriting
set -euo pipefail

TARGET="zcode"
LANG_OPT="zh"
DRY_RUN=false
DEST=""
VERSION="0.2.0"

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
      echo "Usage: $0 [--target zcode|claude|codex|opencode|generic|workbuddy] [--lang zh|en] [--dry-run] [--dest <path>]"
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANIFEST_DIR="$HOME/.local/share/anti-ai-copywriting"
MANIFEST_FILE="$MANIFEST_DIR/install-manifest.json"

case "$TARGET" in
  zcode)
    SKILL_DEST="$HOME/.zcode/skills/anti-ai-copywriting"
    RULE_FILE="$HOME/.zcode/AGENTS.md"
    ;;
  claude)
    SKILL_DEST="$HOME/.claude/skills/anti-ai-copywriting"
    RULE_FILE="$HOME/.claude/CLAUDE.md"
    ;;
  codex)
    SKILL_DEST="$HOME/.codex/skills/anti-ai-copywriting"
    RULE_FILE="$HOME/.codex/AGENTS.md"
    ;;
  opencode)
    SKILL_DEST="$HOME/.opencode/skills/anti-ai-copywriting"
    RULE_FILE="$HOME/.opencode/AGENTS.md"
    ;;
  generic|workbuddy)
    if [[ -z "$DEST" ]]; then
      SKILL_DEST="$HOME/.anti-ai-copywriting/skill"
      RULE_FILE="$HOME/.anti-ai-copywriting/AGENTS.md"
    else
      if [[ "$DEST" == *.md ]]; then
        SKILL_DEST="$(dirname "$DEST")/skill"
        RULE_FILE="$DEST"
      else
        SKILL_DEST="$DEST/skill"
        RULE_FILE="$DEST/AGENTS.md"
      fi
    fi
    ;;
  *)
    echo "Unsupported target: $TARGET" >&2
    exit 1
    ;;
esac

echo "Target platform: $TARGET"
echo "Skill directory: $SKILL_DEST"
echo "Rules file:      $RULE_FILE"

if [[ "$DRY_RUN" == true ]]; then
  echo "[Dry-Run] Would copy $SCRIPT_DIR/skill/anti-ai-copywriting/SKILL.md -> $SKILL_DEST/SKILL.md"
  echo "[Dry-Run] Would inject snippet into $RULE_FILE"
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
SNIPPET_CONTENT="$(cat "$SCRIPT_DIR/rules/AGENTS.snippet.md")"

if [[ -f "$RULE_FILE" ]]; then
  RULE_BACKUP="$RULE_FILE.bak-$TIMESTAMP"
  cp "$RULE_FILE" "$RULE_BACKUP"
  python3 - <<EOF
import re
from pathlib import Path

rule_path = Path("$RULE_FILE")
content = rule_path.read_text(encoding="utf-8")
pattern = r"<!-- BEGIN anti-ai-copywriting.*?<!-- END anti-ai-copywriting -->"
new_snippet = """$SNIPPET_CONTENT"""

if re.search(pattern, content, flags=re.DOTALL):
    updated = re.sub(pattern, new_snippet.strip(), content, flags=re.DOTALL)
else:
    updated = content.rstrip() + "\n\n" + new_snippet.strip() + "\n"

rule_path.write_text(updated, encoding="utf-8")
EOF
else
  printf "%s\n" "$SNIPPET_CONTENT" > "$RULE_FILE"
fi
echo "Injected rules block into $RULE_FILE"

# Record manifest
mkdir -p "$MANIFEST_DIR"
cat <<EOF > "$MANIFEST_FILE"
{
  "version": "$VERSION",
  "target": "$TARGET",
  "installed_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "files": [
    "$SKILL_DEST/SKILL.md"
  ],
  "rule_file": "$RULE_FILE",
  "backups": {
    "skill_backup": "$SKILL_BACKUP",
    "rule_backup": "$RULE_BACKUP"
  }
}
EOF

echo "Installation complete. Manifest saved to $MANIFEST_FILE."
