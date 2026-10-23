#!/usr/bin/env bash
# Uninstaller for anti-ai-copywriting using install-manifest.json
set -euo pipefail

MANIFEST_FILE="$HOME/.local/share/anti-ai-copywriting/install-manifest.json"

if [[ ! -f "$MANIFEST_FILE" ]]; then
  echo "No manifest file found at $MANIFEST_FILE. Nothing to uninstall."
  exit 0
fi

echo "Reading manifest from $MANIFEST_FILE..."

python3 - <<EOF
import json
import os
import re
from pathlib import Path

manifest_path = Path("$MANIFEST_FILE")
data = json.loads(manifest_path.read_text(encoding="utf-8"))

backups = data.get("backups", {})
skill_bak = backups.get("skill_backup")
rule_bak = backups.get("rule_backup")

for f in data.get("files", []):
    fp = Path(f)
    if fp.is_file():
        if skill_bak and Path(skill_bak).is_file():
            Path(skill_bak).replace(fp)
            print(f"Restored file from backup: {fp}")
        else:
            fp.unlink()
            print(f"Removed file: {fp}")
        # remove parent dir if empty
        if fp.parent.is_dir() and not any(fp.parent.iterdir()):
            fp.parent.rmdir()
            print(f"Removed empty dir: {fp.parent}")

rule_file = data.get("rule_file")
if rule_file:
    rp = Path(rule_file)
    if rule_bak and Path(rule_bak).is_file():
        Path(rule_bak).replace(rp)
        print(f"Restored rule file from backup: {rp}")
    elif rp.is_file():
        content = rp.read_text(encoding="utf-8")
        pattern = r"\n*<!-- BEGIN anti-ai-copywriting.*?<!-- END anti-ai-copywriting -->\n*"
        cleaned = re.sub(pattern, "\n", content, flags=re.DOTALL).strip() + "\n"
        rp.write_text(cleaned, encoding="utf-8")
        print(f"Cleaned marker blocks from: {rp}")

manifest_path.unlink()
print("Removed manifest file.")
EOF

echo "Uninstallation finished."
