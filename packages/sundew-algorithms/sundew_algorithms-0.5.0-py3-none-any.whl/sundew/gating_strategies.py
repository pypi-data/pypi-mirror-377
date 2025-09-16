# src/sundew/gating_strategies.py
"""
Concrete implementations of gating strategies.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Any, Dict, List

import numpy as np

from .interfaces import ControlState, GatingDecision, GatingStrategy, ProcessingContext


@dataclass
class TemperatureGatingConfig:
    """Configuration for temperature-based gating."""

    base_temperature: float = 0.08
    exploration_rate: float = 0.05
    temperature_decay: float = 0.999
    min_temperature: float = 0.001
    adaptive_temperature: bool = True


class TemperatureGatingStrategy(GatingStrategy):
    """Temperature-based sigmoid gating (current Sundew approach)."""

    def __init__(self, config: TemperatureGatingConfig):
        self.config = config
        self.current_temperature = config.base_temperature
        self.decision_count = 0

    def gate(
        self,
        significance: float,
        threshold: float,
        context: ProcessingContext,
        control_state: ControlState
    ) -> GatingDecision:
        """Make gating decision using temperature-controlled sigmoid."""

        # Adapt temperature based on system state
        if self.config.adaptive_temperature:
            self._update_temperature(control_state)

        # Compute gating probability
        if self.current_temperature <= 1e-9:
            # Hard gating
            probability = 1.0 if significance >= threshold else 0.0
        else:
            # Soft gating with temperature
            z = (significance - threshold) / max(self.current_temperature, 1e-9)
            probability = 1.0 / (1.0 + math.exp(-np.clip(z, -500, 500)))

        # Add exploration
        exploration_prob = self.get_exploration_probability(control_state)
        if random.random() < exploration_prob:
            probability = random.random()

        # Make binary decision
        should_process = random.random() < probability

        # Create decision object
        decision = GatingDecision(
            should_process=should_process,
            confidence=abs(probability - 0.5) * 2,  # Distance from uncertain (0.5)
            significance=significance,
            reasoning={
                "gating_type": "temperature",
                "probability": probability,
                "temperature": self.current_temperature,
                "threshold": threshold,
                "significance": significance,
                "exploration_used": random.random() < exploration_prob,
                "z_score": (significance - threshold) / max(self.current_temperature, 1e-9)
            }
        )

        self.decision_count += 1
        return decision

    def _update_temperature(self, control_state: ControlState):
        """Adapt temperature based on system performance."""
        # Decrease temperature over time (annealing)
        self.current_temperature *= self.config.temperature_decay
        self.current_temperature = max(self.current_temperature, self.config.min_temperature)

        # Increase temperature if system is unstable
        stability_score = control_state.stability_metrics.get("oscillation", 0.0)
        if stability_score > 0.1:  # High oscillation
            self.current_temperature *= 1.1

        # Increase temperature if energy is low (more conservative)
        if control_state.energy_level < 0.3:
            self.current_temperature *= 1.05

    def get_exploration_probability(self, control_state: ControlState) -> float:
        """Compute exploration probability based on system state."""
        base_exploration = self.config.exploration_rate

        # Increase exploration early in learning
        if self.decision_count < 1000:
            base_exploration *= 2.0

        # Increase exploration if activation rate is far from target
        rate_error = abs(control_state.activation_rate - 0.15)  # Assume target ~0.15
        if rate_error > 0.05:
            base_exploration *= (1.0 + rate_error)

        return min(base_exploration, 0.2)  # Cap at 20%


@dataclass
class AdaptiveGatingConfig:
    """Configuration for adaptive attention-based gating."""

    attention_dim: int = 16
    context_window: int = 20
    confidence_threshold: float = 0.8
    uncertainty_penalty: float = 0.1
    multi_objective_weights: Dict[str, float] = None
    learning_rate: float = 0.01

    def __post_init__(self):
        if self.multi_objective_weights is None:
            self.multi_objective_weights = {
                "accuracy": 0.4,
                "energy": 0.3,
                "latency": 0.2,
                "fairness": 0.1
            }


class AdaptiveGatingStrategy(GatingStrategy):
    """
    Advanced gating strategy using attention mechanisms and multi-objective optimization.
    Learns to balance accuracy, energy efficiency, latency, and fairness.
    """

    def __init__(self, config: AdaptiveGatingConfig):
        self.config = config

        # Initialize attention network (simplified)
        self.attention_weights = np.random.randn(4, config.attention_dim) * 0.1
        self.context_weights = np.random.randn(config.attention_dim, 1) * 0.1

        # History buffers
        self.context_history: List[np.ndarray] = []
        self.decision_history: List[Dict[str, Any]] = []

        # Performance tracking
        self.performance_metrics = {
            "accuracy": 0.5,
            "energy_efficiency": 0.5,
            "latency": 0.5,
            "fairness": 0.5
        }

        # Learning state
        self.update_count = 0

    def gate(
        self,
        significance: float,
        threshold: float,
        context: ProcessingContext,
        control_state: ControlState
    ) -> GatingDecision:
        """Make gating decision using attention-based multi-objective optimization."""

        # Extract context features
        context_vector = self._extract_context_features(context, control_state)

        # Update context history
        self.context_history.append(context_vector.copy())
        if len(self.context_history) > self.config.context_window:
            self.context_history.pop(0)

        # Compute attention-weighted decision
        if len(self.context_history) > 1:
            attention_score = self._compute_attention_score(context_vector)
            confidence = self._compute_confidence(context_vector, attention_score)
        else:
            attention_score = significance
            confidence = 0.5

        # Multi-objective decision making
        decision_score = self._multi_objective_scoring(
            significance, attention_score, confidence, control_state
        )

        # Uncertainty-aware thresholding
        effective_threshold = self._adjust_threshold_for_uncertainty(
            threshold, confidence, control_state
        )

        # Make decision
        should_process = decision_score >= effective_threshold

        # Create detailed decision object
        decision = GatingDecision(
            should_process=should_process,
            confidence=confidence,
            significance=significance,
            reasoning={
                "gating_type": "adaptive_attention",
                "raw_significance": significance,
                "attention_score": attention_score,
                "decision_score": decision_score,
                "effective_threshold": effective_threshold,
                "confidence": confidence,
                "multi_objective_scores": self._get_objective_scores(context_vector, control_state),
                "attention_weights": self.attention_weights.tolist(),
                "context_features": context_vector.tolist()
            }
        )

        # Store decision for learning
        self.decision_history.append({
            "context": context_vector,
            "decision": should_process,
            "significance": significance,
            "timestamp": context.timestamp
        })

        if len(self.decision_history) > self.config.context_window * 2:
            self.decision_history.pop(0)

        self.update_count += 1
        return decision

    def _extract_context_features(
        self,
        context: ProcessingContext,
        control_state: ControlState
    ) -> np.ndarray:
        """Extract relevant features for attention mechanism."""
        features = context.features

        # Basic features (normalized)
        basic_features = np.array([
            min(1.0, features.get("magnitude", 0.0) / 100.0),
            min(1.0, features.get("anomaly_score", 0.0)),
            min(1.0, features.get("context_relevance", 0.0)),
            min(1.0, features.get("urgency", 0.0))
        ])

        # System state features
        system_features = np.array([
            control_state.activation_rate,
            control_state.energy_level,
            control_state.threshold,
            len(self.context_history) / self.config.context_window
        ])

        # Temporal features
        temporal_features = np.array([
            context.sequence_id % 100 / 100.0,  # Position in sequence
            len(context.history) / 10.0,  # History length
        ])

        # Combine all features
        return np.concatenate([basic_features, system_features, temporal_features])

    def _compute_attention_score(self, context_vector: np.ndarray) -> float:
        """Compute attention-weighted significance score."""
        if len(self.context_history) < 2:
            return 0.5

        # Simple attention mechanism
        # In practice, would use more sophisticated transformer-style attention

        # Compute attention weights for historical context
        history_matrix = np.array(self.context_history[:-1])  # Exclude current

        # Simplified dot-product attention
        attention_scores = np.dot(history_matrix, context_vector[:len(history_matrix[0])])
        attention_weights = self._softmax(attention_scores)

        # Weighted combination
        weighted_history = np.dot(attention_weights, history_matrix)

        # Combine with current context
        combined_context = 0.7 * context_vector[:len(weighted_history)] + 0.3 * weighted_history

        # Project to scalar score
        score = np.dot(combined_context, self.context_weights[:len(combined_context)].flatten())
        return float(np.clip(score, 0.0, 1.0))

    def _compute_confidence(self, context_vector: np.ndarray, attention_score: float) -> float:
        """Compute confidence in the gating decision."""
        if len(self.context_history) < 2:
            return 0.5

        # Measure consistency with recent decisions
        recent_scores = [
            self.decision_history[i].get("significance", 0.5)
            for i in range(max(0, len(self.decision_history) - 5), len(self.decision_history))
        ]

        if len(recent_scores) > 1:
            score_variance = np.var(recent_scores)
            consistency = 1.0 / (1.0 + score_variance)
        else:
            consistency = 0.5

        # Combine with attention strength
        attention_strength = abs(attention_score - 0.5) * 2

        confidence = 0.6 * consistency + 0.4 * attention_strength
        return float(np.clip(confidence, 0.0, 1.0))

    def _multi_objective_scoring(
        self,
        significance: float,
        attention_score: float,
        confidence: float,
        control_state: ControlState
    ) -> float:
        """Compute multi-objective decision score."""
        weights = self.config.multi_objective_weights

        # Accuracy objective (based on significance)
        accuracy_score = 0.7 * significance + 0.3 * attention_score

        # Energy efficiency objective
        energy_score = 1.0 - (1.0 - control_state.energy_level) * 0.5

        # Latency objective (prefer quick decisions)
        latency_score = confidence  # High confidence = quick decision

        # Fairness objective (balance activation across time)
        fairness_score = 1.0 - abs(control_state.activation_rate - 0.15) * 2

        # Weighted combination
        combined_score = (
            weights["accuracy"] * accuracy_score +
            weights["energy"] * energy_score +
            weights["latency"] * latency_score +
            weights["fairness"] * fairness_score
        )

        return float(np.clip(combined_score, 0.0, 1.0))

    def _adjust_threshold_for_uncertainty(
        self,
        base_threshold: float,
        confidence: float,
        control_state: ControlState
    ) -> float:
        """Adjust threshold based on uncertainty and system state."""
        # Higher threshold when confidence is low (more conservative)
        uncertainty_adjustment = (1.0 - confidence) * self.config.uncertainty_penalty

        # Adjust based on energy level
        energy_adjustment = 0.0
        if control_state.energy_level < 0.3:
            energy_adjustment = 0.1 * (0.3 - control_state.energy_level)

        adjusted_threshold = base_threshold + uncertainty_adjustment + energy_adjustment
        return float(np.clip(adjusted_threshold, 0.0, 1.0))

    def _get_objective_scores(
        self,
        context_vector: np.ndarray,
        control_state: ControlState
    ) -> Dict[str, float]:
        """Get individual objective scores for interpretability."""
        return {
            "predicted_accuracy": float(np.clip(np.dot(context_vector[:4], [0.3, 0.4, 0.2, 0.1]), 0.0, 1.0)),
            "energy_efficiency": float(control_state.energy_level),
            "decision_confidence": float(self._compute_confidence(context_vector, 0.5)),
            "system_stability": float(1.0 - control_state.stability_metrics.get("oscillation", 0.0))
        }

    def _softmax(self, x: np.ndarray) -> np.ndarray:
        """Numerically stable softmax."""
        exp_x = np.exp(x - np.max(x))
        return exp_x / np.sum(exp_x)

    def get_exploration_probability(self, control_state: ControlState) -> float:
        """Dynamic exploration based on learning progress."""
        base_exploration = 0.1

        # Increase exploration if performance is poor
        avg_performance = np.mean(list(self.performance_metrics.values()))
        if avg_performance < 0.6:
            base_exploration *= 2.0

        # Decay exploration over time
        decay_factor = math.exp(-self.update_count / 10000.0)

        return base_exploration * decay_factor
