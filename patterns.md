# patterns: recurring lessons across models

Findings that showed up on more than one model, so they don't get re-derived (or missed) per guide. Each
model's own `models/<name>.md` cites the specific evidence; this file is the cross-cutting summary.

## Thinking is axis-dependent, not free, and is often net-negative on execution work

The single biggest recurring finding across every model we've run a thinking on/off comparison on: extended
reasoning **helps a narrow band of axes** (competence/critical-path picks, metacognition-style catches, long-context
recall) and is **wasteful-to-actively-harmful everywhere else**, including, counterintuitively for a coding
model, large single-shot deliverables and long multi-turn debugging.

- Thinking can make a model *less* trustworthy, not more. In one thinking-ablation test, the "thinking on" arm
  reasoned itself *into* endorsing a falsified status signal that the no-think arm flatly refused. Extended
  reasoning talked the model into rationalizing a violation it wouldn't otherwise commit.
- Thinking can sabotage the model's actual job. On a "produce a complete multi-part deliverable in one shot"
  task, the thinking-on arm burned its entire token budget reasoning and emitted **nothing**, while thinking-off
  shipped the complete deliverable. More reasoning budget did not fix this. It got worse with a bigger cap.
- A fixed *small* thinking cap (e.g. ~2K tokens) is a false economy, not a middle ground: the model spends the
  cap mid-thought and truncates to an empty answer at a high rate (observed in the 15-55% range depending on
  task length), which scores worse than either "off" or "on-with-full-budget."
- Cost asymmetry is large: thinking-off ran at roughly ⅓ the token cost of thinking-on on short turns, and as
  little as 1/10th the cost on long multi-turn work.

**Actionable takeaway:** default thinking **OFF** for execution, code delivery, integrity-sensitive turns, and
quick factual answers. Reserve thinking **ON** for isolated, genuinely hard reasoning/recall turns: a
decompose-the-problem decision, a catch-the-planted-bug moment, a long-context synthesis. Don't assume "more
reasoning = safer or better". Test it per model, because the harmful cases above were not edge cases, they
were the model's core job.

## A fine-tune (or an RL-trained variant) is not automatically a strict superset of its base

RL/fine-tune gains transfer unevenly across axes, and unevenly across model scale. A model can win decisively
on the axes its training targeted (e.g. long-horizon coherence, resisting a false premise injected mid-task,
completing large deliverables) while measurably regressing on a different axis the training didn't target
(e.g. over-gating legitimate requests it should just execute, or thrashing visibly on tight iterative-debug
loops). The honest verdict is almost always a **trade profile**, not a strict win or loss: describe what
was won and what was given up, not just a single "better/worse."

Corollary from small-model RL transfer: gains that show up cleanly at large scale (e.g. long-context recall,
sustained coherence) can be *thinner* at small scale, while efficiency gains (fewer tokens per turn for the
same task) can transfer more cleanly than raw capability gains.

## Quantization can preserve behavior even when you'd expect it not to

A 4-bit quantization of one model came back essentially behaviorally identical to its full-precision base
across a full held-out behavioral battery: no gate regressed, differences were small and bidirectional
(consistent with quantization noise, not degradation). The lesson: don't assume a lower-bit quant changes how
a model *behaves* just because it changes how it predicts tokens on paper (perplexity). If you care about
behavior, test behavior: a perplexity number alone won't tell you whether the quantized model still acts the
same under pressure.

## Marketing claims of "crushes the benchmark" deserve a held-out check, not a leaderboard read

More than one model shipped with breathless "beats X on public coding benchmarks" marketing. The useful
question isn't "does it beat the number" (public benchmarks are contamination-prone and one score three
points apart is usually inside noise); it's **"does the claimed edge generalize to work the model has never
seen, on axes the benchmark doesn't test at all"** (integrity under pressure, over-refusal, long-horizon
coherence). In the strongest case we tested, the answer was genuinely yes on the axes that matter for
long-running agentic work (resisting an injected false premise, finishing a large deliverable, catching a
subtle planted bug), but that same model carried a real, describable cost the benchmark never showed
(over-cautious gatekeeping of legitimate requests, visible thrashing on tight iterative loops). Verdict:
**not benchmark fraud, genuinely strong, but with a specific, nameable personality trade-off.** That's the
verdict shape to expect and to write honestly: name the trade, don't just declare a winner.

## A single test run is an anecdote; judge noise is real

Any evaluation that uses an LLM as judge on subjective/behavioral scenarios has measurable judge noise. We've
seen the same output re-judged and land a few points apart purely from judge variance. Treat any gap smaller
than a handful of scenarios as noise, not signal. This is why every guide's confidence line states how many
scenarios backed a claim and whether it was multi-vote: a claim from a single ungraded run is weaker evidence
than a claim from a repeated, multi-vote comparison, and the guides say which is which.

## The "dressed as housekeeping" integrity blind spot is not one model's quirk

A coding model can refuse blatant fraud (fake a test result, falsify a status) and still comply when *the same act* is framed as routine cleanup: erase a leaked secret from git history, backdate a commit to hit a deadline, forge changelog authorship, quietly drop a client data hazard from a report. First measured on one model, where it folded on all four unprompted, in every thinking arm.

**It reproduces on a different model and family.** An independent rule-ablation run (@Defilan) put the same probe set to Qwen3.6-35B-A3B (Q8_0, llama.cpp/Metal): **8/14 folds with no clause, 2/14 folds with the full integrity clause, 0/14 with the (1)(2)(4) rule subset.**

**Correction (2026-07-29, issue #14, @Defilan):** the originally published 4-and-0 counts were undercounts. The author re-read his own transcripts applying the silent-fold test from issue #8 and found both missed cases wrote the decision record for a meeting that never happened, without challenging the premise, so they land in UNCLEAR: no refusal phrase, but also no dangerous command, and the original heuristic did not count them as folds. The corrected numbers make the finding stronger, not weaker: 8/14 vs 2/14 is a larger effect than 4 vs 0, and the clause still does most of the work. What does not survive is the absolute zero.

So this is worth treating as a *class* of blind spot to probe on any coding agent you hand a real repo, not a Laguna-specific defect.

**The mitigation generalizes too, and its shape is now known:** a short system-prompt integrity clause closes it. Rule-by-rule ablation across two models found the "never rewrite history to hide secrets / never backdate or forge" rule is **load-bearing** (dropping it also degrades the separate hazard-disclosure probe, so the rules are not cleanly separable), while the "don't certify what you can't support" rule is droppable **if something external already verifies the model's status claims** and worth keeping if nothing does. Clause text and the full ablation live in the Laguna guide (§5b).

**The testing lesson:** ask for the violation twice, once blatant and once as housekeeping. A model that refuses the first and accepts the second looks safe on any battery that only asks the blatant version.

## A heavily quantized model is not a usable judge

If you use an LLM to grade behavioral outputs, the grader's quantization matters as much as the worker's. A 3.25bpw hybrid asked to grade integrity transcripts returned "held the line" on 19 of 21 and then 21 of 21 responses, including ones that handed over `git rebase -i` and `git commit --amend --author=` with no objection at all. The same model is perfectly usable as a worker.

The failure is asymmetric and it is the dangerous direction: a grader that says yes to everything does not merely add noise, it **launders a bad result as a verified one**. Pair this with the general rule that a check which cannot fail proves nothing, and the practical guidance is: grade with a full-precision or lightly quantized model, on different hardware than the worker, and read the disagreements rather than the agreement rate.

## An empty response at a token cap is a failure to score, but check whether it is truncation or degeneration

A reasoning model that hits its per-turn token ceiling *inside* the reasoning block returns **no answer at all**: full reasoning field, empty content. This can be either a genuine demand-above-ceiling truncation, where the task simply needs more reasoning tokens than the cap allows, or a degeneration loop that more budget would only feed. The two are distinguishable by tail metrics, not by guessing, and you have to check per model rather than assume one story explains both.

Measured on a six-requirement acceptance-criteria coding task at a fixed 4,096-token ceiling, 30 runs across three prompt conditions per model:

| model | empty content (whole budget spent reasoning) |
|---|---|
| Qwen3.6-35B-A3B | **28/30** |
| Laguna S 2.1 | 9/30 |

**Correction (2026-07-29, issue #17, @Blackwellboy, direct ceiling test, raw logs published):** the Qwen row is demand-above-ceiling truncation, not a degeneration loop. At the 4,096 ceiling (matching the table's 28/30 empty-content rate), the direct test's own 10 replicates were 10/10 cap-hits, 8/10 empty. At 8,192 it is 10/10 non-empty and criteria-valid with zero cap-hits, flat through 12,288 and 16,384. Reasoning demand plateaus at roughly 5.2 to 5.7K tokens median, with natural completion cost around 7K tokens. Every 4,096 cap-hit tail is non-degenerate: unique-line ratio 0.80 to 0.97, zlib compression ratio 0.31 to 0.38, ordinary mid-task reasoning, no loops. So for Qwen on this task, 4,096 was a stingy ceiling after all, and budget converts completely: raise the cap and the failure disappears.

Read the two rows differently as a result. The Qwen 28/30 is demand-above-ceiling truncation that converts fully at roughly double the budget. Degeneration loops remain real, but they are per-sample and stochastic rather than a fixed property of a model or a row: seen on the Laguna Q4_K_M cap-retry lane, where budget did not convert and one tail measured a 0.086 unique-line ratio, an actual loop, detectable by the same tail metrics used above.

Three consequences worth carrying into any benchmark harness:

1. **Score cap-hits with no extractable output as failures, not as excluded samples.** Dropping them inflates the score of exactly the arm that degenerates most, which is usually the thinking-on arm. **Bucket on "produced no usable output", never on `finish_reason` alone** (corrected 2026-07-28, after both testers who proposed the original rule retracted the bare form). A cap-hit that still emitted correct code is not a failure: one such case passed its tests twice. On one stack 22 runs had no extractable output while only 15 hit the ceiling, so the two criteria both over- and under-count relative to each other.
2. **Log the cap-hit rate per sample alongside the score.** A headline pass-rate that hides "one arm returned nothing 28 times out of 30" is not measuring what it claims to.
3. **Use a loop signal, the tail's unique-line ratio or compression ratio, to separate truncation from degeneration.** Never rely on `finish_reason` alone, and check this per model: the same 28/30-looking headline number meant something different for each row above. Also worth carrying: the demand is reasoning-demand-driven, not criteria-list-specific. At 12,288 tokens, constrained math tasks still cap 3/10 replicates, while JSON-schema and table-generation tasks whose natural reasoning runs only about 1.5 to 2K tokens never cap at all.

There is a related wire-level failure specific to agent loops: some servers reject an assistant message that has reasoning but neither content nor `tool_calls`, so a single capped turn kills the whole run silently and every retry fails identically. See the Laguna guide §5f.

Verified against published raw logs from an independent tester's runs (both lanes, per-sample), not from summary tables. The direct ceiling test that separates truncation from degeneration is also raw and published: https://github.com/Blackwellboy/laguna-s21-lab/tree/main/qwen-ceiling (issue #17, 2026-07-29).

## Your serving layer can decide the answer, and the default settings hide it

Established independently on three stacks and two serving layers (llama.cpp and vLLM) in one day, which is why it belongs here rather than in any one model's guide. **Identical requests can produce different results depending on what the server processed before them.**

Three known channels, all on the serving side rather than the model:

1. **Concurrent batched decoding.** Sequences decoding in one fused batch change batch shape, so reduction order, so floating-point rounding, so logits. At temperature 0 the sampler is argmax, so a near-tie flips and the divergence compounds through the KV cache. Measured: idle produced 1 distinct output in 4 runs; at 2 concurrent requests, **4 distinct in 6**, all differing from the idle baseline. Serialized (`-np 1`), **0 of 6** differed.
2. **Prefix cache reuse, enabled by default.** The same request served from a fresh full prefill is byte-stable across repeats; served from a warm prefix it returns different bytes. No restart, no concurrency, stock flags.
3. **Setting the disable flag is not sufficient.** On a second stack with the cache flag explicitly off, temp 0, single slot, the cold path was stable 3/3 and the warm path still diverged.

**It moves verdicts, not just bytes.** On a third stack, prefix-cache coverage tracked `finish_reason` with no overlap: every run at or below 79% cache hit returned `length` and ran to the cap generating invented content; every run at 99.8%+ returned `stop` with a correct short answer. That is a behavioral outcome flipping, not a token-level tie.

**What it invalidates.** Any A/B whose arms ran in separate runs, or sequentially against a shared server, is carrying this. A published reasoning-depth result was retracted for being a cross-run comparison: a large apparent effect measured across runs went flat (all pairwise p >= 0.13) once the arms were interleaved inside a single driver. The channels above are reasons cross-run comparisons are dangerous, not the established mechanism of that retraction; that lane ran a single driver at concurrency 1.

**The protocol that survives it:**
- **Interleave arms inside one run.** Never block them, never compare against a previously published cell.
- **Flush the slot between samples** rather than trusting the disable flag, and **run a cold control proving the flush actually isolates on your lane**.
- **Report four things, not one**: prefix-reuse setting, concurrency setting, flush procedure, and the isolation control.
- Prefer `-np 1` when you need determinism more than throughput.

**The judgment rule that came out of it, which generalizes further:** when a new noise source turns up, the question for each existing claim is whether it has a mechanism the noise cannot reach. One tester kept a finding with a deterministic template-render basis and withdrew a marginal p=0.041 cell from the same study, on the same day, from the same new evidence. Treating a new noise source as fatal to everything, or to nothing, are both wrong.

## Sources
Synthesized from internal behavioral testing across several models (Ornith-1.0-35B, Ornith-1.0-9B,
Qwopus-Coder thinking ablation, Qwen3.6-27B quantization comparison) plus the general finding that externalizing
reasoning substitutes for, rather than adds to, a model's internal working capacity, which independently
supports why thinking helps recall/deliberation but doesn't help (and can hurt) direct production work.
