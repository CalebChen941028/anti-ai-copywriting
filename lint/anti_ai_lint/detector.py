"""Core text analysis and violation detection logic for anti-ai-copywriting."""

from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class LintViolation:
    category: str
    message: str
    line: int
    column: int
    context: str
    penalty: float


@dataclass
class TextMetrics:
    total_chars: int = 0
    total_words: int = 0
    sentence_count: int = 0
    de_count: int = 0
    de_ratio: float = 0.0
    dash_count: int = 0
    bold_count: int = 0
    exclamation_count: int = 0


@dataclass
class LintReport:
    file_path: Optional[str]
    score: float
    violations: List[LintViolation] = field(default_factory=list)
    metrics: TextMetrics = field(default_factory=TextMetrics)
    passed: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "score": round(self.score, 2),
            "passed": self.passed,
            "metrics": asdict(self.metrics),
            "violations_count": len(self.violations),
            "violations": [asdict(v) for v in self.violations],
        }


def _load_default_wordlists() -> tuple[dict[str, Any], dict[str, Any]]:
    current_dir = Path(__file__).resolve().parent
    # Check parent repo wordlists or fallback
    candidates = [
        current_dir.parent.parent / "wordlists",
        current_dir / "wordlists",
    ]
    zh_data = {}
    en_data = {}
    for base in candidates:
        zh_path = base / "zh.json"
        en_path = base / "en.json"
        if zh_path.is_file() and not zh_data:
            try:
                zh_data = json.loads(zh_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        if en_path.is_file() and not en_data:
            try:
                en_data = json.loads(en_path.read_text(encoding="utf-8"))
            except Exception:
                pass

    if not zh_data:
        zh_data = {
            "forbidden_words": [
                "赋能", "抓手", "闭环", "底层逻辑", "颗粒度", "生态链路", "矩阵",
                "赛道", "多维度", "全方位", "深度融合", "全面提升", "值得注意的是",
                "总而言之", "综上所述", "毋庸置疑", "不可否认",
                "在当今快速发展的背景下", "随着...的飞速发展", "一方面...另一方面"
            ],
            "formulaic_patterns": [
                {"pattern": "不仅(仅)?是.*?更(是)?", "name": "不仅...更是否定式煽情/升华", "penalty": 5},
                {"pattern": "从.*?到.*?的(质变|飞跃|跨越)", "name": "虚假范围递进", "penalty": 4},
                {"pattern": "(进行|作出|造成|加以|具有|得到)[了的]?(详细|深入|系统|全面|实质|重要)?(调研|分析|探讨|研究|总结|考察|评估)", "name": "弱动词搭配抽象名词", "penalty": 3}
            ],
            "hedging_words": ["可能", "或许", "试图", "初步", "尝试", "有望", "倾向于", "似乎"],
            "defensive_disclaimers": ["虽然本研究还不成熟", "受限于现有条件仅能", "水平有限", "难免存在不足"]
        }

    if not en_data:
        en_data = {
            "forbidden_words": [
                "delve into", "delving into", "testament to", "beacon of",
                "tapestry of", "realm of", "navigating the complexities",
                "revolutionize", "paradigm shift", "foster a culture",
                "intricate tapestry", "myriad of", "seamless integration",
                "multifaceted approach", "underscores the importance",
                "pivotal role", "crucial role", "plays a vital role",
                "in today's fast-paced world", "in conclusion", "to summarize",
                "it is important to note that"
            ],
            "formulaic_patterns": [
                {"pattern": r"\bnot only\b.*?\bbut also\b", "name": "Formulaic not only... but also", "penalty": 4},
                {"pattern": r"\bmake an? (investigation|examination|analysis|assessment|evaluation)\b", "name": "Heavy nominalization", "penalty": 3},
                {"pattern": r"\b(furthermore|moreover|additionally)\b.*?\b(furthermore|moreover|additionally)\b", "name": "Stacked mechanical transitions", "penalty": 4}
            ],
            "hedging_words": ["could potentially be suggested", "might tend to indicate", "seems somewhat likely", "appears to possibly"]
        }

    return zh_data, en_data


def analyze_text(
    text: str,
    file_path: Optional[str] = None,
    max_score: float = 10.0,
    wordlists_dir: Optional[str] = None,
) -> LintReport:
    """Analyze text for AI buzzwords, punctuation abuse, particle density, and clichés."""
    if wordlists_dir and os.path.isdir(wordlists_dir):
        zh_p = Path(wordlists_dir) / "zh.json"
        en_p = Path(wordlists_dir) / "en.json"
        zh_data = json.loads(zh_p.read_text("utf-8")) if zh_p.is_file() else {}
        en_data = json.loads(en_p.read_text("utf-8")) if en_p.is_file() else {}
    else:
        zh_data, en_data = _load_default_wordlists()

    violations: List[LintViolation] = []
    lines = text.splitlines()

    total_chars = len(text)
    total_words = len(re.findall(r"\b\w+\b", text))
    de_count = text.count("的")
    # Chinese char count roughly
    cjk_count = len(re.findall(r"[\u4e00-\u9fff]", text))
    de_ratio = (de_count / cjk_count) if cjk_count > 0 else 0.0

    dash_count = text.count("——") + text.count("—")
    bold_count = len(re.findall(r"\*\*[^*]+\*\*", text))
    exclamation_count = text.count("!") + text.count("！")

    sentences = re.split(r"[。！？!?;\n]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    sentence_count = len(sentences)

    metrics = TextMetrics(
        total_chars=total_chars,
        total_words=total_words,
        sentence_count=sentence_count,
        de_count=de_count,
        de_ratio=round(de_ratio, 4),
        dash_count=dash_count,
        bold_count=bold_count,
        exclamation_count=exclamation_count,
    )

    penalty_sum = 0.0

    # 1. Check line-by-line for forbidden words and patterns
    zh_forbidden = zh_data.get("forbidden_words", [])
    en_forbidden = en_data.get("forbidden_words", [])

    for line_idx, line in enumerate(lines, start=1):
        clean_line = line.strip()
        if not clean_line or clean_line.startswith("#") or clean_line.startswith("```"):
            continue

        # Forbidden words (Chinese)
        for w in zh_forbidden:
            for m in re.finditer(re.escape(w), line):
                p = 4.0
                violations.append(
                    LintViolation(
                        category="forbidden_word_zh",
                        message=f"Found forbidden buzzword/cliché: 「{w}」",
                        line=line_idx,
                        column=m.start() + 1,
                        context=line[max(0, m.start() - 15): min(len(line), m.end() + 15)].strip(),
                        penalty=p,
                    )
                )
                penalty_sum += p

        # Forbidden words (English)
        for w in en_forbidden:
            pattern = rf"\b{re.escape(w)}\b"
            for m in re.finditer(pattern, line, re.IGNORECASE):
                p = 4.0
                violations.append(
                    LintViolation(
                        category="forbidden_word_en",
                        message=f"Found forbidden AI trope/phrase: '{w}'",
                        line=line_idx,
                        column=m.start() + 1,
                        context=line[max(0, m.start() - 15): min(len(line), m.end() + 15)].strip(),
                        penalty=p,
                    )
                )
                penalty_sum += p

        # Check defensive disclaimers
        for discl in zh_data.get("defensive_disclaimers", []):
            if discl in line:
                m_start = line.find(discl)
                p = 5.0
                violations.append(
                    LintViolation(
                        category="defensive_disclaimer",
                        message=f"Found defensive disclaimer / self-undermining: 「{discl}」",
                        line=line_idx,
                        column=m_start + 1,
                        context=line[max(0, m_start - 10): min(len(line), m_start + len(discl) + 15)].strip(),
                        penalty=p,
                    )
                )
                penalty_sum += p

    # 2. Formulaic patterns across the entire text or per sentence
    for pat_info in zh_data.get("formulaic_patterns", []):
        pat = pat_info["pattern"]
        name = pat_info.get("name", "Formulaic pattern")
        pen = float(pat_info.get("penalty", 3.0))
        for m in re.finditer(pat, text):
            # calculate line
            preceding = text[: m.start()]
            l_num = preceding.count("\n") + 1
            col = m.start() - preceding.rfind("\n") if "\n" in preceding else m.start() + 1
            violations.append(
                LintViolation(
                    category="formulaic_pattern",
                    message=f"Found formulaic pattern: {name}",
                    line=l_num,
                    column=col,
                    context=m.group(0)[:60],
                    penalty=pen,
                )
            )
            penalty_sum += pen

    for pat_info in en_data.get("formulaic_patterns", []):
        pat = pat_info["pattern"]
        name = pat_info.get("name", "Formulaic pattern")
        pen = float(pat_info.get("penalty", 3.0))
        for m in re.finditer(pat, text, re.IGNORECASE):
            preceding = text[: m.start()]
            l_num = preceding.count("\n") + 1
            col = m.start() - preceding.rfind("\n") if "\n" in preceding else m.start() + 1
            violations.append(
                LintViolation(
                    category="formulaic_pattern_en",
                    message=f"Found formulaic pattern: {name}",
                    line=l_num,
                    column=col,
                    context=m.group(0)[:60],
                    penalty=pen,
                )
            )
            penalty_sum += pen

    # 3. Sentence-level checks (consecutive '的' / hedge stacking)
    zh_hedges = zh_data.get("hedging_words", [])
    for s in sentences:
        # Check '的' density in single sentence
        de_in_s = s.count("的")
        if len(s) > 10 and de_in_s >= 4:
            p = 2.5
            violations.append(
                LintViolation(
                    category="particle_density",
                    message=f"High '的' concentration ({de_in_s} occurrences in single clause)",
                    line=text[: text.find(s)].count("\n") + 1 if s in text else 1,
                    column=1,
                    context=s[:50],
                    penalty=p,
                )
            )
            penalty_sum += p

        # Check stacked hedging
        matched_hedges = [h for h in zh_hedges if h in s]
        if len(matched_hedges) >= 2:
            p = 3.0
            violations.append(
                LintViolation(
                    category="hedging_overuse",
                    message=f"Stacked hedging in single sentence: {', '.join(matched_hedges)}",
                    line=text[: text.find(s)].count("\n") + 1 if s in text else 1,
                    column=1,
                    context=s[:50],
                    penalty=p,
                )
            )
            penalty_sum += p

    # 4. Global metrics penalties
    # Excessive dashes: > 2 per 500 characters
    if cjk_count > 200 and dash_count > (cjk_count / 300):
        p = 3.0
        violations.append(
            LintViolation(
                category="punctuation_abuse",
                message=f"Excessive dashes/em-dashes ({dash_count} occurrences)",
                line=1,
                column=1,
                context=f"Total dashes: {dash_count}",
                penalty=p,
            )
        )
        penalty_sum += p

    # High '的' overall ratio: > 8%
    if cjk_count > 100 and de_ratio > 0.08:
        p = 3.5
        violations.append(
            LintViolation(
                category="particle_ratio",
                message=f"Overall '的' ratio is {de_ratio * 100:.1f}% (recommended <= 5.0%)",
                line=1,
                column=1,
                context=f"de_ratio={de_ratio:.3f}",
                penalty=p,
            )
        )
        penalty_sum += p

    # Markdown bold formatting abuse: > 1 per 150 words
    if total_words > 100 and bold_count > (total_words / 100):
        p = 2.5
        violations.append(
            LintViolation(
                category="formatting_abuse",
                message=f"Excessive bold formatting ({bold_count} instances)",
                line=1,
                column=1,
                context=f"Total bold: {bold_count}",
                penalty=p,
            )
        )
        penalty_sum += p

    passed = penalty_sum <= max_score
    return LintReport(
        file_path=file_path,
        score=penalty_sum,
        violations=violations,
        metrics=metrics,
        passed=passed,
    )
