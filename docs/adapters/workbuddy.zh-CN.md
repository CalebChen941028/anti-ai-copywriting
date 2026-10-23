# WorkBuddy 适配器指南

[English](workbuddy.md) | [简体中文](workbuddy.zh-CN.md)

## 概述

WorkBuddy 是面向企业办公与协同场景的智能体助手平台。`anti-ai-copywriting` 支持通过提示词注入、命令行自动化部署以及 Webhook 外部门禁三种方式接入 WorkBuddy。

---

## 集成方案

### 方案 1：直接提示词注入（推荐）

将 `rules/AGENTS.snippet.zh.md` 中的精炼规则复制到 WorkBuddy 助手的全局系统设定或角色提示词中：

```markdown
# 自然语态与学术专业文案规则（全域强制静默生效）

所有文案与学术输出（学术论文、课题申报书、技术专栏、开发文档、小红书种草、商务汇报）必须严格遵守以下核心纪律：
1. 词汇红线：封锁互联网黑话与伪学术词（赋能、抓手、闭环、底层逻辑、颗粒度、多维度、全方位、深度融合、全面提升；delve into, testament to, realm, revolutionize, leverage）。
2. 句式重构：严禁“这不仅是……更是……”、“从……到……的飞跃”等公式化煽情句；拔除万能弱动词“文字义肢”（进行/作出+名词改用强动词）；控制单句“的”字密度。
3. 破除防御性AI腔：严禁单句叠加犹豫弱化词（可能、或许、试图、初步、尝试）；删去辩解式免责声明，直接客观陈述适用边界。
4. 掐头去尾：严禁“随着……飞速发展”宏大开篇与假大空升华总结，第一句直奔事实、问题或方案。
```

---

### 方案 2：通过命令行自动部署

将规则文件部署至 WorkBuddy 统一读取的配置目录或自定义提示词文件：

```bash
# 全局提示词安装
./install.sh --target workbuddy --lang zh

# 指定提示词输出路径
./install.sh --target workbuddy --dest /path/to/workbuddy/prompts/anti-ai-rules.md --lang zh
```

---

### 方案 3：自动化质量门禁（CI / 后处理 / Webhook）

若 WorkBuddy 流程通过 Webhook 或外部处理脚本衔接下游系统，可在输出前运行 `anti-ai-lint` 作为确定性拦截门禁：

```bash
anti-ai-lint /path/to/generated_output.md --max-score 8.0
```

若文本中存在违禁词或堆叠犹豫词，命令返回状态码 `1`，实现自动阻断与警示。

---

## 安全卸载

```bash
./uninstall.sh --target workbuddy
```

---

## 商标与非关联声明

WorkBuddy 是企业级协作助手产品。`anti-ai-copywriting` 是独立的开源项目，与 WorkBuddy 及其所属主体无任何官方关联、赞助或背书关系。
