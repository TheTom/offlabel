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

**It reproduces on a different model and family.** An independent rule-ablation run (@Defilan) put the same probe set to Qwen3.6-35B-A3B (Q8_0, llama.cpp/Metal): **4 folds with no clause, 0 folds with the integrity clause.** So this is worth treating as a *class* of blind spot to probe on any coding agent you hand a real repo, not a Laguna-specific defect.

**The mitigation generalizes too, and its shape is now known:** a short system-prompt integrity clause closes it. Rule-by-rule ablation across two models found the "never rewrite history to hide secrets / never backdate or forge" rule is **load-bearing** (dropping it also degrades the separate hazard-disclosure probe, so the rules are not cleanly separable), while the "don't certify what you can't support" rule is droppable **if something external already verifies the model's status claims** and worth keeping if nothing does. Clause text and the full ablation live in the Laguna guide (§5b).

**The testing lesson:** ask for the violation twice, once blatant and once as housekeeping. A model that refuses the first and accepts the second looks safe on any battery that only asks the blatant version.

## A heavily quantized model is not a usable judge

If you use an LLM to grade behavioral outputs, the grader's quantization matters as much as the worker's. A 3.25bpw hybrid asked to grade integrity transcripts returned "held the line" on 19 of 21 and then 21 of 21 responses, including ones that handed over `git rebase -i` and `git commit --amend --author=` with no objection at all. The same model is perfectly usable as a worker.

The failure is asymmetric and it is the dangerous direction: a grader that says yes to everything does not merely add noise, it **launders a bad result as a verified one**. Pair this with the general rule that a check which cannot fail proves nothing, and the practical guidance is: grade with a full-precision or lightly quantized model, on different hardware than the worker, and read the disagreements rather than the agreement rate.

## An empty response at a token cap is a failure, not a truncation

A reasoning model that hits its per-turn token ceiling *inside* the reasoning block returns **no answer at all**: full reasoning field, empty content. The instinct is to read this as "the budget was too small" and raise it. Usually it is the opposite, a degeneration loop that more budget would only feed.

Measured on a six-requirement acceptance-criteria coding task at a fixed 4,096-token ceiling, 30 runs across three prompt conditions per model:

| model | empty content (whole budget spent reasoning) |
|---|---|
| Qwen3.6-35B-A3B | **28/30** |
| Laguna S 2.1 | 9/30 |

Not wrong answers. No answer. 4,096 is not a stingy ceiling for that task, and the same request under a lower apparatus dose completes fine, which is what separates a loop from a genuine truncation.

Two consequences worth carrying into any benchmark harness:

1. **Score cap-hits as failures, not as excluded samples.** Dropping them inflates the score of exactly the arm that degenerates most, which is usually the thinking-on arm.
2. **Log the cap-hit rate per sample alongside the score.** A headline pass-rate that hides "one arm returned nothing 28 times out of 30" is not measuring what it claims to.

There is a related wire-level failure specific to agent loops: some servers reject an assistant message that has reasoning but neither content nor `tool_calls`, so a single capped turn kills the whole run silently and every retry fails identically. See the Laguna guide §5f.

Verified against published raw logs from an independent tester's runs (both lanes, per-sample), not from summary tables.

## Sources
Synthesized from internal behavioral testing across several models (Ornith-1.0-35B, Ornith-1.0-9B,
Qwopus-Coder thinking ablation, Qwen3.6-27B quantization comparison) plus the general finding that externalizing
reasoning substitutes for, rather than adds to, a model's internal working capacity, which independently
supports why thinking helps recall/deliberation but doesn't help (and can hurt) direct production work.
