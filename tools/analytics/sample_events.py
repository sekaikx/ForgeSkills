"""
Write a deterministic synthetic JSONL event file for demos and tests.

Usage:
    python sample_events.py --out sample.jsonl --seed 7 --players 120 --build 0.2.0
    python sample_events.py --kind bot --players 40 --build 0.2.0 --out bots.jsonl

Funnel produced: tutorial_done, level_1_done, level_2_done. Same seed, same file.
"""

import argparse
import json
import random
import sys

STEPS = ("tutorial_done", "level_1_done", "level_2_done")
CAUSES = ("spikes", "boss_slam", "fall", "timeout")


def generate(players=100, seed=1, build="0.1.0", kind="human", p=(0.9, 0.6, 0.7)):
    rng = random.Random(seed)
    out = []
    for i in range(players):
        pid = "%s_%s_%03d" % (kind[0], build, i)
        sid = "s_" + pid
        base = {"session": sid, "player": pid, "kind": kind, "build": build}
        t = 0.0

        def add(event, **props):
            ev = dict(base)
            ev.update(t=round(t, 2), event=event, **props)
            out.append(ev)

        add("session_start")
        for lvl, (step, prob) in enumerate(zip(STEPS, p)):
            level = "tutorial" if lvl == 0 else "level_%d" % lvl
            for _ in range(rng.randint(0, 3)):
                t += rng.uniform(5, 40)
                add("death", cause=rng.choice(CAUSES), x=round(rng.uniform(0, 100), 1),
                    y=round(rng.uniform(0, 30), 1), level=level)
            if rng.random() < 0.08:
                t += 5
                add("stuck", x=round(rng.uniform(0, 100), 1), y=round(rng.uniform(0, 30), 1), level=level)
            t += rng.uniform(30, 150)
            if rng.random() < prob:
                add(step)
            else:
                add("quit", level=level)
                break
        t += 1
        add("session_end")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Write synthetic playtest events (JSONL).")
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--players", type=int, default=100)
    ap.add_argument("--build", default="0.1.0")
    ap.add_argument("--kind", default="human", choices=("human", "bot", "agent"))
    args = ap.parse_args(argv)
    try:
        with open(args.out, "w", encoding="utf-8") as fh:
            for ev in generate(args.players, args.seed, args.build, args.kind):
                fh.write(json.dumps(ev, sort_keys=True) + "\n")
    except OSError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
