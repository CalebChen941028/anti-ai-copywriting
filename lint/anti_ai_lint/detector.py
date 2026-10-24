# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Liangliang Chen
"""Core text analysis and violation detection logic for anti-ai-copywriting."""

from __future__ import annotations

import json
import math
import os
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from .fidelity import check_fidelity
except (ImportError, ValueError):
    from anti_ai_lint.fidelity import check_fidelity


@dataclass
class LintViolation:
    category: str
    message: str
    line: int
    column: int
    context: str
    penalty: float
    suggestion: Optional[str] = None


@dataclass
class TextMetrics:
    total_chars: int = 0
    total_words: int = 0
    cjk_count: int = 0
    latin_words: int = 0
    sentence_count: int = 0
    de_count: int = 0
    de_ratio: float = 0.0
    dash_count: int = 0
    bold_count: int = 0
    exclamation_count: int = 0
    burstiness_cv: float = 0.0
    mattr: float = 0.0


@dataclass
class LintReport:
    file_path: Optional[str]
    score: float
    normalized_score: float = 0.0
    genre: str = "general"
    violations: List[LintViolation] = field(default_factory=list)
    metrics: TextMetrics = field(default_factory=TextMetrics)
    passed: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "score": round(self.score, 2),
            "normalized_score": round(self.normalized_score, 2),
            "genre": self.genre,
            "passed": self.passed,
            "metrics": asdict(self.metrics),
            "violations_count": len(self.violations),
            "violations": [asdict(v) for v in self.violations],
        }


def get_remediation_suggestion(category: str, match_text: str, context: str = "") -> str:
    """Provide actionable, concrete remediation suggestions for detected violations."""
    zh_buzz_map = {
        "赋能": "改用强动词：支持、促成、提升、帮助，或结合具体业务动作表达",
        "抓手": "改用具体工具、方案、切入点或举措",
        "闭环": "改用全流程、完整机制、全链条或具体业务流程",
        "底层逻辑": "改用核心原理、基本机制或运作机理",
        "颗粒度": "改用精度、细节程度或具体尺度",
        "生态链路": "改用业务体系、合作网络或服务链条",
        "矩阵": "改用产品组合、业务线或服务体系",
        "赛道": "改用行业、细分市场或业务方向",
        "多维度": "删除空洞修饰词，直接列举具体评估指标或测查维度",
        "全方位": "删除空洞修饰词，直接陈述覆盖的具体环节或范围",
        "深度融合": "具体说明融合方式、协同机制或结合点",
        "全面提升": "明确说明提升的具体指标、幅度或量化结果",
        "值得注意的是": "直接删除套话连接词，以事实或结论开门见山",
        "总而言之": "直接删除收尾套话，讲完论点或数据自然收笔",
        "综上所述": "直接删除套话过渡，段尾自然收束于事实或下一步举措",
        "毋庸置疑": "删除主观断言，让实证数据与逻辑推理展现说服力",
        "不可否认": "删除主观断言，直接陈述被确认的事实或论点",
        "不可或缺": "改用事实或具体机制说明其不可替代性",
        "至关重要": "直接删去或以具体因果机制/数据展现重要性",
        "重中之重": "改用客观优先级表述或具体资源分配比重",
        "再者": "剥离句首机械连接词，依靠段落内容层层顺承推进",
        "不言而喻": "删除断言套话，直接列出推导根据",
        "在当今快速发展的背景下": "掐头去尾：删去宏大背景开篇，从具体研究问题或事实切入",
        "扮演着不可或缺的角色": "拔除文字义肢，改用具象强动词（如：推动、调控、决定）",
        "起到了至关重要的作用": "拔除文字义肢，改用具象强动词（如：主导、触发、促进）",
    }
    if match_text in zh_buzz_map:
        return zh_buzz_map[match_text]

    en_buzz_map = {
        "delve into": "Replace with 'explore', 'examine', 'study', or 'inspect'",
        "delving into": "Replace with 'exploring', 'examining', 'studying', or 'inspecting'",
        "delve": "Replace with 'explore', 'examine', 'study', or 'inspect'",
        "testament to": "Replace with 'reflects', 'shows', 'proves', or 'indicates'",
        "beacon of": "Replace with 'model', 'standard', or 'leader'",
        "tapestry of": "Replace with 'range', 'array', 'collection', or 'diversity'",
        "intricate tapestry": "Replace with 'complex range' or describe specific components",
        "tapestry": "Replace with 'structure', 'range', 'combination', or describe concrete architecture",
        "meticulously": "Replace with 'carefully', 'systematically', 'thoroughly', or specify exact protocol",
        "commendable": "Delete subjective praise; let empirical metrics and results speak for themselves",
        "unwavering": "Delete subjective modifier; describe factual persistence or specific constraints",
        "realm of": "Replace with 'area of', 'field of', or 'domain of'",
        "realm": "Replace with 'area', 'field', 'domain', or 'context'",
        "intricate": "Replace with 'complex', 'detailed', or specify architectural layers",
        "navigating the complexities": "Replace with 'handling', 'working through', or 'addressing'",
        "navigating complexities": "Replace with 'handling' or 'addressing'",
        "revolutionize": "Replace with 'transform', 'alter', or describe specific technical change",
        "paradigm shift": "Replace with 'fundamental change' or describe the methodological distinction",
        "foster a culture": "Replace with 'build', 'encourage', or 'promote'",
        "foster": "Replace with 'build', 'support', 'encourage', or 'promote'",
        "myriad of": "Replace with 'many', 'numerous', or state exact quantity",
        "myriad": "Replace with 'many' or 'numerous'",
        "seamless integration": "Replace with 'smooth integration' or specify the exact interface",
        "seamlessness": "Replace with 'continuity' or 'integration'",
        "seamless": "Replace with 'smooth', 'integrated', or 'direct'",
        "seamlessly": "Replace with 'directly', 'smoothly', or describe the concrete pipeline/interface",
        "comprehensive": "Replace with specific scope: detailed, complete, or list the specific dimensions evaluated",
        "robust": "Replace with concrete technical property: fault-tolerant, resilient, or state stability bounds",
        "multifaceted approach": "Replace with 'detailed method' or state the specific steps",
        "multifaceted": "Replace with 'complex', 'detailed', or state specific components",
        "underscores the importance": "Replace with 'shows' or demonstrate importance through empirical data",
        "underscore the importance": "Replace with 'shows' or cite empirical results",
        "pivotal role": "Replace with active verb showing mechanism: 'drives', 'regulates', 'mediates'",
        "pivotal": "Replace with active verb showing mechanism: 'drives', 'regulates', 'determines'",
        "crucial role": "Replace with active verb showing mechanism: 'drives', 'regulates', 'mediates'",
        "vital role": "Replace with active verb showing mechanism: 'drives', 'regulates', 'mediates'",
        "plays a pivotal role": "Replace with active verb: 'drives', 'regulates', 'mediates'",
        "plays a crucial role": "Replace with active verb: 'drives', 'regulates', 'mediates'",
        "plays a vital role": "Replace with active verb: 'drives', 'regulates', 'mediates'",
        "in today's fast-paced world": "Delete grandiose opening; begin directly with empirical facts or specific problems",
        "in conclusion": "Delete transition phrase; conclude directly on findings or implications",
        "to summarize": "Delete phrase; end directly with conclusions or operational boundaries",
        "it is important to note that": "Delete phrase entirely; state the proposition directly",
        "utilize": "Replace with plain 'use'",
        "leverage": "Replace with 'use', 'apply', or describe the operational mechanism",
    }
    if match_text.lower() in en_buzz_map:
        return en_buzz_map[match_text.lower()]

    zh_lvc_verbs = ("进行", "开展", "展开", "作出", "予以", "给以", "给予", "加以", "具有", "得到", "受到", "作", "做", "致以")
    if "轻动词" in match_text or "弱动词" in match_text or any(v in match_text for v in zh_lvc_verbs) or any(v in context for v in zh_lvc_verbs):
        clean_target = match_text if any(v in match_text for v in zh_lvc_verbs) else (context[:25] if context else match_text)
        return f"消除轻动词与动作名物化（文字义肢）：将「{clean_target}」等形式动词搭配还原为直接动作强动词（例如：将「展开全面的性能测评」重构为「全面测评系统性能」；将「进行深入分析」重构为「深入分析」）"

    if any(k in match_text for k in ("如表", "表中", "Table", "Figure", "表格")):
        return "学术呈现规范：数值结果单独成句紧贴解释，避免套话引出表格（如‘如表所示’或‘As shown in Table’）"

    cat_map = {
        "forbidden_word_zh": f"消除套话「{match_text}」，改用平实具体的中文词汇或直陈事实",
        "forbidden_word_en": f"Eliminate AI trope '{match_text}', replace with concrete native verbs or direct active voice",
        "formulaic_pattern": "重构公式化句式：消除煽情对比或文字义肢，以单纯有力的强动词推进",
        "formulaic_pattern_en": "Refactor formulaic pattern into direct, natural syntax and active verbs",
        "defensive_disclaimer": "删去辩解式免责铺垫，客观界定样本与工具的适用边界（Scope Conditions）与后续方向",
        "hedging_overuse": "消除堆叠的弱化词，陈述事实时采用笃定的直陈语气",
        "particle_density": "将长定语拆解为3至5个顺向短句，严格控制‘的’字出现频次",
        "particle_ratio": "全局‘的’字占比偏高，建议将部分偏正结构改写为主谓或动宾短句",
        "punctuation_abuse": "每千字破折号建议不超过1次，破折号替换为逗号或独立短句",
        "formatting_abuse": "减少正文中的高频粗体强调，依靠段落结构和语义逻辑传达重点",
        "sentence_length_plain": "受控白话层单句长度超标（中文≤30字，英文≤25词），请强制断句拆分为独立短句",
        "vague_quantifier_plain": "受控白话层杜绝模糊量词（如‘若干’、‘一些’、‘等等’），请改用具体阿拉伯数字或明确定义",
        "table_formula_academic": "学术呈现规范：数值结果单独成句紧贴解释，避免套话引出表格（如‘如表所示’）",
        "empty_self_praise_academic": "学术语态规范：删去空洞自夸，客观陈述实证结果与应用场景",
        "rhythmic_monotony": "打破AI单调节奏（Monotonous Drone）：大幅调整句子长短波动，穿插5~10字/词短促斩截句与论述长句，提升文本信息起伏与节奏感（Burstiness）",
        "localized_rhythmic_monotony": "打破段落级局部节奏呆滞：该段落内连续句子长度过匀，建议穿插短促句（5~10字）打破等长单调感",
        "inappropriate_colloquialism": f"语体规范：在专业/学术/公文中剔除口语垫字与网络口吻（如「{match_text}」），恢复严谨务实的专业语态",
        "staccato_overfragmentation": "纠治过碎断气句：检测到连续3句以上超短碎片句，切勿为机械拉大句长方差而刻意切碎句子，保持论述连贯与自然呼吸",
        "english_participial_fronting": f"Eliminate repetitive fronted participial clauses ('{match_text}'): rephrase using direct subject-verb constructions",
        "english_sentence_head_stacking": f"Eliminate repetitive fronted discourse markers ('{match_text}'): vary sentence openings and integrate transitions smoothly",
        "fidelity_added": "信息守恒：润色与翻译不得新增原文没有的数字、代号或细节；核对原文后删除，或还原原文数值",
        "fidelity_dropped": "信息守恒：核对是否误删原文事实；数字、型号、参数不得在润色或翻译中丢失",
    }
    return cat_map.get(category, "遵循自然语态重塑规则，消除机器生成痕迹")


_INAPPROPRIATE_COLLOQUIALISMS = [
    "你猜怎么着", "说白了", "坦率地讲", "坦率地说", "老实讲", "老实说",
    "话说回来", "大伙儿", "老铁", "懂的都懂", "咱就是说", "谁能想到",
    "不得不承认的是", "无可厚非的是"
]


def _load_default_wordlists() -> tuple[dict[str, Any], dict[str, Any]]:
    current_dir = Path(__file__).resolve().parent
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
                "总而言之", "综上所述", "毋庸置疑", "不可否认", "不可或缺", "至关重要",
                "重中之重", "再者", "不言而喻", "在当今快速发展的背景下",
                "扮演着不可或缺的角色", "起到了至关重要的作用"
            ],
            "formulaic_patterns": [
                {"pattern": "随着.{1,30}的(飞速|快速)?发展", "name": "“随着……的飞速发展”公式化宏大开篇", "penalty": 4},
                {"pattern": "在当今.{0,20}(快速发展|日新月异|瞬息万变)的背景下", "name": "“在当今快速发展的背景下”公式化宏大开篇", "penalty": 4},
                {"pattern": "在.{1,20}的背景下", "name": "“在……背景下”套话句式", "penalty": 3},
                {"pattern": "一方面.{1,40}另一方面", "name": "“一方面……另一方面”公式化过渡", "penalty": 3},
                {"pattern": "扮演着.{1,20}的角色", "name": "“扮演着……角色”文字义肢/套话", "penalty": 4},
                {"pattern": "起到了?.{1,20}的作用", "name": "“起到……作用”文字义肢/套话", "penalty": 4},
                {"pattern": "不仅(仅)?是[^。！？\\n]{1,30}更(是)?", "name": "不仅...更是否定式煽情/升华", "penalty": 5},
                {"pattern": "不仅体现在.{1,40}更体现在", "name": "不仅体现在……更体现在……公式化排比", "penalty": 4},
                {"pattern": "不是.{1,30}而是(质的飞跃|协作模式的重塑|根本性的变革|跨越式的发展)", "name": "无实质对立面的伪对比煽情", "penalty": 4},
                {"pattern": "从[^。！？\\n]{1,30}到[^。！？\\n]{1,30}的(质变|飞跃|跨越)", "name": "虚假范围递进", "penalty": 4},
                {"pattern": "(进行|开展|展开|作出|予以|给以|给予|加以|具有|得到|受到|作|做|致以)[了的]?(?:[^，。！？；\\n]{0,8}?)[了的之]?(分析|探讨|调研|考察|评估|测评|审校|整改|梳理|阐述|测查|优化|迭代|部署|排查|总结|研究|复盘)", "name": "轻动词名物化搭配(文字义肢)", "penalty": 3.5},
                {"pattern": "(如表所示|从表中可以看出|结果如表.{1,10}所示)", "name": "套话表格陈述", "penalty": 3},
                {"pattern": "拟通过.{1,40}从而.{1,40}进而", "name": "“拟通过……从而……进而……”套链", "penalty": 3}
            ],
            "hedging_words": ["可能", "或许", "试图", "初步", "尝试", "有望", "倾向于", "似乎", "在某种程度上"],
            "defensive_disclaimers": [
                "虽然本研究还不成熟", "受限于现有条件仅能", "水平有限", "难免存在不足",
                "尚不成熟", "限于篇幅", "囿于现有条件"
            ]
        }

    if not en_data:
        en_data = {
            "forbidden_words": [
                "delve into", "delving into", "delve", "testament to", "beacon of",
                "tapestry of", "intricate tapestry", "tapestry", "meticulously",
                "realm of", "realm", "intricate", "navigating the complexities", "navigating complexities",
                "revolutionize", "paradigm shift", "foster a culture", "foster",
                "commendable", "unwavering", "myriad of", "myriad",
                "seamless integration", "seamlessness", "seamless", "seamlessly",
                "multifaceted approach", "multifaceted", "underscores the importance",
                "underscore the importance", "pivotal role", "pivotal", "crucial role", "vital role",
                "plays a pivotal role", "plays a crucial role", "plays a vital role",
                "in today's fast-paced world", "in conclusion", "to summarize",
                "it is important to note that", "utilize", "leverage", "comprehensive", "robust"
            ],
            "tier_penalties": {
                "delve into": 5.0, "delving into": 5.0, "delve": 5.0,
                "tapestry of": 5.0, "intricate tapestry": 5.0, "tapestry": 5.0,
                "meticulously": 5.0, "testament to": 5.0,
                "realm of": 3.5, "realm": 3.5, "intricate": 3.5,
                "pivotal role": 3.5, "pivotal": 3.5, "beacon of": 3.5,
                "commendable": 3.5, "foster a culture": 3.5, "foster": 3.5,
                "navigating the complexities": 3.5, "navigating complexities": 3.5,
                "unwavering": 3.5, "plays a pivotal role": 3.5,
                "plays a crucial role": 3.5, "plays a vital role": 3.5,
                "comprehensive": 2.0, "robust": 2.0, "leverage": 2.0, "utilize": 2.0,
                "seamless integration": 2.0, "seamlessness": 2.0, "seamless": 2.0, "seamlessly": 2.0,
                "multifaceted approach": 2.0, "multifaceted": 2.0, "myriad of": 2.0, "myriad": 2.0,
                "revolutionize": 2.0, "paradigm shift": 2.0,
                "underscores the importance": 2.0, "underscore the importance": 2.0,
                "crucial role": 2.0, "vital role": 2.0,
                "in today's fast-paced world": 2.0, "in conclusion": 2.0, "to summarize": 2.0,
                "it is important to note that": 2.0
            },
            "formulaic_patterns": [
                {"pattern": r"\bnot only\b[^.!?\r\n]{1,120}?\bbut also\b", "name": "Formulaic not only... but also", "penalty": 4},
                {"pattern": r"\bmake an? (investigation|examination|analysis|assessment|evaluation)\b", "name": "Heavy nominalization (make an analysis/investigation)", "penalty": 3},
                {"pattern": r"\b(furthermore|moreover|additionally)\b[^.!?\r\n]{1,120}?\b(furthermore|moreover|additionally)\b", "name": "Stacked mechanical transitions", "penalty": 4},
                {"pattern": r"\bplays? an? (pivotal|crucial|vital|key|essential) role in\b", "name": "Cliché 'plays a vital/pivotal role in'", "penalty": 4},
                {"pattern": r"\b[Ii]n today's (fast-paced|rapidly changing|interconnected|dynamic) world\b", "name": "Formulaic grand opening 'In today's fast-paced world'", "penalty": 4},
                {"pattern": r"\b[Aa]s shown in (Table|Figure) \d+\b", "name": "Formulaic table/figure presentation", "penalty": 3}
            ],
            "hedging_words": [
                "could potentially be suggested", "might tend to indicate",
                "seems somewhat likely", "appears to possibly",
                "could potentially indicate", "might perhaps suggest"
            ]
        }

    return zh_data, en_data


ABBREVIATIONS = {
    "e.g.", "i.e.", "et al.", "al.", "vs.", "fig.", "tab.", "dr.", "mr.", "mrs.", "ms.", "prof.", "dept.",
    "vol.", "no.", "pp.", "ed.", "eds.", "approx.", "cf.", "eq.", "eqs.", "ref.", "refs.", "u.s.", "u.k.", "e.u.",
    "etc.", "ibid.", "id.", "ca.", "viz.", "suppl.", "sec.", "corp.", "inc.", "ltd.", "co.", "jr.", "sr.",
    "jan.", "feb.", "mar.", "apr.", "jun.", "jul.", "aug.", "sep.", "sept.", "oct.", "nov.", "dec.",
    "ph.d.", "m.sc.", "b.sc.", "d.phil."
}

TITLE_ABBREVIATIONS = {
    "dr.", "mr.", "mrs.", "ms.", "prof.", "dept.", "sr.", "jr.",
    "vs.", "fig.", "tab.", "vol.", "no.", "pp.", "ed.", "eds.", "ca.", "viz."
}

QUOTE_CLOSERS = "\"'’”)])》」』"


def split_sentences_spans(text: str) -> List[Tuple[str, int]]:
    """Split text into sentences with start character offsets, supporting Chinese and English."""
    spans: List[Tuple[str, int]] = []
    start = 0
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        # CJK terminators
        if ch in "。！？；":
            end_idx = i + 1
            while end_idx < n and text[end_idx] in QUOTE_CLOSERS:
                end_idx += 1
            # Check for footnote reference immediately following terminator/quote e.g. [^1] or [1]
            fn_m = re.match(r"^\[\^?[a-zA-Z0-9_-]+\]", text[end_idx:])
            if fn_m:
                end_idx += fn_m.end()
                while end_idx < n and text[end_idx] in QUOTE_CLOSERS:
                    end_idx += 1
            raw_span = text[start:end_idx]
            stripped_span = raw_span.strip()
            if stripped_span:
                leading_ws = len(raw_span) - len(raw_span.lstrip())
                spans.append((stripped_span, start + leading_ws))
            start = end_idx
            i = end_idx
            continue

        # Newlines
        if ch == "\n":
            raw_span = text[start:i]
            stripped_span = raw_span.strip()
            if stripped_span:
                leading_ws = len(raw_span) - len(raw_span.lstrip())
                spans.append((stripped_span, start + leading_ws))
            while i < n and text[i] in "\r\n":
                i += 1
            start = i
            continue

        # ASCII sentence terminators (. ! ?)
        if ch in ".!?":
            is_decimal = False
            if ch == "." and i > 0 and i + 1 < n and text[i - 1].isdigit() and text[i + 1].isdigit():
                is_decimal = True

            is_abbr = False
            if ch == "." and not is_decimal:
                for abbr in ABBREVIATIONS:
                    if i + 1 >= len(abbr):
                        start_idx = i + 1 - len(abbr)
                        if text[start_idx : i + 1].lower() == abbr:
                            if start_idx == 0 or not text[start_idx - 1].isalnum():
                                if abbr in TITLE_ABBREVIATIONS:
                                    is_abbr = True
                                else:
                                    # Non-title abbreviation (e.g. etc., al.): ends sentence if followed by space + uppercase letter or end of text
                                    next_after_ws = i + 1
                                    while next_after_ws < n and text[next_after_ws] in " \t":
                                        next_after_ws += 1
                                    if next_after_ws < n and text[next_after_ws].isupper():
                                        is_abbr = False
                                    elif next_after_ws == n or text[next_after_ws] in "\r\n":
                                        is_abbr = False
                                    else:
                                        is_abbr = True
                                break
                # Single uppercase letter initial (e.g. "A. Smith" or "J. K.")
                if not is_abbr and i > 0 and text[i - 1].isupper():
                    if i == 1 or not text[i - 2].isalpha():
                        is_abbr = True
                # If dot is followed by space and lowercase ASCII character, it is continuation/abbreviation
                if not is_abbr and i + 2 < n and text[i + 1] in " \t" and text[i + 2].islower():
                    is_abbr = True

            if not is_decimal and not is_abbr:
                at_end = (i + 1 == n)
                next_is_ws = (i + 1 < n and text[i + 1] in (" \t\r\n" + QUOTE_CLOSERS + "["))
                if at_end or next_is_ws:
                    end_idx = i + 1
                    while end_idx < n and text[end_idx] in QUOTE_CLOSERS:
                        end_idx += 1
                    # Check for footnote reference immediately following terminator/quote e.g. [^1] or [1]
                    fn_m = re.match(r"^\[\^?[a-zA-Z0-9_-]+\]", text[end_idx:])
                    if fn_m:
                        end_idx += fn_m.end()
                        while end_idx < n and text[end_idx] in QUOTE_CLOSERS:
                            end_idx += 1
                    raw_span = text[start:end_idx]
                    stripped_span = raw_span.strip()
                    if stripped_span:
                        leading_ws = len(raw_span) - len(raw_span.lstrip())
                        spans.append((stripped_span, start + leading_ws))
                    start = end_idx
                    i = end_idx
                    continue
        i += 1

    if start < n:
        raw_span = text[start:]
        stripped_span = raw_span.strip()
        if stripped_span:
            leading_ws = len(raw_span) - len(raw_span.lstrip())
            spans.append((stripped_span, start + leading_ws))

    return spans


def sanitize_text_and_mask(text: str) -> Tuple[str, List[str]]:
    """
    Construct a masked version of text where fenced code blocks, LaTeX math blocks/environments,
    HTML comments, script/style blocks, HTML tags, inline code, inline math, headings,
    horizontal rules, table separators, URLs, and link destinations are replaced with spaces
    of identical length.
    Preserves exact character offsets and newline positions across LF and CRLF.
    """
    buf = list(text)

    def mask_span(start: int, end: int):
        for idx in range(start, end):
            if buf[idx] not in ("\r", "\n"):
                buf[idx] = " "

    # 1. Fenced code blocks (3+ backticks or tildes at line start with optional blockquote)
    lines_raw = text.splitlines(keepends=True)
    in_code_block = False
    fence_char = ""
    fence_len = 0
    curr_off = 0

    for line in lines_raw:
        nl_len = 2 if line.endswith("\r\n") else (1 if line.endswith("\n") else 0)
        content_len = len(line) - nl_len
        content_line = line[:content_len]
        if in_code_block:
            pat = r"^[ \t>]*" + re.escape(fence_char) + r"{" + str(fence_len) + r",}[ \t]*$"
            if re.match(pat, content_line):
                in_code_block = False
                fence_char = ""
                fence_len = 0
            mask_span(curr_off, curr_off + content_len)
        else:
            m_fence = re.match(r"^[ \t>]*(?P<fence>`{3,}|~{3,})", content_line)
            if m_fence:
                fence = m_fence.group("fence")
                in_code_block = True
                fence_char = fence[0]
                fence_len = len(fence)
                mask_span(curr_off, curr_off + content_len)
        curr_off += len(line)

    cur_text = "".join(buf)

    # 2. HTML comments <!-- ... -->
    for m in re.finditer(r"<!--.*?-->", cur_text, re.DOTALL):
        mask_span(m.start(), m.end())

    # 3. HTML script and style blocks
    cur_text = "".join(buf)
    for m in re.finditer(r"<(script|style)\b[^>]*>.*?</\1>", cur_text, re.DOTALL | re.IGNORECASE):
        mask_span(m.start(), m.end())

    # 4. LaTeX display math $$...$$
    cur_text = "".join(buf)
    for m in re.finditer(r"\$\$.*?\$\$", cur_text, re.DOTALL):
        mask_span(m.start(), m.end())

    # 5. LaTeX standard math environments \begin{env}...\end{env}
    math_envs = r"(?:equation|align|alignat|gather|multline|flalign|matrix|pmatrix|bmatrix|Bmatrix|vmatrix|Vmatrix|cases|split|array|math|displaymath)\*?"
    cur_text = "".join(buf)
    for m in re.finditer(rf"\\begin\{{({math_envs})\}}.*?\\end\{{\1\}}", cur_text, re.DOTALL):
        mask_span(m.start(), m.end())

    # 6. LaTeX bracket math \[...\] and \(...\)
    cur_text = "".join(buf)
    for m in re.finditer(r"\\\[.*?\\\]", cur_text, re.DOTALL):
        mask_span(m.start(), m.end())
    cur_text = "".join(buf)
    for m in re.finditer(r"\\\(.*?\\\)", cur_text, re.DOTALL):
        mask_span(m.start(), m.end())

    # 7. HTML tags: <tag ...>
    cur_text = "".join(buf)
    for m in re.finditer(r"<[a-zA-Z/][^>]*>", cur_text, re.DOTALL):
        mask_span(m.start(), m.end())

    # 8. Markdown headings (# Heading), table separators (|---|), thematic breaks (---, ***, ___), and footnote/ref definitions
    lines_masked = cur_text.splitlines(keepends=True)
    curr_off = 0
    for line in lines_masked:
        nl_len = 2 if line.endswith("\r\n") else (1 if line.endswith("\n") else 0)
        content_len = len(line) - nl_len
        content_line = line[:content_len]

        # Markdown headings
        if re.match(r"^[ \t>]*#", content_line):
            mask_span(curr_off, curr_off + content_len)
        # Markdown table separator row (|---|---|)
        elif re.match(r"^[ \t>]*\|?[ \t]*:?-+:?[ \t]*(?:\|[ \t]*:?-+:?[ \t]*)+\|?[ \t]*$", content_line):
            mask_span(curr_off, curr_off + content_len)
        # Thematic break / horizontal rule (---, ***, ___)
        elif re.match(r"^[ \t>]*([-*_])[ \t]*(?:\1[ \t]*){2,}$", content_line):
            mask_span(curr_off, curr_off + content_len)
        # Footnote definition or reference link definition prefix: [^1]: or [ref]:
        else:
            m_fn = re.match(r"^[ \t>]*\[\^?[^\]]+\]:[ \t]*", content_line)
            if m_fn:
                mask_span(curr_off, curr_off + m_fn.end())

        curr_off += len(line)

    # 9. Markdown link & image destinations: ](...)
    cur_text = "".join(buf)
    for m in re.finditer(r"\]\(\s*<?\S+?>?(?:\s+[\"'].*?[\"'])?\s*\)", cur_text):
        mask_span(m.start() + 1, m.end())

    # 10. Raw URLs
    cur_text = "".join(buf)
    for m in re.finditer(r"https?://[^\s)\]>\"']+", cur_text):
        mask_span(m.start(), m.end())

    # 11. Inline code: `...` or ``...``
    cur_text = "".join(buf)
    for m in re.finditer(r"(`+)(.+?)\1", cur_text):
        mask_span(m.start(), m.end())

    # 12. Inline math: $...$
    cur_text = "".join(buf)
    for m in re.finditer(r"(?<!\\)\$(?!\s)([^$\r\n]+?)(?<!\s)(?<!\\)\$", cur_text):
        mask_span(m.start(), m.end())

    sanitized_text = "".join(buf)
    sanitized_lines = sanitized_text.splitlines(keepends=True)
    return sanitized_text, sanitized_lines


def deduplicate_violations(items: List[Tuple[int, int, LintViolation]]) -> List[LintViolation]:
    """
    Given a list of (start_offset, end_offset, violation), deduplicate overlapping
    or subsumed violations so that a single phrase does not trigger multiple stacked
    penalties (e.g. 'pivotal role' inside 'plays a pivotal role in').
    Prefers longer spans or higher penalties when spans overlap.
    """
    if not items:
        return []

    # Sort items: primary key start_offset asc, secondary key length desc (end - start desc), tertiary penalty desc
    sorted_items = sorted(items, key=lambda x: (x[0], -(x[1] - x[0]), -x[2].penalty))

    result: List[Tuple[int, int, LintViolation]] = []
    for s, e, v in sorted_items:
        subsumed = False
        to_replace = -1
        for idx, (res_s, res_e, res_v) in enumerate(result):
            # Same exact span
            if s == res_s and e == res_e:
                subsumed = True
                if v.penalty > res_v.penalty:
                    result[idx] = (s, e, v)
                break
            # Current is completely inside existing span [res_s, res_e]
            if res_s <= s and e <= res_e:
                # Do not suppress specific words inside whole-sentence constraints (like sentence_length)
                if res_v.category.startswith("sentence_length") and not v.category.startswith("sentence_length"):
                    pass
                else:
                    subsumed = True
                    break
            # Existing span is completely inside current span [s, e]
            if s <= res_s and res_e <= e:
                if v.category.startswith("sentence_length") and not res_v.category.startswith("sentence_length"):
                    pass
                else:
                    to_replace = idx
                    break

        if to_replace != -1:
            result[to_replace] = (s, e, v)
        elif not subsumed:
            result.append((s, e, v))

    result.sort(key=lambda x: (x[2].line, x[2].column))
    return [v for _, _, v in result]


def analyze_text(
    text: str,
    file_path: Optional[str] = None,
    max_score: float = 10.0,
    max_normalized_score: Optional[float] = None,
    genre: str = "general",
    wordlists_dir: Optional[str] = None,
    source_text: Optional[str | List[str]] = None,
) -> LintReport:
    """
    Analyze text for AI buzzwords, punctuation abuse, particle density, and clichés.
    Supports code block masking, bilingual sentence splitting, genre-specific rules,
    span deduplication, and normalized score per 1,000 words/characters.

    When ``source_text`` is given (polishing or translation), the output is also checked
    for information conservation: numbers, codes, and acronyms that appear only in the
    output are penalized as possible fabrication, and numbers or codes that vanish from
    the output are penalized as possible omission. Any added anchor fails the gate outright.
    """
    genre = (genre or "general").strip().lower()
    if genre not in ("general", "academic", "plain"):
        genre = "general"

    if wordlists_dir and os.path.isdir(wordlists_dir):
        zh_p = Path(wordlists_dir) / "zh.json"
        en_p = Path(wordlists_dir) / "en.json"
        zh_data = json.loads(zh_p.read_text("utf-8")) if zh_p.is_file() else {}
        en_data = json.loads(en_p.read_text("utf-8")) if en_p.is_file() else {}
    else:
        zh_data, en_data = _load_default_wordlists()

    raw_violations: List[Tuple[int, int, LintViolation]] = []

    # Mask code blocks and inline code
    sanitized_text, sanitized_lines = sanitize_text_and_mask(text)

    # Metrics calculation based on sanitized prose text
    total_chars = len(text)
    # Broaden East Asian characters (CJK Unified, Extensions, Hiragana, Katakana, Hangul)
    cjk_count = len(re.findall(r"[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af\u1100-\u11ff\u3130-\u318f\uff66-\uff9f]", sanitized_text))
    latin_words = len(re.findall(r"[a-zA-Z0-9]+(?:[-'][a-zA-Z0-9]+)*", sanitized_text))
    total_words = cjk_count + latin_words

    de_count = sanitized_text.count("的")
    de_ratio = (de_count / cjk_count) if cjk_count > 0 else 0.0

    double_dashes = sanitized_text.count("——")
    single_dashes = sanitized_text.replace("——", "").count("—")
    dash_count = double_dashes + single_dashes

    # Count bold formatting only in prose body (exclude table rows and leading list item keys)
    prose_bold_lines = []
    for l in sanitized_lines:
        if re.match(r"^[ \t>]*\|.*\|[ \t]*$", l):
            continue
        l_sub = re.sub(r"^[ \t>]*[-*+][ \t]+\*\*[^*]+\*\*[:：]\s*", "", l)
        prose_bold_lines.append(l_sub)
    bold_count = len(re.findall(r"\*\*[^*]+\*\*", "\n".join(prose_bold_lines)))
    exclamation_count = sanitized_text.count("!") + sanitized_text.count("！")

    sentences = split_sentences_spans(sanitized_text)
    sentence_count = len(sentences)

    # Statistical cadence: Burstiness Coefficient of Variation (CV_len = sigma / mu)
    qualifying_lengths: List[int] = []
    for s_text, _ in sentences:
        s_cjk = len(re.findall(r"[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af\u1100-\u11ff\u3130-\u318f\uff66-\uff9f]", s_text))
        s_latin = len(re.findall(r"[a-zA-Z0-9]+(?:[-'][a-zA-Z0-9]+)*", s_text))
        l_total = s_cjk + s_latin
        if l_total >= 2:
            qualifying_lengths.append(l_total)

    burstiness_cv = 0.0
    if len(qualifying_lengths) >= 2:
        n_s = len(qualifying_lengths)
        mean_len = sum(qualifying_lengths) / n_s
        if mean_len > 0:
            variance = sum((x - mean_len) ** 2 for x in qualifying_lengths) / n_s
            std_dev = math.sqrt(variance)
            burstiness_cv = round(std_dev / mean_len, 4)

    # Statistical lexical richness: Moving-Average Type-Token Ratio (MATTR) with window 50
    token_matches = re.findall(
        r"[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af\u1100-\u11ff\u3130-\u318f\uff66-\uff9f]|[a-zA-Z0-9]+(?:[-'][a-zA-Z0-9]+)*",
        sanitized_text.lower()
    )
    total_tokens = len(token_matches)
    window_size = 50
    if total_tokens == 0:
        mattr = 0.0
    elif total_tokens < window_size:
        mattr = round(len(set(token_matches)) / total_tokens, 4)
    else:
        num_windows = total_tokens - window_size + 1
        window_counts: Dict[str, int] = {}
        for tok in token_matches[:window_size]:
            window_counts[tok] = window_counts.get(tok, 0) + 1
        distinct_sum = len(window_counts)

        for i in range(num_windows - 1):
            out_tok = token_matches[i]
            in_tok = token_matches[i + window_size]
            if window_counts[out_tok] == 1:
                del window_counts[out_tok]
            else:
                window_counts[out_tok] -= 1
            window_counts[in_tok] = window_counts.get(in_tok, 0) + 1
            distinct_sum += len(window_counts)

        mattr = round((distinct_sum / window_size) / num_windows, 4)

    metrics = TextMetrics(
        total_chars=total_chars,
        total_words=total_words,
        cjk_count=cjk_count,
        latin_words=latin_words,
        sentence_count=sentence_count,
        de_count=de_count,
        de_ratio=round(de_ratio, 4),
        dash_count=dash_count,
        bold_count=bold_count,
        exclamation_count=exclamation_count,
        burstiness_cv=burstiness_cv,
        mattr=mattr,
    )

    raw_lines = text.splitlines(keepends=True)
    line_offsets: List[int] = []
    curr_off = 0
    for l in sanitized_lines:
        line_offsets.append(curr_off)
        curr_off += len(l)

    # 1. Line-by-line checks for forbidden words and defensive disclaimers
    zh_forbidden = zh_data.get("forbidden_words", [])
    en_forbidden = en_data.get("forbidden_words", [])
    en_tier_penalties = en_data.get("tier_penalties", {})

    for line_idx, line in enumerate(sanitized_lines, start=1):
        clean_line = line.strip()
        if not clean_line:
            continue

        line_start_off = line_offsets[line_idx - 1]
        raw_line = raw_lines[line_idx - 1] if line_idx - 1 < len(raw_lines) else line

        # Forbidden words (Chinese)
        for w in zh_forbidden:
            for m in re.finditer(re.escape(w), line):
                p = 4.0
                context_str = raw_line[
                    max(0, m.start() - 15) : min(len(raw_line), m.end() + 15)
                ].strip()
                g_start = line_start_off + m.start()
                g_end = line_start_off + m.end()
                raw_violations.append((
                    g_start,
                    g_end,
                    LintViolation(
                        category="forbidden_word_zh",
                        message=f"Found forbidden buzzword/cliché: 「{w}」",
                        line=line_idx,
                        column=m.start() + 1,
                        context=context_str,
                        penalty=p,
                        suggestion=get_remediation_suggestion("forbidden_word_zh", w, context_str),
                    )
                ))

        # Forbidden words (English) with proper boundary handling
        for w in en_forbidden:
            w_start_b = r"\b" if re.search(r"^\w", w) else r"(?<!\w)"
            w_end_b = r"\b" if re.search(r"\w$", w) else r"(?!\w)"
            pattern = rf"{w_start_b}{re.escape(w)}{w_end_b}"
            for m in re.finditer(pattern, line, re.IGNORECASE):
                p = float(en_tier_penalties.get(w.lower(), 4.0))
                context_str = raw_line[
                    max(0, m.start() - 15) : min(len(raw_line), m.end() + 15)
                ].strip()
                g_start = line_start_off + m.start()
                g_end = line_start_off + m.end()
                raw_violations.append((
                    g_start,
                    g_end,
                    LintViolation(
                        category="forbidden_word_en",
                        message=f"Found forbidden AI trope/phrase: '{w}'",
                        line=line_idx,
                        column=m.start() + 1,
                        context=context_str,
                        penalty=p,
                        suggestion=get_remediation_suggestion("forbidden_word_en", w, context_str),
                    )
                ))

        # Check defensive disclaimers
        for discl in zh_data.get("defensive_disclaimers", []):
            if discl in line:
                m_start = line.find(discl)
                p = 6.0 if genre == "academic" else 5.0
                context_str = raw_line[
                    max(0, m_start - 10) : min(len(raw_line), m_start + len(discl) + 15)
                ].strip()
                g_start = line_start_off + m_start
                g_end = g_start + len(discl)
                raw_violations.append((
                    g_start,
                    g_end,
                    LintViolation(
                        category="defensive_disclaimer",
                        message=f"Found defensive disclaimer / self-undermining: 「{discl}」",
                        line=line_idx,
                        column=m_start + 1,
                        context=context_str,
                        penalty=p,
                        suggestion=get_remediation_suggestion("defensive_disclaimer", discl, context_str),
                    )
                ))

        # Check inappropriate colloquialisms (in formal genres: academic and general)
        if genre in ("academic", "general"):
            for coll in _INAPPROPRIATE_COLLOQUIALISMS:
                if coll in line:
                    m_start = line.find(coll)
                    context_str = raw_line[
                        max(0, m_start - 10) : min(len(raw_line), m_start + len(coll) + 15)
                    ].strip()
                    g_start = line_start_off + m_start
                    g_end = g_start + len(coll)
                    raw_violations.append((
                        g_start,
                        g_end,
                        LintViolation(
                            category="inappropriate_colloquialism",
                            message=f"Found inappropriate colloquial filler in formal context: 「{coll}」",
                            line=line_idx,
                            column=m_start + 1,
                            context=context_str,
                            penalty=2.5,
                            suggestion=get_remediation_suggestion("inappropriate_colloquialism", coll, context_str),
                        )
                    ))

    # 2. Formulaic patterns across sanitized text
    for pat_info in zh_data.get("formulaic_patterns", []):
        pat = pat_info["pattern"]
        name = pat_info.get("name", "Formulaic pattern")
        pen = float(pat_info.get("penalty", 3.0))
        for m in re.finditer(pat, sanitized_text):
            preceding = sanitized_text[: m.start()]
            l_num = preceding.count("\n") + 1
            col = m.start() - preceding.rfind("\n") if "\n" in preceding else m.start() + 1
            raw_match = text[m.start() : m.end()]
            raw_violations.append((
                m.start(),
                m.end(),
                LintViolation(
                    category="formulaic_pattern",
                    message=f"Found formulaic pattern: {name}",
                    line=l_num,
                    column=col,
                    context=raw_match[:60],
                    penalty=pen,
                    suggestion=get_remediation_suggestion("formulaic_pattern", name, raw_match),
                )
            ))

    for pat_info in en_data.get("formulaic_patterns", []):
        pat = pat_info["pattern"]
        name = pat_info.get("name", "Formulaic pattern")
        pen = float(pat_info.get("penalty", 3.0))
        for m in re.finditer(pat, sanitized_text, re.IGNORECASE):
            preceding = sanitized_text[: m.start()]
            l_num = preceding.count("\n") + 1
            col = m.start() - preceding.rfind("\n") if "\n" in preceding else m.start() + 1
            raw_match = text[m.start() : m.end()]
            raw_violations.append((
                m.start(),
                m.end(),
                LintViolation(
                    category="formulaic_pattern_en",
                    message=f"Found formulaic pattern: {name}",
                    line=l_num,
                    column=col,
                    context=raw_match[:60],
                    penalty=pen,
                    suggestion=get_remediation_suggestion("formulaic_pattern_en", name, raw_match),
                )
            ))

    # 3. Sentence-level checks (consecutive '的', hedge stacking, genre-specific)
    zh_hedges = zh_data.get("hedging_words", [])
    for s_text, s_start in sentences:
        s_line = sanitized_text[:s_start].count("\n") + 1
        s_col = s_start - sanitized_text[:s_start].rfind("\n") if "\n" in sanitized_text[:s_start] else s_start + 1

        # Check '的' density in single sentence
        de_in_s = s_text.count("的")
        if len(s_text) > 10 and de_in_s >= 4:
            p = 2.5
            raw_violations.append((
                s_start,
                s_start + len(s_text),
                LintViolation(
                    category="particle_density",
                    message=f"High '的' concentration ({de_in_s} occurrences in single clause)",
                    line=s_line,
                    column=s_col,
                    context=s_text[:50],
                    penalty=p,
                    suggestion=get_remediation_suggestion("particle_density", s_text),
                )
            ))

        # Check stacked hedging
        matched_hedges = [h for h in zh_hedges if h in s_text]
        if len(matched_hedges) >= 2:
            p = 4.0 if genre == "academic" else 3.0
            raw_violations.append((
                s_start,
                s_start + len(s_text),
                LintViolation(
                    category="hedging_overuse",
                    message=f"Stacked hedging in single sentence: {', '.join(matched_hedges)}",
                    line=s_line,
                    column=s_col,
                    context=s_text[:50],
                    penalty=p,
                    suggestion=get_remediation_suggestion("hedging_overuse", ", ".join(matched_hedges)),
                )
            ))

        # Genre: Controlled Plain Layer (受控白话层)
        if genre == "plain":
            # Skip Markdown table rows
            if re.match(r"^[ \t>]*\|.*\|[ \t]*$", s_text):
                continue

            # Length constraints: Chinese <= 30 chars, English <= 25 words
            s_cjk = len(re.findall(r"[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af\u1100-\u11ff\u3130-\u318f\uff66-\uff9f]", s_text))
            s_latin = len(re.findall(r"[a-zA-Z0-9]+(?:[-'][a-zA-Z0-9]+)*", s_text))
            if s_cjk == 0 and s_latin == 0:
                continue
            if s_cjk >= s_latin and len(s_text) > 30:
                p = 2.5
                raw_violations.append((
                    s_start,
                    s_start + len(s_text),
                    LintViolation(
                        category="sentence_length_plain",
                        message=f"Sentence exceeds plain layer length limit ({len(s_text)} chars > 30 chars)",
                        line=s_line,
                        column=s_col,
                        context=s_text[:50],
                        penalty=p,
                        suggestion=get_remediation_suggestion("sentence_length_plain", s_text),
                    )
                ))
            elif s_latin > s_cjk and s_latin > 25:
                p = 2.5
                raw_violations.append((
                    s_start,
                    s_start + len(s_text),
                    LintViolation(
                        category="sentence_length_plain",
                        message=f"Sentence exceeds plain layer word limit ({s_latin} words > 25 words)",
                        line=s_line,
                        column=s_col,
                        context=s_text[:50],
                        penalty=p,
                        suggestion=get_remediation_suggestion("sentence_length_plain", s_text),
                    )
                ))

            # Vague quantifiers check in plain mode
            for vq in ["若干", "一些", "等等"]:
                if vq in s_text:
                    vq_off = s_text.find(vq)
                    p = 2.0
                    raw_violations.append((
                        s_start + vq_off,
                        s_start + vq_off + len(vq),
                        LintViolation(
                            category="vague_quantifier_plain",
                            message=f"Vague quantifier in plain layer: 「{vq}」",
                            line=s_line,
                            column=s_col + vq_off,
                            context=s_text[:50],
                            penalty=p,
                            suggestion=get_remediation_suggestion("vague_quantifier_plain", vq),
                        )
                    ))

            for m in re.finditer(r"(?:\b(?:several|and so on)\b|\betc\.(?!\w))", s_text, re.IGNORECASE):
                p = 2.0
                raw_violations.append((
                    s_start + m.start(),
                    s_start + m.end(),
                    LintViolation(
                        category="vague_quantifier_plain",
                        message=f"Vague quantifier in plain layer: '{m.group(0)}'",
                        line=s_line,
                        column=s_col + m.start(),
                        context=s_text[:50],
                        penalty=p,
                        suggestion=get_remediation_suggestion("vague_quantifier_plain", m.group(0)),
                    )
                ))

    # 4. Genre: Academic Pro-Voice additional checks
    if genre == "academic":
        for m in re.finditer(r"(极其重要的现实意义|重大理论价值|填补了国内外空白)", sanitized_text):
            preceding = sanitized_text[: m.start()]
            l_num = preceding.count("\n") + 1
            col = m.start() - preceding.rfind("\n") if "\n" in preceding else m.start() + 1
            raw_violations.append((
                m.start(),
                m.end(),
                LintViolation(
                    category="empty_self_praise_academic",
                    message=f"Empty academic self-praise detected: 「{m.group(0)}」",
                    line=l_num,
                    column=col,
                    context=m.group(0),
                    penalty=4.0,
                    suggestion=get_remediation_suggestion("empty_self_praise_academic", m.group(0)),
                )
            ))

    # Deduplicate overlapping or subsumed text span violations
    violations = deduplicate_violations(raw_violations)

    if source_text is not None:
        for issue in check_fidelity(source_text, text):
            violations.append(
                LintViolation(
                    category=f"fidelity_{issue.kind}",
                    message=issue.message,
                    line=issue.line,
                    column=issue.column,
                    context=issue.context,
                    penalty=issue.penalty,
                    suggestion=issue.suggestion,
                )
            )

    # 5. Global metrics penalties
    # Excessive dashes: > 2 per 500 characters / words
    word_basis = cjk_count if cjk_count > 0 else total_words
    if word_basis > 200 and dash_count > (word_basis / 300):
        p = 3.0
        violations.append(
            LintViolation(
                category="punctuation_abuse",
                message=f"Excessive dashes/em-dashes ({dash_count} occurrences)",
                line=1,
                column=1,
                context=f"Total dashes: {dash_count}",
                penalty=p,
                suggestion=get_remediation_suggestion("punctuation_abuse", f"dashes={dash_count}"),
            )
        )

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
                suggestion=get_remediation_suggestion("particle_ratio", f"{de_ratio:.3f}"),
            )
        )

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
                suggestion=get_remediation_suggestion("formatting_abuse", f"bold={bold_count}"),
            )
        )

    # Rhythmic monotony: sentence length variation CV < 0.28 when sentences >= 6
    if len(qualifying_lengths) >= 6 and burstiness_cv < 0.28:
        p = 3.5
        violations.append(
            LintViolation(
                category="rhythmic_monotony",
                message=f"Rhythmic monotony detected: sentence length Coefficient of Variation CV={burstiness_cv:.2f} < 0.28 ({len(qualifying_lengths)} sentences, monotonous AI cadence)",
                line=1,
                column=1,
                context=f"burstiness_cv={burstiness_cv:.3f}, sentences={len(qualifying_lengths)}",
                penalty=p,
                suggestion=get_remediation_suggestion("rhythmic_monotony", f"{burstiness_cv:.2f}"),
            )
        )
    elif burstiness_cv >= 0.28 and (total_chars >= 600 or total_words >= 400):
        # Localized paragraph-level rhythmic monotony: in long-form texts (>=600 chars), check each prose paragraph
        para_pattern = re.compile(r"(?:[ \t]*\n){2,}")
        para_starts = [0] + [m.end() for m in para_pattern.finditer(sanitized_text)]
        para_blocks = para_pattern.split(sanitized_text)
        for p_idx, p_block in enumerate(para_blocks):
            # Skip empty paragraphs or list / enumeration blocks (e.g. 1. 2. 3. or bullets)
            if not p_block.strip() or re.search(r"^[ \t>]*(?:[-*+]|\d+[.)、）])", p_block, re.M):
                continue
            p_sents = split_sentences_spans(p_block)
            p_lengths: List[int] = []
            for s_t, _ in p_sents:
                c = len(re.findall(r"[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af\u1100-\u11ff\u3130-\u318f\uff66-\uff9f]", s_t))
                l = len(re.findall(r"[a-zA-Z0-9]+(?:[-'][a-zA-Z0-9]+)*", s_t))
                if c + l >= 4:
                    p_lengths.append(c + l)
            if len(p_lengths) >= 5:
                p_mean = sum(p_lengths) / len(p_lengths)
                if p_mean > 0:
                    p_var = sum((x - p_mean) ** 2 for x in p_lengths) / len(p_lengths)
                    p_cv = round(math.sqrt(p_var) / p_mean, 4)
                    if p_cv < 0.20:
                        p_off = para_starts[p_idx]
                        p_line = sanitized_text[:p_off].count("\n") + 1
                        violations.append(
                            LintViolation(
                                category="localized_rhythmic_monotony",
                                message=f"Localized rhythmic monotony detected in paragraph at line {p_line}: CV={p_cv:.2f} < 0.20 ({len(p_lengths)} sentences)",
                                line=p_line,
                                column=1,
                                context=p_block[:60].replace("\n", " ").strip(),
                                penalty=2.5,
                                suggestion=get_remediation_suggestion("localized_rhythmic_monotony", f"{p_cv:.2f}"),
                            )
                        )
                        break

    # Staccato over-fragmentation check: >= 3 consecutive micro-sentences (1 to 3 words/chars) in natural prose
    staccato_streak = 0
    staccato_start_idx = 0
    for s_idx, (s_text, s_pos) in enumerate(sentences):
        # Ignore markdown lists, headers, tables, links, or URL lines
        raw_s = text[s_pos : s_pos + len(s_text)]
        if (
            re.search(r"^[ \t>]*(?:[-*+]|\d+[.)、）]|#|\|)", s_text)
            or any(ch in raw_s for ch in ("[", "]", "(", ")", "http", "/", "\\", "`", ":", "："))
        ):
            staccato_streak = 0
            continue
        s_cjk = len(re.findall(r"[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af\u1100-\u11ff\u3130-\u318f\uff66-\uff9f]", s_text))
        s_latin = len(re.findall(r"[a-zA-Z0-9]+(?:[-'][a-zA-Z0-9]+)*", s_text))
        tot_l = s_cjk + s_latin
        if 1 <= tot_l <= 3:
            if staccato_streak == 0:
                staccato_start_idx = s_idx
            staccato_streak += 1
            if staccato_streak >= 3:
                s_line = sanitized_text[:sentences[staccato_start_idx][1]].count("\n") + 1
                streak_text = " ".join(sentences[j][0] for j in range(staccato_start_idx, s_idx + 1))
                violations.append(
                    LintViolation(
                        category="staccato_overfragmentation",
                        message=f"Staccato over-fragmentation detected at line {s_line}: {staccato_streak} consecutive micro-sentences ('{streak_text[:40]}')",
                        line=s_line,
                        column=1,
                        context=streak_text[:60],
                        penalty=2.5,
                        suggestion=get_remediation_suggestion("staccato_overfragmentation", streak_text[:30]),
                    )
                )
                break
        else:
            staccato_streak = 0

    # English sentence-head repetitive constructions (participial clauses & discourse adverbs)
    if latin_words >= 20:
        part_re = re.compile(r"^(?:(?!(?:During|According|Following|Including)\b)(?:[A-Z][a-z]*ing|Having\s+[a-z]+(?:ed|en|t))\b[^,]{3,45},)")
        adv_re = re.compile(r"^(?:Crucially|Notably|Importantly|Strikingly|Essentially|Ultimately|Consequently|Interestingly|Remarkably)\s*,")
        fronted_participle_matches = []
        fronted_adverb_matches = []
        for s_text, s_pos in sentences:
            s_clean = s_text.strip()
            m_p = part_re.match(s_clean)
            if m_p:
                fronted_participle_matches.append((m_p.group(0), s_pos))
            m_a = adv_re.match(s_clean)
            if m_a:
                fronted_adverb_matches.append((m_a.group(0), s_pos))

        if len(fronted_participle_matches) >= 2:
            first_match, s_pos = fronted_participle_matches[0]
            s_line = sanitized_text[:s_pos].count("\n") + 1
            violations.append(
                LintViolation(
                    category="english_participial_fronting",
                    message=f"Repetitive fronted participial clauses detected ({len(fronted_participle_matches)} occurrences, e.g. '{first_match}')",
                    line=s_line,
                    column=1,
                    context=first_match,
                    penalty=2.5,
                    suggestion=get_remediation_suggestion("english_participial_fronting", first_match),
                )
            )

        if len(fronted_adverb_matches) >= 2:
            first_match, s_pos = fronted_adverb_matches[0]
            s_line = sanitized_text[:s_pos].count("\n") + 1
            violations.append(
                LintViolation(
                    category="english_sentence_head_stacking",
                    message=f"Repetitive fronted transitional adverbs detected ({len(fronted_adverb_matches)} occurrences, e.g. '{first_match}')",
                    line=s_line,
                    column=1,
                    context=first_match,
                    penalty=2.5,
                    suggestion=get_remediation_suggestion("english_sentence_head_stacking", first_match),
                )
            )

    penalty_sum = round(sum(v.penalty for v in violations), 2)

    # Normalized score calculation (score per 1,000 words/units)
    if total_words > 0:
        normalized_score = round(penalty_sum / (total_words / 1000.0), 2)
    elif total_chars > 0:
        normalized_score = round(penalty_sum / (total_chars / 1000.0), 2)
    else:
        normalized_score = 0.0

    passed = penalty_sum <= max_score
    if max_normalized_score is not None:
        passed = passed and (normalized_score <= max_normalized_score)
    # An unsupported fact anchor is a hard failure regardless of the score threshold.
    if any(v.category == "fidelity_added" for v in violations):
        passed = False

    return LintReport(
        file_path=file_path,
        score=penalty_sum,
        normalized_score=normalized_score,
        genre=genre,
        violations=violations,
        metrics=metrics,
        passed=passed,
    )
