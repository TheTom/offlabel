# DeepSeek-V4.1-Flash-1017 EXL3 2.9 bpw in Harness 0.2.1-rc.2

Status: observational case study, 2026-10-21. One feature, one implementation lineage, several human-relayed review rounds. No controlled model comparison or prompt ablation.

**Useful for supervised implementation and concrete repairs. Give verification its own deliverable, inspect the assertions, and define when review ends.**

## Deployment scope: verified configuration, incomplete historical attribution

This is an actively maintained observational workflow study, not a completed model benchmark. Configuration inspected on 2026-10-21:

| Component | Observed configuration |
|---|---|
| Base model | [DeepSeek-V4.1-Flash-1017](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017) |
| Quant | EXL3, average trunk weights 2.9 bpw; head 6 bpw; MTP 4 bpw; `mul1` codebook; output scales `always` |
| Quantizer metadata | exllamav3 1.6.2; calibration 250 rows x 2,048 tokens |
| Weights | Quant README reports 43 safetensors shards, 210.7 GB excluding Engram tables; no complete weight fingerprint verified in this study |
| Harness | Installed DeepSeek Harness desktop **0.2.1-rc.2**, macOS arm64; app plist and bundled runtime manifest agree |
| Runtime payload | `723702fcd685d991ab5dbfcb69af5bc368213f68c541c73bdda253b0ddf1beaa` |
| Serving | TensorFold, local image tag `8e0966e`; image ID `sha256:3ffa99c6b950ba3afdae6361fec661fa9606ed9af5d483e0c821df886be6d5f0` |
| Hardware | Two DGX Sparks, tensor parallelism 2 |
| Observed server settings | Context 1,048,576; parallel 4; MTP drafts 5; vision enabled. These are configuration observations, not qualified capability/performance claims |
| Lead-agent profile | `deepseek-v4.1-flash`, reasoning effort `high`, configured output ceiling 32,768 tokens |

The quant parameters were read from the mounted model config, the base identity from its README, and the serving settings from the running process. A verified quant download URL, pinned weight revision, engine source SHA and effective sampling settings remain outstanding. A container tag is not proof of a source SHA.

**Historical attribution limit:** installed version and current profile are not per-turn runtime receipts. The operator identified the implementation worker as DeepSeek. The desktop profile also supports routing fresh teammates to another model. The complete historical agent tree and per-agent model assignments have not been audited; results below describe a DeepSeek-led assisted workflow, not isolated DeepSeek capability. The manual desktop workflow is also distinct from a headless delegation bridge. Keep those lanes separate.

Do not apply the older V4-Flash-0731 guides' sampling or thinking recommendations to this deployment without a matched test.

## Use it like this

| Decision | Guidance from this case |
|---|---|
| Assignment | One implementation package or one invariant to investigate, with relevant context and an explicit output |
| Repair | Supply the reproduction and the violated general rule; ask for related transition cases |
| Verification | Derive expected values outside production code; demonstrate that the same check rejects a deliberate wrong result |
| Review ownership | A separate reviewer checks source, runs probes and decides whether the bounded gate passed |
| Completion | Report implementation, executed checks, independent review and usefulness qualification separately |
| Stop | Once named integrity gates pass, proceed to usefulness testing; do not demand a fresh defect every round |

## An anonymized implementation and review sequence

The task was a session-history store with explicit imports, temporal recall, evidence citations, scoped access and archival. Its PRD already specified staged work, independent oracles and failure controls. The operator pasted the PRD into Harness, then relayed implementation reports and independent Codex review feedback between sessions.

Counts below are the reviewer's recorded executions, except the explicitly identified evidence inspection. They are not model scores or independent task samples.

| Revision | Evidence and review outcome |
|---|---|
| `R1` | Reviewer ran 135 continuity tests. Five additional findings: purged bytes recreated on rejected replay, shared-source purge damage, scope-crossing PR deduplication, missing normal startup wiring, and archive storage not retired. |
| `R2` | Original cases passed; reviewer ran 146 continuity and 70 impacted tests. Seven further findings included wrong source text marked verified, interrupted-generation loss, unauthorized source references, excluded content retained, native-ID collisions, plaintext after purge, and unstable content hashes. |
| `R3` | Reviewer confirmed the seven probes now behaved correctly and ran 154 plus 70 tests. The source-binding and generation design improved. Four remaining findings concerned real historical upgrades, archive/purge races, revocation outside the write transaction, and missing purge invalidation. |
| `R4` | Worker reported those fixes and 168 continuity tests. A separate session ran 14 new tests successfully. Evidence inspection found weak source assertions, simulated historical states, and a lower-level transition test described more broadly than it exercised. The reviewer demonstrated that swapped records passed the letter-based oracle. |
| `R5` | Tests/documentation-only follow-up. Reviewer ran 173 continuity and 70 impacted tests, with no skips in that continuity run. Exact fixture-byte oracles rejected swaps; actual historical implementations generated upgrade inputs; the full archive path used a second writer and reopen/recovery/retry checks. The bounded evidence gate passed. |

The last review recommended an isolated usefulness trial. It did not approve deployment or establish production readiness. A separately tracked global-revision contention limitation remained; its mechanism was not re-audited for this case study.

## Later retrieval qualification: identity is only part of the answer

A subsequent operator-relayed review reported 174 passing tests while a structured-retrieval check still accepted an invalid source association and an unknown outcome for every created-PR result. That report was not independently rerun for this article. The proposed oracle repair checks exact entity identities and multiplicities, expected source-event associations, outcome classes, and exact resolved source bytes.

The proposed negative controls include a valid reference to the wrong event and a duplicate result replacing another expected result while preserving the count. Each mutation must fail the same oracle as the positive case for the intended semantic reason. These checks were requested; their completion is not established here.

This narrows the earlier pass: a bounded storage/evidence gate can pass while a later retrieval-qualification gate remains incomplete. It also gives readers another practical rule: check the relationship between records, not only whether each record looks valid on its own.

## What improved with feedback

The worker implemented meaningful functionality, repaired concrete reproductions, and accepted a source-identity/archive-generation correction. Later it respected a tests-and-documentation-only assignment and produced stronger evidence without changing production behavior. These are observations of useful supervised work.

The final round is particularly informative: verification became a separately scoped task with explicit deliverables. It required exact expected bytes, a swapped-source negative control, historical generators and the full consumer path. The reviewer could then give a bounded pass instead of asking for indefinite scrutiny.

This does not isolate the effect of prompt wording. The worker also received failing examples, design advice, more time and accumulated context. The demonstrated result belongs to the whole assisted workflow.

## Where its reports outran the evidence

- **A passing example became a broad contract claim.** Sequential correctness did not establish behavior during purge, revocation or interrupted publication. Test the transitions with deterministic interruption points and independent connections.
- **The oracle was weaker than its description.** Checking whether A, B or C occurred anywhere in returned uppercase text did not prove exact recovery. The independent reviewer showed all three wrong-record substitutions passed. Compare exact fixture-derived values and validate the checker with a known-bad substitution.
- **Simulated history became historical qualification.** Rewriting a current database into an older shape is useful coverage, but does not replace running the actual old implementation. Preserve both and label them separately.
- **A test action became automatic product behavior.** The final handoff said reopening removed abandoned staging. The test explicitly called `recover_staging` after reopening. Record which actor invoked recovery and through which entry point. No production startup defect is established by this wording correction alone.
- **Independence was ambiguous.** An independently derived oracle, another database connection, a worker-authored probe and a separate reviewer are different properties. Name each precisely.

An error return is also insufficient evidence of no side effects: an earlier import raised an access error after retaining forbidden bytes. Inspect durable state and consumer-visible revisions as well as return values.

## Ask it this way

For an investigation:

```text
Investigate one invariant: [contract]. Established context: [revision, paths,
accepted decisions, prior checks]. Use synthetic temporary state only.

Deliver one executable counterexample or a bounded account of unsuccessful
attempts. Define expected state independently of the implementation. Exercise
[relevant transition] at a deterministic boundary. Report retained state,
references, receipts and consumer-visible effects.

A defect is not required. Do not change production code in this assignment.
State exactly what the experiment establishes and leaves untested.
```

For an evidence repair:

```text
Keep the accepted architecture. Change only the tests and receipt needed to
establish [named claims]. Use fixture-derived expectations and prove the same
oracle rejects [deliberate wrong result]. Distinguish simulated state from
historical fixtures, direct helper calls from the real entry point, and manual
recovery from automatic startup behavior.

Report commands, revision, skips, observed output and limitations. Missing
historical revisions mean incomplete historical qualification. Stop after these
checks; report any newly exposed production defect before expanding scope.
```

These are reusable patterns motivated by this case, not validated optimal prompts. Keep repository instructions and authorization boundaries in every actual assignment.

## The stopping rule matters

The reviewer should be able to return a pass. At `R5`, two small clarifications remained: explicitly invoked recovery and full historical SHA/skip handling. Neither justified restarting storage design.

The next question is whether recall helps answer real questions. Freeze an offline corpus and independent question ledger; measure retrieval coverage, citations, classification, omissions, latency and response size. If inference is authorized and available, compare retrieval off, explicit retrieved evidence and gold evidence under matched conditions. A corpus with zero real PR creations cannot qualify real PR-creation recall. Keep synthetic coverage separate.

Missing usefulness evidence is a different qualification gap from storage corruption. A passing integrity suite proves neither answer quality nor deployment readiness.

## Coverage and limits

| Offlabel axis | Coverage here |
|---|---|
| Vibe/voice | Observational: polished completion reports sometimes exceeded their evidence |
| Refusal calibration | Backlog |
| Sycophancy/spine | Backlog; no controlled pressure test |
| Hallucination/calibration | Observational: claim-to-assertion mismatches, corrected with review |
| Instruction-following | Observational: bounded repair and tests-only scope followed |
| Thinking/reasoning | Backlog; no effort ablation |
| Tools/agents | Observational: implementation and repair through Harness; no native-versus-generic comparison |
| Bias/fairness | Backlog |
| Jailbreak/safety | Backlog |
| Serving/config | Configuration observation only; no causal serving experiment |

No comparative model ranking, success rate, cost saving, exhaustive concurrency claim or recommendation to change reasoning settings follows from this sequence. Test counts increased while test content and code changed. They cannot be treated as an improvement curve for model capability.

## Evidence access and reproducibility limits

The source material is operator-relayed worker handoffs, separate reviewer reports, and direct test/source inspection in a session-history project. The authoring session directly ran the 14 new tests at R4. The 173/70 results at R5 are attributed to the separate reviewer, not rerun while writing this article. Project identifiers, private transcripts, machine paths and project commit IDs are omitted intentionally; R1 through R5 are local labels for successive revisions, not public benchmark versions.

The underlying private evidence is not packaged for public reproduction. Readers can reuse the methodology and prompts, but cannot independently reproduce the historical counts from this document alone. The reported counts therefore remain observational evidence. No positive outcome, refusal score or pressure-resistance score is inferred for untested axes.

## Work in progress

- Verify the exact downloadable quant revision and a weight manifest fingerprint.
- Audit historical Harness versions and lead/teammate model assignments.
- Publish standalone synthetic examples of weak versus exact oracles without project data.
- Complete an offline usefulness trial; distinguish retrieval quality from answer quality.
- Measure supervisor repair effort and total elapsed cost before making efficiency claims.
- Add held-out prompt comparisons, including correct implementations where no defect should be reported.

Future experiments: several held-out tasks including correct implementations; concise assignment versus long checklist; fresh verifier versus continued author session; reasoning-effort ablation only after effective settings are verified. Interleave arms, hold budgets/tools constant, record serving contention and cache conditions, and score real reproductions, false accusations, usable deliverables and supervisor repair effort. Known failures from this case are development examples, not held-out evaluation cases.

Related: [cross-model patterns](../patterns.md), [Muse calibration and clause costs](../models/muse-glimmer-30b.md), [Laguna harness findings](../models/laguna-s-2.1.md), [older DeepSeek DwarfStar guide](../models/deepseek-v4-flash-0731-ds4.md).

## Changelog

- 2026-10-21: initial observational workflow case study through R5; bounded integrity/evidence review passed, usefulness still unqualified.
