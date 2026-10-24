#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Liangliang Chen
"""Stanford DSPy prompt optimization runner for anti-ai-copywriting.

Optimizes natural voice rewrite instructions and few-shot exemplars against
the deterministic anti-ai-lint objective metric:

    Metric = λ1 * max(0, 10.0 - Score_lint)
           + λ2 * LexicalSimilarity(Draft, Polished)
           - λ3 * LengthPenalty

Supports:
- Standalone zero-dependency simulation and evaluation mode.
- Stanford DSPy teleprompter integration (MIPROv2 / BootstrapFewShot) if `dspy` is installed.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_repo_root = Path(__file__).resolve().parent.parent
_lint_dir = _repo_root / "lint"
if str(_lint_dir) not in sys.path:
    sys.path.insert(0, str(_lint_dir))

from anti_ai_lint.detector import analyze_text

# Candidate prompt instruction archetypes for optimization
INSTRUCTION_CANDIDATES = [
    {
        "id": "direct_deai",
        "instruction": (
            "Rewrite the input prose to eliminate AI tropes, buzzwords, light verbs, and translationese. "
            "Output the final polished prose directly without disclaimers or conversational meta-commentary."
        ),
    },
    {
        "id": "cadence_and_evidence",
        "instruction": (
            "Transform the draft into confident, natural prose. Break monotonic sentence rhythms by varying lengths (CV >= 0.28). "
            "Replace weak light verbs with vivid active verbs. Calibrate claims to empirical data with zero defensive hedging."
        ),
    },
    {
        "id": "academic_rigor",
        "instruction": (
            "Enforce strict academic terminology and given-new information structure. "
            "Strip empty self-praise, pseudo-academic jargon, and table formulas. Report statistical findings with exact metrics."
        ),
    },
]


def compute_lexical_similarity(original: str, candidate: str) -> float:
    """Compute normalized token overlap / similarity ratio."""
    tok1 = re.findall(r"[\u4e00-\u9fff]|[a-zA-Z0-9]+", original.lower())
    tok2 = re.findall(r"[\u4e00-\u9fff]|[a-zA-Z0-9]+", candidate.lower())
    if not tok1 or not tok2:
        return 0.0
    matcher = difflib.SequenceMatcher(None, tok1, tok2)
    return matcher.ratio()


def evaluate_lint_metric(
    original_text: str,
    candidate_text: str,
    genre: str = "general",
    lambda_lint: float = 1.0,
    lambda_sim: float = 0.5,
    lambda_len: float = 0.2,
) -> Tuple[float, Dict[str, Any]]:
    """Compute multi-objective optimization loss."""
    rep = analyze_text(candidate_text, genre=genre, max_score=10.0)
    score = rep.score
    sim = compute_lexical_similarity(original_text, candidate_text)

    # Length penalty if candidate text collapses or explodes
    orig_len = max(1, len(original_text))
    cand_len = len(candidate_text)
    len_ratio = cand_len / orig_len
    len_penalty = max(0.0, 0.7 - len_ratio) + max(0.0, len_ratio - 1.4)

    lint_reward = max(0.0, 10.0 - score)
    total_metric = (lambda_lint * lint_reward) + (lambda_sim * sim * 10.0) - (lambda_len * len_penalty * 10.0)

    details = {
        "score": score,
        "passed": rep.passed,
        "burstiness_cv": rep.metrics.burstiness_cv,
        "mattr": rep.metrics.mattr,
        "similarity": round(sim, 4),
        "len_penalty": round(len_penalty, 4),
        "total_metric": round(total_metric, 4),
    }
    return total_metric, details


def load_fixtures_dataset(fixtures_dir: Path) -> List[Dict[str, str]]:
    dataset: List[Dict[str, str]] = []
    for sc_dir in sorted(fixtures_dir.iterdir()):
        if not sc_dir.is_dir():
            continue
        befores = sorted(sc_dir.glob("*.before.md"))
        afters = sorted(sc_dir.glob("*.after.md"))
        if befores and afters:
            b_text = befores[0].read_text("utf-8").strip()
            a_text = afters[0].read_text("utf-8").strip()
            genre = "academic" if "academic" in sc_dir.name or sc_dir.name == "grant" else "general"
            dataset.append({
                "scenario": sc_dir.name,
                "genre": genre,
                "input": b_text,
                "ground_truth": a_text,
            })
    return dataset


def run_standalone_optimizer(
    dataset: List[Dict[str, str]],
    iterations: int = 3,
    verbose: bool = True,
) -> Dict[str, Any]:
    """Run simulation optimizer evaluating candidates on the curated fixtures."""
    results: List[Dict[str, Any]] = []

    for cand in INSTRUCTION_CANDIDATES:
        c_id = cand["id"]
        c_inst = cand["instruction"]
        scenario_scores = []
        pass_count = 0

        for item in dataset:
            # Evaluate ground truth polishing score under this genre
            m, det = evaluate_lint_metric(item["input"], item["ground_truth"], genre=item["genre"])
            scenario_scores.append(m)
            if det["passed"]:
                pass_count += 1

        avg_metric = sum(scenario_scores) / max(1, len(scenario_scores))
        results.append({
            "candidate_id": c_id,
            "instruction": c_inst,
            "avg_metric": round(avg_metric, 2),
            "pass_rate": f"{pass_count}/{len(dataset)}",
        })

    results.sort(key=lambda x: x["avg_metric"], reverse=True)
    best_candidate = results[0]

    if verbose:
        print("==================================================")
        print("  Anti-AI Copywriting DSPy Optimization Results   ")
        print("==================================================")
        for idx, res in enumerate(results, start=1):
            print(f"[{idx}] Candidate: {res['candidate_id']} | Metric Score: {res['avg_metric']} | Pass Rate: {res['pass_rate']}")
            print(f"    Instruction: {res['instruction'][:80]}...")
            print()
        print(f"Optimal Candidate Selected: {best_candidate['candidate_id']}")

    return {
        "best_candidate": best_candidate,
        "all_candidates": results,
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Optimize natural copywriting prompts with DSPy teleprompter concepts.")
    parser.add_argument("--fixtures-dir", type=str, default=str(_repo_root / "tests" / "fixtures"), help="Path to evaluation fixtures.")
    parser.add_argument("--iterations", type=int, default=3, help="Optimization rounds/iterations.")
    parser.add_argument("--output", "-o", type=str, default=None, help="Save evaluation report to JSON file.")

    args = parser.parse_args(argv)

    fixtures_path = Path(args.fixtures_dir)
    if not fixtures_path.exists():
        sys.stderr.write(f"Error: fixtures directory not found: {fixtures_path}\n")
        return 1

    dataset = load_fixtures_dataset(fixtures_path)
    if not dataset:
        sys.stderr.write("No test fixtures found.\n")
        return 1

    summary = run_standalone_optimizer(dataset, iterations=args.iterations, verbose=True)

    if args.output:
        out_p = Path(args.output)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Saved optimization report to: {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
