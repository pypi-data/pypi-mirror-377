from __future__ import annotations

import math
import random
from typing import Any, Mapping


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _get_float(d: Mapping[str, Any], key: str, default: float = 0.0) -> float:
    """Robustly pull a float from a dict-like mapping."""
    v = d.get(key, default)
    # Concrete numeric types are fine for mypy (bool is a subclass of int; acceptable here).
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        try:
            return float(v.strip())
        except ValueError:
            return default
    return default


def significance_score(
    x: Mapping[str, Any],
    w_mag: float,
    w_ano: float,
    w_ctx: float,
    w_urg: float,
) -> float:
    mag = clamp(_get_float(x, "magnitude", 0.0) / 100.0, 0.0, 1.0)
    ano = clamp(_get_float(x, "anomaly_score", 0.0), 0.0, 1.0)
    ctx = clamp(_get_float(x, "context_relevance", 0.0), 0.0, 1.0)
    urg = clamp(_get_float(x, "urgency", 0.0), 0.0, 1.0)

    sig = (w_mag * mag) + (w_ano * ano) + (w_ctx * ctx) + (w_urg * urg)
    sig += random.uniform(-0.03, 0.03)
    return clamp(sig, 0.0, 1.0)


def gate_probability(sig: float, threshold: float, temperature: float) -> float:
    if temperature <= 0.0:  # hard gate
        return 1.0 if sig >= threshold else 0.0
    t = max(1e-6, temperature)
    z = (sig - threshold) / t
    return 1.0 / (1.0 + math.exp(-z))


def gate_probability_with_hysteresis(
    sig: float,
    threshold: float,
    temperature: float,
    last_activation: bool,
    hysteresis_gap: float = 0.02
) -> float:
    """
    Gating with hysteresis to prevent oscillations.

    Args:
        sig: Significance score [0,1]
        threshold: Current threshold [0,1]
        temperature: Gate temperature (0=hard, >0=soft)
        last_activation: Whether last event was activated
        hysteresis_gap: Gap between open/close thresholds

    Returns:
        Probability of activation [0,1]
    """
    if temperature <= 0.0:  # hard gate with hysteresis
        if last_activation:
            # Once activated, need to drop below (threshold - gap) to deactivate
            return 1.0 if sig >= (threshold - hysteresis_gap) else 0.0
        else:
            # When inactive, need to exceed threshold to activate
            return 1.0 if sig >= threshold else 0.0

    # Soft gate with hysteresis
    effective_threshold = threshold
    if last_activation:
        effective_threshold -= hysteresis_gap / 2.0  # Easier to stay active
    else:
        effective_threshold += hysteresis_gap / 2.0  # Harder to activate

    t = max(1e-6, temperature)
    z = (sig - effective_threshold) / t
    return 1.0 / (1.0 + math.exp(-z))
