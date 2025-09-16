# src/sundew/core.py
from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .config import SundewConfig
from .energy import EnergyAccount
from .gating import gate_probability_with_hysteresis


@dataclass(slots=True)
class ProcessingResult:
    """Record returned when an event is processed (activated)."""

    significance: float
    processing_time: float
    energy_consumed: float


@dataclass(slots=True)
class Metrics:
    """Minimal metrics container (queried by demo/tests)."""

    ema_activation_rate: float = 0.0
    processed: int = 0
    activated: int = 0
    total_processing_time: float = 0.0

    # Enhanced energy tracking - fix for energy accounting mismatch
    cumulative_energy_spent: float = 0.0
    cumulative_energy_recovered: float = 0.0
    energy_spent_on_processing: float = 0.0
    energy_spent_on_dormancy: float = 0.0

    # Cap-aware energy management metrics - Phase 1
    max_cap_streak: int = 0
    max_low_streak: int = 0
    total_cap_events: int = 0
    total_low_events: int = 0
    cap_nudges_applied: int = 0
    low_nudges_applied: int = 0

    # Dual rate metrics system - Phase 1
    ema_activation_rate_slow: float = 0.0  # Slower EMA for stability

    # Enhanced telemetry and debugging - Phase 1
    threshold_history: List[float] = field(default_factory=list)
    activation_history: List[bool] = field(default_factory=list)
    energy_history: List[float] = field(default_factory=list)
    significance_history: List[float] = field(default_factory=list)
    controller_error_history: List[float] = field(default_factory=list)
    gating_decision_history: List[Dict[str, float]] = field(default_factory=list)


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _safe_get(d: Dict[str, Any], key: str, default: float = 0.0) -> float:
    try:
        return float(d.get(key, default))
    except Exception:
        return float(default)


class SundewAlgorithm:
    """
    Sundew reference implementation with PI control, energy pressure, and gating.
    Includes deterministic probe cadence and optional refractory cooldown.
    """

    def __init__(self, config: SundewConfig) -> None:
        config.validate()
        self.cfg = config

        # Threshold/controller state
        self.threshold: float = float(self.cfg.activation_threshold)
        self._int_err: float = 0.0

        # Hysteresis for stability - use config value
        self._hysteresis_gap: float = float(self.cfg.hysteresis_gap)
        self._last_activation: bool = False

        # Cap-aware energy management - Phase 1 Quick Win
        self._cap_streak: int = 0  # Count of consecutive events at energy cap
        self._low_streak: int = 0  # Count of consecutive events at low energy
        self._cap_threshold: float = 95.0  # Energy level considered "at cap"
        self._low_threshold: float = 80.0  # Energy level considered "low"
        self._cap_nudge: float = 0.003  # Threshold decrease when at cap
        self._low_nudge: float = 0.001  # Threshold increase when low

        # AI-MD Controller - Phase 1 Quick Win
        self._use_aimd: bool = getattr(self.cfg, "use_aimd_controller", True)
        self._aimd_additive_increase: float = 0.003  # Add to threshold on dormant
        self._aimd_multiplicative_decrease: float = 0.98  # Multiply threshold after activation

        # Metrics
        self.metrics: Metrics = Metrics(ema_activation_rate=0.0)

        # Hot-path cache
        self._ema_alpha: float = float(self.cfg.ema_alpha)
        self._kp: float = float(self.cfg.adapt_kp)
        self._ki: float = float(self.cfg.adapt_ki)
        self._dead: float = float(self.cfg.error_deadband)
        self._min_thr: float = float(self.cfg.min_threshold)
        self._max_thr: float = float(self.cfg.max_threshold)
        self._press: float = float(self.cfg.energy_pressure)
        self._temp: float = float(self.cfg.gate_temperature)

        self._eval_cost: float = float(self.cfg.eval_cost)
        self._base_cost: float = float(self.cfg.base_processing_cost)
        self._dorm_cost: float = float(self.cfg.dormant_tick_cost)
        self._regen_min, self._regen_max = self.cfg.dormancy_regen

        # Optional extras
        self._probe_every_cfg: int = int(getattr(self.cfg, "probe_every", 0) or 0)
        self._refractory_cfg: int = int(getattr(self.cfg, "refractory", 0) or 0)
        self._refractory_left: int = 0

        # Effective probe cadence (never 0). Default to 100 if unset.
        self._eff_probe_every: int = max(1, (self._probe_every_cfg or 100))

        # Energy account
        max_e = float(self.cfg.max_energy)
        self.energy: EnergyAccount = EnergyAccount(max_e, max_e)

        # RNG (for probabilistic gating)
        random.seed(int(self.cfg.rng_seed))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def process(self, x: Dict[str, Any]) -> Optional[ProcessingResult]:
        self.metrics.processed += 1

        # Deterministic probe
        force_probe = self.metrics.processed == 1 or (
            self._eff_probe_every > 0 and (self.metrics.processed % self._eff_probe_every == 0)
        )

        # Respect refractory only when not forcing a probe
        if not force_probe and self._refractory_left > 0:
            self._refractory_left -= 1
            self._tick_dormant_energy()
            self._adapt_threshold(activated=False)
            return None

        sig = self._compute_significance(x)

        # Gate decision with hysteresis to reduce oscillations
        if force_probe:
            activated = True
            gate_prob = 1.0
        else:
            # Use hysteresis-enabled gating for better stability
            gate_prob = gate_probability_with_hysteresis(
                sig,
                self.threshold,
                max(self._temp, 1e-9),
                self._last_activation,
                self._hysteresis_gap,
            )
            activated = random.random() < gate_prob

        # Enhanced telemetry collection - Phase 1
        current_energy = float(getattr(self.energy, "value", 0.0))
        self._collect_telemetry(sig, activated, gate_prob, current_energy, x)

        if not activated:
            self._last_activation = False  # Update hysteresis state
            self._tick_dormant_energy()
            self._adapt_threshold(activated=False)
            return None

        # Activated
        self._last_activation = True  # Update hysteresis state
        start = time.perf_counter()
        proc_time = 0.001 + 0.001 * (1.0 + sig)  # ~1–2 ms
        _ = start + proc_time  # shape only; no sleep

        energy_used = self._eval_cost + self._base_cost * (0.8 + 0.4 * sig)
        self._spend_energy(energy_used)

        self.metrics.activated += 1
        self.metrics.total_processing_time += proc_time

        if self._refractory_cfg > 0:
            self._refractory_left = self._refractory_cfg

        self._adapt_threshold(activated=True)

        return ProcessingResult(
            significance=float(sig),
            processing_time=float(proc_time),
            energy_consumed=float(energy_used),
        )

    def report(self) -> Dict[str, Any]:
        n = max(1, self.metrics.processed)
        act_rate = self.metrics.activated / n
        avg_pt = (
            (self.metrics.total_processing_time / self.metrics.activated)
            if self.metrics.activated
            else 0.0
        )

        energy_remaining = float(getattr(self.energy, "value", 0.0))

        baseline_energy_cost = n * (self._eval_cost + self._base_cost)
        actual_energy_cost = (
            self.metrics.activated * (self._eval_cost + self._base_cost)
            + (n - self.metrics.activated) * self._dorm_cost
        )
        savings_pct = (
            (1.0 - (actual_energy_cost / baseline_energy_cost)) * 100.0
            if baseline_energy_cost > 0
            else 0.0
        )

        # Fix energy accounting - use actual tracked spending
        net_energy_consumed = (
            self.metrics.cumulative_energy_spent - self.metrics.cumulative_energy_recovered
        )
        energy_efficiency = (
            1.0 - (actual_energy_cost / baseline_energy_cost) if baseline_energy_cost > 0 else 0.0
        )

        # EMA debugging info - convert to percentage for comparison
        ema_rate_pct = self.metrics.ema_activation_rate * 100.0
        ema_discrepancy = abs(act_rate * 100.0 - ema_rate_pct)

        # Controller stability metrics
        threshold_utilization = (self.threshold - self._min_thr) / max(
            0.001, self._max_thr - self._min_thr
        )
        energy_at_cap_pct = 100.0 if energy_remaining >= self.cfg.max_energy * 0.99 else 0.0

        # Dual rate metrics: Determine which EMA is being used for control
        energy_fraction = energy_remaining / float(self.cfg.max_energy)
        using_slow_ema = energy_fraction >= 0.95

        return {
            "total_inputs": int(self.metrics.processed),
            "activations": int(self.metrics.activated),
            "activation_rate": float(act_rate),
            "ema_activation_rate": float(self.metrics.ema_activation_rate),
            "ema_activation_rate_slow": float(
                self.metrics.ema_activation_rate_slow
            ),  # Dual rate metrics
            "ema_alpha": float(self._ema_alpha),  # Make EMA alpha explicit
            "ema_alpha_slow": 0.05,  # Slow EMA alpha
            "ema_using_slow_for_control": bool(using_slow_ema),  # Which EMA drives controller
            "ema_discrepancy": float(ema_discrepancy),  # Debug EMA vs actual rate
            "avg_processing_time": float(avg_pt),
            "total_energy_spent": float(self.metrics.cumulative_energy_spent),
            "net_energy_consumed": float(net_energy_consumed),
            "energy_recovered": float(self.metrics.cumulative_energy_recovered),
            "energy_remaining": float(energy_remaining),
            "energy_spent_processing": float(self.metrics.energy_spent_on_processing),
            "energy_spent_dormancy": float(self.metrics.energy_spent_on_dormancy),
            "energy_at_cap_pct": float(energy_at_cap_pct),  # Time at energy cap
            "threshold": float(self.threshold),
            "threshold_utilization": float(threshold_utilization),  # Threshold position in range
            "hysteresis_gap": float(self._hysteresis_gap),
            "baseline_energy_cost": float(baseline_energy_cost),
            "actual_energy_cost": float(actual_energy_cost),
            "estimated_energy_savings_pct": float(savings_pct),
            "energy_efficiency": float(energy_efficiency),
            # Controller debugging
            "controller_integral_error": float(self._int_err),
            "controller_kp": float(self._kp),
            "controller_ki": float(self._ki),
            # Cap-aware energy management metrics - Phase 1
            "cap_streak_current": self._cap_streak,
            "low_streak_current": self._low_streak,
            "max_cap_streak": self.metrics.max_cap_streak,
            "max_low_streak": self.metrics.max_low_streak,
            "total_cap_events": self.metrics.total_cap_events,
            "total_low_events": self.metrics.total_low_events,
            "cap_nudges_applied": self.metrics.cap_nudges_applied,
            "low_nudges_applied": self.metrics.low_nudges_applied,
            "cap_events_pct": float(self.metrics.total_cap_events)
            / max(1, self.metrics.processed)
            * 100,
            "low_events_pct": float(self.metrics.total_low_events)
            / max(1, self.metrics.processed)
            * 100,
            # Enhanced telemetry and debugging statistics - Phase 1
            "telemetry_samples": len(self.metrics.threshold_history),
            "significance_stats": self._compute_significance_stats(),
            "threshold_volatility": self._compute_threshold_volatility(),
            "controller_stability": self._compute_controller_stability(),
            "energy_efficiency_trend": self._compute_energy_trend(),
            "gating_decision_breakdown": self._compute_gating_breakdown(),
        }

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _compute_significance(self, x: Dict[str, Any]) -> float:
        mag = _safe_get(x, "magnitude", 0.0) / 100.0
        ano = _safe_get(x, "anomaly_score", 0.0)
        ctx = _safe_get(x, "context_relevance", 0.0)
        urg = _safe_get(x, "urgency", 0.0)
        s = (
            self.cfg.w_magnitude * mag
            + self.cfg.w_anomaly * ano
            + self.cfg.w_context * ctx
            + self.cfg.w_urgency * urg
        )
        return _clamp(s, 0.0, 1.0)

    def _adapt_threshold(self, activated: Optional[bool] = None) -> None:
        if activated is not None:
            obs = 1.0 if activated else 0.0
            a = self._ema_alpha
            self.metrics.ema_activation_rate = (
                a * obs + (1.0 - a) * self.metrics.ema_activation_rate
            )

            # Dual rate metrics: Slow EMA for stability (α=0.05)
            a_slow = 0.05
            self.metrics.ema_activation_rate_slow = (
                a_slow * obs + (1.0 - a_slow) * self.metrics.ema_activation_rate_slow
            )

        # Choose controller mode
        if self._use_aimd:
            self._adapt_threshold_aimd(activated)
        else:
            self._adapt_threshold_pi(activated)

    def _adapt_threshold_pi(self, activated: Optional[bool] = None) -> None:
        """Original PI controller with energy pressure."""
        # Dual rate metrics: Use slow EMA when energy is near cap to prevent fast EMA driving gating
        current_energy = float(getattr(self.energy, "value", 0.0))
        energy_fraction = current_energy / float(self.cfg.max_energy)

        if energy_fraction >= 0.95:  # Near capacity - use slow EMA for stability
            target_ema = self.metrics.ema_activation_rate_slow
        else:
            target_ema = self.metrics.ema_activation_rate

        err = float(self.cfg.target_activation_rate) - target_ema
        if abs(err) <= self._dead:
            err = 0.0

        # Enhanced telemetry: Collect controller error
        self.metrics.controller_error_history.append(err)

        self._int_err = _clamp(
            self._int_err + err, -self.cfg.integral_clamp, self.cfg.integral_clamp
        )

        delta = self._kp * err + self._ki * self._int_err

        press = self._press * (1.0 - _clamp(energy_fraction, 0.0, 1.0))

        # Cap-aware energy management - Phase 1 Quick Win
        cap_adjustment = self._apply_cap_aware_nudging(current_energy)

        self.threshold = _clamp(
            self.threshold - delta + press + cap_adjustment, self._min_thr, self._max_thr
        )

    def _adapt_threshold_aimd(self, activated: Optional[bool] = None) -> None:
        """AI-MD controller: Additive Increase, Multiplicative Decrease with energy awareness."""
        current_energy = float(getattr(self.energy, "value", 0.0))

        if activated is not None:
            if activated:
                # Multiplicative Decrease after activation
                self.threshold *= self._aimd_multiplicative_decrease
            else:
                # Additive Increase on dormant events
                self.threshold += self._aimd_additive_increase

        # Apply energy pressure (same as PI controller)
        frac = current_energy / float(self.cfg.max_energy)
        press = self._press * (1.0 - _clamp(frac, 0.0, 1.0))
        self.threshold += press

        # Apply cap-aware nudging
        cap_adjustment = self._apply_cap_aware_nudging(current_energy)
        self.threshold += cap_adjustment

        # Ensure bounds
        self.threshold = _clamp(self.threshold, self._min_thr, self._max_thr)

    def _apply_cap_aware_nudging(self, current_energy: float) -> float:
        """
        Apply cap-aware threshold nudging to better utilize energy capacity.

        - If energy ≥ 95 for ≥5 events → decrease threshold (encourage activation)
        - If energy ≤ 80 for ≥5 events → increase threshold (conserve energy)
        """
        adjustment = 0.0

        # Track energy cap streaks
        if current_energy >= self._cap_threshold:
            self._cap_streak += 1
            self._low_streak = 0
            self.metrics.total_cap_events += 1
            self.metrics.max_cap_streak = max(self.metrics.max_cap_streak, self._cap_streak)
        elif current_energy <= self._low_threshold:
            self._low_streak += 1
            self._cap_streak = 0
            self.metrics.total_low_events += 1
            self.metrics.max_low_streak = max(self.metrics.max_low_streak, self._low_streak)
        else:
            self._cap_streak = 0
            self._low_streak = 0

        # Apply nudging based on streaks
        if self._cap_streak >= 5:
            # At cap for 5+ events: decrease threshold to encourage activation
            adjustment = -self._cap_nudge
            self.metrics.cap_nudges_applied += 1
        elif self._low_streak >= 5:
            # Low energy for 5+ events: increase threshold to conserve energy
            adjustment = +self._low_nudge
            self.metrics.low_nudges_applied += 1

        return adjustment

    def _tick_dormant_energy(self) -> None:
        v = float(getattr(self.energy, "value", 0.0))

        # Track dormant costs
        dormant_cost = self._dorm_cost
        self.metrics.energy_spent_on_dormancy += dormant_cost
        self.metrics.cumulative_energy_spent += dormant_cost

        # Apply dormant cost
        v = max(0.0, v - dormant_cost)

        # Apply regeneration with smart tapering - Phase 1 Quick Win
        base_regen = random.uniform(self._regen_min, self._regen_max)

        # Taper regeneration near capacity to prevent overflow
        # Scale recovery by (1 - E/Cap)^γ, with γ=2.0
        energy_fraction = v / float(self.cfg.max_energy)
        taper_factor = (1.0 - energy_fraction) ** 2.0
        tapered_regen = base_regen * max(0.1, taper_factor)  # Minimum 10% regen

        self.metrics.cumulative_energy_recovered += tapered_regen
        v = min(float(self.cfg.max_energy), v + tapered_regen)

        self.energy.value = v

    def _spend_energy(self, amount: float) -> None:
        v = float(getattr(self.energy, "value", 0.0))
        actual_spent = min(amount, v)  # Can't spend more than we have

        # Track processing energy
        self.metrics.energy_spent_on_processing += actual_spent
        self.metrics.cumulative_energy_spent += actual_spent

        self.energy.value = max(0.0, v - actual_spent)

    def _collect_telemetry(
        self,
        significance: float,
        activated: bool,
        gate_prob: float,
        energy: float,
        features: Dict[str, Any],
    ) -> None:
        """Collect enhanced telemetry for debugging and analysis."""
        # Limit history size to prevent memory growth
        max_history = 1000

        # Update core histories
        self.metrics.threshold_history.append(self.threshold)
        self.metrics.activation_history.append(activated)
        self.metrics.energy_history.append(energy)
        self.metrics.significance_history.append(significance)

        # Gating decision details
        gating_decision = {
            "significance": significance,
            "threshold": self.threshold,
            "gate_probability": gate_prob,
            "activated": activated,
            "energy_fraction": energy / float(self.cfg.max_energy),
            "hysteresis_active": self._last_activation,
            "force_probe": self.metrics.processed == 1
            or (
                self._eff_probe_every > 0 and (self.metrics.processed % self._eff_probe_every == 0)
            ),
        }
        self.metrics.gating_decision_history.append(gating_decision)

        # Trim histories if they get too long
        if len(self.metrics.threshold_history) > max_history:
            self.metrics.threshold_history = self.metrics.threshold_history[-max_history:]
            self.metrics.activation_history = self.metrics.activation_history[-max_history:]
            self.metrics.energy_history = self.metrics.energy_history[-max_history:]
            self.metrics.significance_history = self.metrics.significance_history[-max_history:]
            self.metrics.gating_decision_history = self.metrics.gating_decision_history[
                -max_history:
            ]
            self.metrics.controller_error_history = self.metrics.controller_error_history[
                -max_history:
            ]

    def _compute_significance_stats(self) -> Dict[str, float]:
        """Compute significance score statistics."""
        if not self.metrics.significance_history:
            return {"mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0}

        import statistics

        hist = self.metrics.significance_history
        return {
            "mean": float(statistics.mean(hist)),
            "std": float(statistics.stdev(hist)) if len(hist) > 1 else 0.0,
            "min": float(min(hist)),
            "max": float(max(hist)),
        }

    def _compute_threshold_volatility(self) -> float:
        """Compute threshold volatility (standard deviation)."""
        if len(self.metrics.threshold_history) < 2:
            return 0.0

        import statistics

        return float(statistics.stdev(self.metrics.threshold_history))

    def _compute_controller_stability(self) -> Dict[str, float]:
        """Compute controller stability metrics."""
        if len(self.metrics.controller_error_history) < 2:
            return {"error_mean": 0.0, "error_std": 0.0, "oscillations": 0}

        import statistics

        errors = self.metrics.controller_error_history

        # Count oscillations (sign changes)
        oscillations = 0
        for i in range(1, len(errors)):
            if (errors[i] > 0) != (errors[i - 1] > 0):
                oscillations += 1

        return {
            "error_mean": float(statistics.mean(errors)),
            "error_std": float(statistics.stdev(errors)),
            "oscillations": oscillations,
        }

    def _compute_energy_trend(self) -> Dict[str, float]:
        """Compute energy efficiency trend."""
        if len(self.metrics.energy_history) < 10:
            return {"trend": 0.0, "efficiency": 0.0}

        # Simple linear trend of last 10 samples
        recent_energy = self.metrics.energy_history[-10:]
        trend = (recent_energy[-1] - recent_energy[0]) / len(recent_energy)

        # Energy efficiency: how well we maintain energy
        avg_energy = sum(recent_energy) / len(recent_energy)
        efficiency = avg_energy / float(self.cfg.max_energy)

        return {"trend": float(trend), "efficiency": float(efficiency)}

    def _compute_gating_breakdown(self) -> Dict[str, float]:
        """Compute gating decision breakdown."""
        if not self.metrics.gating_decision_history:
            return {"avg_gate_prob": 0.0, "force_probe_pct": 0.0, "hysteresis_influence": 0.0}

        recent_decisions = self.metrics.gating_decision_history[-50:]  # Last 50 decisions

        gate_probs = [d["gate_probability"] for d in recent_decisions]
        force_probes = sum(1 for d in recent_decisions if d.get("force_probe", False))
        hysteresis_active = sum(1 for d in recent_decisions if d.get("hysteresis_active", False))

        return {
            "avg_gate_prob": float(sum(gate_probs) / len(gate_probs)) if gate_probs else 0.0,
            "force_probe_pct": float(force_probes / len(recent_decisions)) * 100
            if recent_decisions
            else 0.0,
            "hysteresis_influence": float(hysteresis_active / len(recent_decisions)) * 100
            if recent_decisions
            else 0.0,
        }
