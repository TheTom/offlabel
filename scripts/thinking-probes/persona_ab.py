#!/usr/bin/env python3
"""Re-measure the persona effect against a baseline we have actually measured.

The original persona result (6/6 fired without a persona, 0/5 with) was taken
in the enable_thinking-absent condition, on one prompt, in blocks. We since
established that the absent condition reasons only about half the time and
that task shape moves it a lot, so the old baseline was not the near-certainty
it looked like. The effect may well be real; the effect SIZE was measured
against a constant that is not constant.

This crosses the two factors instead of holding one at an assumed value:

    persona   in {none, senior-staff-engineer}
    kwarg     in {absent, false}

The false rows are the control. Thinking is structurally unavailable there, so
persona must show no effect; if it appears to, the measurement is broken rather
than the persona being powerful.

Interleaved across all four cells, three prompt shapes, cache disabled, unique
nonce per request, for the same reasons as thinking_ab.py.
"""

import argparse
import json
import re
import time
import urllib.request
from pathlib import Path

PERSONA = "You are a senior staff software engineer."

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

CELLS = [
    ("no-persona", "absent"),
    ("persona", "absent"),
    ("no-persona", "false"),
    ("persona", "false"),
]

THINK_MARKER = re.compile(r"</?think>", re.I)


def post(url, body, timeout):
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--seeds", type=int, default=6)
    ap.add_argument("--temperature", type=float, default=0.6)
    ap.add_argument("--max-tokens", type=int, default=1400)
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--out", default="persona-verify.json")
    args = ap.parse_args()

    plan = [(p, s, persona, kwarg)
            for s in range(args.seeds)
            for p in PROMPTS
            for (persona, kwarg) in CELLS]

    print(f"=== {len(plan)} requests, 4 cells interleaved ===", flush=True)
    rows = []
    for i, (pname, seed, persona, kwarg) in enumerate(plan, 1):
        msgs = []
        if persona == "persona":
            msgs.append({"role": "system", "content": PERSONA})
        msgs.append({"role": "user",
                     "content": f"{PROMPTS[pname]}\n\n(ref {seed}-{i})"})
        body = {
            "model": args.model, "messages": msgs,
            "max_tokens": args.max_tokens, "temperature": args.temperature,
            "cache_prompt": False,
        }
        if kwarg == "false":
            body["chat_template_kwargs"] = {"enable_thinking": False}

        t0 = time.time()
        try:
            d = post(args.base + "/v1/chat/completions", body, args.timeout)
            ch = d["choices"][0]
            content = ch["message"].get("content") or ""
            reasoning = ch["message"].get("reasoning_content") or ""
            finish = ch.get("finish_reason")
            reasoned = bool(reasoning.strip()) or bool(THINK_MARKER.search(content))
        except Exception as exc:                                # noqa: BLE001
            content, reasoning, finish, reasoned = f"ERROR: {exc}", "", "", None
        dt = round(time.time() - t0, 1)
        print(f"  [{i:>2}/{len(plan)}] {pname:<15} {persona:<10} tk={kwarg:<6} "
              f"reasoned={str(reasoned):<5} {dt:>6}s reasoning={len(reasoning):>5}",
              flush=True)
        rows.append({"prompt": pname, "seed": seed, "persona": persona,
                     "kwarg": kwarg, "reasoned": reasoned, "seconds": dt,
                     "reasoning_chars": len(reasoning),
                     "content_chars": len(content), "finish_reason": finish,
                     "content": content, "reasoning": reasoning})
        Path(args.out).write_text(json.dumps(rows, indent=2) + "\n")

    print("\n=== reasoned rate per cell ===")
    print(f"  {'persona':<11} {'kwarg':<7} {'reasoned':>10}  mean_reasoning_chars")
    for persona, kwarg in CELLS:
        rs = [r for r in rows if r["persona"] == persona and r["kwarg"] == kwarg
              and r["reasoned"] is not None]
        n = sum(1 for r in rs if r["reasoned"])
        mr = sum(r["reasoning_chars"] for r in rs) / max(len(rs), 1)
        print(f"  {persona:<11} {kwarg:<7} {n:>4}/{len(rs):<5} {mr:>18.0f}")

    print("\n=== persona effect WITHIN the absent arm, per prompt shape ===")
    for pname in PROMPTS:
        line = f"  {pname:<15}"
        for persona in ("no-persona", "persona"):
            rs = [r for r in rows if r["persona"] == persona
                  and r["kwarg"] == "absent" and r["prompt"] == pname
                  and r["reasoned"] is not None]
            n = sum(1 for r in rs if r["reasoned"])
            line += f"  {persona}={n}/{len(rs)}"
        print(line)

    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
