# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Liangliang Chen
"""Command-line interface for anti-ai-lint."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

try:
    from . import __version__
    from .detector import LintReport, analyze_text
except (ImportError, ValueError):
    parent_dir = str(Path(__file__).resolve().parent.parent)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    from anti_ai_lint import __version__
    from anti_ai_lint.detector import LintReport, analyze_text


def format_text_report(report: LintReport) -> str:
    lines = []
    status = "PASSED" if report.passed else "FAILED"
    target = report.file_path or "<stdin>"
    lines.append(
        f"[{status}] {target} — Score: {report.score:.1f} "
        f"(Normalized: {report.normalized_score:.1f}/1k units, Genre: {report.genre})"
    )
    lines.append(
        f"  Metrics: {report.metrics.total_chars} chars, {report.metrics.total_words} words "
        f"({report.metrics.cjk_count} CJK, {report.metrics.latin_words} Latin), "
        f"'的' ratio: {report.metrics.de_ratio*100:.1f}%, dashes: {report.metrics.dash_count}, "
        f"bold: {report.metrics.bold_count}"
    )
    if report.violations:
        lines.append("  Violations:")
        for v in report.violations:
            loc = f"L{v.line}:C{v.column}"
            lines.append(f"    - [{v.category}] {loc}: {v.message} (+{v.penalty:.1f})")
            if v.context:
                lines.append(f"      context: \"{v.context}\"")
            if v.suggestion:
                lines.append(f"      fix: {v.suggestion}")
    return "\n".join(lines)


def format_hook_report(reports: List[LintReport]) -> str:
    lines = []
    for r in reports:
        target = r.file_path or "<stdin>"
        if r.passed:
            lines.append(f"[anti-ai-lint] PASS ({target}): score={r.score:.1f}")
        else:
            lines.append(
                f"[anti-ai-lint] FAIL ({target}): score={r.score:.1f} "
                f"(normalized={r.normalized_score:.1f}), {len(r.violations)} violations"
            )
            for v in r.violations:
                sugg = f" -> {v.suggestion}" if v.suggestion else ""
                lines.append(f"  L{v.line}:C{v.column} [{v.category}] {v.message}{sugg}")
    return "\n".join(lines)


def format_agent_report(
    reports: List[LintReport], max_score: float, max_normalized_score: Optional[float] = None
) -> str:
    failed_reports = [r for r in reports if not r.passed]
    if not failed_reports:
        return "[anti-ai-lint] PASSED: All checked documents satisfy Anti-AI natural voice rules."

    lines = [
        f'<anti-ai-lint-feedback status="FAILED" files_failed="{len(failed_reports)}" total_files="{len(reports)}">',
        "### Anti-AI Prose Violations Detected",
        "The drafted content contains machine-generated clichés, defensive hedging, or forbidden vocabulary:",
        "",
    ]
    for r in failed_reports:
        target = r.file_path or "<stdin>"
        norm_info = (
            f", Normalized: {r.normalized_score:.1f}/{max_normalized_score:.1f}"
            if max_normalized_score is not None
            else f", Normalized: {r.normalized_score:.1f}/1k"
        )
        lines.append(
            f"#### Target: `{target}` (Score: {r.score:.1f}, Threshold: {max_score:.1f}{norm_info}, Genre: {r.genre})"
        )
        for v in r.violations:
            lines.append(f"- **Line {v.line}, Col {v.column}** [`{v.category}`]: {v.message} (+{v.penalty:.1f})")
            if v.context:
                lines.append(f"  * Context: `{v.context}`")
            if v.suggestion:
                lines.append(f"  * Remediation: {v.suggestion}")
        lines.append("")

    lines.append("### Required Action")
    lines.append("Directly rewrite the affected sections following the natural voice and anti-ai copywriting rules. Output the revised content without defensive disclaimers.")
    lines.append("</anti-ai-lint-feedback>")
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="anti-ai-lint",
        description="Deterministic zero-dependency linter for detecting AI buzzwords, translationese, and fluff.",
    )
    parser.add_argument("paths", nargs="*", help="File or directory paths to check (defaults to stdin if empty).")
    parser.add_argument("--max-score", type=float, default=10.0, help="Maximum allowed penalty score before failure (default: 10.0).")
    parser.add_argument("--max-normalized-score", type=float, default=None, help="Maximum allowed penalty score per 1,000 units (default: None).")
    parser.add_argument(
        "--genre",
        choices=["general", "academic", "plain"],
        default="general",
        help="Target genre conventions: 'general' (default), 'academic' (strict de-hedging and data reporting), or 'plain' (controlled plain layer with strict length limits).",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "hook", "agent"],
        default="text",
        help="Output format: 'text' (human summary), 'json' (structured AST/report), 'hook' (compact git/tool hook), or 'agent' (LLM tool feedback payload).",
    )
    parser.add_argument("--wordlists", type=str, default=None, help="Path to custom wordlists directory.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    args = parser.parse_args(argv)

    reports: List[LintReport] = []
    had_error = False

    if not args.paths:
        # Read from stdin with UTF-8 fallback
        try:
            if hasattr(sys.stdin, "reconfigure"):
                sys.stdin.reconfigure(encoding="utf-8", errors="replace")
            content = sys.stdin.read()
        except Exception:
            try:
                content = sys.stdin.buffer.read().decode("utf-8", errors="replace")
            except Exception:
                content = ""
        rep = analyze_text(
            content,
            file_path=None,
            max_score=args.max_score,
            max_normalized_score=args.max_normalized_score,
            genre=args.genre,
            wordlists_dir=args.wordlists,
        )
        reports.append(rep)
    else:
        ignored_dirs = {".git", ".svn", ".hg", "node_modules", ".venv", "venv", "__pycache__", ".tox", ".pytest_cache"}
        for path_str in args.paths:
            p = Path(path_str)
            if not p.exists():
                sys.stderr.write(f"Error: path not found: {path_str}\n")
                had_error = True
                continue
            if p.is_dir():
                found_any = False
                for sub in sorted(p.rglob("*")):
                    if any(part in ignored_dirs for part in sub.parts):
                        continue
                    if sub.is_file() and sub.suffix.lower() in [".md", ".txt", ".markdown"]:
                        found_any = True
                        try:
                            content = sub.read_text(encoding="utf-8", errors="replace")
                        except OSError as e:
                            sys.stderr.write(f"Error: could not read file {sub}: {e}\n")
                            had_error = True
                            continue
                        rep = analyze_text(
                            content,
                            file_path=str(sub),
                            max_score=args.max_score,
                            max_normalized_score=args.max_normalized_score,
                            genre=args.genre,
                            wordlists_dir=args.wordlists,
                        )
                        reports.append(rep)
                if not found_any:
                    sys.stderr.write(f"Warning: no markdown or text documents found in directory: {path_str}\n")
            else:
                try:
                    content = p.read_text(encoding="utf-8", errors="replace")
                except OSError as e:
                    sys.stderr.write(f"Error: could not read file {p}: {e}\n")
                    had_error = True
                    continue
                rep = analyze_text(
                    content,
                    file_path=str(p),
                    max_score=args.max_score,
                    max_normalized_score=args.max_normalized_score,
                    genre=args.genre,
                    wordlists_dir=args.wordlists,
                )
                reports.append(rep)

    failed_count = sum(1 for r in reports if not r.passed)

    if args.format == "json":
        data = {
            "version": __version__,
            "total_files": len(reports),
            "failed_files": failed_count,
            "genre": args.genre,
            "had_error": had_error,
            "reports": [r.to_dict() for r in reports],
        }
        print(json.dumps(data, ensure_ascii=False, indent=2))
    elif args.format == "hook":
        print(format_hook_report(reports))
    elif args.format == "agent":
        print(format_agent_report(reports, args.max_score, args.max_normalized_score))
    else:
        for r in reports:
            print(format_text_report(r))
            print()
        print(f"Summary: {len(reports)} checked, {failed_count} failed.")

    return 1 if (failed_count > 0 or had_error) else 0


if __name__ == "__main__":
    sys.exit(main())
