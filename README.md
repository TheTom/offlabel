# offlabel

**Benchmarks tell you if a model can solve the problem. They don't tell you what it's like to drive.**

`offlabel` is a set of per-model *operating guides*: practical, evidence-backed notes on how a model actually
behaves once you're past the leaderboard: does it hold a line under pressure or fold? Does thinking mode help
or quietly sabotage the answer? Will it over-refuse benign work, or under-refuse risky work? Does it stay honest
across a long multi-turn task, or capitulate to a false premise and then paper over it?

None of that shows up in a pass@1 number. It shows up when you actually use the thing. This repo is the
"actually use the thing" notes, written down so you don't have to rediscover them yourself.

## The cards

Every model gets a shareable **card**: an at-a-glance infographic with the operating dials (thinking, tools,
sampling) and a green/red **Trust Map** of where it holds vs folds under pressure. Full write-up in each guide.

<p align="left">
  <a href="models/muse-glimmer-30b.md"><img src="cards/img/muse-glimmer-30b.png" width="270" alt="Muse Glimmer 30B offlabel card"></a>
  <a href="models/laguna-s-2.1.md"><img src="cards/img/laguna-s-2.1.png" width="270" alt="Laguna S 2.1 offlabel card"></a>
  <a href="models/ornith-1.0-35b.md"><img src="cards/img/ornith-1.0-35b.png" width="270" alt="Ornith-1.0-35B offlabel card"></a>
  <a href="models/ornith-1.0-9b.md"><img src="cards/img/ornith-1.0-9b.png" width="270" alt="Ornith-1.0-9B offlabel card"></a>
  <a href="models/qwen3.6-27b.md"><img src="cards/img/qwen3.6-27b.png" width="270" alt="Qwen3.6-27B offlabel card"></a>
</p>

**Gemma 4 family** (per-size, because each size behaves differently, see the [family overview](models/gemma-4-family.md)):

<p align="left">
  <a href="models/gemma-4-e2b.md"><img src="cards/img/gemma-4-e2b.png" width="200" alt="Gemma 4 E2B offlabel card"></a>
  <a href="models/gemma-4-e4b.md"><img src="cards/img/gemma-4-e4b.png" width="200" alt="Gemma 4 E4B offlabel card"></a>
  <a href="models/gemma-4-12b.md"><img src="cards/img/gemma-4-12b.png" width="200" alt="Gemma 4 12B offlabel card"></a>
  <a href="models/gemma-4-26b-a4b.md"><img src="cards/img/gemma-4-26b-a4b.png" width="200" alt="Gemma 4 26B-A4B offlabel card"></a>
  <a href="models/gemma-4-31b.md"><img src="cards/img/gemma-4-31b.png" width="200" alt="Gemma 4 31B offlabel card"></a>
</p>

## Why usage guidance and not another benchmark

Static benchmarks assume a model is a fixed function: same input, same output, one true score. Modern models
break that assumption. They're non-deterministic, many public benchmarks are contamination-prone, and the
axes that matter for actually deploying a model (integrity under pressure, sycophancy, calibration, multi-turn
coherence, tool reliability) are mostly untested by standard leaderboards. A model can look great on a
benchmark and still be the wrong tool for your task, or the right tool used the wrong way (wrong sampling
config, thinking mode left on when it should be off, wrong harness for its tool-calling format).

Each guide here is built from **held-out, hands-on behavioral testing**: scenarios the model hasn't seen
before, run head-to-head against a trusted baseline where possible, plus direct observation of how the model
behaves in practice. It's opinionated and specific: we tell you what to do differently, not just what the
model scored.

## How to read a guide

Every file in `models/` follows the same shape (see `TEMPLATE.md` for the full spec):

- **Cheat sheet**: five lines, top of the file: what to reach for it, what to avoid, thinking policy, tool/agent
  fit, and the sharpest trust boundary.
- **Numbered sections**: envelope (best-at / not-for), thinking policy with dose-response where we have it,
  prompting/persona notes, tools & agents, sampling & serving, and the trust map (what it holds the line on vs.
  what it folds on under pressure).
- **Confidence & scope on every claim**: how much testing backs it and what config (quant/build/date) it was
  tested on, so guidance doesn't outlive its evidence. Untested axes are marked `⬚ backlog`, not silently
  assumed.

Every guide also has a matching card in `cards/<name>.html`: a single shareable infographic (see
`cards/_reference.html` for the exact layout to clone; `brand.md` for the palette). The card is the
80/20 summary: cheat sheet + trust map in one image. The guide is the full case.

## The 10-axis behavioral map

Every guide and every card is scored against the same ten axes, so models are comparable across the whole set
instead of each write-up inventing its own frame:

| # | Axis | What it answers |
|---|---|---|
| 1 | **Vibe & voice** | personality, tone, writing style, weird habits |
| 2 | **Refusal calibration** | over-refusal (blocks benign work) vs under-refusal (allows risky work) |
| 3 | **Sycophancy & spine** | pushes back vs capitulates/flatters; false-premise resistance; integrity under pressure |
| 4 | **Hallucination & calibration** | invents facts/bugs; expresses uncertainty vs overconfident; declines unknowables |
| 5 | **Instruction-following & coherence** | sticks to system prompt/format; multi-turn drift |
| 6 | **Thinking / reasoning** | control, dose-response (helps/hurts per axis), token cost |
| 7 | **Tools & agents** | native vs generic harness fit, tool-arg reliability, loop/recovery |
| 8 | **Bias & fairness** | political/cultural/etc. systematic leanings |
| 9 | **Jailbreak / safety robustness** | filter-bypass resistance |
| 10 | **Serving & config** | sampling, quant, serving gotchas |

Coverage per axis is tagged **✅ measured** (formally scored head-to-head), **🟡 observational** (noted from use,
not formally scored), or **⬚ backlog** (not tested yet, we say so instead of guessing).

## Cross-model lessons

Recurring patterns that show up across more than one model (thinking-mode trade-offs, RL-training artifacts,
quantization fidelity, etc.) live in `patterns.md` so they don't get re-derived per guide.

## Scope & honesty

Every guide names its scope: what quant/build/date it was tested on, and what was *not* tested. Guidance here
is a snapshot, not a permanent verdict. Models get patched, fine-tuned, and re-quantized, and a guide gets a
changelog entry when it's re-verified. If a guide's behavioral data is thin, its card says so (`DRAFT` in the
footer), better an honest draft than false confidence.

## Support

If you find offlabel useful, you can support it via [GitHub Sponsors](https://github.com/sponsors/TheTom) or BTC:

BTC: bc1qsfaaf6mkz2yxx2vavg2n0zgsf3qj25uh94t83rwuq7de67dey05sc3tgjx

**Commercial support:** For behavioral model evaluation, red-teaming, or fine-tune assessment engagements, DM [@no_stp_on_snek](https://x.com/no_stp_on_snek) on X.

## License

Apache License 2.0, see [LICENSE](LICENSE).

Copyright 2026 Tom Turney.
