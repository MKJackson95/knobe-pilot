import csv, statistics as st
from collections import defaultdict

SRC = "battery_multi_20260626_162439.csv"
buckets = defaultdict(list)
with open(SRC, newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if r["rating"]:
            buckets[(r["model"], r["measure"], r["condition"])].append(int(r["rating"]))

models = ["claude-haiku-4-5-20251001", "claude-sonnet-4-6", "claude-opus-4-8"]
measures = ["intentionality", "responsibility", "causation", "blame", "praise"]

for m in models:
    print("\n" + m)
    for meas in measures:
        h = buckets.get((m, meas, "harm"))
        p = buckets.get((m, meas, "help"))
        parts = []
        if h:
            parts.append(f"harm={st.mean(h):.2f} (n={len(h)})")
        if p:
            parts.append(f"help={st.mean(p):.2f} (n={len(p)})")
        if h and p:
            parts.append(f"asym={st.mean(h)-st.mean(p):+.2f}")
        print(f"  {meas:16} " + "  ".join(parts))
