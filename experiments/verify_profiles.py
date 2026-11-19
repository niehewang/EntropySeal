#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / "configs/reproduction.json").read_text())

def load_vector(path: Path) -> list[int]:
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text())
        if isinstance(data, dict) and "residual_payload_bytes" in data:
            data = data["residual_payload_bytes"]
        return [int(x) for x in data]
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return [int(r["residual_payload_bytes"]) for r in rows]

def distance(suspect: list[int], template: list[int], tau_count: int, tau_mad: float) -> dict:
    if len(suspect) != len(template) or not suspect:
        raise ValueError("vectors must be non-empty and equal length")
    delta = [a - b for a, b in zip(suspect, template)]
    mismatch = sum(x != 0 for x in delta)
    mad = sum(abs(x) for x in delta) / len(delta)
    score = max(mismatch / tau_count, mad / tau_mad)
    return {"mismatch_count": mismatch, "mad": mad, "normalized_score": score,
            "accepted": mismatch <= tau_count and mad <= tau_mad}

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--owner", choices=sorted(CFG["verifier"]["thresholds"]), required=True)
    ap.add_argument("--suspect", type=Path, required=True)
    ap.add_argument("--fp32-template", type=Path, required=True)
    ap.add_argument("--fp16-template", type=Path, required=True)
    args = ap.parse_args()
    t = CFG["verifier"]["thresholds"][args.owner]
    s = load_vector(args.suspect)
    profiles = {
        "FP32": distance(s, load_vector(args.fp32_template), t["tau_count"], t["tau_mad"]),
        "FP16": distance(s, load_vector(args.fp16_template), t["tau_count"], t["tau_mad"]),
    }
    result = {"owner": args.owner, "accepted": any(v["accepted"] for v in profiles.values()), "profiles": profiles}
    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
