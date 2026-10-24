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


_UNIT_MAP: Dict[str, Tuple[str, float]] = {
    # Time (base: second)
    "ms": ("time_s", 0.001),
    "毫秒": ("time_s", 0.001),
    "s": ("time_s", 1.0),
    "秒": ("time_s", 1.0),
    "min": ("time_s", 60.0),
    "分钟": ("time_s", 60.0),
    "h": ("time_s", 3600.0),
    "小时": ("time_s", 3600.0),
    "day": ("time_s", 86400.0),
    "days": ("time_s", 86400.0),
    "天": ("time_s", 86400.0),
    # Data & storage (base: byte)
    "b": ("data_b", 1.0),
    "byte": ("data_b", 1.0),
    "bytes": ("data_b", 1.0),
    "字节": ("data_b", 1.0),
    "kb": ("data_b", 1000.0),
    "kib": ("data_b", 1024.0),
    "千字节": ("data_b", 1000.0),
    "mb": ("data_b", 1000000.0),
    "mib": ("data_b", 1048576.0),
    "兆字节": ("data_b", 1000000.0),
    "gb": ("data_b", 1000000000.0),
    "gib": ("data_b", 1073741824.0),
    "tb": ("data_b", 1000000000000.0),
    "tib": ("data_b", 1099511627776.0),
    # Magnitudes & Currency (base: unit count / CNY)
    "千万元": ("currency_cny", 10000000.0),
    "万元": ("currency_cny", 10000.0),
    "亿元": ("currency_cny", 100000000.0),
    "万单": ("orders", 10000.0),
    "单": ("orders", 1.0),
    "元": ("currency_cny", 1.0),
    "块": ("currency_cny", 1.0),
    "万": ("count", 10000.0),
    "亿": ("count", 100000000.0),
    "千": ("count", 1000.0),
}

_SORTED_UNITS = sorted(_UNIT_MAP.keys(), key=len, reverse=True)
_UNIT_REGEX = re.compile(
    r"^(?:[ \t]*(?P<unit>" + "|".join(re.escape(u) for u in _SORTED_UNITS) + r"))",
    re.IGNORECASE
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


def _parse_quantity(raw_num: str, trailing_text: str) -> Tuple[str, float] | None:
    """Parse numeric token and adjacent unit suffix into canonical (dimension, base_value)."""
    m = _UNIT_REGEX.match(trailing_text)
    if not m:
        return None
    raw_u = m.group("unit")
    lookup_key = raw_u.lower() if raw_u.isascii() else raw_u
    if lookup_key not in _UNIT_MAP:
        return None
    try:
        val = float(raw_num.replace(",", ""))
    except ValueError:
        return None
    dim, factor = _UNIT_MAP[lookup_key]
    return (dim, round(val * factor, 6))


def extract_anchors(text: str) -> Tuple[Dict[str, Dict[str, object]], str]:
    """Return ``(anchors, normalized_text)``.

    ``anchors`` maps each canonical token to ``{"kind", "pos", "raw", "count", "quantities"}`` where ``pos`` and
    ``raw`` describe the first occurrence and ``count`` is the number of occurrences.
    """
    norm = _normalize_source(text)
    anchors: Dict[str, Dict[str, object]] = {}
    for m in _ANCHOR.finditer(norm):
        kind = m.lastgroup or "num"
        canon = _canonical(kind, m.group(0))
        qty = _parse_quantity(m.group(0), norm[m.end():]) if kind == "num" else None
        if canon not in anchors:
            anchors[canon] = {
                "kind": kind,
                "pos": m.start(),
                "raw": m.group(0),
                "count": 1,
                "quantities": [qty] if qty is not None else [],
            }
        else:
            anchors[canon]["count"] = int(anchors[canon]["count"]) + 1
            if qty is not None:
                anchors[canon]["quantities"].append(qty)  # type: ignore[attr-defined]
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
    dropped from the output (penalty 3.0). Valid unit and magnitude conversions (e.g. 850ms <-> 0.85秒,
    3000万元 <-> 3千万元) are recognized as equivalent and not flagged as additions or omissions.
    """
    src_anchors, _ = extract_anchors(source_text)
    out_anchors, out_norm = extract_anchors(output_text)
    src_norm = _normalize_source(source_text)

    # Collect available canonical quantities in source for semantic equivalence matching
    available_src_quantities: Dict[Tuple[str, float], int] = {}
    src_qty_to_tokens: Dict[Tuple[str, float], List[str]] = {}
    for s_tok, s_info in src_anchors.items():
        for q in s_info.get("quantities", []):
            available_src_quantities[q] = available_src_quantities.get(q, 0) + 1
            src_qty_to_tokens.setdefault(q, []).append(s_tok)

    matched_src_tokens: set[str] = set()

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
            # Check if this output token can be matched via unit/magnitude equivalence
            matched_by_quantity = False
            for q in info.get("quantities", []):
                if available_src_quantities.get(q, 0) > 0:
                    available_src_quantities[q] -= 1
                    matched_by_quantity = True
                    # Mark corresponding source tokens as matched
                    for st in src_qty_to_tokens.get(q, []):
                        matched_src_tokens.add(st)
                    break
            if matched_by_quantity:
                continue
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
        if token in out_anchors or token in matched_src_tokens or info["kind"] == "acr":
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
