# Thinking probes

Three tools for measuring **whether a model actually reasons**, and what
controls it, on an OpenAI-compatible endpoint.

Separate from `spine-probes/`, which measures integrity behaviour. Different
question, same house rules: standard library only, no install step, every raw
response saved.

These exist because of a wrong result. We reported that the `enable_thinking`
chat-template kwarg was inert on Laguna S 2.1, reasoning from the template
source, which sets `| default(false)`. The template was read correctly. The
conclusion was still wrong, because the server supplies that kwarg itself when
the client omits it, so the default never runs. See
[#5](https://github.com/TheTom/offlabel/issues/5) for the full correction.

Two habits came out of that and are baked into these tools.

**Reading is not measuring.** `render_check.py` inspects rendered output rather
than template source, and needs no statistics to do it.

**A finding needs a cell where it cannot happen.** Both sampling tools include a
control arm where the effect is structurally impossible. If the effect shows up
there anyway, the instrument is broken and every other number is suspect.

## `render_check.py`: what the template actually renders

The cheapest and most decisive check here. `/apply-template` returns the
formatted prompt without generating, so it is deterministic and repeats exactly.

```bash
python3 render_check.py --base http://localhost:8080
```

It varies one kwarg across four arms (absent, empty object, `false`, `true`) and
reports which arms render identically. **Test the absent arm.** It is the one
most people never check and the one most people actually run.

Point it at the template file as well and it renders the same file in stock
jinja2 and compares:

```bash
python3 render_check.py --base http://localhost:8080 \
  --template models/templates/poolside-Laguna-S-2.1.jinja
```

An arm reported as `SERVER OVERRIDES TEMPLATE` means the server is supplying
that kwarg itself. In that case the template's default for it is unreachable,
and reasoning about behaviour from the template alone will mislead you. That is
exactly the trap we fell into.

Use `--kwarg` for anything other than `enable_thinking`.

## `thinking_ab.py`: does the rendering change behaviour

Interleaved sampling across the same arms, to confirm the rendering has the
consequence it looks like it should.

```bash
python3 thinking_ab.py --base http://localhost:8080 --model my-model --seeds 5
```

Classifies each response three ways, which is the distinction a single field
cannot make:

| signal | verdict |
|---|---|
| `reasoning_content` non-empty | `REASONED_PARSED` |
| `<think>` markers in content | `REASONED_UNPARSED` |
| neither | `NO_REASONING` |

`REASONED_UNPARSED` is the important one. Any occurrence means a stack reading
only `reasoning_content` would report that arm as not firing when it did, so a
published firing rate from such a stack is measuring the parser as much as the
model.

## `persona_ab.py`: does a system prompt change it

Crosses a persona system prompt against the kwarg, four cells:

```bash
python3 persona_ab.py --base http://localhost:8080 --model my-model --seeds 6
```

The two `false` cells are the control. Thinking is structurally unavailable
there, so the persona must show no effect. If it appears to, stop and fix the
measurement before believing the other two cells.

## Design notes, and one warning

Both sampling tools interleave arms round robin, vary the prompt across three
shapes, send `cache_prompt: false` with a unique nonce per request, and hold
`max_tokens` fixed across every arm with no retry.

That is not fussiness. Our first pass ran arms in blocks, on one repeated
prompt, with the cache on, and produced 5/5 in one arm against 0/5 in another.
It was mostly an artifact. **Manufactured consistency looks exactly like a
strong result**, and no amount of staring at the numbers reveals it.

Vary the token budget across arms and you have the same problem in another form:
a difference in outcomes that cannot be attributed to the variable you meant to
test.

Task shape moves these numbers a lot, so the per-shape breakdown in the output
is worth reading before drawing a conclusion from the pooled figure.
