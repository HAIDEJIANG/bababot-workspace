from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional

VALID_CONDITIONS = ["NE", "FN", "NS", "OH", "SV", "AR"]
CONDITION_PRIORITY = {c: i for i, c in enumerate(VALID_CONDITIONS)}


@dataclass
class SupplierCandidate:
    vendor: str
    pn: str
    qty: str = "1"
    condition: Optional[str] = None
    source_page: int = 1
    raw: str = ""


def normalize_condition(cond: Optional[str]) -> Optional[str]:
    if not cond:
        return None
    c = cond.strip().upper()
    return c if c in CONDITION_PRIORITY else None


def choose_condition(available: Iterable[str], requested: Optional[str] = None) -> Optional[str]:
    normalized = [normalize_condition(c) for c in available]
    valid = [c for c in normalized if c]
    if not valid:
        return None
    if requested:
        req = normalize_condition(requested)
        return req if req in valid else None
    return sorted(valid, key=lambda c: CONDITION_PRIORITY[c])[0]


def filter_suppliers(
    suppliers: List[SupplierCandidate],
    pn: str,
    requested_condition: Optional[str] = None,
    top_n: int = 10,
) -> List[SupplierCandidate]:
    # Exact PN only
    exact = [s for s in suppliers if s.pn.strip().upper() == pn.strip().upper()]

    # Dedup vendor + choose best condition per vendor
    by_vendor = {}
    for s in exact:
        cond = normalize_condition(s.condition)
        if requested_condition:
            req = normalize_condition(requested_condition)
            if not req or cond != req:
                continue
        else:
            if cond is None:
                continue

        key = s.vendor.strip().upper()
        if key not in by_vendor:
            by_vendor[key] = s
            continue

        prev = by_vendor[key]
        prev_rank = CONDITION_PRIORITY.get(normalize_condition(prev.condition) or "AR", 999)
        cur_rank = CONDITION_PRIORITY.get(cond or "AR", 999)
        if cur_rank < prev_rank:
            by_vendor[key] = s

    ranked = sorted(
        by_vendor.values(),
        key=lambda s: (
            CONDITION_PRIORITY.get(normalize_condition(s.condition) or "AR", 999),
            s.vendor.lower(),
        ),
    )
    return ranked[:top_n]
