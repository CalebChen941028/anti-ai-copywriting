#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Liangliang Chen
# Uninstaller for anti-ai-copywriting using multi-target install-manifest.json
set -euo pipefail

TARGET_FILTER=""
DEST_FILTER=""
UNINSTALL_ALL=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target)
      TARGET_FILTER="$2"
      shift 2
      ;;
    --dest)
      DEST_FILTER="$2"
      shift 2
      ;;
    --all)
      UNINSTALL_ALL=true
      shift
      ;;
    -h|--help)
      echo "Usage: $0 [--target <zcode|claude|codex|opencode|deepseek|workbuddy|cursor|windsurf|cline|aider|antigravity|harness2|generic>] [--dest <path>] [--all]"
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
  esac
done

BASE_HOME="${ANTI_AI_HOME:-$HOME}"
MANIFEST_DIR="${ANTI_AI_MANIFEST_DIR:-$BASE_HOME/.local/share/anti-ai-copywriting}"
MANIFEST_FILE="$MANIFEST_DIR/install-manifest.json"

if [[ ! -f "$MANIFEST_FILE" ]]; then
  echo "No manifest file found at $MANIFEST_FILE. Nothing to uninstall."
  exit 0
fi

if [[ -n "$DEST_FILTER" ]]; then
  DEST_FILTER="$(python3 -c 'import os, sys; print(os.path.abspath(os.path.expanduser(sys.argv[1])))' "$DEST_FILTER")"
fi

echo "Reading manifest from $MANIFEST_FILE..."

python3 - "$MANIFEST_FILE" "$TARGET_FILTER" "$DEST_FILTER" "$UNINSTALL_ALL" <<'EOF'
import json
import os
import re
import sys
from pathlib import Path

manifest_path = Path(sys.argv[1])
target_filter = sys.argv[2].strip()
dest_filter = sys.argv[3].strip()
uninstall_all = sys.argv[4].lower() == "true"

try:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
except Exception as e:
    print(f"Error reading manifest: {e}", file=sys.stderr)
    sys.exit(1)

targets = data.get("targets", {})

# Handle legacy single-target manifest
if not targets and "files" in data:
    legacy_t = data.get("target", "default")
    targets = {legacy_t: data}

if not targets:
    print("No installed targets found in manifest.")
    manifest_path.unlink(missing_ok=True)
    sys.exit(0)

# Determine which targets to uninstall
to_uninstall = []
if uninstall_all:
    to_uninstall = list(targets.keys())
elif target_filter and dest_filter:
    target_key = f"{target_filter}:{dest_filter}"
    if target_key in targets:
        to_uninstall = [target_key]
    else:
        matched = [
            k for k in targets
            if targets[k].get("target") == target_filter
            and (k.endswith(f":{dest_filter}") or dest_filter in k or any(dest_filter in f for f in targets[k].get("files", [])) or (targets[k].get("rule_file") and dest_filter in targets[k]["rule_file"]))
        ]
        if not matched:
            print(f"Target '{target_filter}' at destination '{dest_filter}' not found in manifest. Registered targets: {list(targets.keys())}", file=sys.stderr)
            sys.exit(1)
        to_uninstall = matched
elif dest_filter:
    matched = [
        k for k in targets
        if k.endswith(f":{dest_filter}") or dest_filter in k or any(dest_filter in f for f in targets[k].get("files", [])) or (targets[k].get("rule_file") and dest_filter in targets[k]["rule_file"])
    ]
    if not matched:
        print(f"No targets found matching destination '{dest_filter}'. Registered targets: {list(targets.keys())}", file=sys.stderr)
        sys.exit(1)
    to_uninstall = matched
elif target_filter:
    if target_filter in targets:
        to_uninstall = [target_filter]
    else:
        matched = [k for k in targets if targets[k].get("target") == target_filter]
        if not matched:
            print(f"Target '{target_filter}' not found in manifest. Registered targets: {list(targets.keys())}", file=sys.stderr)
            sys.exit(1)
        if len(matched) > 1:
            print(
                f"Multiple installations found for target '{target_filter}': {matched}.\n"
                f"Please specify --dest <path> to uninstall a specific project, or use --all to uninstall all.",
                file=sys.stderr
            )
            sys.exit(1)
        to_uninstall = matched
elif len(targets) == 1:
    to_uninstall = list(targets.keys())
else:
    print(
        f"Multiple targets installed: {list(targets.keys())}.\n"
        f"Please specify --target <name>, --dest <path>, or --all to uninstall all.",
        file=sys.stderr
    )
    sys.exit(1)

for t_key in to_uninstall:
    info = targets[t_key]
    print(f"\nUninstalling target: {t_key} ...")
    backups = info.get("backups", {})
    skill_bak = backups.get("skill_backup")
    rule_bak = backups.get("rule_backup")

    # 1. Restore or remove skill files
    for f in info.get("files", []):
        fp = Path(f)
        if fp.is_file():
            if skill_bak and Path(skill_bak).is_file():
                Path(skill_bak).replace(fp)
                print(f"  Restored skill file from backup: {fp}")
            else:
                fp.unlink()
                print(f"  Removed skill file: {fp}")
            
            # Remove parent directory if empty
            parent = fp.parent
            if parent.is_dir() and not any(parent.iterdir()):
                parent.rmdir()
                print(f"  Removed empty skill dir: {parent}")

    # 2. Safe bounded marker cleanup on rule file
    rule_file_path = info.get("rule_file")
    if rule_file_path:
        rp = Path(rule_file_path)
        if rp.is_file():
            content = rp.read_text(encoding="utf-8")
            pattern = r"\n*<!-- BEGIN anti-ai-copywriting.*?<!-- END anti-ai-copywriting -->\n*"
            cleaned = re.sub(pattern, "\n", content, flags=re.DOTALL).strip()
            if cleaned:
                rp.write_text(cleaned + "\n", encoding="utf-8")
                print(f"  Cleaned marker blocks from: {rp}")
            else:
                rp.unlink()
                print(f"  Removed empty rule file: {rp}")
                if rp.parent.is_dir() and not any(rp.parent.iterdir()):
                    rp.parent.rmdir()
                    print(f"  Removed empty rule dir: {rp.parent}")
            if rule_bak and Path(rule_bak).is_file():
                Path(rule_bak).unlink()
        elif rule_bak and Path(rule_bak).is_file():
            Path(rule_bak).replace(rp)
            print(f"  Restored rule file from backup: {rp}")

    # Remove uninstalled target from manifest
    del targets[t_key]

# Update or remove manifest
if targets:
    data["targets"] = targets
    manifest_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nRemaining registered targets: {list(targets.keys())}")
else:
    manifest_path.unlink()
    print("\nAll targets uninstalled. Removed manifest file.")
    if manifest_path.parent.is_dir() and not any(manifest_path.parent.iterdir()):
        manifest_path.parent.rmdir()

EOF

echo "Uninstallation finished."
