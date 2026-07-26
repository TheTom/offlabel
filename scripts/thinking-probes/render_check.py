#!/usr/bin/env python3
"""Compare what a chat template renders for each value of a template kwarg.

This is the cheapest and most decisive check in this directory, because it
involves no sampling: llama.cpp's /apply-template returns the formatted prompt
without generating, so the answer is deterministic and repeats exactly.

It exists because reading a template is not the same as measuring it. A template
can carry `{%- set enable_thinking = enable_thinking | default(false) -%}` and
still be handed `true` by the server on every request where the client omits the
kwarg, which makes the default unreachable. That is only visible in the rendered
output, and it is what a whole wrong conclusion rested on for us (offlabel#5).

With --template, it also renders the same file locally in stock jinja2 and diffs
the two. Server and local agreeing means the template decides. Disagreeing means
the server is supplying the value itself, which is the interesting case.
"""

import argparse
import itertools
import json
import re
import urllib.request
from pathlib import Path

MESSAGES = [{"role": "user", "content": "Say hi."}]

# {% generation %} / {% endgeneration %} are a HuggingFace assistant-masking
# extension that stock jinja2 cannot compile. They do not affect the branches
# this tool inspects, so they are stripped for the local render only.
GENERATION_TAG = re.compile(r"\{%-?\s*(end)?generation\s*-?%\}")


def server_render(base, kwarg, value, timeout):
    body = {"messages": MESSAGES}
    if value is not None:
        body["chat_template_kwargs"] = {kwarg: value} if value != {} else {}
    req = urllib.request.Request(
        base.rstrip("/") + "/apply-template",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r).get("prompt", "")


def local_render(path, kwarg, value):
    try:
        from jinja2 import Environment
    except ImportError:
        return None
    src = GENERATION_TAG.sub("", Path(path).read_text(encoding="utf-8"))
    tmpl = Environment().from_string(src)
    kw = {} if value is None else {kwarg: value}
    return tmpl.render(messages=MESSAGES, add_generation_prompt=True, **kw)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True,
                    help="llama.cpp server root, e.g. http://localhost:8080")
    ap.add_argument("--kwarg", default="enable_thinking",
                    help="chat template kwarg to vary (default enable_thinking)")
    ap.add_argument("--template", default="",
                    help="optional path to the .jinja file, to also render it "
                         "locally in stock jinja2 and compare")
    ap.add_argument("--tail", type=int, default=30,
                    help="characters of the rendered tail to display")
    ap.add_argument("--timeout", type=int, default=60)
    args = ap.parse_args()

    # "absent" sends no chat_template_kwargs at all, which is the arm that shows
    # what the server does when the client says nothing. It is the one most
    # people never test, and the one most people actually run in production.
    arms = [("absent", None), ("empty-kwargs", {}), ("false", False), ("true", True)]

    print(f"=== server render ({args.kwarg}) ===")
    server = {}
    for label, value in arms:
        try:
            server[label] = server_render(args.base, args.kwarg, value, args.timeout)
        except Exception as exc:                                # noqa: BLE001
            print(f"  {label:<13} ERROR {type(exc).__name__}: {exc}")
            continue
        tail = server[label][-args.tail:].replace("\n", "\\n")
        print(f"  {label:<13} len={len(server[label]):>5}  tail={tail!r}")

    print("\n=== which arms render identically? ===")
    for a, b in itertools.combinations(sorted(server), 2):
        same = server[a] == server[b]
        mark = "identical" if same else "DIFFERENT"
        print(f"  {a:<13} vs {b:<13} {mark}")

    if args.template:
        print("\n=== local jinja2 render of the same template ===")
        local = {}
        for label, value in arms:
            if label == "empty-kwargs":
                continue          # identical to absent locally by construction
            out = local_render(args.template, args.kwarg, value)
            if out is None:
                print("  jinja2 not installed, skipping local render")
                break
            local[label] = out
            tail = out[-args.tail:].replace("\n", "\\n")
            print(f"  {label:<13} tail={tail!r}")

        if local:
            print("\n=== server versus local, per arm ===")
            for label in local:
                if label not in server:
                    continue
                agree = server[label][-args.tail:] == local[label][-args.tail:]
                note = "template decides" if agree else "SERVER OVERRIDES TEMPLATE"
                print(f"  {label:<13} {note}")
            print("\n  Any arm marked SERVER OVERRIDES TEMPLATE means the server")
            print("  supplies that kwarg itself, so the template's default for it")
            print("  never runs. Do not reason about behaviour from the template")
            print("  alone in that case.")


if __name__ == "__main__":
    main()
