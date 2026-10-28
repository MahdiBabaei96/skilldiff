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


def holm_adjust(ps: list[float]) -> list[float]:
    """Holm-adjust a predeclared family of tests, preserving input order.

    Includes tests with no observed drop; selecting only failures first would
    understate the number of comparisons. Valid under arbitrary dependence.
    """
    adjusted = [1.0] * len(ps)
    previous = 0.0
    for rank, i in enumerate(sorted(range(len(ps)), key=ps.__getitem__)):
        previous = min(1.0, max(previous, ps[i] * (len(ps) - rank)))
        adjusted[i] = previous
    return adjusted


def rate(k: int, n: int) -> float | None:
    return k / n if n else None
