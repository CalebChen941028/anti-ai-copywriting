"""Command-line interface for anti-ai-lint."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from . import __version__
from .detector import LintReport, analyze_text


def format_text_report(report: LintReport) -> str:
    lines = []
    status = "PASSED" if report.passed else "FAILED"
    target = report.file_path or "<stdin>"
    lines.append(f"[{status}] {target} — Score: {report.score:.1f}")
    lines.append(
        f"  Metrics: {report.metrics.total_chars} chars, {report.metrics.total_words} words, "
        f"'的' ratio: {report.metrics.de_ratio*100:.1f}%, dashes: {report.metrics.dash_count}, "
        f"bold: {report.metrics.bold_count}"
    )
    if report.violations:
        lines.append("  Violations:")
        for v in report.violations:
            loc = f"L{v.line}:C{v.column}"
            lines.append(f"    - [{v.category}] {loc}: {v.message} (+{v.penalty})")
            if v.context:
                lines.append(f"      context: \"{v.context}\"")
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="anti-ai-lint",
        description="Deterministic zero-dependency linter for detecting AI buzzwords, translationese, and fluff.",
    )
    parser.add_argument("paths", nargs="*", help="File or directory paths to check (defaults to stdin if empty).")
    parser.add_argument("--max-score", type=float, default=10.0, help="Maximum allowed penalty score before failure (default: 10.0).")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format (default: text).")
    parser.add_argument("--wordlists", type=str, default=None, help="Path to custom wordlists directory.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    args = parser.parse_args(argv)

    reports: List[LintReport] = []

    if not args.paths:
        # Read from stdin
        content = sys.stdin.read()
        rep = analyze_text(content, file_path=None, max_score=args.max_score, wordlists_dir=args.wordlists)
        reports.append(rep)
    else:
        for path_str in args.paths:
            p = Path(path_str)
            if not p.exists():
                sys.stderr.write(f"Error: path not found: {path_str}\n")
                continue
            if p.is_dir():
                for sub in p.rglob("*"):
                    if sub.is_file() and sub.suffix.lower() in [".md", ".txt", ".markdown"]:
                        content = sub.read_text(encoding="utf-8", errors="replace")
                        rep = analyze_text(content, file_path=str(sub), max_score=args.max_score, wordlists_dir=args.wordlists)
                        reports.append(rep)
            else:
                content = p.read_text(encoding="utf-8", errors="replace")
                rep = analyze_text(content, file_path=str(p), max_score=args.max_score, wordlists_dir=args.wordlists)
                reports.append(rep)

    failed_count = sum(1 for r in reports if not r.passed)

    if args.format == "json":
        data = {
            "version": __version__,
            "total_files": len(reports),
            "failed_files": failed_count,
            "reports": [r.to_dict() for r in reports],
        }
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        for r in reports:
            print(format_text_report(r))
            print()
        print(f"Summary: {len(reports)} checked, {failed_count} failed.")

    return 1 if failed_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
