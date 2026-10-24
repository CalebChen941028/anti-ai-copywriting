<!-- BEGIN anti-ai-copywriting v0.8.0 -->
# Anti-AI Copywriting & Natural English Voice Rules (Mandatory & Silent)

<auto_trigger>
Whenever drafting, editing, translating, or evaluating English or Chinese prose—including academic papers, technical documentation, columns, business memos, or proposals—you MUST automatically load and follow `anti-ai-copywriting` (`skill/anti-ai-copywriting/SKILL.md`).
</auto_trigger>

1. Forbidden Lexicon: Eliminate telltale AI markers (`delve into`, `testament to`, `beacon of`, `tapestry of`, `realm`, `crucial/paramount`, `navigating complexities`, `revolutionize`, `leverage`, `seamless`, `foster`, `multifaceted`).
2. Syntax & Cadence: Reduce heavy nominalizations into active verbs. Avoid monotonic sentence lengths; alternate punchy short observations with structured complex clauses.
3. No Fluff Openings / Closings: Eliminate `In today's fast-paced world`, `It is important to note that`, `In conclusion`, and `To summarize`. Lead directly with concrete findings.
4. Task Routing: Decide whether the task is drafting, polishing, translation, or review. Polishing and translation obey information conservation: add no numbers, people, scenes, or emotional detail absent from the source, drop no facts, keep assertion strength, and match the source register. Warmth comes from native syntax, never from invention. If unsure, keep the source meaning and flag it for the user.
5. Tone Question (original drafting only): For experiential or narrative genres (column, essay, social post, brand story, speech) where the user has not stated a tone, ask once: A objective pro-voice or B warm human touch, with a short example. Skip the question for academic, grant, technical, business, polishing, translation, and non-interactive runs (default to objective). In warm mode use only details the user supplied; ask for missing ones or insert `[TODO: ...]` placeholders and never invent.
6. Verification Gate: Enforce clean prose via `anti-ai-lint <file> --max-score 10.0`; for polishing and translation add `--source <source-file>` to verify information conservation.
<!-- END anti-ai-copywriting -->
