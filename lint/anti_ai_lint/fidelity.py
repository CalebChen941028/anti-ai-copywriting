# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Liangliang Chen
"""Source-fidelity (information conservation) check for polishing and translation.

Polishing and translation must not add facts that the source does not contain.
This module compares the verifiable "fact anchors" (numbers, alphanumeric codes
such as ``H100`` or ``CASP14``, and all-caps acronyms) of a source text against an
output text and reports anchors that appear only in the output (possible
fabrication) or only in the source (possible omission).

The check is a deterministic, zero-dependency heuristic. It cannot see invented
adjectives, scenes, or emotions that carry no digits or acronyms, so a clean result
means "no unsupported anchors found", not "faithful". Chinese numerals
(e.g. 三个通宵) are intentionally not tracked because characters such as 一 are far too
ambiguous for a reliable rule.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Dict, List, Tuple

ADDED_PENALTY = 5.0
DROPPED_PENALTY = 3.0

_LIST_MARKER = re.compile(r"^[ \t>]*(?:[-*+]|\d+[.)、）])[ \t]+", re.MULTILINE)
_HEADING_MARK = re.compile(r"^[ \t>]*#{1,6}[ \t]+", re.MULTILINE)
_FOOTNOTE_REF = re.compile(r"\[\^?[A-Za-z0-9_-]+\]")
# Alternation order matters: letter-led codes first, then plain numbers, then acronyms.
_ANCHOR = re.compile(
    r"(?P<code>(?<![A-Za-z0-9])[A-Za-z]+\d[A-Za-z0-9]*)"
    r"|(?P<num>\d+(?:[.,]\d+)*)"
    r"|(?P<acr>(?<![A-Za-z])[A-Z]{2,}(?![a-z]))"
)


@dataclass
class FidelityIssue:
    kind: str  # "added" or "dropped"
    token: str
    line: int
    column: int
    context: str
    penalty: float
    message: str
    suggestion: str


def _normalize_source(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = _HEADING_MARK.sub("", text)
    text = _LIST_MARKER.sub("", text)
    text = _FOOTNOTE_REF.sub(" ", text)
    return text


def _canonical(kind: str, raw: str) -> str:
    """Normalize numbers (drop thousands separators) so 1,200 equals 1200."""
    if kind != "num":
        return raw
    return raw.replace(",", "")


def extract_anchors(text: str) -> Tuple[Dict[str, Dict[str, object]], str]:
    """Return ``(anchors, normalized_text)``.

    ``anchors`` maps each canonical token to ``{"kind", "pos", "raw", "count"}`` where ``pos`` and
    ``raw`` describe the first occurrence and ``count`` is the number of occurrences.
    """
    norm = _normalize_source(text)
    anchors: Dict[str, Dict[str, object]] = {}
    for m in _ANCHOR.finditer(norm):
        kind = m.lastgroup or "num"
        canon = _canonical(kind, m.group(0))
        if canon not in anchors:
            anchors[canon] = {"kind": kind, "pos": m.start(), "raw": m.group(0), "count": 1}
        else:
            anchors[canon]["count"] = int(anchors[canon]["count"]) + 1
    return anchors, norm


def _locate(norm: str, pos: int) -> Tuple[int, int, str]:
    before = norm[:pos]
    line = before.count("\n") + 1
    column = pos - before.rfind("\n") if "\n" in before else pos + 1
    start = max(0, pos - 15)
    context = norm[start : pos + 20].replace("\n", " ").strip()
    return line, column, context


def check_fidelity(source_text: str, output_text: str) -> List[FidelityIssue]:
    """Compare fact anchors of ``output_text`` against ``source_text``.

    Returns issues for anchors added in the output (penalty 5.0) and for numbers or codes
    dropped from the output (penalty 3.0). A plain number is "added" when it occurs more
    often in the output than in the source, so a new "3 weeks" is caught even if the source
    already contains another "3". Codes and acronyms are compared as sets. Dropped acronyms
    are ignored because translation commonly expands or contracts them.
    """
    src_anchors, _ = extract_anchors(source_text)
    out_anchors, out_norm = extract_anchors(output_text)
    src_norm = _normalize_source(source_text)

    issues: List[FidelityIssue] = []
    for token, info in out_anchors.items():
        src_info = src_anchors.get(token)
        if src_info is not None:
            surplus = info["kind"] == "num" and int(info["count"]) > int(src_info["count"])
            if not surplus:
                continue
            detail = (
                f"occurs {info['count']} times in the output but only {src_info['count']} in the source"
            )
        else:
            detail = "appears in the output but not in the source"
        line, column, context = _locate(out_norm, int(info["pos"]))
        issues.append(
            FidelityIssue(
                kind="added",
                token=str(info["raw"]),
                line=line,
                column=column,
                context=context,
                penalty=ADDED_PENALTY,
                message=f"Fact anchor '{info['raw']}' {detail} (possible fabricated detail)",
                suggestion=(
                    "润色与翻译必须信息守恒：核对原文，若原文没有该数字/代号/缩写，请删除；"
                    "Polishing and translation must not add facts: delete it or restore the source value."
                ),
            )
        )
    for token, info in src_anchors.items():
        if token in out_anchors or info["kind"] == "acr":
            continue
        line, column, context = _locate(src_norm, int(info["pos"]))
        issues.append(
            FidelityIssue(
                kind="dropped",
                token=str(info["raw"]),
                line=1,
                column=1,
                context=f"source L{line}: {context}",
                penalty=DROPPED_PENALTY,
                message=f"Fact anchor '{info['raw']}' from the source is missing in the output (possible omission)",
                suggestion=(
                    "核对是否误删事实：数字、型号、参数不得在润色或翻译中丢失；"
                    "Restore the value unless it was deliberately removed padding."
                ),
            )
        )
    issues.sort(key=lambda i: (i.kind != "added", i.line, i.column))
    return issues
