"""Small, dependency-free statistics for before/after pass counts."""
from __future__ import annotations

from math import comb


def fisher_one_sided(before_pass: int, before_n: int, after_pass: int, after_n: int) -> float:
    """P(after passes <= observed | fixed margins): the chance of seeing a drop
    at least this large if adding the skill made no difference."""
    total_pass = before_pass + after_pass
    total = before_n + after_n
    if total == 0 or before_n == 0 or after_n == 0:
        return 1.0
    denom = comb(total, after_n)
    lo = max(0, total_pass - before_n)
    p = 0.0
    for k in range(lo, after_pass + 1):
        p += comb(total_pass, k) * comb(total - total_pass, after_n - k) / denom
    return min(1.0, p)


def confidence(p: float) -> str:
    # With 3 repeats per arm, 3/3 -> 0/3 gives exactly p = 0.05, the strongest
    # evidence that sample size can produce, so the boundary is inclusive.
    if p <= 0.05:
        return "high"
    if p < 0.25:
        return "medium"
    return "low"


def rate(k: int, n: int) -> float | None:
    return k / n if n else None
