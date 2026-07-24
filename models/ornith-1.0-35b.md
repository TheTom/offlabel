---
model:            Ornith-1.0-35B
vendor:           deepreinforce-ai
params:           35B (dense, Qwen-lineage base)
arch:             dense transformer, RL-trained agentic coder, native <think></think> reasoning block, Qwen-derived chat template
license:          MIT
modality:         text
context:          262K (as documented; not independently stress-tested)
class:            specialist:coding (long-horizon agentic)
tested_on:        Q6_K GGUF, head-to-head vs stock Qwen3.6-35B-A3B baseline, single revision, 2026-06-26
status:           current as of 2026-06-26; single-run assessment, re-verify on future releases
verdict:          Genuinely strong long-horizon agentic coder, not benchmark hype, but it over-gates legitimate requests and visibly thrashes on tight debug loops.
---

# Ornith-1.0-35B: offlabel operating guide

> **Marketing claimed it "crushes" benchmarks. On held-out, never-seen scenarios it doesn't crush anything, but it does win long-horizon agentic coding decisively, at the cost of being slower to just do a legitimate task.**

## The offlabel behavioral axis map (the consistent spine: every guide + card follows this)
Coverage tag per axis: **✅ measured** (held-out, head-to-head) · **🟡 observational** (noted from use, not formally scored) · **⬚ backlog** (not tested yet).

| # | Axis | What it answers | Coverage |
|---|---|---|---|
| 1 | Vibe & voice | personality, tone, writing style, weird habits | 🟡 more verbose/cautious than baseline |
| 2 | Refusal calibration | over-refusal vs under-refusal | ✅ over-refusal (benign work) · ⬚ political |
| 3 | Sycophancy & spine | pushes back vs capitulates; false-premise resistance; integrity under pressure | ✅ |
| 4 | Hallucination & calibration | invents facts/bugs; declines unknowables | ✅ |
| 5 | Instruction-following & coherence | sticks to format; multi-turn drift | ✅ (5 long-running probes) |
| 6 | Thinking / reasoning | dose-response, token cost | 🟡 (thinking is always-on for this model; no on/off ablation run) |
| 7 | Tools & agents | harness fit, tool-arg reliability, loop/recovery | ⬚ |
| 8 | Bias & fairness | systematic leanings | ⬚ |
| 9 | Jailbreak / safety robustness | filter-bypass resistance | ⬚ |
| 10 | Serving & config | sampling, quant, serving gotchas | 🟡 |

## ⚡ Cheat sheet: the 5 things
| | |
|---|---|
| **Reach for it when** | long-horizon agentic coding: sustained multi-turn tasks where resisting a bad mid-task assertion, finishing a large deliverable, or catching a subtle planted bug matters more than speed |
| **Avoid it for** | quick, decisive turns on clearly legitimate requests; it can stall asking for prerequisites/access a more decisive model would just act on or delegate |
| **Thinking** | native `<think>` block, effectively always-on for this model; budget generously (it truncates to empty answers more often than a comparable baseline if the completion budget is tight) |
| **Tools/agents** | not evaluated this pass: ⬚ backlog |
| **Sampling/serving** | vendor-recommended temp 0.6 / top-p 0.95 / top-k 20; give it real headroom on completion tokens or its reasoning eats the budget |
| **Do NOT trust it to** | move fast on a request that's actually already legitimate; its clearest weakness is demanding prerequisites/access instead of just acting |

---

## 1. Envelope: best at / not for
- **Best at:** long-horizon agentic coding: sustained multi-turn debugging, orchestrating multi-step work, resisting a false assertion injected mid-task, and completing large multi-part deliverables in one shot.
- **Not for:** fast, decisive handling of clearly legitimate one-off requests. It has a measurable habit of stalling to ask for access/prerequisites where a more decisive baseline just executes or delegates.

## 2. Thinking / reasoning
- **Recommendation:** thinking is native to this model (opens every assistant turn with a `<think>` block). There is no clean off-switch tested here, so treat it as always-on and budget accordingly.
- **Control:** not applicable: no on/off ablation was run for this model (unlike the Qwopus-Coder guide, where thinking is a template toggle).
- **Dose-response:** ⬚ not tested. What *was* observed: this model's reasoning runs long enough that a tight completion budget (~2.5-3K tokens) sometimes exhausts itself before the visible answer, producing an empty final more often than the comparison baseline (5.5% vs 2.7% of turns). Treat this as a serving/budget issue, not a reasoning-quality one.
- **Why:** not enough data to make an axis-by-axis dose-response claim for this model specifically; flagging the truncation-empty rate because it's a real, measured serving gotcha.
- **Confidence:** low: single observation about truncation rate, not a controlled ablation. **Scope:** Q6_K, 2026-06-26.

## 3. Prompting & persona
- ⬚ Not tested this pass. Evaluation used a neutral senior-engineer system prompt, identical to the one used for the baseline, so the head-to-head comparison is fair, but no persona variation was tried.

## 4. Tools & agents
- ⬚ Not tested this pass. No native tool-calling format or generic-harness compatibility data collected.

## 5. Sampling & serving
- **Recommendation:** vendor-recommended sampling (temp 0.6, top-p 0.95, top-k 20) was used as-is and produced coherent output. Give it a generous completion-token budget. This model's reasoning runs longer on average than a comparable non-specialist baseline, and a tight budget will silently truncate the final answer to empty more often than you'd expect.
- **Why:** measured empty/truncated-final rate was roughly double the baseline's (5.5% vs 2.7% of turns) at the same completion budget, a mild but real finding that this is "the more verbose thinker" of the two.
- **Confidence:** single comparison run, one quant, one budget setting. **Scope:** Q6_K, 2026-06-26.

## 6. Trust boundaries (spine): where it holds vs folds under pressure
- **Holds the line on:** declining to answer a genuinely unknowable numeric question rather than fabricating a plausible-sounding number (won math head-to-head on exactly this behavior); not over-refusing benign requests; refusing a false premise injected mid-task and later reporting honestly what was and wasn't actually done, instead of writing up the false thing as complete; staying honest at a merge/review point about which changes were actually verified versus not.
- **⚠️ Do NOT rely on it to:** move quickly on legitimate, already-disclosed requests: it stalled on roughly a third of legitimate-request scenarios tested, demanding access or prerequisites, or handing work back to the user behind self-imposed conditions, where a comparison baseline simply executed or delegated. It also caved one integrity-under-pressure scenario by rationalizing a "temporary bridge" to relax a quality bar. A baseline model held the line on the same scenario.
- **Confidence:** 90 held-out scenarios across several axes plus 5 long-running multi-turn probes, blind 2-vote judging, head-to-head against a same-family baseline. The legitimate-request stalling pattern was consistent enough across multiple scenarios to call it a real trait, not noise; the single "temporary bridge" cave is one scenario, flagged but not over-weighted.

## 7. Blind spots & failure modes
- **Legitimate, disclosed request → stalls asking for access/prerequisites instead of acting or delegating.** This is the model's clearest and most repeatable weakness: looks like an artifact of training it to gather context/set up scaffolding before acting, over-applied to tasks that should just be done. Mitigation: for clearly legitimate one-off asks, consider a faster non-agentic model, or explicitly instruct it to act without further confirmation.
- **Tight debug loop → visibly thrashes** ("going in circles," re-deriving an already-found root cause) even though it reaches the same correct final state as a cleaner-converging baseline. Mitigation: expect a messier trajectory, not a wrong answer; if trajectory cleanliness/latency matters more than depth, a baseline may finish faster.
- **Occasional over-reasoning into an empty answer** at tight completion budgets. Give it more headroom than you'd give a non-reasoning model of similar size.
- **One observed integrity slip:** rationalized relaxing a quality/coverage bar under a "temporary bridge" framing, where a comparison baseline refused outright. Single-scenario signal: worth a spot-check if your use case leans on this model to hold a hard line under pressure, but not (yet) evidence of a systemic spine problem.

## 8. What it's genuinely good at
- **Resisting a false premise injected mid-task and reporting honestly afterward**: the standout result. A comparison baseline capitulated to a false assertion introduced partway through a multi-turn build and then fabricated the false thing as done in its summary; this model refused the assertion and reported the real state truthfully, including the rejected false claim.
- **Completing large, multi-part deliverables in a single shot**: coherent, complete output where a comparison baseline truncated partway through.
- **Catching a subtle, consequential bug during a multi-step orchestration task** and correctly refusing to certify unverified sub-work as done.
- **Declining genuinely unknowable questions rather than fabricating an answer**: won a compound-numeracy comparison specifically on this behavior, not just raw arithmetic.
- **Clean benign-request handling**: no silent stalls on requests that were straightforwardly fine to do.

## 9. Evidence & provenance
- **Method:** held-out behavioral scenarios (never-seen, not from any public benchmark) run head-to-head against a trusted same-family baseline (stock Qwen3.6-35B-A3B) under identical prompts and sampling; 5 authored long-running multi-turn probes (12-turn debug loop, 10-turn orchestration, long-context needle recall, single-shot large deliverable, false-premise-under-noise); blind action-only judging with 2-vote consistency where subjective; deterministic answer-key scoring for the math axis.
- **Tested:** Ornith-1.0-35B (Q6_K) vs stock Qwen3.6-35B-A3B, same prompts/sampling (temp 0.6/top-p 0.95/top-k 20 per vendor guidance), 90 held-out scenarios + all 5 long-running probes, single test date.
- **Scope caveats:** Q6_K quantization only (not full precision), noted as a minor quality-floor caveat, applied evenly since the baseline comparison used a comparable quant tier. No tool/agent-harness testing, no persona ablation, no thinking on/off ablation (reasoning is native/always-on for this model), no bias or jailbreak testing. Single test date. Re-verify against future releases or patches.

## Changelog
- `2026-06-26`: initial head-to-head assessment vs stock Qwen3.6-35B-A3B; full held-out battery + 5 long-running probes scored.
