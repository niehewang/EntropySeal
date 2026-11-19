"""Black-box codelength-profile decision rules."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence


@dataclass(frozen=True)
class ProfileDecision:
    mismatch_count: int
    mad: float
    normalized_score: float
    accepted: bool


def profile_distance(suspect: Sequence[int], template: Sequence[int], tau_count: int, tau_mad: float) -> ProfileDecision:
    if len(suspect) != len(template) or not suspect:
        raise ValueError("suspect/template vectors must be non-empty and have equal length")
    diffs = [int(s) - int(t) for s, t in zip(suspect, template)]
    mismatch = sum(d != 0 for d in diffs)
    mad = sum(abs(d) for d in diffs) / len(diffs)
    score = max(mismatch / int(tau_count), mad / float(tau_mad))
    return ProfileDecision(mismatch, float(mad), float(score), mismatch <= int(tau_count) and mad <= float(tau_mad))


def owner_decision(suspect: Sequence[int], templates: Mapping[str, Sequence[int]], tau_count: int, tau_mad: float) -> dict:
    """Evaluate all registered precision profiles and OR their acceptance decisions."""
    decisions = {name: profile_distance(suspect, vec, tau_count, tau_mad) for name, vec in templates.items()}
    return {
        "accepted": any(d.accepted for d in decisions.values()),
        "profiles": decisions,
        "best_profile": min(decisions, key=lambda name: decisions[name].normalized_score),
    }
