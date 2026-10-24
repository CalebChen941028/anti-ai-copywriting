# anti-ai-copywriting（自然语态与学术文案引擎）

[English](README.md) | [简体中文](README.zh-CN.md)

[![CI](https://github.com/CalebChen941028/anti-ai-copywriting/actions/workflows/ci.yml/badge.svg)](https://github.com/CalebChen941028/anti-ai-copywriting/actions)
[![Version: 0.8.0](https://img.shields.io/badge/version-0.8.0-green.svg)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)

**一套指导 AI 生成自然语言、符合母语特征、无明显 AI 腔调的双语规范准则（面向 AI 编程智能体与大模型工作流）。**

系统性消除大模型输出中的恶性欧化、翻译腔、伪学术黑话、公式化煽情排比与防御性免责。覆盖四类核心任务：起草 (Drafting)、润色 (Polishing)、翻译 (Translation) 与评审 (Review)。在润色与翻译场景下严格遵循**信息守恒**（零增添、零遗漏、断言强度不变）；在经验起草场景下提供可选的**温感叙事语态**，且严禁杜撰未提供的细节。

---

## 1. 系统定位与行业范式对比

当前市面上的 AI 文本工具普遍落入两类极端：一类是**事后惩罚型检测工具**，仅在成文后打分；另一类是**粗暴同义词替换的商业改写降重工具**，容易破坏学术与专业写作所必须的术语与事实。`anti-ai-copywriting` 开辟了第三种路径：**先验生成规范引导结合环内确定性拦截门禁**。

> [!NOTE]
> 本表仅从技术机制维度对常见工具类别作宏观范式比对，并非针对任何商业产品的跑分评测，亦未对任何具体竞品进行实测对比。

| 评估维度 | 事后检测工具类<br>*(Turnitin, GPTZero 等)* | 改写降重工具类<br>*(商业改写降重服务)* | `anti-ai-copywriting`<br>*(本项目)* |
| :--- | :--- | :--- | :--- |
| **干预时机** | 事后打分；在文本生成后进行被动判定 | 事后改写，替换同义词 | **起草前先验注入约束** (`<auto_trigger>`) + **环内确定性拦截门禁** |
| **事实与术语纪律** | 无（仅负责标记） | 盲目同义词换装，容易篡改专有名词与断言关系 | **润色与翻译严格遵循信息守恒**，支持 `--source` 比对数字、型号与专有缩写 |
| **文体节奏建模** | 依赖黑盒模型打分 | 制造不通顺语序逃避检测 | **纯标准库句长变异系数** ($CV_{len} \ge 0.28$) 与 **MATTR** (窗口 50)，完全透明可查 |
| **词汇依据** | 通常不公开 | 通常不公开 | **公开 JSON 词表**，基于科学论文超额词实证文献与汉语形式动词闭集 |
| **情感与语态选择** | 无 | 无 | 原创起草支持可选的**温感叙事模式**；严禁杜撰未提供的客观事实 |
| **开发者生态** | Web 控制台或付费 API | 网页表单或付费订阅 | **零依赖 CLI**、**原生 MCP 服务**、**GitHub Action**、**Pre-commit 钩子** 与 **DPO 导出器** |

---

## 2. 真实大模型实测：mimo-v2.6-flash（Solo Model vs. Model + Skill + Tool Gate）

> [!NOTE]
> 完整 8 大科目实测案例详析、指标推导、语言学病理诊断与复现指南请参阅：**[全量实测对比与基准评测报告 (docs/BENCHMARK_REPORT.zh-CN.md)](docs/BENCHMARK_REPORT.zh-CN.md)**。

> [!IMPORTANT]
> **真实 API 数据来源声明**：本表为通过 OpenCode Go 网关（`https://opencode.ai/zen/go/v1/chat/completions`）对真实模型 **`mimo-v2.6-flash`** 执行端到端推理的**双盲对照实测数据**（评测时间：2026-10-24T11:28:04Z → 11:33:58Z）。全程 **24 次真实 HTTP POST 全部返回 200**（平均时延 14,391 ms），累计消耗 **27,976 tokens**（Prompt 14,554 + Completion 13,422，其中 Reasoning 7,635 tokens）。每次调用均有服务端唯一 `response_id` 存据。原始文本与不可篡改的凭据记录持久化于 `tests/fixtures_mimo/`，由 `python3 scripts/run_mimo_benchmark.py` 一键复现。仓库已彻底清除所有演示模拟产物，唯一以本实测为真值基准。

基于同一组客观中立提示词对 `mimo-v2.6-flash` 的 8 大科目（6 大起草场景 + 2 大信息守恒场景）实测对比如下：

| 评测场景分类 | 语体模式 | 单一模型扣分 (Solo) | 模型+技能工具 (After) | 扣分降幅 | AI 违规项数 | 门禁判定 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **学术论文摘要** (`academic`) | 学术级 | 16.5 分 | **4.0 分** | **-75.8%** | 5 处 -> **1 处** | ❌ FAIL -> **✅ PASS** |
| **商业管理备忘** (`business`) | 通用级 | 2.5 分 | **0.0 分** | **-100.0%** | 1 处 -> **0 处** | ✅ -> **✅** |
| **英文顶会论文** (`en_academic`) | 英文学术 | 2.5 分 | **0.0 分** | **-100.0%** | 1 处 -> **0 处** | ✅ -> **✅** |
| **科研基金申报** (`grant`) | 学术级 | 5.5 分 | **3.0 分** | **-45.5%** | 2 处 -> **1 处** | ✅ -> **✅** |
| **前沿科普专栏** (`popsci`) | 通用级 | 3.0 分 | 3.0 分 | 持平（反例） | 1 处 -> 1 处 | ✅ -> **✅** |
| **社交数码实测** (`social`) | 通用级 | 5.5 分 | **3.0 分** | **-45.5%** | 2 处 -> **1 处** | ✅ -> **✅** |
| **故障通报润色** (`polish`，信息守恒) | 通用级 + `--source` | 5.0 分 | **0.0 分** | **-100.0%** | 1 处（杜撰 35.7%）-> **0 处** | ❌ 硬拦截 -> **✅ PASS** |
| **技术文档英译中** (`translate`，信息守恒) | 通用级 + `--source` | 3.5 分 | 3.5 分 | 持平（反例） | 1 处 -> 1 处 | ✅ -> **✅** |
| **全场景宏观均值**（8 科） | - | **5.50 分** | **2.06 分** | **-62.5%** | **1.75 处 -> 0.62 处（-64.3%）** | **75.0% -> 100% 通过** |

- **信息守恒硬兜底**：单一模型在润色场景自行根据 14 次与 9 次推算并杜撰出「降幅达 35.7%」写入通报，被 `fidelity_added` 规则强制拦截；技能+工具门禁组实现数字 100% 守恒，杜撰清零。
- **开篇套话与节律纠偏**：学术场景单一模型原生出现“随着……的飞速发展”公式化开篇、轻动词名物化文字义肢及呆滞句长节奏（$CV_{len} = 0.25$），技能组通过事实先行与节律调控将扣分由 16.5 分降至 4.0 分。
- **真实反例如实披露**：科普专栏与英译中场景两组持平，如实记录真实模型在不同任务上的客观表现，未做任何人工修饰。
- **DPO 对齐语料支持**：完整成对偏好数据已导出三种对齐格式至 `data/mimo_dpo/`。

### 2.2 高难度进阶极限实测：deepseek-v4.1-flash（跨段落长文、量纲转换与对抗黑话）

> [!NOTE]
> 为验证引擎在更长篇幅、更精密量纲与强对抗性场景下的鲁棒性，新增针对 **`deepseek-v4.1-flash`** 的极限基准实测套件。详细审计记录见 [tests/fixtures_advanced/BENCHMARK_REPORT.md](tests/fixtures_advanced/BENCHMARK_REPORT.md)。

> [!IMPORTANT]
> **真实 API 审计保障**：全部调用通过 OpenCode Go 网关（`https://opencode.ai/zen/go/v1/chat/completions`，会话：`session-deepseek-advanced-benchmark-2026`）直连模型 **`deepseek-v4.1-flash`** 完成。累计 **10 次真实 HTTP POST 全部返回 200 OK**（平均时延 19,009 ms），消耗 **29,843 tokens**（Prompt 7,569 + Completion 22,274，其中 Reasoning 17,461 tokens），每条均含网关签发唯一 `response_id`。全部产物存档于 `tests/fixtures_advanced/`，可通过 `python3 scripts/run_advanced_benchmark.py` 一键无 Mock 复现。

| 进阶高难度场景 | 核心挑战考察点 | 单一模型 (Solo) | 模型+技能门禁 (After) | 门禁判定 | 闭环机制体现 |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **长文双活架构演进** (`long_architecture`) | 1500+字长文本风格漂移、段落节奏呆滞、虚词堆叠 | 4.0 分 / 1 处违规 | **0.0 分 / 0 处违规** | ❌ 拦截 -> **✅ 通关** | 先验规则约束，1503词达标且全段落呼吸感健康 |
| **金融清算系统改造成效** (`financial_unit_fidelity`) | `--source` 下精密数字、物理与金融量纲等价归一 | 7.5 分 / 2 处违规 | **5.0 分 / 2 处违规** | ❌ 拦截 -> **✅ 通关** | 环内自愈机制生效（57.5分 -> 5.0分放行）；等价量纲平滑放行，虚构数值彻底杜绝 |
| **对抗性大厂战略黑话清洗** (`adversarial_cliche`) | 10+处空洞动词与黑话套话清洗（赋能/抓手/闭环/组合拳） | 2.5 分 / 1 处违规 | **2.5 分 / 1 处违规** | ✅ 通关 -> **✅ 通关** | 黑话全部拔除还原为落地行动，仅残留极少样式加粗 |
| **诱导性学术论述评述** (`multiturn_remediation`) | 诱导性宏大叙事与空洞自夸高风险提示 | 11.0 分 / 3 处违规 | **0.0 分 / 0 处违规** | ❌ 拦截 -> **✅ 通关** | 先验免疫（Pre-conditioning）阻断违规，首轮零分 |

### 2.3 四大极限深水区压力实测：deepseek-v4.1-flash（代码公式隔离、反伪口语化、多源综合守恒与长篇英文）

> [!NOTE]
> 针对代码混排、过度反AI口语化反噬、跨文件多源事实张冠李戴以及长篇英文句首套话四大深水区，构建了极限前沿基准评测。详细审计记录见 [tests/fixtures_extreme/BENCHMARK_REPORT.md](tests/fixtures_extreme/BENCHMARK_REPORT.md)。

> [!IMPORTANT]
> **真实 API 审计保障**：全部调用通过 OpenCode Go 网关（`https://opencode.ai/zen/go/v1/chat/completions`，会话：`session-deepseek-extreme-benchmark-2026`）直连模型 **`deepseek-v4.1-flash`** 完成。累计 **12 次真实 HTTP POST（含 1 次截断安全重试）全部返回 200 OK**（平均时延 28,095 ms），消耗 **45,156 tokens**（Prompt 12,129 + Completion 33,027，其中 Reasoning 26,112 tokens），每条均含网关签发唯一 `response_id`。全部产物存档于 `tests/fixtures_extreme/`，可通过 `python3 scripts/run_extreme_benchmark.py` 一键无 Mock 复现。

| 极限深水区场景 | 核心挑战考察点 | 单一模型 (Solo) | 模型+技能门禁 (After) | 门禁判定 | 闭环机制与实证发现 |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **代码与LaTeX公式密集型** (`code_math_interleave`) | DPDK用户态网络白皮书，检验围栏代码块内部符号、端口号与数学公式隔离 | 42.0 分 / 9 处违规 | **12.5 分 / 3 处违规** | ❌ 拦截 -> **✅ 显著收敛** | 代码块内部符号零误报；自愈轮由 65.0 分大幅收敛至 12.5 分，终稿主动识别量纲瑕疵 |
| **反伪口语化与碎句断气** (`anti_camouflage_colloquial`) | 严厉诱导“使用大白话、像聊天一样”，检验严肃公文语体失范 | 2.5 分 / 1 处违规 | **3.5 分 / 1 处违规** | ✅ 通关 -> **✅ 通关** | 裸模型落入陷阱，被 `inappropriate_colloquialism` 命中「说白了」；技能组恢复庄重语态 |
| **多源事实综合守恒** (`multi_source_synthesis`) | 跨架构、性能与财务 3 份独立分册，检验联合事实锚点池与防张冠李戴 | 37.5 分 / 8 处违规 | **0.0 分 / 0 处违规** | ❌ 拦截 -> **✅ 完美通关** | 裸模型跨册数字过度复述（7处违规）；技能组经环内自愈（40.0分 -> 0.0分），数字严丝合缝 |
| **长篇英文前沿白皮书** (`long_english_whitepaper`) | 600-900 词技术 Position Paper，检验句首分词短语连用与论述转折副词堆叠 | 0.0 分 / 0 处违规 | **3.0 分 / 1 处违规** | ✅ 通关 -> **✅ 通关** | 两组全文节奏均优良（$CV \ge 0.40$）；技能组因破折号残留得 3.0 分，反例透明披露 |

---

## 3. 核心能力与 AI 工程架构

- **任务分流、信息守恒与温感交互协议**（`skill/anti-ai-copywriting/SKILL.md` 第 0 节）：
  - 智能体首先对任务进行四分流：起草 (Drafting)、润色 (Polishing)、翻译 (Translation) 或评审 (Review)。
  - **润色与翻译场景严格遵循信息守恒**：事实权归原文所有。零增添事实（不杜撰数字、专名、情绪、背景细节）、零遗漏核心事实、断言强度不变、语体对齐原文。温感与母语感纯粹源于“意合化”语法解压与去欧化，绝不靠虚构细节煽情。
  - **经验叙事类起草场景支持温感交互**：面向散文、专栏、数码实测、品牌故事或演讲等经验性文体，若用户未明确语调且处于交互式会话，智能体主动出具 A/B 示例供用户选择（A. 客观克制 vs. B. 温感叙事）。温感模式仅使用用户提供的真实细节；若缺乏细节，必须以 `[待补充细节: ...]` 占位，严禁自行杜撰。
  - 学术论文、基金申报、技术方案、商业备忘、润色、翻译以及非交互式批量运行默认直接采用客观克制语调，绝不触发提问。
- **信息守恒确定性门禁、多源事实联合池与语义量纲等价引擎**：
  - `anti-ai-lint out.md --source original.md [source2.md ...]`，对输出文本相对于原文的事实锚点进行双向比对。
  - **多源事实联合守恒池**：支持接收多份源文件构建联合事实池，在综合提炼中严格阻断任何源文件未记载的衍生数据（`fidelity_added`），同时豁免对背景冗余细节的合理精简。
  - **代码与公式底层符号隔离保护**：自动识别并隔离围栏代码块（Fenced Code Blocks）与展示公式（Display Math），防止代码内部的端口号、内存地址与公式运算符污染正文事实；行内代码（`` `850ns` ``）与行内公式自动剥离包裹符号，确保技术硬核指标正常接受严格守恒核验。
  - **精密量纲语义等价识别**：支持物理时间（`ms ↔ 秒`、`min ↔ 分钟`、`h ↔ 小时`、`day ↔ 天`）、存储容量（`B ↔ KB ↔ MB ↔ GB ↔ TB`）与中文金融计数级（`万 ↔ 亿`、`3000万元 ↔ 3千万元`）的语义等价识别，杜绝合理单位转换误报。
- **信息论节奏感度量、反伪口语化与长文段落局部呆滞检测**：
  - 基于纯 Python 标准库实现全局句长变异系数（Coefficient of Variation, $CV_{len} = \sigma / \mu$）。全局 $CV_{len} < 0.28$ 判定为 `rhythmic_monotony`（扣 3.5 分）。
  - **长文本段落级局部节奏呆滞检测**（`localized_rhythmic_monotony`）：对 $\ge 600$ 字符长文自动扫描各自然段，若非枚举段落内连续 $\ge 5$ 句的局部变异系数 $CV < 0.20$，施加 2.5 分惩罚并指导穿插短促句，打破长篇大段中等长 AI 腔。
  - **严肃文体反伪口语化与碎句断气拦截**：`inappropriate_colloquialism` 拦截在专业/学术/公文中出现的聊天垫字（「说白了」「你猜怎么着」等）；`staccato_overfragmentation` 捕捉连续 $\ge 3$ 个极短碎片句（如“对。没错。就是它。”），防止恶意刷高方差。
  - **长篇英文句首套话与副词机械堆叠纠偏**：识别英文句首现在分词短语连用（`english_participial_fronting`，如连续句首使用 `Leveraging...` / `Delving...`）与句首论述转折副词堆叠（`english_sentence_head_stacking`，如 `Crucially,` / `Notably,`）。
  - 引入滑动窗口词汇丰富度（MATTR / Moving-Average Type-Token Ratio，窗口 50），避免传统 TTR 受文本长度影响的问题。
- **科学论文超额词频突变词表**（参考 Kobak et al., 2025, *Science Advances*）：
  - 依据该文献追踪 1500 万篇 PubMed 论文摘要得出的风格词异动，提炼高危词表。分级扣分为本项目启发式规则设定，非文献原始统计值：
    - **Tier S（极高跃升，扣 5.0 分）**：`delve`, `delve into`, `delving into`, `tapestry of`, `intricate tapestry`, `meticulously`, `testament to`。
    - **Tier A（中高跃升，扣 3.5 分）**：`realm`, `realm of`, `intricate`, `pivotal role`, `pivotal`, `beacon of`, `commendable`, `foster`, `navigating complexities`, `unwavering`。
    - **Tier B（高频通用，扣 2.0 分）**：`comprehensive`, `robust`, `leverage`, `utilize`, `seamless integration`, `seamless`, `seamlessly`, `multifaceted`, `myriad`, `revolutionize`。
- **汉语形式动词/轻动词结构（Light Verb Constructions, LVC）闭集**：
  - 朱德熙现代汉语形式动词闭集：`进行|开展|展开|作出|予以|给以|给予|加以|具有|得到|受到|作|做|致以`。
  - 名物化动作靶点扩充：`分析|探讨|调研|考察|评估|测评|审校|整改|梳理|阐述|测查|优化|迭代|部署|排查|总结|研究|复盘`。
  - 自动提供动作名词去名物化复原规则（如将“针对系统展开了全面的性能测评”精简为“全面测评了系统性能”）。
- **Model Context Protocol (MCP) 原生工具服务**：
  - 零外部依赖的纯标准库 JSON-RPC 2.0 stdio MCP 服务（`anti-ai-mcp` 或 `python3 -m anti_ai_lint.mcp_server`）。
  - 面向 Cursor、Claude Code、Windsurf、Zed、Cline 开放三大原子工具：`lint_prose`、`remediate_violation` 与 `get_style_contract`。
- **现代化 AI 工程交付体系**：
  - 官方 GitHub Action (`action.yml`)：支持在 PR 代码行直接输出 Workflow Commands 行内注释（`::warning` / `::error`）。
  - Pre-commit 提交前拦截钩子（`.pre-commit-hooks.yaml`）。
  - Stanford DSPy 提示词优化评估脚本（`scripts/dspy_optimizer.py`）。
  - DPO / SimPO 偏好对齐语料库导出器（`scripts/export_dpo_pairs.py`），生成 HuggingFace TRL、ChatML 与 ShareGPT 三元组。
- **全平台多智能体适配**：
  - 全面适配 **Codex**, **Claude Code**, **DeepSeek**, **OpenCode**, **WorkBuddy**, **Cursor**, **Windsurf**, **Cline**, **Aider**, **Antigravity**, **Harness²**, **ZCode**。

---

## 4. 安装与部署

### 4.1 智能体规则与技能安装

使用统一安装脚本（支持多目标清单追踪与 `--lang zh|en` 语义切换）：

```bash
# 安装到 Codex：
./install.sh --target codex --lang zh

# 安装到 Claude Code CLI：
./install.sh --target claude --lang en

# 安装到 DeepSeek（CLI / API 智能体）：
./install.sh --target deepseek --lang zh

# 安装到 OpenCode：
./install.sh --target opencode --lang zh

# 安装到 WorkBuddy：
./install.sh --target workbuddy --lang zh

# 安装到 Cursor 项目仓库：
./install.sh --target cursor --dest /path/to/project --lang zh

# 安装到 Windsurf 项目仓库：
./install.sh --target windsurf --dest /path/to/project --lang zh

# 安装到 Cline / Aider / Antigravity：
./install.sh --target cline --dest /path/to/project --lang zh
./install.sh --target aider --dest /path/to/project --lang zh
./install.sh --target antigravity --lang zh

# 安装到 ZCode：
./install.sh --target zcode --lang zh

# 安装到通用项目目录：
./install.sh --target generic --dest /path/to/project --lang zh
```

详细接入文档请参阅 [智能体适配器与集成指南](docs/adapters/README.zh-CN.md)。

---

### 4.2 独立 Python 质检工具（`anti-ai-lint`）

在本地或虚拟环境中安装：

```bash
pip install ./lint
```

亦可免安装直接运行：

```bash
python3 -m anti_ai_lint /path/to/document.md --max-score 8.0
```

---

### 4.3 Model Context Protocol (MCP) 服务配置

在 Cursor、Windsurf、Claude Code 或 Zed 中接入 MCP 服务：

```bash
# 直接以 stdio 方式启动：
python3 -m anti_ai_lint.mcp_server

# 或使用安装好的可执行命令：
anti-ai-mcp
```

在项目 `.cursor/mcp.json` 或 Cline 设置中添加：

```json
{
  "mcpServers": {
    "anti-ai-copywriting": {
      "command": "python3",
      "args": ["-m", "anti_ai_lint.mcp_server"]
    }
  }
}
```

---

### 4.4 GitHub Action 与 Pre-commit 门禁

**GitHub Actions 流水线配置 (`.github/workflows/prose-lint.yml`)**：

```yaml
name: Natural Prose Linter
on: [push, pull_request]

jobs:
  lint-prose:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ./action.yml
        with:
          paths: 'docs/'
          genre: 'academic'
          max-score: '10.0'
```

**Pre-commit 提交前检查 (`.pre-commit-config.yaml`)**：

```yaml
repos:
  - repo: https://github.com/CalebChen941028/anti-ai-copywriting
    rev: v0.7.0
    hooks:
      - id: anti-ai-lint
        args: ["--format", "hook", "--genre", "general"]
```

---

## 5. 检查模式与输出格式

```bash
# 默认检查单个文件
anti-ai-lint paper.md

# 学术场景模式（适合论文、基金申报与预提交）
anti-ai-lint paper.md --genre academic --format hook --max-score 8.0

# 受控白话层质检
anti-ai-lint guide.md --genre plain --format agent

# GitHub Action 模式（输出 PR 行内报错与警告标记）
anti-ai-lint docs/ --format github

# 润色或翻译场景：对比原文进行信息守恒事实锚点核验
anti-ai-lint polished.md --source original.md --format hook
```

### 5.1 润色与翻译场景：信息守恒事实核验（`--source`）

`--source` 参数将受检文本与原文的**事实锚点**进行严格比对：纯数字（如 `1,200` 自动等价于 `1200`）、字母开头的型号代码（如 `H100`、`CASP14`）以及全大写英文缩写。任何仅在输出文本中出现而在原文中不存在的锚点（`fidelity_added`），无论 `--max-score` 阈值设定为多少，均将直接判定为门禁失败；若原文中的关键数字或型号在译文/润色稿中丢失（`fidelity_dropped`），每项扣除 3.0 分。

来自 `tests/workflow_cases/` 目录的真实评测结果（可使用表格末列命令复现）：

| 测试案例 | 原文文件 | 输出文本文件 | 门禁判定与结果 |
| :--- | :--- | :--- | :--- |
| 中文润色（严格忠实） | `polish/source.md` | `polish/faithful.md` | ✅ PASS，扣分 0.0 |
| 中文润色（杜撰细节） | `polish/source.md` | `polish/fabricated.md`（虚构了“3周”与“36%”） | ❌ FAIL，2 处 `fidelity_added`，扣分 10.0 |
| 英译中（严格忠实） | `translate/source.en.md` | `translate/faithful.zh.md` | ✅ PASS，扣分 0.0 |
| 英译中（杜撰细节） | `translate/source.en.md` | `translate/fabricated.zh.md`（虚构了“87%”） | ❌ FAIL，1 处 `fidelity_added`，扣分 5.0 |

```bash
anti-ai-lint tests/workflow_cases/polish/fabricated.md --source tests/workflow_cases/polish/source.md --format hook
```

> [!WARNING]
> **锚点核验的边界与局限**：该检查仅能精准捕获数字、型号代码与大写缩写等离散锚点。若润色或翻译中凭空杜撰了不包含此类锚点的形容词、场景、心理活动或情绪描述（例如“在绝望的深夜”、“令人窒息的重压”），或篡改了因果逻辑语义，门禁无法自动识别。中文汉字数字（如“三个通宵”）暂不在比对范围内。因此，通过门禁仅代表“未检出无根据的事实锚点”，并不等同于绝对忠实，关键专业文案仍须保留人工审校。

### 输出格式说明（`--format`）

- `text`：终端可读摘要，标明行列位置、节奏变异系数（CV）、MATTR 与改写建议。
- `json`：机器可读的结构化 AST 与指标报告。
- `hook`：单行/紧凑摘要，适用于 git pre-commit 与 Harness² 环内拦截。
- `agent`：专为大模型反思循环设计的 `<anti-ai-lint-feedback>` 格式载荷。
- `github`：GitHub Actions Workflow Commands 标记格式（`::warning` 与 `::error`）。

---

## 6. 学术参考文献与标准依据

本项目的架构设计参考了以下学术研究与行业标准。其中 AI 检测类论文（第 3–5 项）仅作为节奏感与变异度度量的理论背景：本项目不包含任何基于模型的概率检测器。第 9–12 项标准与规范则构成了润色与翻译场景下“信息守恒”准则的基石。

1. **Kobak, D., González-Márquez, R., Horvát, E.-Á., & Lause, J. (2025)**. Delving into LLM-assisted writing in biomedical publications through excess vocabulary. *Science Advances, 11*(27), eadt3813. https://doi.org/10.1126/sciadv.adt3813 (arXiv:2406.07016).
2. **Meister, C., Pimentel, T., Haller, P., Jäger, L., Cotterell, R., & Levy, R. (2021)**. Revisiting the uniform information density hypothesis. In *Proceedings of the 2021 Conference on Empirical Methods in Natural Language Processing (EMNLP)* (arXiv:2109.11635).
3. **Mitchell, E., Lee, Y., Khazatsky, A., Manning, C. D., & Finn, C. (2023)**. DetectGPT: Zero-shot machine-generated text detection using probability curvature. In *Proceedings of the 40th International Conference on Machine Learning (ICML)* (arXiv:2301.11305).
4. **Hans, A., Schwarzschild, A., Cherepanova, V., Kazemi, H., Saha, A., Goldblum, M., Geiping, J., & Goldstein, T. (2024)**. Spotting LLMs with Binoculars: Zero-shot detection of machine-generated text. In *Proceedings of the 41st International Conference on Machine Learning (ICML)* (arXiv:2401.12070).
5. **Dugan, L., Hwang, A., Trhlik, F., Ludan, J. M., Zhu, A., Xu, H., Ippolito, D., & Callison-Burch, C. (2024)**. RAID: A shared benchmark for robust evaluation of machine-generated text detectors. In *Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (ACL)* (arXiv:2405.07940).
6. **朱德熙. (1982)**. *语法讲义*. 商务印书馆.（关于汉语形式动词结构与名物化。）
7. **ASD-STE100 规范**. 欧洲航空航天与防务工业协会（ASD）. 简化技术英语规范.
8. **Xu, R., et al. (2026)**. Harness^2: Recursive agent harnessing for an open world. arXiv:2610.14224.
9. **ISO 17100:2015**. *Translation services — Requirements for translation services*. 国际标准化组织.
10. **ISO 18587:2017**. *Translation services — Post-editing of machine translation output — Requirements*. 国际标准化组织.
11. **GB/T 19363.1-2008**. 翻译服务 译文质量要求 第1部分：笔译. 中国国家标准化管理委员会.
12. **严复. (1898)**. 《天演论》译例言（“信、达、雅”原则）.

---

## 7. 卸载与清理

干净卸载已安装的规则与技能，恢复备份，绝不触碰用户个人其他配置：

```bash
# 卸载指定目标
./uninstall.sh --target codex
./uninstall.sh --target cursor --dest /path/to/project

# 卸载所有已注册目标
./uninstall.sh --all
```

---

## 8. 商标与非背书声明

本仓库中提及的所有产品名称、商标、服务标志与机构名称（包括 Anthropic、Claude、Claude Code、OpenAI、ChatGPT、Codex、DeepSeek、Google、Gemini、Antigravity、Cursor、Windsurf、Codeium、Cline、Aider、WorkBuddy 等）均为其各自所有者的财产。在此提及仅用于技术兼容性标识与说明，不代表各所有者对本项目的任何赞助、认可或关联。

---

## 9. 开源许可证

本项目基于 [MIT](LICENSE) 开源许可证发布 © 2026 Liangliang Chen
