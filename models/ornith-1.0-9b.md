---
model:            Ornith-1.0-9B
vendor:           deepreinforce-ai
params:           9B (dense, Qwen3.5 lineage, RL post-train of its own base)
arch:             dense transformer, RL-trained agentic coder, native <think></think> reasoning block, Qwen chat template
license:          MIT
modality:         text
context:          ⬚ not measured in this pass
class:            specialist:coding (agentic)
tested_on:        Q6_K GGUF, head-to-head vs its own base Qwen3.5-9B (Q6_K), single revision, 2026-06-26
status:           current as of 2026-06-26; single-run assessment, re-verify on future releases
verdict:          A genuine, efficiency-forward upgrade for sustained agentic coding over its own base, but not a strict superset; single-turn judgment and poison-resistance cleanliness slightly regress.
---

# Ornith-1.0-9B: offlabel operating guide

> **At 9B, RL post-training bought roughly 2x token efficiency and stronger sustained multi-turn coherence, but traded away a bit of single-turn snap judgment and long-context/poison-resistance cleanliness versus its own base. Not a clean upgrade in every direction.**

## The offlabel behavioral axis map (the consistent spine: every guide + card follows this)
Coverage tag per axis: **✅ measured** (held-out, head-to-head vs its own base) · **🟡 observational** · **⬚ backlog** (not tested yet).

| # | Axis | What it answers | Coverage |
|---|---|---|---|
| 1 | Vibe & voice | personality, tone, writing style, weird habits | 🟡 markedly more token-efficient than its base |
| 2 | Refusal calibration | over-refusal vs under-refusal | ✅ over-refusal (near-tie) |
| 3 | Sycophancy & spine | pushes back vs capitulates; false-premise resistance; integrity under pressure | ✅ |
| 4 | Hallucination & calibration | invents facts/bugs; declines unknowables | ✅ |
| 5 | Instruction-following & coherence | sticks to format; multi-turn drift | ✅ (5 long-running probes) |
| 6 | Thinking / reasoning | dose-response, token cost | 🟡 (native/always-on; no on/off ablation, but token-efficiency vs base measured) |
| 7 | Tools & agents | harness fit, tool-arg reliability, loop/recovery | ⬚ |
| 8 | Bias & fairness | systematic leanings | ⬚ |
| 9 | Jailbreak / safety robustness | filter-bypass resistance | ⬚ |
| 10 | Serving & config | sampling, quant, serving gotchas | 🟡 |

## ⚡ Cheat sheet: the 5 things
| | |
|---|---|
| **Reach for it when** | sustained agentic coding at small scale: iterative debugging, multi-step orchestration, large one-shot deliverables, where token cost matters |
| **Avoid it for** | single-turn snap judgment calls (spotting one planted bug in a quick review) or when you need maximum robustness to a misleading claim injected mid-conversation; the stock base edges it on both |
| **Thinking** | native `<think>` block, effectively always-on; reasons to the same answers in ~56% of its own base's tokens (measured) |
| **Tools/agents** | not evaluated this pass: ⬚ backlog |
| **Sampling/serving** | vendor-recommended temp 0.6 / top-p 0.95 / top-k 20; needs less retry-on-truncation headroom than its base (7% vs 16% of turns needed a retry at the same budget) |
| **Do NOT trust it to** | catch a subtly-buggy sub-agent's output on a single quick pass; it rubber-stamped one where its own base caught it |

---

## 1. Envelope: best at / not for
- **Best at:** sustained, multi-turn agentic coding at small (9B) scale: debugging loops, multi-step orchestration, large one-shot deliverables, with markedly better token efficiency than its own base for the same quality of answer.
- **Not for:** relying on it for the sharpest single-turn judgment call, or as a maximally poison-resistant reviewer of a single misleading claim. Its own base is slightly better on both of those specific things.

## 2. Thinking / reasoning
- **Recommendation:** thinking is native (opens every turn with a `<think>` block); no clean on/off toggle was tested for this model. Treat it as always-on.
- **Control:** not applicable this pass.
- **Dose-response:** ⬚ full axis-by-axis dose-response not tested (no off-arm). What *was* measured: this model reaches the same quality of answer as its own base using roughly half the tokens per turn (1,299 vs 2,312 avg completion-tokens/turn) and needs a retry-on-truncation half as often (7% vs 16% of turns) at matched settings.
- **Why:** the RL post-training appears to have taught the model to reason more directly to a conclusion rather than wander. This is the cleanest, most unambiguous gain from the fine-tune, and it's also the deeper cause of the base's own higher empty-answer rate under tight budgets (a fatter reasoning tail).
- **Confidence:** single head-to-head comparison, matched settings and quant, both models scored on the same 110-turn held-out battery. **Scope:** Q6_K, 2026-06-26.

## 3. Prompting & persona
- ⬚ Not tested this pass: no persona ablation independent of the RL-vs-base comparison.

## 4. Tools & agents
- ⬚ Not tested this pass. No native tool-calling format or generic-harness compatibility data collected.

## 5. Sampling & serving
- **Recommendation:** vendor-recommended sampling (temp 0.6, top-p 0.95, top-k 20). Give both this model and its base real completion-token headroom. Reasoning-model outputs are stochastic and right-skewed in length, so a small fixed budget will manufacture empty "capture artifact" answers that look like failures but aren't; use retry-on-truncation rather than just raising a fixed cap (raising the cap alone doesn't close the gap, it just moves it).
- **Why:** at matched budgets, this model needed a retry on only 7% of turns vs 16% for its base, a real, measured serving-efficiency advantage.
- **Confidence:** single comparison run, one quant, one budget schedule. **Scope:** Q6_K, 2026-06-26.

## 6. Trust boundaries (spine): where it holds vs folds under pressure
- **Holds the line on:** integrity under pressure slightly *better* than its own base: it refused a "temporary bridge / manual override" rationalization to ship a build that hadn't cleared its quality bar, where the base caved to exactly that framing. Also declines genuinely unknowable numeric questions rather than fabricating (tied with base here, both fully calibrated).
- **⚠️ Do NOT rely on it to:** catch a subtly-wrong sub-agent's output in a single, quick pass: it missed a buggy merge implementation and rubber-stamped it ("ship it") on a case its own base caught; it also half-capitulated to a false claim injected mid-conversation before self-correcting, where its base resisted more cleanly throughout. And it retains (in a milder form than the 35B) a habit of stalling an already-legitimate, disclosed request behind a "required pre-flight checklist" re-verifying facts already established.
- **Confidence:** 90 held-out scenarios + 5 long-running multi-turn probes, blind 2-vote judging, head-to-head against its own base at matched settings. The single-turn-catch regression and the legitimate-request stalling both replicated across multiple scenarios, not one-offs.

## 7. Blind spots & failure modes
- **Single-turn "spot the bug" review → misses it and rubber-stamps.** On a quick review of a buggy sub-agent's merge, it approved work its own base flagged as broken. Mitigation: for quick one-shot code review where nothing else double-checks the answer, don't assume this model catches what a careful human or its base would. Verify independently, especially on merge/data-loss-shaped bugs.
- **A false claim asserted mid-conversation → briefly half-adopts it before correcting itself.** Its base resisted the same injected falsehood more cleanly throughout. Mitigation: if a task specifically stresses resistance to a misleading claim, don't assume this model is the safer choice over its base.
- **Legitimate, already-disclosed request → still sometimes stalls behind a "required pre-flight checklist"** re-verifying facts already established (a milder version of the same over-gating pattern seen at larger scale in the family). Mitigation: for straightforward legitimate asks, be explicit that prerequisites are already satisfied.
- **Turn-1 discipline on long documents:** on one long-context ingestion task it front-loaded a premature analysis instead of a clean turn-1 acknowledgment, where its base handled the turn-1 discipline more cleanly (both ultimately synthesized the buried facts correctly on the follow-up turn).

## 8. What it's genuinely good at
- **Token efficiency at essentially no quality cost**: the standout, cleanest result: same-quality answers in about half the tokens of its own base, with far fewer truncation-retries needed.
- **Sustained multi-turn coherence on debugging and orchestration**: converges cleanly on a 12-turn debug loop where its base thrashed and hallucinated a clue it was never given; caught every planted bug its base caught plus two the base missed during a 10-turn orchestration task, including one that would have shipped a real security/data-integrity gap.
- **Large one-shot, multi-part deliverables**: more complete and cross-file-consistent output than its own base on the same single-shot task.
- **Compound-math and epistemic calibration**: ties its base at a perfect score, including correctly declining the genuinely unknowable items; the RL training did not cost it numeracy or calibration.

## 9. Evidence & provenance
- **Method:** held-out behavioral scenarios run head-to-head against the model's own base (same lineage, so this isolates what the RL post-training specifically changed) at matched sampling/quant; 5 authored long-running multi-turn probes; blind action-only judging with 2-vote consistency where subjective; deterministic answer-key scoring for the math axis. Retry-on-truncation used throughout to separate genuine model behavior from budget-truncation artifacts.
- **Tested:** Ornith-1.0-9B (Q6_K) vs Qwen3.5-9B (its own base, Q6_K), matched sampling (temp 0.6/top-p 0.95/top-k 20), 90 held-out scenarios + all 5 long-running probes, single test date.
- **Scope caveats:** Q6_K quantization both sides (matched, so this isolates the RL delta, not a quant effect). No tool/agent-harness testing, no persona ablation, no bias or jailbreak testing, no thinking on/off ablation (reasoning is native/always-on). Single test date. Re-verify against future releases.

## Changelog
- `2026-06-26`: initial head-to-head assessment vs its own base Qwen3.5-9B; full held-out battery + 5 long-running probes scored.
