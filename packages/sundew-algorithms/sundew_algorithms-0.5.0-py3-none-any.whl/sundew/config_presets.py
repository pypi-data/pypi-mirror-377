from __future__ import annotations

from dataclasses import replace
from typing import Any, Callable, Dict, Final, Mapping

from .config import SundewConfig


def _clone(cfg: SundewConfig, **updates: Any) -> SundewConfig:
    """Return a copy of cfg with field overrides (typed & mypy-friendly)."""
    return replace(cfg, **updates)


# ---------------- Baseline ----------------


def _baseline() -> SundewConfig:
    """
    Former defaults used earlier in the project and in the first plots.
    Conservative and prone to under-activation (maximizes savings).
    """
    return SundewConfig(
        activation_threshold=0.70,
        target_activation_rate=0.25,
        ema_alpha=0.10,
        adapt_kp=0.06,
        adapt_ki=0.01,
        error_deadband=0.010,
        integral_clamp=0.50,
        min_threshold=0.30,
        max_threshold=0.95,
        energy_pressure=0.15,
        gate_temperature=0.00,  # hard gate
        max_energy=100.0,
        dormant_tick_cost=0.5,
        dormancy_regen=(1.0, 3.0),
        eval_cost=0.6,
        base_processing_cost=10.0,
        w_magnitude=0.30,
        w_anomaly=0.40,
        w_context=0.20,
        w_urgency=0.10,
        rng_seed=42,
        probe_every=200,
        refractory=0,
    )


# ---------------- Tuned v1 ----------------


def _tuned_v1() -> SundewConfig:
    """First PI iteration that softened pressure and improved activation rate."""
    return SundewConfig(
        activation_threshold=0.70,
        target_activation_rate=0.25,
        ema_alpha=0.10,
        adapt_kp=0.06,
        adapt_ki=0.01,
        error_deadband=0.010,
        integral_clamp=0.50,
        min_threshold=0.20,
        max_threshold=0.90,
        energy_pressure=0.05,
        gate_temperature=0.10,
        max_energy=100.0,
        dormant_tick_cost=0.5,
        dormancy_regen=(1.0, 3.0),
        eval_cost=0.6,
        base_processing_cost=10.0,
        w_magnitude=0.30,
        w_anomaly=0.40,
        w_context=0.20,
        w_urgency=0.10,
        rng_seed=42,
        probe_every=0,
        refractory=0,
    )


# ---------------- Tuned v2 (recommended) ----------------


def _tuned_v2() -> SundewConfig:
    """
    Recommended general-purpose settings:
    - slightly higher gains, smaller deadband
    - softer energy pressure
    - tighter max_threshold to avoid hard-pegging
    """
    return SundewConfig(
        activation_threshold=0.70,
        target_activation_rate=0.25,
        ema_alpha=0.10,
        adapt_kp=0.08,  # up from 0.06
        adapt_ki=0.02,  # up from 0.01
        error_deadband=0.005,  # down from 0.01
        integral_clamp=0.50,
        min_threshold=0.20,  # down from 0.30
        max_threshold=0.90,  # down from 0.95
        energy_pressure=0.03,  # softer conservation pressure
        gate_temperature=0.10,
        max_energy=100.0,
        dormant_tick_cost=0.5,
        dormancy_regen=(1.0, 3.0),
        eval_cost=0.6,
        base_processing_cost=10.0,
        w_magnitude=0.30,
        w_anomaly=0.40,
        w_context=0.20,
        w_urgency=0.10,
        rng_seed=42,
        probe_every=0,
        refractory=0,
    )


# ---------------- ECG-focused ----------------


def _ecg_v1() -> SundewConfig:
    """
    ECG-oriented trade-off:
    - Lower starting threshold & softer gate to raise recall
    - Slightly faster controller
    - Bias significance toward anomaly/context
    """
    return SundewConfig(
        activation_threshold=0.60,
        target_activation_rate=0.12,
        ema_alpha=0.08,
        adapt_kp=0.09,
        adapt_ki=0.02,
        error_deadband=0.005,
        integral_clamp=0.50,
        min_threshold=0.45,
        max_threshold=0.95,
        energy_pressure=0.08,
        gate_temperature=0.12,
        max_energy=100.0,
        dormant_tick_cost=0.5,
        dormancy_regen=(1.0, 3.0),
        eval_cost=0.6,
        base_processing_cost=10.0,
        w_magnitude=0.20,
        w_anomaly=0.50,
        w_context=0.20,
        w_urgency=0.10,
        rng_seed=42,
        probe_every=0,
        refractory=0,
    )


def _ecg_mitbih_best() -> SundewConfig:
    """Frozen ‘best trade-off’ from an MIT-BIH sweep."""
    return SundewConfig(
        activation_threshold=0.65,
        target_activation_rate=0.13,
        ema_alpha=0.10,
        adapt_kp=0.08,
        adapt_ki=0.02,
        error_deadband=0.005,
        integral_clamp=0.50,
        min_threshold=0.45,
        max_threshold=0.90,
        energy_pressure=0.05,
        gate_temperature=0.12,
        max_energy=100.0,
        dormant_tick_cost=0.5,
        dormancy_regen=(1.0, 3.0),
        eval_cost=0.6,
        base_processing_cost=10.0,
        w_magnitude=0.20,
        w_anomaly=0.50,
        w_context=0.20,
        w_urgency=0.10,
        rng_seed=42,
        probe_every=0,
        refractory=0,
    )


# ---------------- Variants ----------------


def _aggressive() -> SundewConfig:
    """Faster to hit target; more activations; lower energy savings."""
    return _clone(
        _tuned_v2(),
        adapt_kp=0.12,
        adapt_ki=0.04,
        error_deadband=0.003,
        energy_pressure=0.02,
        gate_temperature=0.15,
        max_threshold=0.88,
    )


def _conservative() -> SundewConfig:
    """Maximize savings (will under-activate in quiet streams)."""
    return _clone(
        _tuned_v2(),
        adapt_kp=0.05,
        adapt_ki=0.01,
        error_deadband=0.010,
        energy_pressure=0.05,
        gate_temperature=0.05,
        min_threshold=0.25,
        max_threshold=0.92,
    )


def _high_temp() -> SundewConfig:
    """Probe/explore more (useful for anomaly-heavy streams)."""
    return _clone(_tuned_v2(), gate_temperature=0.20, energy_pressure=0.025)


def _low_temp() -> SundewConfig:
    """Nearly hard gate; sharper selectivity."""
    return _clone(_tuned_v2(), gate_temperature=0.00, energy_pressure=0.035)


def _energy_saver() -> SundewConfig:
    """Prioritize battery; accept lower activation rate."""
    return _clone(
        _tuned_v2(),
        energy_pressure=0.08,
        adapt_kp=0.06,
        adapt_ki=0.01,
        max_threshold=0.92,
        gate_temperature=0.05,
    )


def _target_0p30() -> SundewConfig:
    """Convenience preset for a higher target activation rate."""
    return _clone(_tuned_v2(), target_activation_rate=0.30)


def _auto_tuned() -> SundewConfig:
    """
    Auto-tuned preset based on control system analysis:
    - Unstuck threshold (max_threshold=0.88)
    - Faster EMA tracking (ema_alpha=0.25) - balanced for stability
    - Reduced hysteresis (hysteresis_gap=0.02)
    - More aggressive controller gains for better tracking
    - Better selectivity (temperature=0.12)
    """
    return SundewConfig(
        # Core auto-tuned parameters - more aggressive for better activation
        activation_threshold=0.50,  # Lower starting threshold
        target_activation_rate=0.15,  # Higher target rate
        ema_alpha=0.25,  # Fast but stable EMA tracking

        # More responsive controller for better tracking
        adapt_kp=0.020,  # Higher proportional gain
        adapt_ki=0.008,  # Moderate integral gain
        error_deadband=0.005,
        integral_clamp=0.25,  # Prevent windup near bounds

        # Unstick threshold but allow more range
        min_threshold=0.15,
        max_threshold=0.88,  # Prevent saturation

        # Better selectivity
        energy_pressure=0.03,  # Reduced pressure for more activation
        gate_temperature=0.12,  # More responsive gating
        hysteresis_gap=0.02,  # Reduced over-damping

        # Standard energy model
        max_energy=100.0,
        dormant_tick_cost=0.5,
        dormancy_regen=(1.0, 3.0),
        eval_cost=0.6,
        base_processing_cost=10.0,

        # Balanced significance weights
        w_magnitude=0.30,
        w_anomaly=0.40,
        w_context=0.20,
        w_urgency=0.10,

        rng_seed=42,
        probe_every=0,
        refractory=0,
    )


# ---------------- Registry & helpers ----------------

_PRESETS: Final[Dict[str, Callable[[], SundewConfig]]] = {
    "baseline": _baseline,
    "tuned_v1": _tuned_v1,
    "tuned_v2": _tuned_v2,  # current general recommendation
    "auto_tuned": _auto_tuned,  # auto-tuner optimized preset
    "ecg_v1": _ecg_v1,  # ECG-focused generic preset
    "ecg_mitbih_best": _ecg_mitbih_best,
    "aggressive": _aggressive,
    "conservative": _conservative,
    "high_temp": _high_temp,
    "low_temp": _low_temp,
    "energy_saver": _energy_saver,
    "target_0p30": _target_0p30,
}


def list_presets() -> list[str]:
    """Return a sorted list of available preset names."""
    return sorted(_PRESETS.keys())


def get_preset(name: str, overrides: Mapping[str, Any] | None = None) -> SundewConfig:
    """
    Return a :class:`SundewConfig` for the named preset.

    Optionally override fields:

        cfg = get_preset("tuned_v2", overrides={"target_activation_rate": 0.30})

    Raises
    ------
    KeyError
        If the preset name is unknown.
    AttributeError
        If an override key is not a field on :class:`SundewConfig`.
    """
    try:
        cfg = _PRESETS[name]()  # build
    except KeyError as e:
        raise KeyError(f"Unknown preset '{name}'. Available: {list_presets()}") from e

    if overrides:
        for k, v in overrides.items():
            if not hasattr(cfg, k):
                raise AttributeError(f"SundewConfig has no field '{k}'")
            setattr(cfg, k, v)
    return cfg
