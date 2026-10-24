# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Liangliang Chen
"""Model Context Protocol (MCP) server for anti-ai-copywriting.

Provides standard JSON-RPC 2.0 stdio tools for AI coding agents:
- lint_prose: Analyze text or files for AI clichés, light verbs, and rhythm monotony.
  Optional ``source_text``/``source_path`` enables the polishing/translation fidelity check.
- remediate_violation: Get actionable rewrite guidance for specific violations.
- get_style_contract: Retrieve genre-specific natural style contracts.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, TextIO

try:
    from . import __version__
    from .detector import analyze_text, get_remediation_suggestion
except (ImportError, ValueError):
    parent_dir = str(Path(__file__).resolve().parent.parent)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    from anti_ai_lint import __version__
    from anti_ai_lint.detector import analyze_text, get_remediation_suggestion


MCP_SERVER_INFO = {
    "name": "anti-ai-copywriting",
    "version": __version__,
}

MCP_PROTOCOL_VERSION = "2024-11-05"

STYLE_CONTRACTS: Dict[str, Dict[str, str]] = {
    "zh": {
        "general": (
            "# 自然语态通用公理 (Chinese General Style Contract)\n\n"
            "1. 词汇红线：绝对封锁互联网黑话（赋能、抓手、闭环、底层逻辑、颗粒度、生态链路、矩阵、赛道、多维度、全方位）。\n"
            "2. 拔除文字义肢：消除万能弱动词（进行、开展、展开、作出、予以、加以）搭配抽象动作名词，还原为直接强动词。\n"
            "3. 掐头去尾：杜绝「随着……飞速发展」、「在当今快速发展的背景下」宏大开篇与「总而言之」套话收尾。\n"
            "4. 节奏起伏 (Burstiness)：避免全篇匀速句长，交替使用短促斩截句（5~10字）与缜密论述长句（CV >= 0.28）。\n"
            "5. 控制助词密度：每句助词「的」不超过2个，全篇「的」字比例低于5.0%。"
        ),
        "academic": (
            "# 学术专业语态公理 (Chinese Academic Pro-Voice Contract)\n\n"
            "1. 客观笃定：严禁单句堆叠犹豫弱化词（可能、或许、试图、尝试、有望），严禁辩解式免责声明。\n"
            "2. 适用边界：将局限性客观表述为「适用边界 (Scope Conditions)」与实证推进方向，不自我拆台。\n"
            "3. 真实因果与事实对比：区别处理对比句式，坚决封锁无实质对立面的伪对比煽情（不仅是……更是……），保留严谨实证纠偏。\n"
            "4. 术语纪律与数据句式：同一概念全文简称统一；数值结果单独成句紧贴解释，禁止「如表所示/从表中可以看出」套话引出表格。\n"
            "5. 课题申报直线推进：条目动词开头（构建/验证/估计/随访），删除「拟通过……从而……进而……」套链。"
        ),
        "plain": (
            "# 受控白话层公理 (Chinese Controlled Plain Layer Contract)\n\n"
            "1. 长度硬约束：中文单句长度严格控制在 <= 30 字符以内，长句强制断句为顺向短句。\n"
            "2. 杜绝模糊量词：严禁使用「若干」、「一些」、「等等」，必须使用具体阿拉伯数字或精确定义。\n"
            "3. 表述平实顺向：按时序展开事实，杜绝倒装与层层嵌套的长前饰定语。"
        ),
        "warm": (
            "# 温感叙事公理 (Chinese Warm Human-Touch Contract，仅适用于原创起草)\n\n"
            "1. 情感只来自真实细节：具体体感、时间、距离、等待分钟数、真实取舍；不用情绪形容词与感叹号替代细节。\n"
            "2. 严禁杜撰：用户没有提供的经历、数字、人物、引语一律不得编造；缺细节时先向用户索取，或写【待补：…】占位。\n"
            "3. 直面代价与不完美：不说满话，直陈两难与遗憾；结论与感慨留给读者。\n"
            "4. 继续封锁合成情绪：不仅是……更是……、质的飞跃、时代浪潮、深远意义。\n"
            "5. 润色与翻译不适用本公理：语域与情感强度一律对标原文。"
        ),
        "fidelity": (
            "# 信息守恒公理 (Chinese Information-Conservation Contract，润色与翻译)\n\n"
            "1. 零新增事实：不得增加原文没有的数字、人物、场景、因果、情绪细节。\n"
            "2. 零误删事实：数字、型号、参数、专名、引文不得丢失；只允许删除无信息量的客套与套话。\n"
            "3. 断言强度不变：原文的限定语（可能、关联、初步）若体现真实不确定性必须保留，不得把“关联”升级为“导致”。\n"
            "4. 语域对标：原文多冷就多冷，原文多温就多温；不额外煽情，也不抹平作者的语气。\n"
            "5. 温度来自句法解压：化解欧化长句、形式动词与翻译腔，按母语意合语序改写，而不是增生细节。\n"
            "6. 术语、数字、单位与专名前后一致；拿不准处保留原文并向用户标注待确认。\n"
            "7. 校验：anti-ai-lint <输出文件> --source <原文文件>。"
        ),
    },
    "en": {
        "general": (
            "# Natural English Style Contract\n\n"
            "1. Eliminate AI Clichés: Absolute ban on 'delve into', 'testament to', 'beacon of', 'intricate tapestry', 'realm', 'revolutionize', 'leverage', 'seamless', 'foster', 'multifaceted', 'pivotal role'.\n"
            "2. De-nominalization: Unpack sluggish noun phrases back into active verbs (e.g. 'made an assessment' -> 'assessed').\n"
            "3. Lead with Findings: Delete 'In today's fast-paced world', 'It is important to note that', 'In conclusion'. State conclusions directly.\n"
            "4. Rhythmic Cadence: Break the 20-word monotone AI drone. Alternate punchy short observations (5-8 words) with structured complex clauses (CV >= 0.28).\n"
            "5. Punctuation Restraint: Cap em-dashes at <= 1 per 1,000 words. Prefer full stops and precise commas."
        ),
        "academic": (
            "# Academic Pro-Voice Contract (English)\n\n"
            "1. Evidence-Calibrated Verbs: Reserve causal verbs ('drives', 'causes', 'mediates') strictly for causal designs (RCTs, counterfactual interventions). Use 'associated with' or 'predicted' for observational data.\n"
            "2. Affirmative De-hedging: When data prove the claim, use confident active voice instead of stacked hedging ('could potentially be suggested that...').\n"
            "3. Given-New Flow: Every paragraph begins with an anchor premise and advances to the empirical finding without stacking mechanical transitions (Moreover, Furthermore, Additionally).\n"
            "4. Precise Statistical Reporting: State exact confidence intervals and effect sizes (e.g. 'a 2.3% reduction (95% CI 1.1–3.5; P = 0.002)'). Never rely on ungrounded 'significantly changed'.\n"
            "5. Scope Boundaries: Frame limitations as operational scope conditions rather than apologetic disclaimers."
        ),
        "plain": (
            "# Controlled Plain Layer Contract (English)\n\n"
            "1. Strict Sentence Length: Sentences must not exceed 25 words. Split complex sentences into independent declarative clauses.\n"
            "2. Zero Vague Quantifiers: Ban 'several', 'and so on', 'etc.'. State exact numbers or operational specifications.\n"
            "3. Active Voice & Direct Nouns: Use straightforward agent-action phrasing."
        ),
        "warm": (
            "# Warm Human-Touch Contract (English, original drafting only)\n\n"
            "1. Warmth comes from real detail: concrete sensations, times, distances, minutes waited, genuine trade-offs. Never substitute mood adjectives or exclamation marks for detail.\n"
            "2. Never fabricate: experiences, numbers, people, or quotes the user did not supply must not be invented. Ask for them, or insert [TODO: ...] placeholders.\n"
            "3. State costs and imperfections plainly; leave the feeling to the reader.\n"
            "4. Keep banning synthetic emotion: 'not only ... but also' uplift, 'quantum leap', 'testament to', 'profound significance'.\n"
            "5. Does not apply to polishing or translation: register and emotional intensity follow the source."
        ),
        "fidelity": (
            "# Information-Conservation Contract (English, polishing and translation)\n\n"
            "1. Zero added facts: no numbers, people, scenes, causal claims, or emotional detail absent from the source.\n"
            "2. Zero dropped facts: numbers, model names, parameters, proper nouns, and citations survive. Only padding with no information may be deleted.\n"
            "3. Preserve assertion strength: keep hedges that express real uncertainty; never upgrade 'associated with' to 'causes'.\n"
            "4. Match register: as cold or as warm as the source, no extra drama, no flattening of the author's voice.\n"
            "5. Warmth comes from syntax, not invention: unpack nominalizations and translationese into native word order.\n"
            "6. Keep terminology, numbers, units, and names consistent. Where unsure, keep the source wording and flag it for the user.\n"
            "7. Verify with: anti-ai-lint <output-file> --source <source-file>."
        ),
    },
}

TOOLS_SPEC = [
    {
        "name": "lint_prose",
        "description": "Analyze prose text or markdown files for AI buzzwords, light verbs, syntactic clichés, and rhythm monotony.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Raw markdown or prose text to analyze.",
                },
                "file_path": {
                    "type": "string",
                    "description": "Optional file path to inspect (read from disk if text is omitted).",
                },
                "genre": {
                    "type": "string",
                    "enum": ["general", "academic", "plain"],
                    "default": "general",
                    "description": "Target genre conventions ('general', 'academic', or 'plain').",
                },
                "max_score": {
                    "type": "number",
                    "default": 10.0,
                    "description": "Maximum allowed penalty score before failure.",
                },
                "max_normalized_score": {
                    "type": "number",
                    "description": "Optional maximum penalty score per 1,000 words.",
                },
                "source_text": {
                    "type": "string",
                    "description": "Original text for polishing or translation. Enables the information-conservation check (added or dropped numbers, codes, acronyms).",
                },
                "source_path": {
                    "type": "string",
                    "description": "Optional path of the original file (read from disk if source_text is omitted).",
                },
            },
        },
    },
    {
        "name": "remediate_violation",
        "description": "Get actionable remediation recommendations and concrete natural language rewrites for a detected violation.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Violation category (e.g. 'forbidden_word_zh', 'forbidden_word_en', 'formulaic_pattern', 'rhythmic_monotony', 'defensive_disclaimer').",
                },
                "match_text": {
                    "type": "string",
                    "description": "Matched cliché phrase, buzzword, or metric label.",
                },
                "context": {
                    "type": "string",
                    "description": "Surrounding context sentence or clause.",
                },
            },
            "required": ["category", "match_text"],
        },
    },
    {
        "name": "get_style_contract",
        "description": "Retrieve the natural style contract and anti-ai writing axioms for a target genre and language.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "genre": {
                    "type": "string",
                    "enum": ["general", "academic", "plain", "warm", "fidelity"],
                    "default": "general",
                    "description": "Style contract: 'general', 'academic', 'plain', 'warm' (original drafting with real-detail warmth), or 'fidelity' (polishing and translation information conservation).",
                },
                "lang": {
                    "type": "string",
                    "enum": ["zh", "en"],
                    "default": "zh",
                    "description": "Target language: 'zh' (Chinese) or 'en' (English).",
                },
            },
        },
    },
]


def handle_tool_call(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    try:
        if name == "lint_prose":
            text = args.get("text")
            file_path = args.get("file_path")
            if not text and file_path:
                p = Path(file_path)
                if not p.is_file():
                    return {
                        "content": [{"type": "text", "text": f"Error: file not found: {file_path}"}],
                        "isError": True,
                    }
                try:
                    text = p.read_text(encoding="utf-8", errors="replace")
                except OSError as err:
                    return {
                        "content": [{"type": "text", "text": f"Error reading file {file_path}: {err}"}],
                        "isError": True,
                    }
            elif text is None:
                text = ""

            genre = str(args.get("genre", "general")).strip().lower()
            try:
                max_score = float(args.get("max_score", 10.0))
            except (ValueError, TypeError):
                max_score = 10.0

            max_norm = args.get("max_normalized_score")
            if max_norm is not None:
                try:
                    max_norm = float(max_norm)
                except (ValueError, TypeError):
                    max_norm = None

            source_text = args.get("source_text")
            source_path = args.get("source_path")
            if source_text is None and source_path:
                sp = Path(str(source_path))
                if not sp.is_file():
                    return {
                        "content": [{"type": "text", "text": f"Error: source file not found: {source_path}"}],
                        "isError": True,
                    }
                try:
                    source_text = sp.read_text(encoding="utf-8", errors="replace")
                except OSError as err:
                    return {
                        "content": [{"type": "text", "text": f"Error reading source file {source_path}: {err}"}],
                        "isError": True,
                    }
            if source_text is not None:
                source_text = str(source_text)

            report = analyze_text(
                text=text,
                file_path=file_path,
                max_score=max_score,
                max_normalized_score=max_norm,
                genre=genre,
                source_text=source_text,
            )
            data = report.to_dict()
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(data, ensure_ascii=False, indent=2),
                    }
                ],
                "isError": not report.passed,
            }

        elif name == "remediate_violation":
            category = str(args.get("category", "") or "")
            match_text = str(args.get("match_text", "") or "")
            context = str(args.get("context", "") or "")
            suggestion = get_remediation_suggestion(category, match_text, context)
            result_payload = {
                "category": category,
                "match_text": match_text,
                "suggestion": suggestion,
            }
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result_payload, ensure_ascii=False, indent=2),
                    }
                ],
                "isError": False,
            }

        elif name == "get_style_contract":
            genre = str(args.get("genre") or "general").strip().lower()
            lang = str(args.get("lang") or "zh").strip().lower()
            if lang not in STYLE_CONTRACTS:
                lang = "zh"
            if genre not in STYLE_CONTRACTS[lang]:
                genre = "general"
            contract_text = STYLE_CONTRACTS[lang][genre]
            return {
                "content": [{"type": "text", "text": contract_text}],
                "isError": False,
            }

        else:
            return {
                "content": [{"type": "text", "text": f"Error: unknown tool '{name}'"}],
                "isError": True,
            }
    except Exception as err:
        return {
            "content": [{"type": "text", "text": f"Internal tool execution error: {err}"}],
            "isError": True,
        }


def _process_single_message(msg: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(msg, dict):
        return {
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32600, "message": "Invalid Request: message must be an object"},
        }

    msg_id = msg.get("id")
    method = msg.get("method")
    params = msg.get("params") or {}
    if not isinstance(params, dict):
        params = {}

    if not method:
        if msg_id is not None:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32600, "message": "Invalid Request: missing method"},
            }
        return None

    # Handle client notification
    if method == "notifications/initialized":
        return None

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": MCP_PROTOCOL_VERSION,
                "serverInfo": MCP_SERVER_INFO,
                "capabilities": {
                    "tools": {},
                },
            },
        }

    elif method == "ping":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {},
        }

    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "tools": TOOLS_SPEC,
            },
        }

    elif method == "tools/call":
        tool_name = params.get("name", "")
        tool_args = params.get("arguments", {})
        if not isinstance(tool_args, dict):
            tool_args = {}
        call_res = handle_tool_call(tool_name, tool_args)
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": call_res,
        }

    else:
        if msg_id is not None:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32601,
                    "message": f"Method '{method}' not found",
                },
            }
        return None


def process_jsonrpc_message(msg: Any) -> Optional[Any]:
    """Process incoming JSON-RPC 2.0 message (single object or batch array)."""
    if isinstance(msg, list):
        if not msg:
            return {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32600, "message": "Invalid Request: empty batch"},
            }
        responses = []
        for item in msg:
            resp = _process_single_message(item)
            if resp is not None:
                responses.append(resp)
        return responses if responses else None
    return _process_single_message(msg)


def run_mcp_server(
    in_stream: Optional[TextIO] = None,
    out_stream: Optional[TextIO] = None,
) -> int:
    """Run MCP server stdio event loop."""
    inp = in_stream or sys.stdin
    out = out_stream or sys.stdout

    if hasattr(inp, "reconfigure"):
        try:
            inp.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    if hasattr(out, "reconfigure"):
        try:
            out.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    try:
        for line in inp:
            raw = line.strip()
            if not raw:
                continue
            try:
                req = json.loads(raw)
            except Exception as err:
                err_resp = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": f"Parse error: {err}"},
                }
                out.write(json.dumps(err_resp) + "\n")
                out.flush()
                continue

            try:
                resp = process_jsonrpc_message(req)
                if resp is not None:
                    out.write(json.dumps(resp, ensure_ascii=False) + "\n")
                    out.flush()
            except Exception as loop_err:
                err_resp = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32603, "message": f"Internal error: {loop_err}"},
                }
                out.write(json.dumps(err_resp) + "\n")
                out.flush()
    except (BrokenPipeError, KeyboardInterrupt):
        return 0

    return 0


def main() -> int:
    return run_mcp_server()


if __name__ == "__main__":
    sys.exit(main())
