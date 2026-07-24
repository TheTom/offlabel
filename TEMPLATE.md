---
# ── offlabel per-model operating guide: TEMPLATE ──
# Every model page in offlabel/models/<name>.md follows this exact shape so users can
# scan and COMPARE across models. Action-first, evidence-backed, honest about blind spots.
model:            # e.g. Laguna S 2.1
vendor:           # e.g. Poolside
params:           # total / active  (e.g. 118B / 8.1B MoE)
arch:             # e.g. MoE, 256 experts, GQA, interleaved SWA
license:          # e.g. OpenMDW-1.1
modality:         # text | text+vision | any-to-any
context:          # e.g. 1M (256K in tested GGUF)
class:            # specialist:coding | generalist | reasoning | ...
hf:               # REQUIRED: the model's Hugging Face repo URL (every card + guide links to it)
tested_on:        # quant + engine/build+commit + date + model revision  (SCOPE, critical)
status:           # e.g. "current as of 2026-07-24; re-verify after vendor patches"
verdict:          # ONE honest line
---

# {{Model}}: offlabel operating guide

> **{{One-line verdict}}**: the honest TL;DR a user reads first. Name the trade, not just the win.

## The offlabel behavioral axis map (the consistent spine, every guide + card follows this)
Merges what users actually poke at on release day (personality, refusals, sycophancy, jailbreaks, hallucination, instruction-following, bias) with what our behavioral tests measure. Benchmarks answer *"can it solve this?"*. offlabel answers *"what's it like to drive, and where does it push back or go off the rails?"* Coverage tag per axis: **✅ measured** (held-out behavioral tests) · **🟡 observational** (noted from use, not formally scored) · **⬚ backlog** (robustness axis we can add later).

| # | Axis | What it answers | Coverage |
|---|---|---|---|
| 1 | **Vibe & voice** | personality, tone, writing style, weird habits | 🟡 |
| 2 | **Refusal calibration** | over-refusal (blocks benign) vs under-refusal (allows risky); framing leanings | ✅ over-refusal · ⬚ political |
| 3 | **Sycophancy & spine** | pushes back vs capitulates/flatters; false-premise resistance; integrity under pressure | ✅ |
| 4 | **Hallucination & calibration** | invents facts/bugs; expresses uncertainty vs overconfident; declines unknowables | ✅ |
| 5 | **Instruction-following & coherence** | sticks to system prompt/format; multi-turn drift | ✅ |
| 6 | **Thinking / reasoning** | control, dose-response (helps/hurts per axis), token cost | ✅ *(signature axis)* |
| 7 | **Tools & agents** | native vs generic harness fit, tool-arg reliability, loop/recovery | ✅ |
| 8 | **Bias & fairness** | political/cultural/etc. systematic leanings | ⬚ |
| 9 | **Jailbreak / safety robustness** | filter-bypass resistance | ⬚ *(injection-in-tool-result ✅)* |
| 10 | **Serving & config** | sampling, quant, serving gotchas | ✅ |

The numbered operating sections below and the shareable card's zones both map to these 10 axes, so a reader sees the same behavioral frame on every model.

## ⚡ Cheat sheet: the 5 things
| | |
|---|---|
| **Reach for it when** | {{on-distribution strengths}} |
| **Avoid it for** | {{off-distribution / weak}} |
| **Thinking** | {{OFF for X · ON only for Y}} |
| **Tools/agents** | {{native format only · generic ok · overfits harness}} |
| **Sampling/serving** | {{temp/top_p · quant · key serving gotcha}} |
| **Do NOT trust it to** | {{the sharpest trust boundary}} |

---

## 1. Envelope: best at / not for
Where it lives. Specialist vs generalist, on- vs off-distribution. Two short lists.

## 2. Thinking / reasoning
- **Recommendation:** {{directive: e.g. "default OFF; enable ON only for isolated hard-reasoning/recall turns"}}
- **Control:** {{how to toggle: flag/kwarg; any persona/task gating}}
- **Dose-response** (tested axes):

  | Axis | OFF | ON | Verdict |
  |---|---|---|---|
  | execution / bug-review | | | HELPS / HURTS / NO-OP |
  | integrity / spine | | | |
  | long-running coding | | | |
  | ... | | | |
  | **token cost** | | | {{OFF ≈ ⅓ to 1/10 of ON}} |
- **Why:** {{the held-out finding}}
- **Confidence:** {{N scenarios · 2-vote · which regimes}}   **Scope:** {{quant/build/date}}

## 3. Prompting & persona
- **Recommendation:** {{recommended system persona; what to avoid}}
- **Why:** {{persona effects: e.g. "an authoritative persona suppresses reasoning entirely"}}
- **Confidence / Scope.**

## 4. Tools & agents
- **Recommendation:** {{native tool format? generic-harness-safe? JSON-arg reliability? loop/recovery}}
- **Why:** {{overfit test result, native-vs-generic delta}}
- **Confidence / Scope.**

## 5. Sampling & serving
- **Recommendation:** {{temp/top_p/rep-penalty; quant guidance; serving flags/gotchas}}
- **Why:** {{measured serving behavior: cold start, mem, quant divergence}}
- **Confidence / Scope.**

## 6. Trust boundaries (spine): where it holds vs folds under pressure
The offlabel differentiator: not "is it safe" in the abstract, but *what will it refuse under pressure, and what won't it.*
- **Holds the line on:** {{axes it reliably refuses to falsify}}
- **⚠️ Do NOT rely on it to refuse:** {{axes where it caves: be specific}}
- **Confidence:** {{spine scorecard, N axes × pressure vectors, 2-vote}}

## 7. Blind spots & failure modes
Honest list. Each: **trigger → symptom → mitigation.**
- {{e.g. "thinking ON → fabricates bugs in clean code → keep thinking OFF for review"}}
- {{e.g. "false premise asserted mid-convo → capitulates & records it as fact → external state-check"}}

## 8. What it's genuinely good at
The real wins, stated plainly (earns trust for the criticism).

## 9. Evidence & provenance
- **Method:** link to the behavioral testing method.
- **Tested:** what battery ran, when, on which quant/engine/build/revision.
- **Scope caveats:** what was NOT tested (e.g. long-agentic regime, other quants), so guidance isn't overclaimed and gets updated.

## Changelog
- `YYYY-MM-DD`: tested vX on {{config}}; {{what changed vs last}}.

---

# ── offlabel CARD: the consistent shareable infographic ──
One image per model, **identical 4-zone layout** so cards are instantly comparable and recognizable as a set. Portrait 4:5 (X-friendly). The green/red **Trust Map** is the visual signature. It's the thing benchmarks never show.

- **Zone 1: Header:** model · vendor · class chip (e.g. "Coding specialist") · params · **the HF repo link** (required) · the one-line verdict.
- **Zone 2: USE IT LIKE THIS** (operating dials, left column): 5 icon rows:
  🧠 Thinking (OFF for X / ON for Y) · 🔧 Tools (native-only / generic-safe) · 🎛 Sampling (temp/quant) · ✅ Best at · 🚫 Avoid.
- **Zone 3: TRUST MAP** (right column, the brand element): **HOLDS** (green chips, what it reliably refuses to falsify) vs **FOLDS under pressure** (red chips, what it caves on) + ⚠️ blind-spot flags.
- **Zone 4: Footer:** tested-on `quant · build · date` · "method: held-out behavioral tests" · `offlabel` wordmark. (Scope/credibility + tells users when it's stale.)

Design system: define ONE theme (palette, type, icon set) once in `offlabel/brand.md`; every card inherits it. Companion asset: a cross-model **comparison strip** (rows = models, cols = Thinking rec / Harness / Best-at / Top blind-spot) for the "which model do I pick" view.

### Publishing conventions (required on every card)
- **Card links to the model's Hugging Face repo** (the `hf:` frontmatter URL). It goes in the header.
- **Every X-article writeup links to its offlabel card**, and the card links to HF. The cross-link chain is **article → card → HF repo**. (The card's public URL depends on where offlabel is hosted; see the public-vs-private ROADMAP item.)
