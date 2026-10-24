<!-- BEGIN anti-ai-copywriting v0.4.0 -->
# Anti-AI Copywriting & Natural Voice Rules (Mandatory & Silent)

<auto_trigger>
Whenever drafting, editing, translating, or evaluating Chinese or English prose—including academic manuscripts, grant proposals, technical documentation, columns, social media copy, and business memos—you MUST automatically load and strictly follow `anti-ai-copywriting` (`skill/anti-ai-copywriting/SKILL.md`).
</auto_trigger>

All written or rewritten prose across Chinese and English must strictly adhere to these core rules:
1. Forbidden Lexicon: Eliminate buzzwords and formulaic AI tropes (Chinese: `赋能`, `抓手`, `闭环`, `底层逻辑`, `颗粒度`, `全方位`, `深度融合`, `随着...飞速发展`, `不仅是...更是...`; English: `delve into`, `testament to`, `beacon of`, `tapestry of`, `realm`, `crucial/paramount`, `navigating complexities`, `revolutionize`, `leverage`, `seamless`).
2. Syntax & Rhythm: Avoid nominalizations, excessive passive voice, and redundant hedging (`possibly/perhaps/might tend to`, `可能或许试图`). Control particle '的' density in Chinese; alternate sentence lengths in English.
3. No Fluff Openings / Closings: Begin directly with empirical facts, concrete problems, or immediate actions. Conclude on operational implications rather than repetitive philosophical summaries.
4. Deterministic Gate: Run `anti-ai-lint <file> --max-score 10.0` to verify zero AI residue.
<!-- END anti-ai-copywriting -->
