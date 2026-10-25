# 社区提交与开源生态注册指南

[English](COMMUNITY_SUBMISSIONS.md) | [简体中文](COMMUNITY_SUBMISSIONS.zh-CN.md)

本文档归档了将 `anti-ai-copywriting` 提交至主流开源目录、Agent 规则社区及开发者论坛的即用型 PR 模板、注册元数据与宣发文案草案。

---

## 1. Model Context Protocol (MCP) 注册与收录

### A. 官方 MCP 注册表 / `awesome-mcp-servers`

**PR 目标仓库**：`punkpeye/awesome-mcp-servers` 或 Anthropic 官方 MCP 服务器索引

**建议分类**：`Writing / Content / Text Processing` 或 `Development / Code Review`

```markdown
- [anti-ai-copywriting](https://github.com/CalebChen941028/anti-ai-copywriting) - 确定性零依赖自然语言质量门禁与上下文守护服务器，系统性消除中英文大模型输出中的 AI 套话、翻译腔与节奏呆滞。
```

**MCP Stdio 配置（`mcpServers` 块）**：

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

**暴露工具接口**：
- `lint_prose`：分析输入文本的 AI 黑话、形式动词名物化、标点滥用与句法方差，支持 `--source` 多源事实守恒核验。
- `remediate_violation`：针对特定违规类型给出基于规则的精准改写建议。
- `get_style_contract`：获取指定文体（`academic`, `plain`, `business`, `grant`, `social`）的完整词表与规则合约。

---

## 2. 智能体规则库收录（Agent Rules Catalogs）

### A. `awesome-cursorrules` (`PatrickJS/awesome-cursorrules`)

**目标仓库文件路径**：`rules/anti-ai-copywriting.mdc` 或 `rules/anti-ai-academic-prose.mdc`

**Frontmatter 与规则正文**：

```markdown
---
description: 引导 Cursor 智能体输出符合母语特征的自然语言，杜绝 AI 套话、防御性免责与恶性欧化。
globs: ["**/*.md", "**/*.markdown", "**/*.txt"]
---

<!-- BEGIN anti-ai-copywriting v0.9.0 -->
# 自然语态与学术专业文案规则（全域强制静默生效）

凡起草、润色、翻译或评审文案（包括学术论文、技术专栏、汇报与文档），必须遵守以下规范：
1. 词汇红线：封锁套话与伪学术黑话（赋能、抓手、闭环、底层逻辑、颗粒度、深度融合；delve into, testament to, realm, revolutionize, leverage）。
2. 句式重构：拔除形式动词“文字义肢”（进行/开展/作出加名物化还原为强动词）；交替使用短促句与复合长句（句长离散系数 CV_len >= 0.28）。
3. 掐头去尾：严禁“随着……飞速发展”等宏大开篇与假大空升华总结，第一句直奔事实、问题或方案。
4. 信息守恒（润色与翻译）：零新增事实、零误删事实、断言强度不变、语域对标原文。
5. 确定性门禁：输出后执行 `anti-ai-lint <file> --max-score 10.0` 自动校验。
<!-- END anti-ai-copywriting -->
```

### B. `awesome-claude-prompts` / Claude Desktop 系统指令

**Prompt 推荐配置**：

```markdown
已加载反 AI 腔规范 (v0.9.0)。无论生成或润色中文或英文文本：
- 第一句直接切入事实、问题或数据；严禁使用“随着……的发展”或“In today's fast-paced world”等宏大铺垫开篇。
- 拔除被动语态与动词名物化（“对系统进行了优化” -> “优化了系统性能”；“made an evaluation of” -> “evaluated”）。
- 学术论文中严格清除多层犹豫词（“可能或许试图尝试”）与辩解式免责声明，直接客观陈述适用边界。
- 润色与翻译严格遵循信息守恒：严禁无中生有增添原文不存在的数值、结论或情绪细节。
```

---

## 3. 开发者社区宣发文案草案（Launch Posts）

### A. Show HN (Hacker News) 英文发帖草案

详见 [COMMUNITY_SUBMISSIONS.md](COMMUNITY_SUBMISSIONS.md#3-launch-post-drafts-social--developer-channels)。

### B. V2EX / 知乎 / 掘金等技术社区发帖草案

**标题**：`开源分享：anti-ai-copywriting —— 彻底清洗大模型 AI 腔、文字义肢与套话的确定性门禁与写作规则引擎`

**正文要点**：
```markdown
大家在用 Claude / GPT / DeepSeek 写技术文档、学术论文或长文翻译时，经常会遇到一眼即识的“AI 味”：
- 动不动就“赋能/抓手/闭环/底层逻辑/颗粒度/深度融合”
- “不仅是……更是……”、“从……到……的飞跃”
- 万能形式动词文字义肢：“对系统进行了全面的性能测评”
- 匀速呆滞的句式节奏与方块段落（句长离散系数过低）
- 润色或翻译时模型擅自编造数据（如擅自加一句“同比提升了 35.7%”）

针对这些问题，我们开发了开源项目 anti-ai-copywriting (v0.9.0)：
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
