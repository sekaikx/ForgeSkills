import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "analytics"))

import playtest_report as pr
import sample_events


def write(path, events):
    path.write_text("\n".join(json.dumps(e) for e in events) + "\n")
    return str(path)


def players(kind, build, n, reach, prefix="p"):
    """n players, first `reach` of them complete step 'a'."""
    ev = []
    for i in range(n):
        base = {"session": "%s%s%d" % (prefix, build, i), "player": "%s%s%d" % (prefix, build, i),
                "kind": kind, "build": build}
        ev.append(dict(base, t=0, event="session_start"))
        if i < reach:
            ev.append(dict(base, t=10, event="a"))
        ev.append(dict(base, t=20, event="session_end"))
    return ev


def test_wilson_known_values():
    lo, hi = pr.wilson(50, 100)
    assert abs(lo - 0.4038) < 1e-3 and abs(hi - 0.5962) < 1e-3
    lo, hi = pr.wilson(0, 10)
    assert lo == 0.0 and abs(hi - 0.2775) < 1e-3
    assert pr.wilson(0, 0) == (0.0, 1.0)


def test_two_prop_z_known():
    z, p = pr.two_prop_z(50, 100, 70, 100)
    assert abs(z - 2.8868) < 1e-3
    assert abs(p - 0.00386) < 1e-4
    assert pr.two_prop_z(5, 10, 5, 10)[1] == 1.0


def test_insufficient_data_refusal(tmp_path):
    ev = players("human", "A", 10, 5) + players("human", "B", 100, 90)
    res = pr.compare_builds(ev, ["a"], "A", "B", 30)
    assert res["human"][0]["verdict"] == "insufficient data"
    assert res["human"][0]["p"] is None


def test_compare_verdicts():
    ev = players("human", "A", 100, 50) + players("human", "B", 100, 70)
    assert pr.compare_builds(ev, ["a"], "A", "B", 30)["human"][0]["verdict"] == "better"
    assert pr.compare_builds(ev, ["a"], "B", "A", 30)["human"][0]["verdict"] == "worse"
    ev = players("human", "A", 100, 50) + players("human", "B", 100, 52)
    assert pr.compare_builds(ev, ["a"], "A", "B", 30)["human"][0]["verdict"] == "no detectable difference"


def test_gate_uses_lower_bound(tmp_path):
    # point estimate 0.65 passes 0.6, but lower bound (~0.55) does not
    f = write(tmp_path / "e.jsonl", players("human", "A", 100, 65))
    assert pr.main([f, "--funnel", "a", "--gate", "a>=0.6"]) == 1
    f2 = write(tmp_path / "e2.jsonl", players("human", "A", 1000, 650))
    assert pr.main([f2, "--funnel", "a", "--gate", "a>=0.6"]) == 0


def test_gate_fails_below_min_n(tmp_path):
    f = write(tmp_path / "e.jsonl", players("human", "A", 10, 10))
    assert pr.main([f, "--funnel", "a", "--gate", "a>=0.1"]) == 1


def test_human_bot_separation(tmp_path):
    ev = players("human", "A", 100, 90, "h") + players("bot", "A", 100, 10, "b")
    rep = {k: pr.analyse_kind([e for e in ev if e["kind"] == k], ["a"]) for k in ("human", "bot")}
    assert rep["human"]["funnel"][0]["conversion"] == 0.9
    assert rep["bot"]["funnel"][0]["conversion"] == 0.1
    f = write(tmp_path / "e.jsonl", ev)
    out = tmp_path / "r.md"
    assert pr.main([f, "--funnel", "a", "--out", str(out)]) == 0
    text = out.read_text()
    assert "## human players" in text and "## bot players" in text
    # a gate on humans ignores bots
    assert pr.main([f, "--funnel", "a", "--gate", "a>=0.8"]) == 0


def test_unreadable_input_exit_2(tmp_path):
    assert pr.main([str(tmp_path / "missing.jsonl"), "--funnel", "a"]) == 2
    bad = tmp_path / "bad.jsonl"
    bad.write_text("{not json\n")
    assert pr.main([str(bad), "--funnel", "a"]) == 2


def test_strict_funnel_and_biggest_dropoff():
    ev = players("human", "A", 100, 90)
    # 30 of the 90 also did b; 60 skipped nothing but lack b
    for e in [e for e in ev if e["event"] == "a"][:30]:
        ev.append(dict(e, event="b", t=15))
    r = pr.analyse_kind(ev, ["a", "b"])
    assert r["biggest_dropoff"] == "b"
    assert r["funnel"][1]["n"] == 90 and r["funnel"][1]["reached"] == 30


def test_sample_events_deterministic(tmp_path):
    a, b = tmp_path / "a.jsonl", tmp_path / "b.jsonl"
    assert sample_events.main(["--out", str(a), "--seed", "3", "--players", "50"]) == 0
    assert sample_events.main(["--out", str(b), "--seed", "3", "--players", "50"]) == 0
    assert a.read_bytes() == b.read_bytes()
    assert pr.main([str(a), "--funnel", "tutorial_done,level_1_done,level_2_done", "--json",
                    "--out", str(tmp_path / "o.json")]) == 0
    assert math.isfinite(json.loads((tmp_path / "o.json").read_text())["kinds"]["human"]["median_session_s"])
