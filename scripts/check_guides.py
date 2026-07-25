#!/usr/bin/env python3
"""Lint offlabel guides. Run: python3 scripts/check_guides.py

Checks:
  1. Every models/*.md has parseable YAML frontmatter. (An unquoted value
     containing ': ' silently breaks GitHub's renderer, which is how this
     script came to exist.)
  2. Required frontmatter keys are present.
  3. No em-dashes or en-dashes anywhere in tracked .md / cards .html (house rule).
"""
import re
import subprocess
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required: pip install pyyaml")

REQUIRED = ["model", "vendor", "hf", "tested_on", "status", "verdict"]
DASHES = ("—", "–")  # em, en


def tracked(pattern):
    """Only lint git-tracked files, so unpublished local drafts don't fail CI."""
    out = subprocess.run(
        ["git", "ls-files", pattern], capture_output=True, text=True, check=True
    ).stdout.split()
    return sorted(out)


errors = []

for path in tracked("models/*.md"):
    text = open(path, encoding="utf-8").read()
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        errors.append(f"{path}: missing YAML frontmatter block")
        continue
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        first = str(exc).splitlines()[0]
        errors.append(
            f"{path}: frontmatter is not valid YAML ({first}). "
            "A value containing ': ' must be quoted."
        )
        continue
    if not isinstance(data, dict):
        errors.append(f"{path}: frontmatter did not parse to a mapping")
        continue
    for key in REQUIRED:
        # A "-family" page is an overview that aggregates per-size guides, each of
        # which carries its own hf link, so it has no single upstream repo.
        if key == "hf" and path.endswith("-family.md"):
            continue
        if not data.get(key):
            errors.append(f"{path}: frontmatter missing required key '{key}'")

for path in tracked("*.md") + tracked("cards/*.html"):
    text = open(path, encoding="utf-8").read()
    for dash in DASHES:
        if dash in text:
            line = text[: text.index(dash)].count("\n") + 1
            name = "em-dash" if dash == "—" else "en-dash"
            errors.append(f"{path}:{line}: contains {name} (house rule: use : , or .)")
            break

if errors:
    print("FAIL")
    for err in errors:
        print(f"  {err}")
    sys.exit(1)

print("OK: all guides have valid frontmatter, required keys, and no em/en-dashes")
