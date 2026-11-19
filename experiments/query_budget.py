#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / "configs/reproduction.json").read_text())
GROUP_ID = {"current_pool": "G0", "kodak": "G1", "clic2024": "G2"}

def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def order_indices(group: str, order_index: int, hashes: list[str]) -> list[int]:
    gid = GROUP_ID.get(group, group)
    keyed = []
    for i, digest in enumerate(hashes):
        raw = f"ENTROPYSEAL_A5Q_ORDER_V1|{gid}|{order_index}|{digest}".encode("ascii")
        keyed.append((hashlib.sha256(raw).digest(), i))
    return [i for _, i in sorted(keyed)]

def profile(s, t, tau_count, tau_mad):
    d = [a - b for a, b in zip(s, t)]
    mismatch = sum(x != 0 for x in d)
    mad = sum(abs(x) for x in d) / len(d)
    score = max(mismatch / tau_count, mad / tau_mad)
    return mismatch, mad, score, mismatch <= tau_count and mad <= tau_mad

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--group", choices=sorted(GROUP_ID), required=True)
    ap.add_argument("--payload", type=Path, required=True, help="CSV with identity, challenge_id, residual_payload_bytes")
    ap.add_argument("--manifest", type=Path, required=True, help="CSV with challenge_id, raw_rgb_sha256")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    payload = read_csv(args.payload)
    manifest = sorted(read_csv(args.manifest), key=lambda r: int(r["challenge_id"]))
    hashes = [r["raw_rgb_sha256"] for r in manifest]
    vec = {}
    for ident in sorted({r["identity"] for r in payload}):
        rows = sorted((r for r in payload if r["identity"] == ident), key=lambda r: int(r["challenge_id"]))
        vec[ident] = [int(r["residual_payload_bytes"]) for r in rows]
    rows = []
    for order in range(CFG["query_budget"]["order_count"]):
        perm = order_indices(args.group, order, hashes)
        for budget in CFG["query_budget"]["budgets"]:
            idx = perm[:budget]
            for owner, th in CFG["verifier"]["thresholds"].items():
                templates = {p: [vec[f"{owner}_{p}"][i] for i in idx] for p in ("FP32", "FP16")}
                for suspect, full in vec.items():
                    s = [full[i] for i in idx]
                    ds = {p: profile(s, t, th["tau_count"], th["tau_mad"]) for p, t in templates.items()}
                    best = min(ds, key=lambda p: (ds[p][2], 0 if p == "FP16" else 1))
                    rows.append({"group": args.group, "order": order, "budget": budget, "owner": owner,
                                 "suspect": suspect, "accepted": any(x[3] for x in ds.values()),
                                 "best_profile": best, "best_score": ds[best][2]})
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
    print(json.dumps({"rows": len(rows), "out": str(args.out)}, indent=2))

if __name__ == "__main__":
    main()
