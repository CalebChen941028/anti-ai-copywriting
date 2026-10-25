# Community Submissions & Ecosystem Registrations

[English](COMMUNITY_SUBMISSIONS.md) | [简体中文](COMMUNITY_SUBMISSIONS.zh-CN.md)

This directory contains ready-to-use pull request templates, registry manifests, and launch post drafts for submitting `anti-ai-copywriting` across open-source directories and developer communities.

---

## 1. Model Context Protocol (MCP) Registries

### A. Official MCP Server Registry / `awesome-mcp-servers`

**Pull Request Target**: `punkpeye/awesome-mcp-servers` (or official Anthropic MCP server list)

**Suggested Category**: `Writing / Content / Text Processing` or `Development / Code Review`

```markdown
- [anti-ai-copywriting](https://github.com/CalebChen941028/anti-ai-copywriting) - Deterministic zero-dependency linter and in-loop style guardian for AI writing, eliminating AI buzzwords, translationese, and cadence monotony in Chinese and English.
```

**MCP Stdio Configuration (`mcpServers` block)**:

```json
{
  "mcpServers": {
    "anti-ai-copywriting": {
      "command": "python3",
      "args": ["-m", "anti_ai_lint.mcp_server"],
      "description": "Deterministic natural language quality linter and remediation server"
    }
  }
}
```

**Tool Capabilities**:
- `lint_prose`: Analyzes text for AI clichés, light-verb nominalizations, punctuation abuse, and cadence variance. Supports `--source` factual conservation.
- `remediate_violation`: Provides rule-grounded rewrite recommendations for specific violation categories.
- `get_style_contract`: Returns full style contract and wordlists for a given genre (`academic`, `plain`, `business`, `grant`, `social`).

---

## 2. Agent Rule Catalogs

### A. `awesome-cursorrules` (`PatrickJS/awesome-cursorrules`)

**File Location in Target Repo**: `rules/anti-ai-copywriting.mdc` or `rules/anti-ai-academic-prose.mdc`

**Frontmatter & Rule Content**:

```markdown
---
description: Guides Cursor agents to write natural, native-sounding prose free of obvious AI clichés, hedging, and translationese.
globs: ["**/*.md", "**/*.markdown", "**/*.txt"]
---

<!-- BEGIN anti-ai-copywriting v0.8.0 -->
# Anti-AI Copywriting & Natural Voice Rules (Mandatory & Silent)

Whenever drafting, editing, translating, or evaluating prose (academic papers, docs, columns, memos), follow these guidelines:
1. Forbidden Lexicon: Eliminate telltale AI markers (delve into, testament to, beacon of, tapestry of, realm, crucial/paramount, navigating complexities, revolutionize, leverage, seamless, foster, multifaceted).
2. Syntax & Cadence: Reduce nominalizations to active verbs. Avoid monotonic sentence lengths (target CV_len >= 0.28).
3. No Fluff Openings / Closings: Eliminate "In today's fast-paced world", "It is important to note that", and "In conclusion". Lead directly with concrete findings.
4. Information Conservation (Polishing/Translation): Add zero facts, drop zero facts, preserve assertion strength, and match source register.
5. Verification Gate: Verify prose via `anti-ai-lint <file> --max-score 10.0`.
<!-- END anti-ai-copywriting -->
```

### B. `awesome-claude-prompts` / Claude Desktop System Prompts

**Prompt Snippet**:

```markdown
You are configured with Anti-AI Copywriting guidelines (v0.8.0). Whenever generating or polishing Chinese or English prose:
- Lead directly with facts, problems, or data; never use grand cliché openings ("随着...的发展", "In today's fast-paced world").
- Eliminate passive nominalizations ("进行深入分析" -> "深入分析了"; "made an evaluation of" -> "evaluated").
- In academic texts, purge stacked hedges ("可能或许试图") and defensive disclaimers; state empirical boundaries neutrally.
- When polishing or translating, strictly obey information conservation: never invent numbers or emotional nuances absent from the source.
```

---

## 3. Launch Post Drafts (Social / Developer Channels)

### A. Show HN (Hacker News)

**Title**: `Show HN: Anti-AI Copywriting – Deterministic linting and writing rules for AI agents`

**Body**:
```markdown
Hi HN! We built `anti-ai-copywriting` (https://github.com/CalebChen941028/anti-ai-copywriting) to tackle a frustration many of us face: LLMs writing with identical, exhausting AI cadence — "delve into", "a testament to", stacked nominalizations, defensive disclaimers, and monotonic sentence lengths.

Instead of another black-box detector or probabilistic humanizer, it operates via two components:
1. Proactive writing rules & task routing (`drafting`, `polishing`, `translation`, `review`). Polishing and translation strictly adhere to information conservation axioms (no added numbers, no dropped facts, assertion strength preserved).
2. A deterministic, zero-dependency Python stdlib linter (`anti-ai-lint`) that checks:
   - Kobak et al. (Science Advances / Nature 2024) PubMed excess vocabulary
   - Coefficient of Variation for sentence and macro-paragraph lengths (CV_len >= 0.28, CV_para >= 0.15)
   - Consecutive sentence-starter repetition detection
   - Light verb constructions (文字义肢) in Chinese
   - Strict factual conservation against source texts (`--source file1.md file2.md`)

It includes a native Model Context Protocol (MCP) server, GitHub Action, pre-commit hook, and adapters for Claude Code, Codex, DeepSeek, Cursor, Windsurf, OpenCode, and WorkBuddy.

We also released dual-blind empirical benchmarks evaluated against DeepSeek-v4.1-flash and mimo-v2.6-flash, plus an authoritative human gold-standard baseline (USENIX ATC '14 Raft paper, Linux kernel docs, etc.) with 0.0 false-positive pass rates.

Code is MIT licensed: https://github.com/CalebChen941028/anti-ai-copywriting
Feedback and critique are very welcome!
```

### B. V2EX / 知乎 / 开发者社区发帖草案

**标题**: `开源分享：anti-ai-copywriting —— 彻底清洗大模型 AI 腔、文字义肢与套话的确定性门禁与写作规则引擎`

**正文要点**:
```markdown
大家在用 Claude / GPT / DeepSeek 写技术文档、学术论文或长文翻译时，经常会遇到一眼即识的“AI 味”：
- 动不动就“赋能/抓手/闭环/底层逻辑/颗粒度/深度融合”
- “不仅是……更是……”、“从……到……的飞跃”
- 万能形式动词文字义肢：“对系统进行了全面的性能测评”
- 匀速呆滞的句式节奏与方块段落（句长离散系数过低）
- 润色或翻译时模型擅自编造数据（如擅自加一句“同比提升了 35.7%”）

针对这些问题，我们开发了开源项目 anti-ai-copywriting (v0.8.0)：
1. 前置规范与温感交互：明确起草、润色、翻译、评审四类任务；润色与翻译严守信息守恒公理（零新增、零误删、断言强度不变）；
2. 确定性零依赖 Linter：纯 Python 标准库实现，支持学术/通用/白话三种语体门禁；
3. 多前沿算法拦截：
   - 宏观段落方差（CV_para < 0.15 拦截方块文本）
   - 句首语法结构固化拦截（连续「通过……」「基于……」）
   - 欧化长句与形式动词闭集匹配还原
   - 物理、数字与金额多量级语义等价归一化（ms ↔ s，万元 ↔ 亿元）
4. 全生态智能体无缝适配：已内建支持 Codex、Claude Code、DeepSeek、OpenCode、WorkBuddy、Cursor、Windsurf、Cline、Aider 等，支持 MCP 标准协议与 GitHub Actions。
5. 真实数据实证：包含在 DeepSeek-v4.1-flash 与 mimo-v2.6-flash 上的全量盲测调用记录（全量 200 OK，包含思考链耗时与 token 统计），以及 Raft 论文、Linux 内核文档、王坚《在线》等 4 篇权威母语金标文献（零误报验证）。

开源地址：https://github.com/CalebChen941028/anti-ai-copywriting
欢迎大家 Star 与体验！
```
