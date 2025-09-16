# src/sundew/significance_models.py
"""
Concrete implementations of significance models.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .interfaces import ProcessingContext, SignificanceModel


@dataclass
class LinearSignificanceConfig:
    """Configuration for linear significance model."""

    w_magnitude: float = 0.30
    w_anomaly: float = 0.40
    w_context: float = 0.20
    w_urgency: float = 0.10
    noise_std: float = 0.01
    feature_normalization: bool = True


class LinearSignificanceModel(SignificanceModel):
    """Linear combination significance model (current Sundew approach)."""

    def __init__(self, config: LinearSignificanceConfig):
        self.config = config
        self.weights = np.array([
            config.w_magnitude,
            config.w_anomaly,
            config.w_context,
            config.w_urgency
        ])

        # Validate weights sum to 1.0
        if abs(self.weights.sum() - 1.0) > 1e-6:
            raise ValueError("Significance weights must sum to 1.0")

    def compute_significance(
        self,
        context: ProcessingContext
    ) -> Tuple[float, Dict[str, Any]]:
        """Compute linear combination of features."""
        features = context.features

        # Extract and normalize features
        magnitude = self._safe_get(features, "magnitude", 0.0)
        if self.config.feature_normalization:
            magnitude = magnitude / 100.0  # Assume magnitude is 0-100 scale

        anomaly = self._safe_get(features, "anomaly_score", 0.0)
        context_rel = self._safe_get(features, "context_relevance", 0.0)
        urgency = self._safe_get(features, "urgency", 0.0)

        # Clamp all features to [0, 1]
        feature_vector = np.array([
            np.clip(magnitude, 0.0, 1.0),
            np.clip(anomaly, 0.0, 1.0),
            np.clip(context_rel, 0.0, 1.0),
            np.clip(urgency, 0.0, 1.0)
        ])

        # Compute weighted sum
        significance = np.dot(self.weights, feature_vector)

        # Add small amount of noise for exploration
        if self.config.noise_std > 0:
            noise = np.random.normal(0, self.config.noise_std)
            significance += noise

        # Clamp to [0, 1]
        significance = np.clip(significance, 0.0, 1.0)

        # Create explanation
        explanation = {
            "model_type": "linear",
            "feature_contributions": {
                "magnitude": float(self.weights[0] * feature_vector[0]),
                "anomaly": float(self.weights[1] * feature_vector[1]),
                "context": float(self.weights[2] * feature_vector[2]),
                "urgency": float(self.weights[3] * feature_vector[3])
            },
            "raw_features": {
                "magnitude": float(feature_vector[0]),
                "anomaly": float(feature_vector[1]),
                "context": float(feature_vector[2]),
                "urgency": float(feature_vector[3])
            },
            "weights": self.weights.tolist()
        }

        return float(significance), explanation

    def update(
        self,
        context: ProcessingContext,
        outcome: Optional[Dict[str, Any]]
    ) -> None:
        """Linear model has no learning - no update needed."""
        pass

    def get_parameters(self) -> Dict[str, Any]:
        """Get model parameters."""
        return {
            "weights": self.weights.tolist(),
            "config": {
                "w_magnitude": self.config.w_magnitude,
                "w_anomaly": self.config.w_anomaly,
                "w_context": self.config.w_context,
                "w_urgency": self.config.w_urgency,
                "noise_std": self.config.noise_std,
                "feature_normalization": self.config.feature_normalization
            }
        }

    def set_parameters(self, params: Dict[str, Any]) -> None:
        """Set model parameters."""
        if "weights" in params:
            self.weights = np.array(params["weights"])
        if "config" in params:
            cfg = params["config"]
            self.config = LinearSignificanceConfig(**cfg)

    def _safe_get(self, d: Dict[str, Any], key: str, default: float = 0.0) -> float:
        """Safely extract float from dictionary."""
        try:
            return float(d.get(key, default))
        except (ValueError, TypeError):
            return default


@dataclass
class NeuralSignificanceConfig:
    """Configuration for neural significance model."""

    hidden_sizes: List[int] = field(default_factory=lambda: [32, 16])
    activation: str = "relu"
    dropout_rate: float = 0.1
    learning_rate: float = 0.001
    l2_regularization: float = 0.0001
    temporal_window: int = 10
    attention_heads: int = 4
    use_temporal_attention: bool = True
    batch_size: int = 32
    update_frequency: int = 10  # Update every N samples


class NeuralSignificanceModel(SignificanceModel):
    """
    Neural network-based significance model with temporal attention.
    Uses a lightweight architecture suitable for edge deployment.
    """

    def __init__(self, config: NeuralSignificanceConfig):
        self.config = config
        self.feature_dim = 4  # magnitude, anomaly, context, urgency

        # Initialize simple feedforward network (numpy implementation)
        self._init_network()

        # Temporal history buffer
        self.history_buffer: List[np.ndarray] = []
        self.update_count = 0

        # Learning state
        self.learning_enabled = True
        self._accumulated_gradients = []
        self._batch_buffer = []

    def _init_network(self):
        """Initialize neural network weights."""
        np.random.seed(42)  # For reproducibility

        # Input layer to first hidden layer
        layer_sizes = [self.feature_dim] + self.config.hidden_sizes + [1]
        self.weights = []
        self.biases = []

        for i in range(len(layer_sizes) - 1):
            # He initialization
            w = np.random.randn(layer_sizes[i], layer_sizes[i+1]) * np.sqrt(2.0 / layer_sizes[i])
            b = np.zeros(layer_sizes[i+1])

            self.weights.append(w)
            self.biases.append(b)

        # Attention weights for temporal model
        if self.config.use_temporal_attention:
            self.attention_weights = np.random.randn(self.config.hidden_sizes[0], self.config.attention_heads) * 0.1
            self.attention_bias = np.zeros(self.config.attention_heads)

    def compute_significance(
        self,
        context: ProcessingContext
    ) -> Tuple[float, Dict[str, Any]]:
        """Compute significance using neural network."""
        features = context.features

        # Extract and normalize features
        feature_vector = np.array([
            self._safe_get(features, "magnitude", 0.0) / 100.0,  # Normalize to [0,1]
            self._safe_get(features, "anomaly_score", 0.0),
            self._safe_get(features, "context_relevance", 0.0),
            self._safe_get(features, "urgency", 0.0)
        ])

        # Clamp to [0, 1]
        feature_vector = np.clip(feature_vector, 0.0, 1.0)

        # Update history buffer
        self.history_buffer.append(feature_vector.copy())
        if len(self.history_buffer) > self.config.temporal_window:
            self.history_buffer.pop(0)

        # Forward pass through network
        if self.config.use_temporal_attention and len(self.history_buffer) > 1:
            significance, attention_weights = self._forward_with_attention(feature_vector)
        else:
            significance, attention_weights = self._forward_simple(feature_vector), None

        # Clamp output
        significance = np.clip(significance, 0.0, 1.0)

        # Create explanation
        explanation = {
            "model_type": "neural",
            "network_layers": len(self.weights),
            "temporal_context": len(self.history_buffer),
            "input_features": feature_vector.tolist(),
            "attention_weights": attention_weights.tolist() if attention_weights is not None else None,
            "network_output": float(significance)
        }

        return float(significance), explanation

    def _forward_simple(self, x: np.ndarray) -> float:
        """Simple feedforward pass."""
        current = x

        for i, (w, b) in enumerate(zip(self.weights, self.biases)):
            current = np.dot(current, w) + b

            # Apply activation (except last layer)
            if i < len(self.weights) - 1:
                if self.config.activation == "relu":
                    current = np.maximum(0, current)
                elif self.config.activation == "tanh":
                    current = np.tanh(current)
                elif self.config.activation == "sigmoid":
                    current = 1 / (1 + np.exp(-np.clip(current, -500, 500)))

                # Apply dropout during training (simplified)
                if self.learning_enabled and self.config.dropout_rate > 0:
                    dropout_mask = np.random.random(current.shape) > self.config.dropout_rate
                    current = current * dropout_mask / (1 - self.config.dropout_rate)

        # Final activation (sigmoid for output in [0,1])
        output = 1 / (1 + np.exp(-np.clip(current[0], -500, 500)))
        return output

    def _forward_with_attention(self, current_features: np.ndarray) -> Tuple[float, np.ndarray]:
        """Forward pass with temporal attention mechanism."""
        if len(self.history_buffer) < 2:
            return self._forward_simple(current_features), np.array([1.0])

        # Simple attention: compute similarity between current and historical features
        history_matrix = np.array(self.history_buffer[:-1])  # Exclude current

        # Compute attention scores (simplified dot-product attention)
        attention_scores = np.dot(history_matrix, current_features)
        attention_weights = self._softmax(attention_scores)

        # Weighted combination of historical context
        historical_context = np.dot(attention_weights, history_matrix)

        # Combine current features with historical context
        combined_features = 0.7 * current_features + 0.3 * historical_context

        # Forward pass with combined features
        significance = self._forward_simple(combined_features)

        return significance, attention_weights

    def _softmax(self, x: np.ndarray) -> np.ndarray:
        """Numerically stable softmax."""
        exp_x = np.exp(x - np.max(x))
        return exp_x / np.sum(exp_x)

    def update(
        self,
        context: ProcessingContext,
        outcome: Optional[Dict[str, Any]]
    ) -> None:
        """Update network based on outcome (simplified online learning)."""
        if not self.learning_enabled or outcome is None:
            return

        # Simple reward signal based on outcome
        reward = self._compute_reward(outcome)

        # Store for batch update
        features = np.array([
            self._safe_get(context.features, "magnitude", 0.0) / 100.0,
            self._safe_get(context.features, "anomaly_score", 0.0),
            self._safe_get(context.features, "context_relevance", 0.0),
            self._safe_get(context.features, "urgency", 0.0)
        ])

        self._batch_buffer.append((features, reward))

        # Update every N samples
        self.update_count += 1
        if self.update_count % self.config.update_frequency == 0:
            self._batch_update()

    def _compute_reward(self, outcome: Dict[str, Any]) -> float:
        """Compute reward signal from processing outcome."""
        # Simple reward: positive for processing high-significance items efficiently
        energy_efficiency = outcome.get("energy_efficiency", 0.5)
        accuracy = outcome.get("accuracy", 0.5)

        # Combine efficiency and accuracy
        reward = 0.6 * accuracy + 0.4 * energy_efficiency
        return float(reward)

    def _batch_update(self):
        """Perform batch gradient update (simplified)."""
        if len(self._batch_buffer) < self.config.batch_size:
            return

        # Very simplified gradient update - in practice would use proper backprop
        batch_features = np.array([item[0] for item in self._batch_buffer[-self.config.batch_size:]])
        batch_rewards = np.array([item[1] for item in self._batch_buffer[-self.config.batch_size:]])

        # Simple policy gradient-style update
        for features, reward in zip(batch_features, batch_rewards):
            # Forward pass to get current prediction
            pred = self._forward_simple(features)

            # Simple gradient approximation
            error = reward - pred

            # Update weights (very simplified - proper implementation would use backprop)
            learning_rate = self.config.learning_rate
            for i in range(len(self.weights)):
                # Simple weight update rule
                gradient_approx = error * learning_rate * 0.1
                self.weights[i] += gradient_approx * np.random.randn(*self.weights[i].shape) * 0.01

        # Clear batch buffer
        self._batch_buffer = []

    def get_parameters(self) -> Dict[str, Any]:
        """Get model parameters."""
        return {
            "weights": [w.tolist() for w in self.weights],
            "biases": [b.tolist() for b in self.biases],
            "attention_weights": self.attention_weights.tolist() if hasattr(self, "attention_weights") else None,
            "attention_bias": self.attention_bias.tolist() if hasattr(self, "attention_bias") else None,
            "config": {
                "hidden_sizes": self.config.hidden_sizes,
                "activation": self.config.activation,
                "dropout_rate": self.config.dropout_rate,
                "learning_rate": self.config.learning_rate,
                "temporal_window": self.config.temporal_window,
                "attention_heads": self.config.attention_heads,
                "use_temporal_attention": self.config.use_temporal_attention
            }
        }

    def set_parameters(self, params: Dict[str, Any]) -> None:
        """Set model parameters."""
        if "weights" in params:
            self.weights = [np.array(w) for w in params["weights"]]
        if "biases" in params:
            self.biases = [np.array(b) for b in params["biases"]]
        if "attention_weights" in params and params["attention_weights"] is not None:
            self.attention_weights = np.array(params["attention_weights"])
        if "attention_bias" in params and params["attention_bias"] is not None:
            self.attention_bias = np.array(params["attention_bias"])

    def _safe_get(self, d: Dict[str, Any], key: str, default: float = 0.0) -> float:
        """Safely extract float from dictionary."""
        try:
            return float(d.get(key, default))
        except (ValueError, TypeError):
            return default
