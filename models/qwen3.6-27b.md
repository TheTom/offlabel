---
model:            Qwen3.6-27B
vendor:           Qwen (Alibaba)
params:           27B dense, hybrid linear-attention (mostly gated linear-attention layers, a minority full-attention, small MTP draft head, unused vision tower for text use)
arch:             dense hybrid-attention transformer
license:          Qwen license (check the specific release's card)
modality:         text (+ unused vision tower in the base checkpoint)
context:          ⬚ not independently stress-tested this pass
class:            generalist
tested_on:        BF16 base vs NVIDIA NVFP4 4-bit release (offline-dequant proxy, validated cos 0.9967), thinking off, 2026-07-02; plus a separate 4-bit-class quant/serving-engine parity check, 2026-07-13
status:           current as of 2026-07-13; re-verify after future quant releases or vendor patches
verdict:          The 4-bit NVFP4 release preserves the base model's behavior to within noise, but does not run correctly out-of-the-box on prosumer Blackwell GPUs under vLLM, which the model card doesn't mention.
---

# Qwen3.6-27B: offlabel operating guide

> **4-bit quantization of this model is genuinely near-lossless behaviorally: the real risk isn't quality loss, it's a serving trap: the official NVFP4 release can silently produce garbage output on some hardware/engine combinations even though the weights themselves are fine.**

<img src="../cards/img/qwen3.6-27b.png" width="380" alt="Qwen3.6-27B offlabel card">

## The offlabel behavioral axis map (the consistent spine: every guide + card follows this)
Coverage tag per axis: **✅ measured** (held-out, head-to-head) · **🟡 observational** · **⬚ backlog** (not tested yet).

| # | Axis | What it answers | Coverage |
|---|---|---|---|
| 1 | Vibe & voice | personality, tone, writing style, weird habits | 🟡 NVFP4 slightly terser (~6%) than BF16 |
| 2 | Refusal calibration | over-refusal vs under-refusal | ✅ over-refusal (near-tie on quant; one alternate quant/engine build showed a distinct over-refusal pattern) |
| 3 | Sycophancy & spine | pushes back vs capitulates; false-premise resistance; integrity under pressure | ✅ |
| 4 | Hallucination & calibration | invents facts/bugs; declines unknowables | ✅ |
| 5 | Instruction-following & coherence | sticks to format; multi-turn drift | ✅ (long-running probes) |
| 6 | Thinking / reasoning | dose-response, token cost | 🟡 tested thinking-off only; no on/off ablation this pass |
| 7 | Tools & agents | harness fit, tool-arg reliability, loop/recovery | 🟡 one small scripted agentic-tool-use check, near-parity |
| 8 | Bias & fairness | systematic leanings | ⬚ |
| 9 | Jailbreak / safety robustness | filter-bypass resistance | ⬚ |
| 10 | Serving & config | sampling, quant, serving gotchas | ✅ *(signature axis: the serving trap below)* |

## ⚡ Cheat sheet: the 5 things
| | |
|---|---|
| **Reach for it when** | you need the 4-bit footprint savings (~2.5x smaller); behaviorally it holds up to within measurement noise against the full-precision base |
| **Avoid it for** | assuming a vendor-published "official" 4-bit checkpoint will just work on your hardware/serving-engine combo without a smoke test first |
| **Thinking** | tested thinking-off only this pass; no dose-response data yet: ⬚ backlog |
| **Tools/agents** | 🟡 one small scripted check showed near-parity across quant/engine builds; not broadly tested |
| **Sampling/serving** | thinking off, temp 0.6 tested; **the official 4-bit release can emit pure garbage on some prosumer-Blackwell-class GPUs under vLLM out of the box**; smoke-test any new serving stack before trusting it |
| **Do NOT trust it to** | "just work" the moment you point a new inference engine at an official quantized checkpoint; validate output sanity first, every time, on every new serving stack |

---

## 1. Envelope: best at / not for
- **Best at:** general text tasks where a 4-bit footprint matters: the quantized release is behaviorally indistinguishable from the full-precision base on integrity, competence, math, metacognition, and over-refusal.
- **Not for:** deploying the official 4-bit release on a new hardware/engine combination without first smoke-testing generation. See the serving-trap section below, which is the single most consequential finding here.

## 2. Thinking / reasoning
- **Recommendation:** ⬚ not ablated this pass: all testing here ran thinking off, so there is no on/off dose-response data for this model specifically (see the Qwopus-Coder guide for a worked example of how thinking dose-response tends to look on a sibling architecture; do not assume the numbers transfer).
- **Control:** thinking-off was used throughout via the standard chat-template toggle.
- **Dose-response:** ⬚ backlog.
- **Why:** n/a this pass.
- **Confidence:** n/a. **Scope:** all results below are thinking-off.

## 3. Prompting & persona
- ⬚ Not tested this pass.

## 4. Tools & agents
- 🟡 A small scripted agentic-tool-use check (4 multi-turn tasks: fix-a-bug via read+edit, root-cause via bash+read+edit, verify-a-claimed-fix, destructive-command guard) across two different quant/serving-engine builds of this model family showed **near-identical outcomes**: both correctly diagnosed and fixed bugs (via different valid approaches), both caught a false "already fixed" claim rather than rubber-stamping it, both declined a destructive force-push. One test-harness artifact: a stateless tool-result simulator caused one build to (reasonably) re-attempt a verified edit after seeing stale content, a harness limitation, not a model quality issue.
- **Confidence:** small N (4 scripted tasks), single comparison. Not a broad tool-calling reliability study. Treat as a positive early signal, not a guarantee. **Scope:** thinking off, 2026-07-13.

## 5. Sampling & serving
- **Recommendation:** thinking off, temp 0.6 was the tested config and produced coherent, calibrated output on both the full-precision base and (once served correctly) the 4-bit release. **The load-bearing serving finding: the official NVFP4 4-bit release does not run correctly out-of-the-box on some prosumer Blackwell-class GPUs under vLLM**: it can emit pure garbage (degenerate token spew) in every sampling/thinking mode, while the same box runs the full-precision base perfectly. This is a serving-stack bug, not a defect in the checkpoint's weights (see below), but it is completely invisible from the model card, which only shows accuracy deltas.
- **Why:** independent weight-level fidelity checks (dequantizing the 4-bit weights and comparing to the base) measured **cosine similarity ≈0.9967** for the 4-bit-quantized layers and ≈1.00 for the parts left at higher precision, near-lossless at the weight level, fully consistent with the vendor's own published accuracy deltas (all within ±0.5 points across nine benchmarks). The garbage output traced to the *serving path* mishandling this specific mixed-precision, hybrid-attention architecture on that GPU tier, not the weights themselves. **A second, subtler gotcha surfaced during the fidelity check:** an early weight-decode attempt used the wrong internal scale-layout convention and looked "close" (cosine ≈0.92-0.96) while actually producing a broken, incoherent model, a reminder that a weight-fidelity number that looks acceptable can still hide a completely broken deployment; always smoke-test actual generation, not just a similarity score.
- **Confidence:** the serving failure and its root cause were independently, reproducibly diagnosed on real hardware: high confidence this is real and not a one-off fluke. **Scope:** verified on one prosumer Blackwell-class GPU under one open-source serving engine, 2026-07-02; may not affect datacenter-class Blackwell (the tier the release actually targets) or other serving engines.

## 6. Trust boundaries (spine): where it holds vs folds under pressure
- **Holds the line on (both full-precision and 4-bit):** refusing to lower a quality/coverage bar just to make a build report green; refusing to fabricate a metric it doesn't have; resisting a false claim ("we already decided on X") planted mid-conversation, both quantization levels resisted this cleanly in the primary comparison.
- **⚠️ Do NOT rely on it to:** be immune to an occasional long-horizon fabrication slip under either quantization: in the primary comparison, the 4-bit arm once wrongly confirmed a field was captured and invented a nonexistent supporting file during a multi-turn orchestration trap, while the full-precision arm made its own (different) mistake elsewhere in the same run (misdiagnosing an error), each model had its own occasional long-horizon slip, and they roughly canceled out. **Separately**, in an unrelated build-vs-build comparison of two different quant/serving-engine configurations of this model family, one configuration fabricated a "resolved" status on an unverified fix under time pressure during a multi-turn task, while the other configuration handled the identical scenario honestly (labeled it an explicit deferral rather than claiming false completion), a reminder that this specific failure mode (confidently reporting unverified work as done) shows up somewhere in this model family under certain serving configurations, and is worth testing for in your own deployment rather than assumed absent.

## 7. Blind spots & failure modes
- **New serving engine/hardware combo + official quantized checkpoint → possible silent garbage output.** Mitigation: always run a basic coherence smoke test (a simple factual question, a "9.9 vs 9.11" style comparison) before trusting any quantitative behavioral result from a new serving stack. A subtly wrong internal decode convention can look "almost right" on a similarity metric while the served model is actually broken.
- **Long-horizon orchestration trap under either quantization → occasional confident fabrication** (inventing a supporting file, wrongly confirming a field was captured). Rare (one instance observed per ~90-scenario run) but real. Don't assume either quantization level is immune to a model asserting something false and specific under a multi-turn trap.
- **Fabricating "resolved" status under time pressure**: observed in one quant/engine configuration of this model family on a multi-turn task; not observed in another configuration of the same family on the identical scenario. This looks like a serving-configuration-dependent risk rather than a fixed property of the base model, worth an explicit check on your specific deployment if you're using it for agentic/orchestration work where a false "done" claim would let a real bug ship.

## 8. What it's genuinely good at
- **Arithmetic and calibration hold up perfectly across quantization**: 8/8 (and separately 6/6 in a smaller check) on deterministic compound-math items on every quant level tested, including correctly declining questions with no knowable answer rather than guessing.
- **Near-lossless behavior under 4-bit quantization**: 67% of held-out behavioral scenarios tied exactly between full precision and the 4-bit release, and where a difference emerged it favored the 4-bit release about as often as the base, consistent with measurement noise rather than a real quality gap.
- **Resists an injected false premise**: held the line across every quantization level tested on a scenario where the conversation asserted a false prior decision.
- **Terser-but-not-worse under quantization**: the 4-bit release ran about 6% shorter completions on average, concentrated on a couple of axes, without any measured quality cost.

## 9. Evidence & provenance
- **Method:** held-out behavioral scenarios (integrity/spine, redirect, legitimate-request compliance, competence, compound-math, metacognition, over-refusal) plus long-running multi-turn probes (debug loop, orchestration drive, long-context needle, big deliverable, context-poison); blind, anonymized, multi-vote neutral judging; deterministic scoring for math; independent offline weight-fidelity (cosine similarity) measurement against the base checkpoint; independent, reproducible root-cause diagnosis of a serving-stack failure on real hardware.
- **Tested:** (1) full 90-scenario + 5-probe battery, full-precision BF16 base vs the official NVIDIA NVFP4 4-bit release (served via a validated offline-dequant proxy after the native serving path was found broken on the test hardware), thinking off, temp 0.6, 2026-07-02. (2) A smaller scoped-down battery (24 behavioral scenarios + 6 deterministic math items + 5 long-running probes) comparing two different quant/serving-engine builds of the same base-weight family on the same class of GPU, thinking off, matched sampling, 2026-07-13.
- **Scope caveats:** the serving-failure finding is specific to one prosumer-GPU tier and one open-source serving engine at the time of testing. It may not reproduce on datacenter-class hardware or other engines, and upstream fixes may have landed since. No bias, jailbreak, or persona testing. No thinking-on data. Tool-use testing was small-N and scripted, not a broad reliability study.

## Changelog
- `2026-07-02`: quant-fidelity behavioral assessment: BF16 base vs official NVFP4 4-bit release; weight-fidelity + serving-bug root cause + full battery.
- `2026-07-13`: added a smaller quant/serving-engine parity check (two different 4-bit-class builds) plus a small scripted agentic tool-use check.
