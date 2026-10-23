"""
Validate the gamedev skills library.

Checks the things that silently rot in a skill library:
  - YAML frontmatter present, parseable, with required keys
  - name matches the directory name
  - description is substantial and starts with a use-case signal
  - every cross-referenced skill name actually exists
  - every `tools/...` path referenced in the body exists on disk
  - the transcript technique IDs cited (T-nn) exist in the knowledge base

Usage:
    python tools/validate_skills.py
    python tools/validate_skills.py --root . --json
"""

import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED_KEYS = ("name", "description")
RECOMMENDED = ("license", "compatibility", "metadata")
MIN_DESC_CHARS = 60


def parse_frontmatter(text):
    """Minimal YAML front-matter reader: enough for flat scalars and the
    '>' folded block used by these skills. No external dependency."""
    if not text.startswith("---"):
        return None, text
    end = text.find("\n---", 3)
    if end == -1:
        return None, text
    raw = text[3:end].strip("\n")
    body = text[end + 4:]

    data = {}
    key = None
    buf = []
    mode = None

    def flush():
        nonlocal key, buf, mode
        if key is None:
            return
        if mode == "folded":
            data[key] = " ".join(s.strip() for s in buf if s.strip())
        elif mode == "list":
            data[key] = [s.strip("- ").strip() for s in buf if s.strip()]
        else:
            data[key] = buf[0].strip() if len(buf) == 1 else " ".join(s.strip() for s in buf)
        key, buf, mode = None, [], None

    for line in raw.split("\n"):
        if not line.strip():
            continue
        if line.startswith("  ") and key is not None:
            if line.strip().startswith("- "):
                mode = "list"
            buf.append(line)
            continue
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if m:
            flush()
            key = m.group(1)
            val = m.group(2).strip()
            if val in (">", "|", ">-", "|-"):
                mode = "folded"
                buf = []
            elif val:
                buf = [val]
                mode = None
            else:
                mode = "list"
                buf = []
    flush()
    return data, body


def find_skills(root):
    """Locate SKILL.md files, accepting either layout.

    `root/.agents/skills/` is the Cursor workspace layout; `root/skills/` is the
    standalone distribution layout. Both are valid; silently finding zero skills
    is not, which is why validate() treats an empty result as an error.
    """
    base = Path(root)
    found = []
    for rel in (Path(".agents") / "skills", Path("skills"), Path(".")):
        d = base / rel
        if d.is_dir():
            found.extend(p.parent for p in d.glob("gamedev-*/SKILL.md"))
    # dedupe while preserving order
    seen, out = set(), []
    for p in found:
        rp = p.resolve()
        if rp not in seen:
            seen.add(rp)
            out.append(p)
    return sorted(out)


def collect_tech_ids(docs_root):
    """Collect T-nn ids from the knowledge base.

    Accepts either layout: the workspace keeps docs under `docs/gamedev/`, the
    standalone distribution keeps them under `docs/`. Tries the explicit path
    first, then falls back to scanning, so moving the library does not silently
    disable the citation check.
    """
    roots = [Path(docs_root)]
    parent = Path(docs_root).parent
    if parent.is_dir():
        roots.append(parent)
    ids = set()
    for r in roots:
        if not r.is_dir():
            continue
        for md in r.rglob("*.md"):
            try:
                text = md.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for m in re.finditer(r"\bT-(\d{2})\b", text):
                ids.add(f"T-{m.group(1)}")
        if ids:
            break
    return ids


def validate(root=".", docs="docs/gamedev"):
    root = Path(root)
    skills = find_skills(root)
    names = {p.name for p in skills}
    tech_ids = collect_tech_ids(root / docs)

    results = []
    for d in skills:
        path = d / "SKILL.md"
        text = path.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(text)
        issues = []

        if fm is None:
            issues.append(("error", "missing or malformed YAML frontmatter"))
            fm = {}

        for k in REQUIRED_KEYS:
            if not fm.get(k):
                issues.append(("error", f"missing required key: {k}"))

        if fm.get("name") and fm["name"] != d.name:
            issues.append(("error", f"name '{fm['name']}' != directory '{d.name}'"))

        desc = fm.get("description", "")
        if len(desc) < MIN_DESC_CHARS:
            issues.append(("error", f"description too short ({len(desc)} chars)"))
        elif not re.search(r"\b(use|when|for|whenever|before|after)\b", desc, re.I):
            issues.append(("warn", "description should state when to use it"))

        for k in RECOMMENDED:
            if k not in fm:
                issues.append(("warn", f"missing recommended key: {k}"))

        # cross-references must resolve
        for ref in set(re.findall(r"`(gamedev-[a-z0-9-]+)`", body)):
            if ref not in names:
                issues.append(("error", f"references missing skill: {ref}"))

        # tool paths must exist
        for tp in set(re.findall(r"`(tools/[A-Za-z0-9_./-]+\.py)`", body)):
            if not (root / tp).exists():
                issues.append(("error", f"references missing tool: {tp}"))

        # transcript ids must exist in the knowledge base
        if tech_ids:
            for tid in set(re.findall(r"\bT-(\d{2})\b", body)):
                full = f"T-{tid}"
                if full not in tech_ids:
                    issues.append(("warn", f"cites unknown technique {full}"))

        # size sanity
        words = len(body.split())
        if words < 400:
            issues.append(("warn", f"thin body ({words} words)"))
        if words > 2500:
            issues.append(("warn", f"very long body ({words} words) — consider splitting"))

        results.append({
            "skill": d.name,
            "path": str(path),
            "words": words,
            "issues": issues,
            "ok": not any(s == "error" for s, _ in issues),
        })

    errors = sum(1 for r in results for s, _ in r["issues"] if s == "error")
    warns = sum(1 for r in results for s, _ in r["issues"] if s == "warn")

    # An empty scan is a failure, not a pass. A validator that reports "0 errors"
    # after finding nothing is worse than no validator at all.
    fatal = None
    if not results:
        fatal = (f"no skills found under {root} — looked for "
                 f".agents/skills/gamedev-*/SKILL.md and skills/gamedev-*/SKILL.md")
        errors += 1
    elif not tech_ids:
        fatal = f"no T-nn technique citations found under {root / docs}"
        errors += 1

    return {
        "root": str(root),
        "skills_found": len(results),
        "errors": errors,
        "warnings": warns,
        "techniques_known": len(tech_ids),
        "fatal": fatal,
        "results": results,
    }


def print_report(rep):
    print("=" * 72)
    print(f"SKILL LIBRARY VALIDATION — {rep['skills_found']} skills, "
          f"{rep['techniques_known']} techniques known")
    print("=" * 72)
    if rep.get("fatal"):
        print(f"FATAL: {rep['fatal']}")
        print("=" * 72)
        return 1
    for r in rep["results"]:
        status = "OK  " if r["ok"] else "FAIL"
        print(f"[{status}] {r['skill']:<32} {r['words']:>5} words")
        for sev, msg in r["issues"]:
            mark = "  ERR " if sev == "error" else "  warn"
            print(f"        {mark} {msg}")
    print("-" * 72)
    print(f"ERRORS {rep['errors']}   WARNINGS {rep['warnings']}")
    print("=" * 72)
    return 0 if rep["errors"] == 0 else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args()
    rep = validate(a.root)
    if a.out:
        Path(a.out).write_text(json.dumps(rep, indent=2), encoding="utf-8")
        print(f"wrote {a.out}")
    sys.exit(print_report(rep) if not a.json else (print(json.dumps(rep, indent=2)) or
                                                   (0 if rep["errors"] == 0 else 1)))
