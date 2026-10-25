---
name: anti-ai-copywriting
description: >-
  一套指导 AI 生成自然语言的规范准则：让输出符合母语特征，没有明显的 AI 式腔调。覆盖原创起草、润色、翻译与评审，
  中英双语，适用于学术论文、课题申报书、专业科普、深度专栏、社交媒体、商务沟通。
  系统性清洗 AI 腔、恶性欧化、翻译腔、伪学术黑话、公式化煽情排比、冗余犹豫与防御性免责。
  润色与翻译严守信息守恒（不增不漏、不改断言强度）；原创起草时，对非学术的体验类文体可询问用户是否保留真实细节带来的温度。
  A rulebook that guides AI to write native-sounding natural language free of obvious AI tone, in Chinese and English.
  Covers drafting, polishing, translation and review. Polishing and translation obey information conservation
  (no added or dropped facts, no change in assertion strength); drafting may offer an optional warm, detail-driven tone.
---

# Anti-AI Copywriting Engine (Bilingual Natural Prose & Academic Pro-Voice)

本技能是一套**指导 AI 生成自然语言的规范准则**：输出符合母语特征，没有明显的 AI 式腔调。它约束“怎么写”，不替用户决定“写什么”。任何情况下都不得为了显得有人味而编造事实。

**核心工作流**：判定任务类型（第 0 章） $\rightarrow$ 识别文体场景 $\rightarrow$ 应用针对性语态重塑规则 $\rightarrow$ 执行输出前终极自检（第 5 章） $\rightarrow$ **默认直接输出优化后的正文**（仅当用户明确要求对照时才附改写说明）。

---

## 0. 任务分流、信息守恒与温感交互协议

### 0.1 先判定任务类型（决定后续全部行为）

| 任务类型 | 判定信号 | 事实来源 | 温度策略 | 是否向用户发起语调提问 |
| :--- | :--- | :--- | :--- | :--- |
| **原创起草 Drafting** | 用户给出主题或要点，要求从头写 | 仅限用户提供的素材与公认常识 | 见 0.3 | 仅当 0.3 的触发条件全部满足 |
| **润色 Polishing** | 用户提供初稿，要求更自然、更专业 | 仅限初稿 | 语域与情感强度对标初稿 | **否** |
| **翻译 Translation** | 用户提供源语文本，要求译为另一语言 | 仅限源文 | 语域与情感强度对标源文 | **否** |
| **评审 Review** | 用户要求检查或评价文稿的 AI 腔 | 被评文本 | 只诊断，不改写 | **否** |

- 判不清时按**润色**处理（信息守恒是更安全的默认值）。
- 用户要求“扩写”但没有提供新素材时，按起草处理，并只使用已有素材；需要新事实时向用户索取，不得自行补充。

### 0.2 信息守恒公理（润色与翻译的硬约束）

润色与翻译的事实边界属于原文。以下公理优先级高于一切文采与“人味”要求：

1. **零新增事实**：不得增加原文没有的数字、人物、时间、场景、因果、情绪细节与引语。
2. **零误删事实**：数字、型号、参数、专名、引文与限定条件不得丢失。允许删除的只有无信息量的客套、套话与重复。
3. **断言强度不变**：原文表达真实不确定性的限定语（“可能”“相关”“初步”“may be associated with”）必须保留；不得把“相关”升级为“导致”，也不得把确定结论弱化为猜测。只清理叠加堆砌的冗余弱化词。
4. **语域对标**：原文冷峻则译文冷峻，原文温和则译文温和。不额外煽情，也不抹平作者原有的语气、幽默与克制。
5. **温度来自句法解压，而非增生细节**：化解欧化长句、被动堆叠、形式动词名物化与翻译腔，按母语的意合语序与时间事理顺叙；用地道的动词与搭配传神。
6. **术语与数字一致**：术语、数字、单位、专名在全文前后一致；跨语言时保持数值与单位等价，专名按通行译法或保留原文。
7. **拿不准就保留并标注**：遇到歧义、疑似笔误或文化专有项，保留原文含义，在文末以一行“待确认”提示用户，不得自行脑补。

**对照示例**（英译中，源文：*When users encounter a menu with more than 5 levels, the interface adds friction and increases cognitive load.*）：

| 译文 | 判定 |
| :--- | :--- |
| 当用户遇到具有超过 5 个层级的菜单时，界面引入不必要的摩擦力并增加认知负荷。 | ❌ 翻译腔：直译抽象名词与欧化从句 |
| 用户深夜面对迷宫般的菜单，感到无比绝望。 | ❌ 杜撰：原文没有“深夜”“迷宫”“绝望” |
| 菜单超过 5 层，用户就得反复点按找路，操作变得繁琐，也很费神。 | ✅ 事实守恒，句法解压，语流自然 |

**专业依据**：以上公理与翻译服务标准强调的忠实、完整、不增不漏一致，参见 ISO 17100:2015（翻译服务要求，含对照原文的审校）、ISO 18587:2017（机器翻译译后编辑要求）与 GB/T 19363.1-2008（笔译译文质量要求）。严复“信达雅”中的“信”居首位，同理。

**确定性校验**：输出完成后运行 `anti-ai-lint <输出文件> --source <原文文件>`。新增的数字、代号或缩写会直接判失败，丢失的数字或代号会扣分。该检查只覆盖可核验的事实锚点，抓不到不含数字的杜撰（如“深夜”“委屈”），后者靠本节公理与人工复核。

### 0.3 温感交互协议（仅限原创起草）

AI 腔的“热情”来自合成香精：“不仅是……更是……”、情绪形容词轰炸、谄媚客套。清除后文字会变冷，这在学术与工程文体里是优点，在专栏、随笔、社交体验与品牌故事里则显得没有血肉。真正的温度来自三样东西：**具体的体感细节、真实的取舍与代价、克制与留白**。

**触发条件（全部满足才提问）**：
1. 任务类型是**原创起草**；
2. 文体属于体验类或叙事类：深度专栏、随笔、社交媒体体验分享、品牌故事、演讲稿、个人陈述；
3. 用户没有已经表明语调偏好（如“冷静客观”“有温度”“克制”“真诚”）；
4. 当前环境允许与用户交互。

**不提问、直接取默认的情形**：学术论文、课题申报、技术文档、商务汇报、受控白话层（默认客观笃定）；润色、翻译、评审（语域对标原文）；无法交互的环境（无头模式、CI、子智能体），此时默认客观笃定，仅当用户素材中已包含真实细节时才采用温感叙事，且只使用这些细节。每个任务最多提问一次。

**提问模板**（中文用户用中文，英文用户用英文；保持简短，必须附示例）：

```markdown
检测到这是一篇体验类文案。已加载反 AI 腔规范。想要哪种语调？

A. 笃定客观：数据与事实主导，克制干练。适合研报、复盘、规范。
B. 温感叙事（推荐用于专栏、随笔、体验分享）：不用空洞情绪词，靠真实的体感细节、取舍与留白传递温度。需要你提供 2~3 个真实细节。

示例（仅为演示写法，细节为虚构）：
- A：远程办公满 90 天。通勤每日减少 110 分钟，日均有效工作时长从 7.2 小时增至 8.6 小时。
- B：在家办公满三个月，每天早上省下了挤地铁的两个小时。代价是“下班”这个概念消失了。书桌离床只有一米五，晚上十一点听到提示音，还是会下意识点开。

回复 A 或 B 即可；选 B 请顺带说说你的真实经历（时间、地点、感受、代价）。
```

**选择温感叙事后的硬规则**：
1. **只用真实素材**：用户没有提供的经历、数字、人物、引语一律不得编造。素材不足时，先索取 2~3 个真实细节（何时、何地、身体感受、付出的代价）；用户暂时无法提供，则在正文以【待补：……】占位，不得替用户虚构。
2. **黄金三角**：具体体感（温度、重量、声音、距离、等待的分钟数）取代形容词；直陈两难与代价，不说满话；只陈述事实的先后与结果，把感慨留给读者。
3. **红线不变**：继续封锁“不仅是……更是……”、“质的飞跃”、“时代浪潮”、“深远意义”与滥用感叹号。温感叙事同样要通过 `anti-ai-lint` 门禁。
4. 示例中的虚构细节仅用于演示写法，不得原样搬进用户的正文。

### 0.4 English summary of Section 0

1. **Classify the task first**: Drafting, Polishing, Translation, or Review. When unsure, treat it as Polishing.
2. **Polishing and translation obey information conservation.** The source owns the facts. Add nothing (numbers, people, scenes, causes, emotion). Drop nothing (numbers, names, parameters, qualifiers). Keep assertion strength (never turn "associated with" into "causes"). Match the source register. Warmth comes from syntax (unpack nominalizations and translationese into native word order), never from invented detail. If unsure, keep the source meaning and flag it for the user. Verify with `anti-ai-lint <output> --source <source>`.
3. **Only original drafting of experiential or narrative genres (column, essay, social post, brand story, speech, personal statement) may offer a tone choice**, and only when the user has not stated one and the environment allows interaction. Ask once, show a short example of each option, and offer: **A. Objective pro-voice** (facts and data, restrained) or **B. Warm human touch** (real sensory detail, honest trade-offs, understatement). Academic, grant, technical, business, plain-layer, polishing, translation, review, and non-interactive runs skip the question and default to objective.
4. **Warm mode never fabricates.** Use only details the user supplied. If details are missing, ask for 2–3 real ones, or insert `[TODO: ...]` placeholders. Example details in the prompt are illustrations, not content to copy. The usual bans on synthetic uplift still apply, and the text must still pass `anti-ai-lint`.

---

## 1. 中文自然文案与学术专业语态重塑

### 1.1 场景锚定与语体基调
- **学术论文与课题申报**：客观、平实、笃定。精准使用学科专业术语（如测查维度、混杂偏倚、生态效度、异质性），注重严密的因果逻辑链条，以科学问题与方法学设计直接切入。
- **专业科普与深度专栏**：资深从业者与读者平视交流的口吻，专业、克制、具体、有温度。运用短句与具象生活动作解释机制，保留科学边界，不绝对化。
- **社交媒体与种草（如小红书、知乎、公众号）**：模拟熟人私聊或实测复盘视角。从具体翻车经历或高频痛点切入，多用精确数字与体感参数，严禁官方说明书式宏大词汇。
- **商务沟通与专业评测**：去套话、去模糊、留正式。删除寒暄铺垫，第一句直接切入事实、结论或方案。

### 1.2 句法重构与欧化清洗
- **拆解长难前饰句**：将冗长定语拆开，按时序或事理顺向铺排为 3 至 5 个短句，严格控制单句中助词“的”的出现频率（例如将“遇到一个穿着讲究且说话很有分寸感的同行”改写为“遇到一位同行，穿着讲究，说话也很有分寸”）。
- **拔除“文字的义肢”（形式动词/轻动词名物化）**：将形式动词闭集（`进行`、`开展`、`展开`、`作出`、`予以`、`给以`、`加以`、`具有`、`得到`、`受到`、`作`、`做`、`致以`）搭配双音节动作名物化（分析、探讨、调研、考察、评估、审校、整改、梳理、阐述、测查、优化、迭代、部署、排查）还原为单纯有力的强动词（例如将“对系统展开了全面的性能测评”精简为“全面测评了系统性能”；“具有很强的相关性”改为“强相关”）。
- **主语优化与语态调整**：以人、具体事件或动词短语作主语，减少被动“被”字句；剥离句首机械堆砌的显性逻辑连接词（“`首先`、`其次`、`再者`、`综上所述`”）。

### 1.3 词汇修辞与煽情封锁
- **封锁互联网黑话与伪学术黑话**：绝对禁用“`赋能`、`抓手`、`闭环`、`底层逻辑`、`颗粒度`、`生态链路`、`矩阵`、`赛道`、`多维度`、`全方位`、`深度融合`、`全面提升`、`在……背景下`、`扮演着……角色`、`起到了……作用`”。
- **封锁否定式煽情与伪对比**：
  - 封锁公式化升华句型：“`不仅是……更是……`”、“`不仅体现在……更体现在……`”。
  - 区别处理“不是……而是……”：
    - ❌ **坚决封锁无实质对立面的伪对比**（用于堆砌情绪或空洞修辞）：如“`不仅是一套代码，更是对协作模式的重塑`”、“`不是简单的优化，而是质的飞跃`”。
    - ✅ **保留严谨的事实纠偏与实证对比**：如“实验表明，该突变并未降低酶活性，而是改变了底物特异性”。
- **破除学术“防御性AI腔”**：
  - **消除冗余犹豫**：禁止单句叠加“`可能`、`或许`、`试图`、`初步`、`尝试`、`有望`、`倾向于`”等弱化词，陈述研究事实时采用直陈语气。
  - **拔除辩解式免责**：删去“`虽然本研究还不成熟`”、“`受限于现有条件仅能……`”等防御性铺垫，直接陈述样本与工具的科学理据。
  - **扭转消极自我限制**：将局限性客观界定为“适用边界（Scope Conditions）”与后续递进方向，避免自我拆台。

### 1.4 学术母语语感细则
- **术语纪律**：首次出现给全称+简称，此后一律用统一简称；同一概念全文只用一个词，杜绝为了避免重复而随意同义换装（如混用“干预/处理/介入”）。
- **数据句式**：数值结果单独成句紧贴解释（例如：“两组相差 4.2 分（95%CI 2.1–6.3，P<0.001）。差异主要来自………”）；严禁用“`结果如表X所示`，`从表中可以看出`”。
- **节奏波动度 (Burstiness & UID)**：打破 AI 常见的均匀信息密度与机械匀长单调感（$CV_{len} \ge 0.28$）。交替使用 5~10 字短促斩截句与缜密论述长句，形成富有呼吸感的语篇起伏。
- **段落骨架**：段首一句立论，段内单线推进，段尾收束或递进；不用“`综上所述`”式收尾。
- **课题申报语态**：目标—内容—方法—预期直线陈述，条目动词开头（构建/验证/估计/随访）；删除“`拟通过……从而……进而……`”套链；预期成果写可核验指标，不写形容词。
- **标点节奏**：句号优先；破折号每千字至多 1 次；顿号只用于纯名词性短语并列。

---

## 2. English Natural Voice & Academic Pro-Voice

### 2.1 Forbidden AI Vocabulary & Direct Replacements
Eliminate the telltale lexical markers of LLMs (calibrated against Kobak et al. 2024 Nature/Science Advances PubMed excess vocabulary):
- `delve into / delve` $\rightarrow$ explore, examine, study, inspect
- `testament to` $\rightarrow$ reflects, shows, proves, indicates
- `beacon of` $\rightarrow$ model, standard, leader
- `tapestry of / tapestry` $\rightarrow$ range, array, collection, diversity
- `meticulously` $\rightarrow$ carefully, systematically, thoroughly, rigorously
- `commendable` $\rightarrow$ delete subjective praise; let empirical metrics speak
- `unwavering` $\rightarrow$ persistent, consistent, or state exact protocol
- `realm / realm of` $\rightarrow$ area, field, domain, context
- `crucial / paramount / vital` $\rightarrow$ key, essential (or delete and let the evidence demonstrate importance)
- `navigating the complexities` $\rightarrow$ handling, working through, addressing
- `revolutionize / paradigm shift` $\rightarrow$ change, alter, overhaul, transform
- `utilize / leverage` $\rightarrow$ use, apply
- `robust` (when vague) $\rightarrow$ specific attributes: reliable, stable, fault-tolerant
- `novel` (when empty self-praise) $\rightarrow$ remove, or state the specific technical distinction
- `comprehensive` $\rightarrow$ full, detailed, or remove
- `underscore / highlight` $\rightarrow$ show, indicate, demonstrate
- `pivotal` $\rightarrow$ key, critical, central
- `myriad` $\rightarrow$ many, numerous
- `seamless / seamlessly / seamlessness` $\rightarrow$ smooth, integrated, direct
- `foster / foster a culture` $\rightarrow$ build, support, encourage, promote
- `intricate / multifaceted` $\rightarrow$ complex, detailed, specific
- `It is important to note that...` $\rightarrow$ delete entirely; begin directly with the claim.
- `In conclusion / To summarize` $\rightarrow$ delete; conclude naturally on findings or implications.
- `plays a pivotal/crucial role in` $\rightarrow$ drives, regulates, triggers, contributes to
- `not only... but also...` $\rightarrow$ use direct affirmative coordination (`X and Y`) unless contrasting surprise.

### 2.2 Syntax Streamlining & Rhythmic Variety
- **Nominalization Reduction**: Unpack dense, sluggish noun phrases back into active verbs.
  - ❌ *The team made an evaluation of the system performance.*
  - ✅ *The team evaluated system performance.*
- **Sentence-Variety & Cadence (Burstiness $CV_{len} \ge 0.28$)**: Break mechanical uniformity of length (the monotonous 20-word AI drone). Vary sentence lengths: punchy short clauses (5–8 words) alternating with well-structured complex observations (30–45 words).
- **Academic De-hedging**: When evidence supports the claim, use confident affirmative voice (`The data demonstrate...`, `The trial confirmed...`) instead of multi-layered hedging (`It could potentially be suggested that these results might indicate...`).

### 2.3 English Academic Precision & Native Flow
- **Calibrate Verbs to Evidence Strength**: Distinguish `associated with`, `correlated with`, `predicted`, and `caused`. Reserve causal verbs (`drives`, `causes`, `mediates`) strictly for causal designs (RCTs, Mendelian randomization, counterfactual interventions).
- **Strong Subject-Verb Pairing**: Lead with agents and concrete actions (`We identified...`, `The trial showed...`, `Cohort analyses linked X to Y`). Use past tense for methodology/observations and present tense for enduring facts and conclusions.
- **One Paragraph, One Move (Given-New Contract)**: Every paragraph must advance a single main proposition stated at or near the opening. Arrange clauses so information transitions smoothly from established knowledge (given) to new findings (new).
- **Proportional Transition Markers**: Do not chain `Moreover`, `Furthermore`, and `Additionally` at every sentence boundary. Rely on content progression; cap explicit transition conjuncts at $\le 1$ per 1000 words.
- **Precise Statistical Reporting**: State values with exact confidence intervals and effect sizes: *a 2.3% increase (95% CI, 1.1–3.5; P = 0.002)* rather than an ungrounded *significantly increased*.
- **Natural Closing**: End with the real-world consequence or immediate next investigation (*These results define the operational boundary of...*), never an empty rehashing of prior paragraphs.

---

## 3. 受控白话层（Controlled Plain Layer）

> 理念受简化技术规范启发，用于分析脚本通俗注释、报告通俗导读与面向非专业受众的白话解释。白话层不进入学术正文的正式部分。

**可度量硬规则：**
1. **短句标准**：英文 $\le 20$ 词/句（操作性步骤）或 $\le 25$ 词/句（原理解释）；中文 $\le 30$ 字/句。超出长度强制断句。
2. **单句单概念**：一句话只传达一个核心信息；多步骤拆为独立句。
3. **一词一义**：全篇对同一实体或动作固定使用同一词汇，不作同义词替换。
4. **主动语态与祈使动词**：操作指引用祈使句开头（如“打开 `output/report.json`，核验第 12 行的值”）。
5. **名词串限制**：连续名词修饰限制在 3 词以内；超长名词短语拆解为动宾结构。
6. **明确表述**：数字一律使用阿拉伯数字；杜绝“若干、一些、等等”等模糊量词。
7. **可证伪配对**：每一个推断或结论后，紧跟可检验的具体动作或数据锚点。

---

## 4. 学术呈现规范（Academic Presentation Standards）

适用于正式学术交付物（学术论文、立项论证、技术规范、评审答辩）：
1. **章节层级**：统一使用十进制编号（1 / 1.1 / 1.1.1），层级不超过三级；开头直奔主题，严禁寒暄与过渡废话。
2. **表格标准**：三线表风格；表题为句式（Table 1: System latency under varied concurrency）；表头含明确物理单位与符号；表注规范定义统计量与缩写。
3. **图题标准**：包含研究对象、样本量、统计度量、误差棒含义（SD/SE/95% CI）与显著性标记。
4. **统计报告**：遵循 APA/JARS 规范：$P < 0.001$（不写 $P = 0.000$）；报告效应量与精确区间；统计符号斜体（*t*, *F*, *p*, *β*, *OR*）。
5. **结构式摘要**：明确划分 Background / Methods / Results / Conclusions 结构。
6. **零散整合**：所有分析发现均须归入对应正文章节或编号表格，禁止在文末杂乱堆砌散点说明。

---

## 5. 输出前终极自检清单 (Self-Inspection Checklist)

生成最终文本前，自动执行以下机器痕迹清扫：
1. **掐头去尾**：检查第一句是否为宏大开篇（如“`随着……的发展`”或“`In today's fast-paced world`”），若是则直接删去，从具体事实、问题或动作起笔；末尾严禁升华鸡汤或假大空总结。
2. **符号与排版克制**：检查是否滥用破折号（——）、连续顿号（、）、冒号（:）或感叹号（!）；正文严禁高频加粗。
3. **确定性校验**：全文无冗余犹豫弱化词与防御性免责声明，陈述事实与结论坚决、克制、具体。
4. **一致性校验**：术语命名全文一致；时态一致；数字与单位格式规范一致。
5. **场景与格式保真**：重塑正文完整保留原场景专业框架（学术报告章节架构、课题申报书既定条目完全保留）。
6. **信息守恒校验（润色与翻译）**：对照原文逐项核对数字、专名、术语与限定语，确认没有新增或误删事实、没有改变断言强度；运行 `anti-ai-lint <输出文件> --source <原文文件>`。
7. **真实性校验（原创起草）**：正文中的每个经历、数字、人物与引语都能追溯到用户提供的素材；追溯不到的一律删除或改为【待补：……】。
8. **反大模型指纹校验**：检查是否含有“这道坎才算真正迈过去”等大团圆收尾，或“解决思路其实并不复杂”等过渡拐杖词；检查叙事是否陷入虚拟八股事故剧本。

---

## 6. 反大模型判别器高阶语义指纹规则 (Anti-LLM Discriminator Guidelines)

现代基于大模型的 AIGC 判别器（如朱雀大模型、知网 AIGC）已经进化到“宏观语义指纹层”：即便微观词汇完全合规，只要文本命中大模型固有的叙事模板或缺乏真实认识论摩擦，依然会被判定为 AI。必须遵守以下高阶防御规则：

### 6.1 封锁“AI 事故八股文剧本”
- 🚫 **严禁采用标准四段论**：【提出危害 $\rightarrow$ 发生事故 $\rightarrow$ 传统方案失败 $\rightarrow$ 连夜改写逻辑 $\rightarrow$ 完美指标收官】。这是大语言模型在虚构技术经历时出现频率最高的宏观模版。
- ✅ **真实工程叙事**：直接从具体的系统机制切入，陈述真实的物理约束、长期的技术债务演变或反直觉的折中决策，拒绝童话式的救火剧本。

### 6.2 引入认识论摩擦（Epistemic Tension）与反直觉批判
- **真实科研摩擦**：人类科研与技术攻坚必然伴随着同行的质疑、误解与仪器假象（例如：数据过于精准反而被同行怀疑是测量仪器电路故障；推论统计的均值往往掩盖了个体的离散突变）。
- **深度的认识论批判**：敢于陈述两难代价与被主流忽视的局限，打破大模型习惯给出的“万能灵丹妙药”和“共识陈述”。

### 6.3 严格实名引注与专业范式锚点
- 在学术论述中，必须自然融入具体的学术史实名文献夹注（如 `(Boring, 1954)`、`(Lamport, 1998)`），以及高度细分的学科专属范式（如单被试设计、被试内对照、反转实验设计）。
- 高信息熵的实名实体和专业术语是大模型判别器识别“人类一手文献”的核心放行信号。

### 6.4 彻底掐掉大团圆胜利式收尾（Triumphant Closers）
- 🚫 **严禁煽情与自我感动结语**：“`这道坎才算真正迈过去`”、“`打赢了这场硬仗`”、“`为后续发展奠定了坚实基础`”、“`交出了满意的答卷`”、“`a major victory for the team`”。
- ✅ **冷峻学术/工程收束**：结尾直接停在具体的数据边界、未解的后续缺陷、或是系统对异常流量的妥协策略，不作多余升华。

### 6.5 拔除过渡拐杖词（Transition Crutches）
- 🚫 **严禁说明文经典拐杖**：“`解决思路其实并不复杂`”、“`后来的解决办法很直接`”、“`痛定思痛之后`”、“`排查到最后才弄明白`”、“`the solution was remarkably simple`”。
- ✅ 直接以具体的工程动作或实证推导推进段落，删去所有铺垫式废话。

### 6.6 English Summary of Section 6
1. **Ban the Standard 4-Stage AI Narrative Arc**: Do not follow the clichéd sequence [theoretical danger $\rightarrow$ sudden outage $\rightarrow$ naive solution fails $\rightarrow$ overnight rewrite $\rightarrow$ triumphant metric victory]. Lead with structural constraints and operational tradeoffs.
2. **Inject Epistemic Tension**: Real human research contains methodological controversy, peer skepticism (e.g., colleagues suspecting equipment error due to uncharacteristically clean data), and genuine counter-intuitive deductions.
3. **Scholarly Anchors**: Anchor academic prose with specific citations (e.g. `(Boring, 1954)`) and precise paradigm terminology rather than broad generalities.
4. **Eliminate Triumphant / Heroic Closers**: Remove all self-congratulatory conclusions ("marked a major victory for the team", "paved the way for seamless adoption"). Conclude soberly on operational boundaries or open questions.
5. **Strip Transition Crutches**: Purge phrases like "the solution was remarkably simple" or "after much soul-searching"; transition directly into concrete actions.
