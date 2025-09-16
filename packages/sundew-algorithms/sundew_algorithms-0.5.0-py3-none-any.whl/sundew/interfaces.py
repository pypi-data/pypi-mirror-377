# src/sundew/interfaces.py
"""
Abstract interfaces for modular Sundew architecture.
Enables pluggable significance models, gating strategies, control policies, and energy models.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np


@dataclass
class ProcessingContext:
    """Context information available during processing."""

    timestamp: float
    sequence_id: int
    features: Dict[str, Any]
    history: List[Dict[str, Any]]  # Recent feature history
    metadata: Dict[str, Any]


@dataclass
class GatingDecision:
    """Result of a gating decision."""

    should_process: bool
    confidence: float
    significance: float
    reasoning: Dict[str, Any]  # For interpretability


@dataclass
class ControlState:
    """Current state of the control system."""

    threshold: float
    activation_rate: float
    energy_level: float
    error_integral: float
    stability_metrics: Dict[str, float]


class SignificanceModel(ABC):
    """Abstract interface for computing significance scores from input features."""

    @abstractmethod
    def compute_significance(
        self,
        context: ProcessingContext
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Compute significance score from input context.

        Args:
            context: Processing context with features and history

        Returns:
            Tuple of (significance_score, explanation_dict)
            significance_score: float in [0, 1]
            explanation_dict: Interpretability information
        """
        pass

    @abstractmethod
    def update(
        self,
        context: ProcessingContext,
        outcome: Optional[Dict[str, Any]]
    ) -> None:
        """
        Update model based on processing outcome (for learning models).

        Args:
            context: Original processing context
            outcome: Results of processing (accuracy, energy, etc.)
        """
        pass

    @abstractmethod
    def get_parameters(self) -> Dict[str, Any]:
        """Get current model parameters for serialization."""
        pass

    @abstractmethod
    def set_parameters(self, params: Dict[str, Any]) -> None:
        """Set model parameters for deserialization."""
        pass


class GatingStrategy(ABC):
    """Abstract interface for making gating decisions."""

    @abstractmethod
    def gate(
        self,
        significance: float,
        threshold: float,
        context: ProcessingContext,
        control_state: ControlState
    ) -> GatingDecision:
        """
        Make gating decision based on significance and current state.

        Args:
            significance: Significance score from SignificanceModel
            threshold: Current activation threshold
            context: Processing context
            control_state: Current control system state

        Returns:
            GatingDecision with processing decision and metadata
        """
        pass

    @abstractmethod
    def get_exploration_probability(self, control_state: ControlState) -> float:
        """Get current exploration probability for learning."""
        pass


class ControlPolicy(ABC):
    """Abstract interface for threshold adaptation and control."""

    @abstractmethod
    def update_threshold(
        self,
        current_state: ControlState,
        target_activation_rate: float,
        recent_activations: List[bool],
        energy_state: Dict[str, float]
    ) -> Tuple[float, ControlState]:
        """
        Update activation threshold based on recent performance.

        Args:
            current_state: Current control system state
            target_activation_rate: Desired activation rate
            recent_activations: Recent activation decisions
            energy_state: Current energy information

        Returns:
            Tuple of (new_threshold, updated_control_state)
        """
        pass

    @abstractmethod
    def predict_stability(
        self,
        current_state: ControlState,
        horizon: int = 100
    ) -> Dict[str, float]:
        """
        Predict system stability metrics over given horizon.

        Args:
            current_state: Current control system state
            horizon: Prediction horizon in time steps

        Returns:
            Dictionary of stability metrics (convergence_time, oscillation, etc.)
        """
        pass

    @abstractmethod
    def get_theoretical_bounds(self) -> Dict[str, Tuple[float, float]]:
        """Get theoretical performance bounds (convergence rate, stability region, etc.)."""
        pass


class EnergyModel(ABC):
    """Abstract interface for energy accounting and prediction."""

    @abstractmethod
    def compute_processing_cost(
        self,
        significance: float,
        processing_type: str,
        context: ProcessingContext
    ) -> float:
        """
        Compute energy cost for processing given input.

        Args:
            significance: Significance score of the input
            processing_type: Type of processing (e.g., 'inference', 'training')
            context: Processing context

        Returns:
            Energy cost in model-specific units
        """
        pass

    @abstractmethod
    def compute_idle_cost(self, duration: float) -> float:
        """Compute energy cost for idle/dormant period."""
        pass

    @abstractmethod
    def update_energy_state(
        self,
        current_energy: float,
        cost: float,
        regeneration: float = 0.0
    ) -> float:
        """Update energy state after consumption and regeneration."""
        pass

    @abstractmethod
    def predict_energy_trajectory(
        self,
        current_energy: float,
        predicted_activations: List[float],
        horizon: int
    ) -> List[float]:
        """
        Predict energy levels over time given activation pattern.

        Args:
            current_energy: Current energy level
            predicted_activations: Predicted activation probabilities
            horizon: Prediction horizon

        Returns:
            Predicted energy levels at each time step
        """
        pass

    @abstractmethod
    def get_energy_pressure(self, current_energy: float, max_energy: float) -> float:
        """Compute energy pressure term for control system."""
        pass


@dataclass
class ProcessingResult:
    """Result of processing an input sample."""

    activated: bool
    significance: float
    energy_consumed: float
    processing_time: float
    threshold_used: float
    explanation: Dict[str, Any]  # For interpretability
    component_metrics: Dict[str, Dict[str, float]]  # Per-component performance


# Convenience type aliases for complex signatures
FeatureVector = Union[Dict[str, Any], np.ndarray]
ActivationHistory = List[Tuple[float, bool, float]]  # (timestamp, activated, significance)
