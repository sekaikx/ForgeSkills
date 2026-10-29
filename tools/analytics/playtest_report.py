"""
Playtest funnel report from JSONL event logs.

Event schema, one JSON object per line:
    {"t": 12.5, "session": "s1", "player": "p1", "kind": "human",
     "build": "0.3.1", "event": "session_start", ...props}
  t        float seconds since session start
  kind     "human" | "bot" | "agent"   (never pooled with each other)
Required events: session_start, session_end, and every --funnel step.
Optional events: death {cause, x, y, level}, quit {level}, stuck {x, y, level}.

A player reaches funnel step i only if they also reached steps 1..i-1.
Step 1 is measured against players with a session_start; step i against step i-1.
Intervals are Wilson 95%. Everything is reported per kind.

Usage:
    python playtest_report.py events.jsonl --funnel tutorial_done,level_1_done
    python playtest_report.py a.jsonl b.jsonl --funnel a,b --json --out report.md
    python playtest_report.py ev.jsonl --funnel a,b --compare 0.1,0.2 --min-n 30
    python playtest_report.py ev.jsonl --funnel a,b --gate "a>=0.6"

Exit codes: 0 ok, 1 gate failed, 2 unreadable input or bad arguments.
Requires: Python 3.8+ stdlib only.
"""

import argparse
import json
import math
import re
import sys
from collections import Counter, defaultdict

Z95 = 1.959963984540054
KINDS = ("human", "bot", "agent")


# ------------------------------------------------------------------ statistics

def wilson(k, n, z=Z95):
    """Wilson score interval for k successes in n trials. Returns (lo, hi)."""
    if n <= 0:
        return (0.0, 1.0)
    p = k / n
    z2 = z * z
    denom = 1 + z2 / n
    centre = (p + z2 / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def two_prop_z(k1, n1, k2, n2):
    """Pooled two-proportion z-test. Returns (z, two-sided p)."""
    if n1 <= 0 or n2 <= 0:
        return (0.0, 1.0)
    pool = (k1 + k2) / (n1 + n2)
    se = math.sqrt(pool * (1 - pool) * (1 / n1 + 1 / n2))
    if se == 0:
        return (0.0, 1.0)
    z = (k2 / n2 - k1 / n1) / se
    return (z, math.erfc(abs(z) / math.sqrt(2)))


def median(xs):
    xs = sorted(xs)
    if not xs:
        return None
    m = len(xs) // 2
    return xs[m] if len(xs) % 2 else (xs[m - 1] + xs[m]) / 2


# --------------------------------------------------------------------- loading

class InputError(Exception):
    pass


def load_events(paths):
    events = []
    for path in paths:
        try:
            with open(path, "r", encoding="utf-8") as fh:
                for i, line in enumerate(fh, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        ev = json.loads(line)
                    except ValueError as e:
                        raise InputError("%s:%d invalid JSON (%s)" % (path, i, e))
                    if not isinstance(ev, dict):
                        raise InputError("%s:%d not a JSON object" % (path, i))
                    for key in ("session", "player", "kind", "event"):
                        if key not in ev:
                            raise InputError("%s:%d missing field '%s'" % (path, i, key))
                    events.append(ev)
        except (OSError, UnicodeDecodeError) as e:
            raise InputError("cannot read %s: %s" % (path, e))
    return events


# -------------------------------------------------------------------- analysis

def funnel_counts(events, steps):
    """Per-player strict funnel. Returns list of (step, reached_count) and n_start."""
    started = {e["player"] for e in events if e["event"] == "session_start"}
    have = defaultdict(set)
    for e in events:
        have[e["player"]].add(e["event"])
    alive = set(started)
    out = []
    for s in steps:
        alive = {p for p in alive if s in have[p]}
        out.append((s, len(alive)))
    return len(started), out


def funnel_rows(events, steps):
    n_start, counts = funnel_counts(events, steps)
    rows = []
    prev = n_start
    for s, k in counts:
        lo, hi = wilson(k, prev)
        rows.append({"step": s, "n": prev, "reached": k,
                     "conversion": (k / prev) if prev else None,
                     "lo": lo, "hi": hi, "lost": prev - k})
        prev = k
    return n_start, rows


def session_lengths(events):
    start, end, last = {}, {}, {}
    for e in events:
        sid, t = e["session"], e.get("t")
        if not isinstance(t, (int, float)):
            continue
        last[sid] = max(last.get(sid, t), t)
        if e["event"] == "session_start":
            start[sid] = min(start.get(sid, t), t)
        elif e["event"] == "session_end":
            end[sid] = max(end.get(sid, t), t)
    return [end.get(s, last[s]) - start[s] for s in start if s in last]


def analyse_kind(events, steps):
    n_start, rows = funnel_rows(events, steps)
    deaths = defaultdict(Counter)
    stuck = Counter()
    quits = Counter()
    for e in events:
        lvl = str(e.get("level", "unknown"))
        if e["event"] == "death":
            deaths[lvl][str(e.get("cause", "unknown"))] += 1
        elif e["event"] == "stuck":
            stuck[lvl] += 1
        elif e["event"] == "quit":
            quits[lvl] += 1
    worst = None
    cand = [r for r in rows if r["n"] > 0 and r["lost"] > 0]
    if cand:
        worst = max(cand, key=lambda r: (r["lost"] / r["n"], r["lost"]))
    return {
        "players": len({e["player"] for e in events}),
        "sessions": len({e["session"] for e in events}),
        "players_started": n_start,
        "median_session_s": median(session_lengths(events)),
        "funnel": rows,
        "biggest_dropoff": worst["step"] if worst else None,
        "deaths": {l: c.most_common(5) for l, c in sorted(deaths.items())},
        "stuck": dict(sorted(stuck.items())),
        "quit": dict(sorted(quits.items())),
    }


def compare_builds(events, steps, a, b, min_n):
    out = {}
    for kind in KINDS:
        ev = [e for e in events if e["kind"] == kind]
        ea = [e for e in ev if e.get("build") == a]
        eb = [e for e in ev if e.get("build") == b]
        if not ea and not eb:
            continue
        _, ra = funnel_rows(ea, steps)
        _, rb = funnel_rows(eb, steps)
        rows = []
        for x, y in zip(ra, rb):
            row = {"step": x["step"], "n_a": x["n"], "n_b": y["n"],
                   "conv_a": x["conversion"], "conv_b": y["conversion"]}
            if x["n"] < min_n or y["n"] < min_n:
                row.update(verdict="insufficient data", p=None, z=None)
            else:
                z, p = two_prop_z(x["reached"], x["n"], y["reached"], y["n"])
                if p >= 0.05:
                    v = "no detectable difference"
                else:
                    v = "better" if z > 0 else "worse"
                row.update(verdict=v, p=p, z=z)
            rows.append(row)
        out[kind] = rows
    return out


GATE_RE = re.compile(r"^\s*([A-Za-z0-9_]+)\s*>=\s*([0-9.]+)\s*$")


def parse_gate(text):
    m = GATE_RE.match(text)
    if not m:
        raise InputError('bad --gate "%s", expected step>=0.6' % text)
    thr = float(m.group(2))
    if not 0 <= thr <= 1:
        raise InputError("gate threshold must be in [0,1]")
    return m.group(1), thr


def check_gate(result, step, thr, min_n):
    rows = {r["step"]: r for r in result["funnel"]}
    if step not in rows:
        raise InputError("gate step '%s' is not in --funnel" % step)
    r = rows[step]
    if r["n"] < min_n:
        return False, "insufficient data (n=%d < %d)" % (r["n"], min_n)
    ok = r["lo"] >= thr
    return ok, "%s lower 95%% bound %.3f %s %.3f (point %.3f, n=%d)" % (
        step, r["lo"], ">=" if ok else "<", thr, r["conversion"], r["n"])


# ------------------------------------------------------------------- rendering

def pct(x):
    return "n/a" if x is None else "%.1f%%" % (100 * x)


def render(report):
    L = ["# Playtest report", ""]
    L.append("Funnel: " + " > ".join(report["funnel_steps"]))
    for kind, r in report["kinds"].items():
        L += ["", "## %s players" % kind, ""]
        if r["biggest_dropoff"]:
            w = next(x for x in r["funnel"] if x["step"] == r["biggest_dropoff"])
            L.append("**Biggest drop-off: %s** - lost %d of %d (%s)." % (
                w["step"], w["lost"], w["n"], pct(w["lost"] / w["n"])))
        else:
            L.append("Biggest drop-off: none observed.")
        ms = r["median_session_s"]
        L += ["",
              "%d players, %d sessions, median session %s." % (
                  r["players"], r["sessions"],
                  "n/a" if ms is None else "%.0f s" % ms),
              "", "| Step | n | Reached | Conversion | 95% Wilson |",
              "|---|---|---|---|---|"]
        for x in r["funnel"]:
            L.append("| %s | %d | %d | %s | %s - %s |" % (
                x["step"], x["n"], x["reached"], pct(x["conversion"]),
                pct(x["lo"]), pct(x["hi"])))
        L += ["", "Deaths per level (top causes):"]
        if r["deaths"]:
            for lvl, causes in r["deaths"].items():
                L.append("- %s: " % lvl + ", ".join("%s x%d" % c for c in causes))
        else:
            L.append("- none logged")
        L.append("Stuck: " + (", ".join("%s x%d" % kv for kv in r["stuck"].items()) or "none logged"))
        L.append("Quit by level: " + (", ".join("%s x%d" % kv for kv in r["quit"].items()) or "none logged"))
    if "compare" in report:
        c = report["compare"]
        L += ["", "## Build comparison: %s (A) vs %s (B)" % (c["a"], c["b"]),
              "", "Two-proportion z-test per step; one comparison per kind, never pooled.", ""]
        if not c["kinds"]:
            L.append("insufficient data (no events for either build)")
        for kind, rows in c["kinds"].items():
            L += ["### %s" % kind, "",
                  "| Step | n A | n B | A | B | p | Verdict |", "|---|---|---|---|---|---|---|"]
            for x in rows:
                L.append("| %s | %d | %d | %s | %s | %s | %s |" % (
                    x["step"], x["n_a"], x["n_b"], pct(x["conv_a"]), pct(x["conv_b"]),
                    "-" if x["p"] is None else "%.4f" % x["p"], x["verdict"]))
            L.append("")
    if "gate" in report:
        g = report["gate"]
        L += ["", "## Gate", "", "%s: %s" % ("PASS" if g["passed"] else "FAIL", g["detail"])]
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------------ main

def build_parser():
    ap = argparse.ArgumentParser(description="Funnel report from JSONL playtest events.")
    ap.add_argument("files", nargs="+", help="JSONL event files")
    ap.add_argument("--funnel", required=True, help="comma-separated funnel event names, in order")
    ap.add_argument("--build", help="only use events from this build")
    ap.add_argument("--compare", metavar="BUILD_A,BUILD_B",
                    help="two-proportion z-test per step, B against A")
    ap.add_argument("--min-n", type=int, default=30,
                    help="minimum denominator per step for any verdict (default 30)")
    ap.add_argument("--gate", metavar="STEP>=X",
                    help="exit 1 if the LOWER Wilson 95%% bound of the step conversion is "
                         "below X. Gates on the lower bound, not the point estimate. "
                         "Also fails when n < --min-n.")
    ap.add_argument("--gate-kind", default="human", choices=KINDS,
                    help="player kind the gate applies to (default human)")
    ap.add_argument("--out", help="write markdown report to this file")
    ap.add_argument("--json", action="store_true", help="print JSON instead of markdown")
    return ap


def main(argv=None):
    args = build_parser().parse_args(argv)
    steps = [s.strip() for s in args.funnel.split(",") if s.strip()]
    if not steps:
        print("error: empty --funnel", file=sys.stderr)
        return 2
    try:
        events = load_events(args.files)
        gate = parse_gate(args.gate) if args.gate else None
        cmp_builds = None
        if args.compare:
            cmp_builds = [b.strip() for b in args.compare.split(",")]
            if len(cmp_builds) != 2 or not all(cmp_builds):
                raise InputError("--compare needs BUILD_A,BUILD_B")
        if args.build:
            events = [e for e in events if e.get("build") == args.build]
        report = {"funnel_steps": steps, "min_n": args.min_n, "kinds": {}}
        for kind in KINDS:
            ev = [e for e in events if e["kind"] == kind]
            if ev:
                report["kinds"][kind] = analyse_kind(ev, steps)
        unknown = {e["kind"] for e in events} - set(KINDS)
        if unknown:
            raise InputError("unknown kind(s): %s" % ", ".join(sorted(map(str, unknown))))
        if cmp_builds:
            report["compare"] = {"a": cmp_builds[0], "b": cmp_builds[1],
                                 "kinds": compare_builds(events, steps, cmp_builds[0],
                                                         cmp_builds[1], args.min_n)}
        rc = 0
        if gate:
            res = report["kinds"].get(args.gate_kind)
            if res is None:
                report["gate"] = {"passed": False, "detail": "insufficient data (no %s events)" % args.gate_kind}
            else:
                ok, detail = check_gate(res, gate[0], gate[1], args.min_n)
                report["gate"] = {"passed": ok, "detail": "[%s] %s" % (args.gate_kind, detail)}
            rc = 0 if report["gate"]["passed"] else 1
    except InputError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    text = json.dumps(report, indent=2) if args.json else render(report)
    if args.out:
        try:
            with open(args.out, "w", encoding="utf-8") as fh:
                fh.write(text)
        except OSError as e:
            print("error: cannot write %s: %s" % (args.out, e), file=sys.stderr)
            return 2
    else:
        sys.stdout.write(text if text.endswith("\n") else text + "\n")
    return rc


if __name__ == "__main__":
    sys.exit(main())
