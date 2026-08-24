import csv
from collections import Counter, defaultdict

# Read the saved results back in.
rows = []
with open("trueself_bymodel_results.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append(r)

# Group ratings by (model, condition).
buckets = defaultdict(list)
for r in rows:
    if r["rating"] != "":          # skip any failed parses
        buckets[(r["model"], r["condition"])].append(int(r["rating"]))

# Print a compact distribution for each group.
for (model, cond) in sorted(buckets.keys()):
    ratings = buckets[(model, cond)]
    counts = Counter(ratings)
    dist = "  ".join(f"{v}:{counts.get(v, 0)}" for v in range(1, 8))
    print(f"{model:32} {cond:5}  n={len(ratings):3}  [{dist}]")