"""Measure what each skill costs in context tokens, split by when the cost is paid.

  always    frontmatter name + description: loaded into every conversation for routing
  on use    SKILL.md body: loaded only when the agent picks the skill
  on demand references/*.md: loaded only when a step says so

Caps (defaults; override with flags):
  description  <= 110 tokens   - routing text only; it is paid on every turn of every chat
  body         <= 2100 tokens  - steps and hard rules; long tables go to references/

Uses tiktoken (cl100k_base) when installed, else ~4 characters per token.

Usage:
  python tools/token_budget.py [--root .] [--desc-cap 110] [--body-cap 2100] [--json] [--strict]

Exit 1 with --strict when any skill exceeds a cap; exit 2 when no skills are found.
"""
import argparse
import json
import re
import sys
from pathlib import Path

from validate_skills import BODY_TOKEN_CAP, DESC_TOKEN_CAP

try:
    import tiktoken
    _ENC = tiktoken.get_encoding("cl100k_base")

    def count(text):
        return len(_ENC.encode(text))
    METHOD = "tiktoken cl100k_base"
except Exception:
    def count(text):
        return round(len(text) / 4)
    METHOD = "estimate: chars / 4"

FRONT = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.S)


def split_skill(text):
    m = FRONT.match(text)
    if not m:
        return "", text
    front, body = m.group(1), m.group(2)
    name, desc, in_desc = "", [], False
    for line in front.splitlines():
        if line.startswith("name:"):
            name = line[5:].strip()
            in_desc = False
        elif line.startswith("description:"):
            rest = line[12:].strip()
            if rest and rest not in (">", ">-", "|", "|-"):
                desc.append(rest)
            in_desc = True
        elif in_desc and line[:1] in (" ", "\t"):
            desc.append(line.strip())
        else:
            in_desc = False
    return name + "\n" + " ".join(desc), body


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--desc-cap", type=int, default=DESC_TOKEN_CAP)
    ap.add_argument("--body-cap", type=int, default=BODY_TOKEN_CAP)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args()

    skills_dir = Path(a.root) / "skills"
    files = sorted(skills_dir.glob("*/SKILL.md"))
    if not files:
        print(f"no skills found under {skills_dir}", file=sys.stderr)
        return 2

    rows = []
    for f in files:
        routing, body = split_skill(f.read_text(encoding="utf-8"))
        refs = sorted((f.parent / "references").glob("*.md")) if (f.parent / "references").is_dir() else []
        ref_tokens = {r.name: count(r.read_text(encoding="utf-8")) for r in refs}
        d, b = count(routing), count(body)
        over = []
        if d > a.desc_cap:
            over.append(f"description {d} > {a.desc_cap}")
        if b > a.body_cap:
            over.append(f"body {b} > {a.body_cap}")
        rows.append({"skill": f.parent.name, "always": d, "on_use": b,
                     "on_demand": ref_tokens, "over": over})

    always = sum(r["always"] for r in rows)
    bodies = sorted(r["on_use"] for r in rows)
    typical = always + sum(bodies[len(bodies) // 2: len(bodies) // 2 + 2])
    if a.json:
        print(json.dumps({"method": METHOD, "skills": rows, "always_total": always,
                          "typical_task_total": typical}, indent=2))
    else:
        print(f"token budget ({METHOD})")
        print(f"{'SKILL':<34}{'ALWAYS':>8}{'ON USE':>8}{'REFS':>8}   NOTE")
        print("-" * 72)
        for r in rows:
            refs = sum(r["on_demand"].values())
            print(f"{r['skill']:<34}{r['always']:>8}{r['on_use']:>8}{refs:>8}   {'; '.join(r['over'])}")
        print("-" * 72)
        print(f"always loaded (all {len(rows)} descriptions): {always} tokens")
        print(f"typical task (descriptions + 2 median skill bodies): {typical} tokens")
        print(f"largest body: {max(bodies)} tokens; median body: {bodies[len(bodies) // 2]} tokens")
    if a.strict and any(r["over"] for r in rows):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
