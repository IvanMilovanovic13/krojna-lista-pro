# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Iterable

MIN_DRAWER_H = 80
DRAWER_STEP_MM = 1


def snap_mm(val: float, step: int = DRAWER_STEP_MM) -> int:
    return int(step * round(float(val) / float(step)))


def floor_mm(val: float, step: int = DRAWER_STEP_MM) -> int:
    return int(float(val) // float(step)) * step


def drawer_target_total(total: float, n: int, *, min_h: int = MIN_DRAWER_H, step: int = DRAWER_STEP_MM) -> int:
    return max(int(n * min_h), floor_mm(total, step))


def equal_drawer_heights(total_target: float, n: int, *, min_h: int = MIN_DRAWER_H, step: int = DRAWER_STEP_MM) -> list[int]:
    n = max(1, int(n))
    total = int(total_target)
    base = max(min_h, floor_mm(total / n, step))
    vals = [base] * n
    vals[-1] += int(total - sum(vals))
    return vals


def normalize_drawer_heights(values: Iterable[float], total_target: float, n: int, *, min_h: int = MIN_DRAWER_H, step: int = DRAWER_STEP_MM) -> list[int]:
    vals = [max(min_h, snap_mm(v, step)) for v in list(values)[:n]]
    if len(vals) < n:
        vals.extend([min_h] * (n - len(vals)))
    diff = int(total_target) - sum(vals)
    while diff != 0:
        changed = False
        if diff > 0:
            for idx in reversed(range(n)):
                vals[idx] += step
                diff -= step
                changed = True
                if diff <= 0:
                    break
        else:
            for idx in reversed(range(n)):
                if vals[idx] - step >= min_h:
                    vals[idx] -= step
                    diff += step
                    changed = True
                    if diff >= 0:
                        break
        if not changed:
            break
    return vals


def _fit_scaled_values_to_total(
    values: Iterable[float],
    total_target: float,
    *,
    min_h: int = MIN_DRAWER_H,
    step: int = DRAWER_STEP_MM,
) -> list[int]:
    vals = [max(min_h, snap_mm(v, step)) for v in values]
    if not vals:
        return []
    diff = int(total_target) - sum(vals)
    order = sorted(range(len(vals)), key=lambda i: vals[i], reverse=True)
    while diff != 0:
        changed = False
        if diff > 0:
            for idx in order:
                vals[idx] += step
                diff -= step
                changed = True
                if diff <= 0:
                    break
        else:
            for idx in order:
                if vals[idx] - step >= min_h:
                    vals[idx] -= step
                    diff += step
                    changed = True
                    if diff >= 0:
                        break
        if not changed:
            break
    return vals


def redistribute_drawers_equal(
    heights: Iterable[float],
    *,
    changed_idx: int,
    requested_height: float,
    locks: dict[int, bool] | None,
    total_target: float,
    min_h: int = MIN_DRAWER_H,
    step: int = DRAWER_STEP_MM,
) -> list[int]:
    vals = [max(min_h, snap_mm(v, step)) for v in list(heights)]
    n = len(vals)
    if n == 0:
        return []
    changed_idx = max(0, min(n - 1, int(changed_idx)))
    lock_map = {int(k): bool(v) for k, v in (locks or {}).items()}
    locked_others = [i for i in range(n) if i != changed_idx and lock_map.get(i, False)]
    free_others = [i for i in range(n) if i != changed_idx and not lock_map.get(i, False)]
    locked_sum = sum(vals[i] for i in locked_others)
    total = int(total_target)

    if not free_others:
        vals[changed_idx] = max(min_h, total - locked_sum)
        return vals

    free_count = len(free_others)
    max_changed = total - locked_sum - free_count * min_h
    requested = max(min_h, min(snap_mm(requested_height, step), max_changed))
    modulus = free_count * step
    allowed: list[int] = []
    for candidate in range(min_h, max_changed + step, step):
        remaining = total - locked_sum - candidate
        if remaining < free_count * min_h:
            continue
        if remaining % modulus == 0:
            allowed.append(candidate)
    if allowed:
        requested = min(allowed, key=lambda c: (abs(c - requested), c))

    vals[changed_idx] = requested
    remaining = total - locked_sum - requested
    each_other = int(remaining / free_count)
    for idx in free_others:
        vals[idx] = each_other
    return vals


def redistribute_drawers_proportional(
    heights: Iterable[float],
    *,
    changed_idx: int,
    requested_height: float,
    total_target: float,
    min_h: int = MIN_DRAWER_H,
    step: int = DRAWER_STEP_MM,
) -> list[int]:
    vals = [max(min_h, snap_mm(v, step)) for v in list(heights)]
    n = len(vals)
    if n == 0:
        return []
    changed_idx = max(0, min(n - 1, int(changed_idx)))
    other_indices = [i for i in range(n) if i != changed_idx]
    total = int(total_target)

    max_changed = total - len(other_indices) * min_h
    requested = max(min_h, min(snap_mm(requested_height, step), max_changed))
    vals[changed_idx] = requested

    if not other_indices:
        return [requested]

    remaining = total - requested
    basis = [max(min_h, vals[i]) for i in other_indices]
    basis_sum = float(sum(basis))
    if basis_sum <= 0:
        scaled = equal_drawer_heights(remaining, len(other_indices), min_h=min_h, step=step)
    else:
        raw = [(remaining * b) / basis_sum for b in basis]
        scaled = _fit_scaled_values_to_total(raw, remaining, min_h=min_h, step=step)

    for pos, idx in enumerate(other_indices):
        vals[idx] = int(scaled[pos])
    return vals


def rebalance_drawers_proportional(
    heights: Iterable[float],
    *,
    fixed_indices: Iterable[int] | None,
    total_target: float,
    min_h: int = MIN_DRAWER_H,
    step: int = DRAWER_STEP_MM,
    basis_heights: Iterable[float] | None = None,
) -> list[int]:
    vals = [max(min_h, snap_mm(v, step)) for v in list(heights)]
    n = len(vals)
    if n == 0:
        return []
    fixed = {max(0, min(n - 1, int(i))) for i in (fixed_indices or [])}
    free_indices = [i for i in range(n) if i not in fixed]
    total = int(total_target)
    if not free_indices:
        return normalize_drawer_heights(vals, total, n, min_h=min_h, step=step)

    fixed_sum = sum(vals[i] for i in fixed)
    remaining = total - fixed_sum
    min_remaining = len(free_indices) * min_h
    if remaining < min_remaining:
        fixed_list = sorted(fixed, key=lambda i: vals[i], reverse=True)
        deficit = min_remaining - remaining
        for idx in fixed_list:
            reducible = max(0, vals[idx] - min_h)
            take = min(reducible, deficit)
            vals[idx] -= take
            deficit -= take
            if deficit <= 0:
                break
        fixed_sum = sum(vals[i] for i in fixed)
        remaining = total - fixed_sum

    basis_source = list(basis_heights) if basis_heights is not None else list(vals)
    if len(basis_source) < n:
        basis_source.extend(vals[len(basis_source):])
    basis = [max(min_h, snap_mm(basis_source[i], step)) for i in free_indices]
    basis_sum = float(sum(basis))
    if basis_sum <= 0:
        scaled = equal_drawer_heights(remaining, len(free_indices), min_h=min_h, step=step)
    else:
        raw = [(remaining * b) / basis_sum for b in basis]
        scaled = _fit_scaled_values_to_total(raw, remaining, min_h=min_h, step=step)
    for pos, idx in enumerate(free_indices):
        vals[idx] = int(scaled[pos])
    return vals


def recalc_with_locks_equal(
    heights: Iterable[float],
    *,
    locks: dict[int, bool] | None,
    total_target: float,
    min_h: int = MIN_DRAWER_H,
    step: int = DRAWER_STEP_MM,
) -> list[int]:
    vals = [max(min_h, snap_mm(v, step)) for v in list(heights)]
    n = len(vals)
    if n == 0:
        return []
    lock_map = {int(k): bool(v) for k, v in (locks or {}).items()}
    locked = [i for i in range(n) if lock_map.get(i, False)]
    free = [i for i in range(n) if i not in locked]
    total = int(total_target)
    locked_sum = sum(vals[i] for i in locked)
    if not free:
        return normalize_drawer_heights(vals, total, n, min_h=min_h, step=step)
    remaining = total - locked_sum
    each = max(min_h, floor_mm(remaining / len(free), step))
    for idx in free:
        vals[idx] = each
    vals[free[-1]] += int(remaining - sum(vals[i] for i in free))
    return normalize_drawer_heights(vals, total, n, min_h=min_h, step=step)
