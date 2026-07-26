#!/usr/bin/env python3
"""Confirmation run for the enable_thinking finding, hardened against the
confounds the first pass left open.

The first pass ran arms in blocks (all absent, then all false, then all true).
Block order cannot be separated from drift, warmup, or server-side state, and
the whole point of this run is that someone else may publish the result.

Changes from that pass:
  - arms INTERLEAVED round-robin, so drift hits every arm equally
  - multiple prompt shapes, so the result is not an artifact of one prompt
  - cache_prompt disabled and a unique nonce per request, so no reply can be
    served from a cached prefix
  - the deterministic /apply-template rendering recorded per arm alongside the
    sampled behaviour, so prompt-level and behaviour-level evidence sit together

The prompt-level rendering is the primary evidence: it involves no sampling.
The sampled arms exist to show the rendering has the behavioural consequence
it looks like it should.
"""

import argparse
import itertools
import json
import re
import time
import urllib.request
from pathlib import Path

PROMPTS = {
    "code-refactor": (
        "Refactor this Go function so the error is wrapped with context, and "
        "explain what you changed.\n\n"
        "func load(p string) ([]byte, error) {\n"
        "\tb, err := os.ReadFile(p)\n"
        "\tif err != nil {\n\t\treturn nil, err\n\t}\n"
        "\treturn b, nil\n}"
    ),
    "design-question": (
        "We store per-tenant config in one Postgres table with a tenant_id "
        "column. Traffic is growing. What are the trade-offs of splitting to "
        "schema-per-tenant?"
    ),
    "short-factual": (
        "In one sentence: what does the -race flag do in the Go toolchain?"
    ),
}

ARMS = {
    "absent": None,
    "false": {"enable_thinking": False},
    "true": {"enable_thinking": True},
}

THINK_MARKER = re.compile(r"</?think>", re.I)


def post(url, body, timeout):
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def rendered_tail(base, arm, timeout):
    """Deterministic: what the model is actually handed. No sampling."""
    body = {"messages": [{"role": "user", "content": "Say hi."}]}
    if ARMS[arm] is not None:
        body["chat_template_kwargs"] = ARMS[arm]
    try:
        p = post(base + "/apply-template", body, timeout).get("prompt", "")
    except Exception as exc:                                    # noqa: BLE001
        return f"ERROR: {type(exc).__name__}", None
    return p[-28:], p.rstrip().endswith("<think>")


def verdict(content, reasoning):
    if reasoning.strip():
        return "REASONED_PARSED"
    if THINK_MARKER.search(content):
        return "REASONED_UNPARSED"
    return "NO_REASONING"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, help="e.g. http://localhost:18080")
    ap.add_argument("--model", required=True)
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--temperature", type=float, default=0.6)
    ap.add_argument("--max-tokens", type=int, default=1400)
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--out", default="thinking-ab-verify.json")
    args = ap.parse_args()

    print("=== deterministic prompt rendering (no sampling) ===")
    render = {}
    for arm in ARMS:
        tail, opens = rendered_tail(args.base, arm, args.timeout)
        render[arm] = {"tail": tail, "ends_with_open_think": opens}
        print(f"  {arm:<8} tail={tail!r}  opens_think={opens}")

    # Interleave: every (prompt, seed) triple runs all three arms adjacently,
    # so any drift over the run is shared rather than assigned to one arm.
    plan = [(p, s, a)
            for s in range(args.seeds)
            for p in PROMPTS
            for a in ARMS]

    print(f"\n=== interleaved sampling: {len(plan)} requests ===")
    rows = []
    for i, (pname, seed, arm) in enumerate(plan, 1):
        # Unique nonce defeats any prefix cache even if cache_prompt is honoured
        # inconsistently; cache_prompt=false is belt and braces.
        body = {
            "model": args.model,
            "messages": [{"role": "user",
                          "content": f"{PROMPTS[pname]}\n\n(ref {seed}-{i})"}],
            "max_tokens": args.max_tokens,
            "temperature": args.temperature,
            "cache_prompt": False,
        }
        if ARMS[arm] is not None:
            body["chat_template_kwargs"] = ARMS[arm]
        t0 = time.time()
        try:
            d = post(args.base + "/v1/chat/completions", body, args.timeout)
            ch = d["choices"][0]
            content = ch["message"].get("content") or ""
            # Servers disagree on the field name: llama.cpp populates
            # reasoning_content, vLLM exposes reasoning. Reading only the first
            # makes every arm look like NO_REASONING on a vLLM lane, which is
            # this tool inventing the answer it exists to measure
            # (offlabel#8, @Blackwellboy).
            reasoning = (ch["message"].get("reasoning_content")
                         or ch["message"].get("reasoning") or "")
            finish = ch.get("finish_reason")
            v = verdict(content, reasoning)
        except Exception as exc:                                # noqa: BLE001
            content, reasoning, finish, v = f"ERROR: {exc}", "", "", "ERROR"
        dt = round(time.time() - t0, 1)
        print(f"  [{i:>2}/{len(plan)}] {pname:<15} {arm:<7} {v:<18} "
              f"{dt:>6}s reasoning={len(reasoning):>5} content={len(content):>5} "
              f"finish={finish}", flush=True)
        rows.append({"prompt": pname, "seed": seed, "arm": arm, "verdict": v,
                     "seconds": dt, "reasoning_chars": len(reasoning),
                     "content_chars": len(content), "finish_reason": finish,
                     "content": content, "reasoning": reasoning})
        Path(args.out).write_text(json.dumps(
            {"render": render, "results": rows}, indent=2) + "\n")

    print("\n=== per arm, all prompts pooled ===")
    print(f"  {'arm':<8} {'parsed':>7} {'unparsed':>9} {'none':>6} {'err':>4}  mean_reasoning")
    for arm in ARMS:
        rs = [r for r in rows if r["arm"] == arm]
        c = lambda v: sum(1 for r in rs if r["verdict"] == v)      # noqa: E731
        mr = sum(r["reasoning_chars"] for r in rs) / max(len(rs), 1)
        print(f"  {arm:<8} {c('REASONED_PARSED'):>7} {c('REASONED_UNPARSED'):>9} "
              f"{c('NO_REASONING'):>6} {c('ERROR'):>4}  {mr:>10.0f}")

    print("\n=== per prompt shape (is the effect prompt-specific?) ===")
    for pname in PROMPTS:
        line = f"  {pname:<15}"
        for arm in ARMS:
            rs = [r for r in rows if r["arm"] == arm and r["prompt"] == pname]
            n = sum(1 for r in rs if r["verdict"] == "REASONED_PARSED")
            line += f"  {arm}={n}/{len(rs)}"
        print(line)

    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
