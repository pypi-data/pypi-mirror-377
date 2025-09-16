# src/sundew/config.py
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Dict, Mapping, Tuple


@dataclass(slots=True)
class SundewConfig:
    """
    Configuration for the Sundew algorithm.

    Notes
    -----
    * Call :meth:`validate` to perform sanity checks.
    * Defaults reflect a conservative, energy-saving profile.
    * Field names and semantics are stable for external users.
    """

    # Activation & rate control
    activation_threshold: float = 0.78
    target_activation_rate: float = 0.15
    ema_alpha: float = 0.15  # Faster adaptation for better responsiveness

    # PI controller - improved stability
    adapt_kp: float = 0.012  # Reduced for smoother response
    adapt_ki: float = 0.004  # Lower integral gain to prevent windup
    error_deadband: float = 0.003  # Tighter deadband for precision
    integral_clamp: float = 0.30   # Reduced to prevent large corrections

    # Threshold bounds
    min_threshold: float = 0.20
    max_threshold: float = 0.92

    # Energy pressure & gating
    energy_pressure: float = 0.04
    gate_temperature: float = 0.08
    hysteresis_gap: float = 0.02  # Gap between activation/deactivation thresholds

    # Energy model
    max_energy: float = 100.0
    dormant_tick_cost: float = 0.5
    dormancy_regen: Tuple[float, float] = (1.0, 3.0)  # (min, max) regen per dormant tick
    eval_cost: float = 0.6
    base_processing_cost: float = 10.0

    # Significance weights (should sum to 1.0 for a convex combination)
    w_magnitude: float = 0.30
    w_anomaly: float = 0.40
    w_context: float = 0.20
    w_urgency: float = 0.10

    # Misc
    rng_seed: int = 42

    # Optional features
    refractory: int = 0         # ticks to sleep after activation
    probe_every: int = 0        # force a probe every N events (0 = off)

    # --------------------------- Validation & helpers ---------------------------

    def validate(self) -> None:
        """Raise ``ValueError`` if any checks fail."""
        _require_range(self.min_threshold, 0.0, 1.0, "min_threshold")
        _require_range(self.max_threshold, 0.0, 1.0, "max_threshold")
        if self.min_threshold > self.max_threshold:
            raise ValueError("min_threshold must be ≤ max_threshold within [0, 1].")

        if self.gate_temperature < 0.0:
            raise ValueError("gate_temperature must be non-negative.")

        _require_range(self.target_activation_rate, 0.0, 1.0, "target_activation_rate")
        _require_range(self.activation_threshold, 0.0, 1.0, "activation_threshold")

        # Starting threshold must lie within the permitted band.
        if not (self.min_threshold <= self.activation_threshold <= self.max_threshold):
            raise ValueError(
                "activation_threshold must lie within [min_threshold, max_threshold]."
            )

        # Non-negative scalars
        for name in (
            "ema_alpha",
            "adapt_kp",
            "adapt_ki",
            "error_deadband",
            "integral_clamp",
            "energy_pressure",
            "hysteresis_gap",
            "max_energy",
            "dormant_tick_cost",
            "eval_cost",
            "base_processing_cost",
            "w_magnitude",
            "w_anomaly",
            "w_context",
            "w_urgency",
        ):
            value = getattr(self, name)
            if value < 0:
                raise ValueError(f"{name} must be non-negative.")

        # Enforce convex combination for weights
        weight_sum = self.w_magnitude + self.w_anomaly + self.w_context + self.w_urgency
        if abs(weight_sum - 1.0) > 1e-6:
            raise ValueError(
                "w_magnitude + w_anomaly + w_context + w_urgency must sum to 1.0."
            )

        # Regen ordering and non-negativity
        regen_lo, regen_hi = self.dormancy_regen
        if regen_lo < 0.0 or regen_hi < 0.0 or regen_lo > regen_hi:
            raise ValueError(
                "dormancy_regen must be a non-negative (min, max) with min ≤ max."
            )

        # Optional feature knobs
        if self.refractory < 0:
            raise ValueError("refractory must be ≥ 0.")
        if self.probe_every < 0:
            raise ValueError("probe_every must be ≥ 0.")

    # --------------------------- Convenience methods ---------------------------

    def to_dict(self) -> Dict[str, Any]:
        """Lightweight dict serialization (stable field order not guaranteed)."""
        # Manual for speed & slots compatibility; avoids importing dataclasses.asdict
        return {
            "activation_threshold": self.activation_threshold,
            "target_activation_rate": self.target_activation_rate,
            "ema_alpha": self.ema_alpha,
            "adapt_kp": self.adapt_kp,
            "adapt_ki": self.adapt_ki,
            "error_deadband": self.error_deadband,
            "integral_clamp": self.integral_clamp,
            "min_threshold": self.min_threshold,
            "max_threshold": self.max_threshold,
            "energy_pressure": self.energy_pressure,
            "gate_temperature": self.gate_temperature,
            "hysteresis_gap": self.hysteresis_gap,
            "max_energy": self.max_energy,
            "dormant_tick_cost": self.dormant_tick_cost,
            "dormancy_regen": self.dormancy_regen,
            "eval_cost": self.eval_cost,
            "base_processing_cost": self.base_processing_cost,
            "w_magnitude": self.w_magnitude,
            "w_anomaly": self.w_anomaly,
            "w_context": self.w_context,
            "w_urgency": self.w_urgency,
            "rng_seed": self.rng_seed,
            "refractory": self.refractory,
            "probe_every": self.probe_every,
        }

    @classmethod
    def from_dict(cls, cfg: Mapping[str, Any]) -> SundewConfig:
        """
        Create a config from a mapping, ignoring unknown keys.
        Does *not* call :meth:`validate` automatically.
        """
        known: Dict[str, Any] = {k: cfg[k] for k in _CONFIG_KEYS if k in cfg}
        return cls(**known)

    def with_overrides(self, **updates: Any) -> SundewConfig:
        """Return a copy with the given field overrides."""
        return replace(self, **updates)

    def weights(self) -> Tuple[float, float, float, float]:
        """Return (w_magnitude, w_anomaly, w_context, w_urgency)."""
        return (self.w_magnitude, self.w_anomaly, self.w_context, self.w_urgency)


# Known keys for from_dict; kept separate to avoid reflection at runtime.
_CONFIG_KEYS: Tuple[str, ...] = (
    "activation_threshold",
    "target_activation_rate",
    "ema_alpha",
    "adapt_kp",
    "adapt_ki",
    "error_deadband",
    "integral_clamp",
    "min_threshold",
    "max_threshold",
    "energy_pressure",
    "gate_temperature",
    "hysteresis_gap",
    "max_energy",
    "dormant_tick_cost",
    "dormancy_regen",
    "eval_cost",
    "base_processing_cost",
    "w_magnitude",
    "w_anomaly",
    "w_context",
    "w_urgency",
    "rng_seed",
    "refractory",
    "probe_every",
)


def _require_range(x: float, lo: float, hi: float, name: str) -> None:
    if not (lo <= x <= hi):
        raise ValueError(f"{name} must be in [{lo}, {hi}].")
