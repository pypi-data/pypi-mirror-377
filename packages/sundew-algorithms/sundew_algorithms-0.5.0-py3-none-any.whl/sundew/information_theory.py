#!/usr/bin/env python3
"""
Information-theoretic threshold selection for Sundew algorithm.

This module implements advanced threshold adaptation using mutual information,
entropy measures, and information-theoretic criteria for optimal selective
activation decisions.
"""

from abc import ABC, abstractmethod
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np


@dataclass
class InformationMetrics:
    """Container for information-theoretic metrics."""
    mutual_information: float
    entropy: float
    conditional_entropy: float
    information_gain: float
    kl_divergence: float
    jensen_shannon_divergence: float

    def to_dict(self) -> Dict[str, float]:
        return {
            'mutual_information': self.mutual_information,
            'entropy': self.entropy,
            'conditional_entropy': self.conditional_entropy,
            'information_gain': self.information_gain,
            'kl_divergence': self.kl_divergence,
            'jensen_shannon_divergence': self.jensen_shannon_divergence
        }


class InformationTheoreticThreshold(ABC):
    """Abstract base class for information-theoretic threshold adaptation."""

    @abstractmethod
    def update_threshold(self, significance_scores: np.ndarray,
                        activations: np.ndarray, context: Dict[str, Any]) -> float:
        """Update threshold based on information-theoretic criteria."""
        pass

    @abstractmethod
    def compute_metrics(self, significance_scores: np.ndarray,
                       activations: np.ndarray) -> InformationMetrics:
        """Compute comprehensive information-theoretic metrics."""
        pass


class MutualInformationThreshold(InformationTheoreticThreshold):
    """
    Threshold adaptation using mutual information maximization.

    Selects thresholds that maximize the mutual information between
    significance scores and activation decisions, providing optimal
    information transfer in selective processing.
    """

    def __init__(self,
                 history_size: int = 1000,
                 n_bins: int = 50,
                 alpha: float = 0.1,
                 min_threshold: float = 0.1,
                 max_threshold: float = 0.9,
                 regularization: float = 1e-8):
        self.history_size = history_size
        self.n_bins = n_bins
        self.alpha = alpha  # Adaptation rate
        self.min_threshold = min_threshold
        self.max_threshold = max_threshold
        self.regularization = regularization

        # History buffers
        self.significance_history = deque(maxlen=history_size)
        self.activation_history = deque(maxlen=history_size)
        self.threshold_history = deque(maxlen=100)

        # Current threshold
        self.current_threshold = 0.5

        # Statistics
        self.total_samples = 0
        self.adaptation_count = 0

    def _compute_entropy(self, probabilities: np.ndarray) -> float:
        """Compute Shannon entropy of probability distribution."""
        # Add regularization to avoid log(0)
        prob = probabilities + self.regularization
        prob = prob / np.sum(prob)  # Renormalize

        # Filter out zero probabilities
        prob = prob[prob > 0]
        return -np.sum(prob * np.log2(prob))

    def _compute_joint_distribution(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Compute joint probability distribution using binning."""
        # Discretize continuous values
        x_bins = np.linspace(0, 1, self.n_bins + 1)
        y_bins = np.array([0, 1])  # Binary for activations

        x_discrete = np.digitize(x, x_bins) - 1
        x_discrete = np.clip(x_discrete, 0, self.n_bins - 1)

        y_discrete = np.clip(y.astype(int), 0, 1)  # Ensure binary values

        # Compute joint histogram
        joint_counts = np.zeros((self.n_bins, 2))
        for i in range(len(x)):
            if 0 <= x_discrete[i] < self.n_bins and 0 <= y_discrete[i] < 2:
                joint_counts[x_discrete[i], y_discrete[i]] += 1

        # Convert to probabilities
        total = np.sum(joint_counts)
        if total == 0:
            return np.ones_like(joint_counts) / joint_counts.size

        return joint_counts / total

    def _compute_mutual_information(self, x: np.ndarray, y: np.ndarray) -> float:
        """Compute mutual information between continuous x and binary y."""
        if len(x) == 0 or len(y) == 0:
            return 0.0

        # Get joint distribution
        joint_prob = self._compute_joint_distribution(x, y)

        # Marginal distributions
        marginal_x = np.sum(joint_prob, axis=1)
        marginal_y = np.sum(joint_prob, axis=0)

        # Compute mutual information
        mi = 0.0
        for i in range(joint_prob.shape[0]):
            for j in range(joint_prob.shape[1]):
                if joint_prob[i, j] > self.regularization:
                    mi += joint_prob[i, j] * np.log2(
                        joint_prob[i, j] / (marginal_x[i] * marginal_y[j] + self.regularization)
                    )

        return max(0, mi)  # MI should be non-negative

    def _optimize_threshold_mi(self, significance_scores: np.ndarray) -> float:
        """Find threshold that maximizes mutual information."""
        if len(significance_scores) < 10:
            return self.current_threshold

        # Test multiple threshold candidates
        threshold_candidates = np.linspace(
            self.min_threshold, self.max_threshold, 20
        )

        best_threshold = self.current_threshold
        best_mi = -1

        for threshold in threshold_candidates:
            # Simulate activations with this threshold
            activations = (significance_scores >= threshold).astype(float)

            # Skip if all same (no information)
            if len(np.unique(activations)) < 2:
                continue

            # Compute mutual information
            mi = self._compute_mutual_information(significance_scores, activations)

            if mi > best_mi:
                best_mi = mi
                best_threshold = threshold

        return best_threshold

    def update_threshold(self, significance_scores: np.ndarray,
                        activations: np.ndarray, context: Dict[str, Any]) -> float:
        """Update threshold using mutual information maximization."""
        # Update history
        self.significance_history.extend(significance_scores)
        self.activation_history.extend(activations)
        self.total_samples += len(significance_scores)

        # Need sufficient history for reliable estimation
        if len(self.significance_history) < 50:
            return self.current_threshold

        # Convert to numpy arrays
        sig_array = np.array(list(self.significance_history))
        act_array = np.array(list(self.activation_history))

        # Optimize threshold
        optimal_threshold = self._optimize_threshold_mi(sig_array)

        # Smooth adaptation
        new_threshold = (1 - self.alpha) * self.current_threshold + self.alpha * optimal_threshold

        # Apply bounds
        new_threshold = np.clip(new_threshold, self.min_threshold, self.max_threshold)

        # Update
        self.current_threshold = new_threshold
        self.threshold_history.append(new_threshold)
        self.adaptation_count += 1

        return new_threshold

    def compute_metrics(self, significance_scores: np.ndarray,
                       activations: np.ndarray) -> InformationMetrics:
        """Compute comprehensive information-theoretic metrics."""
        if len(significance_scores) == 0:
            return InformationMetrics(0, 0, 0, 0, 0, 0)

        # Mutual information
        mi = self._compute_mutual_information(significance_scores, activations)

        # Entropy of activations (binary)
        p_active = np.mean(activations)
        p_inactive = 1 - p_active

        if p_active == 0 or p_active == 1:
            entropy = 0
        else:
            entropy = -p_active * np.log2(p_active) - p_inactive * np.log2(p_inactive)

        # Conditional entropy H(Y|X)
        conditional_entropy = entropy - mi

        # Information gain (same as MI for binary classification)
        information_gain = mi

        # KL divergence from uniform distribution
        uniform_p = 0.5
        kl_div = 0
        if p_active > 0:
            kl_div += p_active * np.log2(p_active / uniform_p)
        if p_inactive > 0:
            kl_div += p_inactive * np.log2(p_inactive / uniform_p)

        # Jensen-Shannon divergence
        m = (p_active + uniform_p) / 2
        js_div = 0.5 * (p_active * np.log2(p_active / m) if p_active > 0 else 0)
        js_div += 0.5 * (uniform_p * np.log2(uniform_p / m))

        return InformationMetrics(
            mutual_information=mi,
            entropy=entropy,
            conditional_entropy=conditional_entropy,
            information_gain=information_gain,
            kl_divergence=kl_div,
            jensen_shannon_divergence=js_div
        )

    def get_adaptation_stats(self) -> Dict[str, Any]:
        """Get adaptation statistics."""
        return {
            'total_samples': self.total_samples,
            'adaptation_count': self.adaptation_count,
            'current_threshold': self.current_threshold,
            'threshold_history': list(self.threshold_history),
            'history_size': len(self.significance_history),
            'threshold_stability': np.std(list(self.threshold_history)) if self.threshold_history else 0
        }


class EntropyBasedThreshold(InformationTheoreticThreshold):
    """
    Threshold adaptation based on entropy minimization/maximization.

    Adapts thresholds to achieve target entropy levels in activation patterns,
    providing control over information content in selective processing decisions.
    """

    def __init__(self,
                 target_entropy: float = 0.5,
                 entropy_weight: float = 0.7,
                 activation_rate_weight: float = 0.3,
                 target_activation_rate: float = 0.15,
                 adaptation_rate: float = 0.05,
                 history_size: int = 500):
        self.target_entropy = target_entropy
        self.entropy_weight = entropy_weight
        self.activation_rate_weight = activation_rate_weight
        self.target_activation_rate = target_activation_rate
        self.adaptation_rate = adaptation_rate
        self.history_size = history_size

        self.current_threshold = 0.6
        self.entropy_history = deque(maxlen=100)
        self.activation_rate_history = deque(maxlen=100)

    def _compute_activation_entropy(self, activations: np.ndarray) -> float:
        """Compute entropy of activation pattern."""
        if len(activations) == 0:
            return 0

        p_active = np.mean(activations)
        p_inactive = 1 - p_active

        if p_active == 0 or p_active == 1:
            return 0

        return -p_active * np.log2(p_active) - p_inactive * np.log2(p_inactive)

    def update_threshold(self, significance_scores: np.ndarray,
                        activations: np.ndarray, context: Dict[str, Any]) -> float:
        """Update threshold to achieve target entropy."""
        if len(activations) == 0:
            return self.current_threshold

        # Compute current metrics
        current_entropy = self._compute_activation_entropy(activations)
        current_activation_rate = np.mean(activations)

        self.entropy_history.append(current_entropy)
        self.activation_rate_history.append(current_activation_rate)

        # Compute errors
        entropy_error = self.target_entropy - current_entropy
        activation_rate_error = self.target_activation_rate - current_activation_rate

        # Combined error with weighting
        combined_error = (self.entropy_weight * entropy_error +
                         self.activation_rate_weight * activation_rate_error)

        # Adaptive threshold adjustment
        threshold_adjustment = self.adaptation_rate * combined_error

        # Update threshold
        new_threshold = self.current_threshold - threshold_adjustment
        new_threshold = np.clip(new_threshold, 0.05, 0.95)

        self.current_threshold = new_threshold
        return new_threshold

    def compute_metrics(self, significance_scores: np.ndarray,
                       activations: np.ndarray) -> InformationMetrics:
        """Compute entropy-focused metrics."""
        entropy = self._compute_activation_entropy(activations)

        # Simplified metrics for entropy-based approach
        return InformationMetrics(
            mutual_information=0,  # Not computed in this approach
            entropy=entropy,
            conditional_entropy=0,
            information_gain=0,
            kl_divergence=abs(entropy - self.target_entropy),
            jensen_shannon_divergence=0
        )


class InformationTheoreticController:
    """
    Master controller for information-theoretic threshold adaptation.

    Provides a unified interface for various information-theoretic threshold
    adaptation strategies with automatic method selection and performance
    monitoring.
    """

    def __init__(self,
                 method: str = "mutual_information",
                 **kwargs):
        """
        Initialize information-theoretic controller.

        Args:
            method: Method to use ("mutual_information", "entropy", "adaptive")
            **kwargs: Method-specific parameters
        """
        self.method = method

        # Initialize appropriate threshold adapter
        if method == "mutual_information":
            self.adapter = MutualInformationThreshold(**kwargs)
        elif method == "entropy":
            self.adapter = EntropyBasedThreshold(**kwargs)
        elif method == "adaptive":
            # Use multiple methods and select best
            self.adapter = self._create_adaptive_adapter(**kwargs)
        else:
            raise ValueError(f"Unknown method: {method}")

        # Performance tracking
        self.performance_history = []
        self.method_comparisons = defaultdict(list)

    def _create_adaptive_adapter(self, **kwargs):
        """Create adaptive controller that switches between methods."""
        # For now, default to mutual information
        # Future: implement method switching based on performance
        return MutualInformationThreshold(**kwargs)

    def update_threshold(self, significance_scores: np.ndarray,
                        activations: np.ndarray,
                        context: Optional[Dict[str, Any]] = None) -> float:
        """Update threshold using selected information-theoretic method."""
        if context is None:
            context = {}

        # Update threshold
        new_threshold = self.adapter.update_threshold(
            significance_scores, activations, context
        )

        # Compute and store metrics
        metrics = self.adapter.compute_metrics(significance_scores, activations)

        self.performance_history.append({
            'threshold': new_threshold,
            'metrics': metrics.to_dict(),
            'activation_rate': np.mean(activations) if len(activations) > 0 else 0,
            'method': self.method
        })

        return new_threshold

    def get_current_threshold(self) -> float:
        """Get current threshold value."""
        return self.adapter.current_threshold

    def get_comprehensive_report(self) -> Dict[str, Any]:
        """Get comprehensive information-theoretic analysis report."""
        if not self.performance_history:
            return {"status": "no_data"}

        recent_metrics = self.performance_history[-10:]  # Last 10 updates

        # Aggregate metrics
        avg_mi = np.mean([m['metrics']['mutual_information'] for m in recent_metrics])
        avg_entropy = np.mean([m['metrics']['entropy'] for m in recent_metrics])
        avg_activation_rate = np.mean([m['activation_rate'] for m in recent_metrics])
        threshold_stability = np.std([m['threshold'] for m in recent_metrics])

        report = {
            'method': self.method,
            'current_threshold': self.get_current_threshold(),
            'performance_summary': {
                'avg_mutual_information': avg_mi,
                'avg_entropy': avg_entropy,
                'avg_activation_rate': avg_activation_rate,
                'threshold_stability': threshold_stability,
                'total_adaptations': len(self.performance_history)
            },
            'recent_performance': recent_metrics[-5:],  # Last 5 for detail
        }

        # Add method-specific stats
        if hasattr(self.adapter, 'get_adaptation_stats'):
            report['adaptation_stats'] = self.adapter.get_adaptation_stats()

        return report

    def export_analysis_data(self) -> Dict[str, Any]:
        """Export data for external analysis and visualization."""
        return {
            'method': self.method,
            'performance_history': self.performance_history,
            'method_comparisons': dict(self.method_comparisons),
            'configuration': {
                'adapter_type': type(self.adapter).__name__,
                'adapter_config': getattr(self.adapter, '__dict__', {})
            }
        }


# Utility functions for information-theoretic analysis

def compute_information_gain(before_entropy: float, after_entropy: float) -> float:
    """Compute information gain from entropy reduction."""
    return max(0, before_entropy - after_entropy)


def mutual_information_score(x: np.ndarray, y: np.ndarray, bins: int = 20) -> float:
    """Compute mutual information between two continuous variables."""
    # Simple implementation using binning
    x_bins = np.histogram_bin_edges(x, bins=bins)
    y_bins = np.histogram_bin_edges(y, bins=bins)

    xy_hist, _, _ = np.histogram2d(x, y, bins=[x_bins, y_bins])
    x_hist, _ = np.histogram(x, bins=x_bins)
    y_hist, _ = np.histogram(y, bins=y_bins)

    # Convert to probabilities
    xy_prob = xy_hist / np.sum(xy_hist)
    x_prob = x_hist / np.sum(x_hist)
    y_prob = y_hist / np.sum(y_hist)

    # Compute MI
    mi = 0
    for i in range(len(x_prob)):
        for j in range(len(y_prob)):
            if xy_prob[i, j] > 0:
                mi += xy_prob[i, j] * np.log2(
                    xy_prob[i, j] / (x_prob[i] * y_prob[j])
                )

    return mi


def entropy_based_feature_selection(features: np.ndarray,
                                   targets: np.ndarray,
                                   n_features: int = 5) -> List[int]:
    """Select features based on mutual information with targets."""
    feature_scores = []

    for i in range(features.shape[1]):
        score = mutual_information_score(features[:, i], targets)
        feature_scores.append((i, score))

    # Sort by score and return top N
    feature_scores.sort(key=lambda x: x[1], reverse=True)
    return [idx for idx, _ in feature_scores[:n_features]]


if __name__ == "__main__":
    # Example usage and testing
    print("Information-Theoretic Threshold Controller")
    print("=" * 50)

    # Create test data
    np.random.seed(42)
    n_samples = 1000

    # Generate synthetic significance scores with structure
    significance_scores = np.random.beta(2, 5, n_samples)  # Bimodal-ish distribution

    # Create ground truth with some correlation to significance
    ground_truth = (significance_scores > 0.3).astype(float)
    ground_truth += 0.1 * np.random.random(n_samples)  # Add noise
    ground_truth = (ground_truth > 0.5).astype(float)

    # Initialize controller
    controller = InformationTheoreticController(
        method="mutual_information",
        history_size=200,
        alpha=0.1
    )

    print(f"Testing with {n_samples} samples...")

    # Simulate adaptive threshold updates
    batch_size = 50
    for i in range(0, n_samples, batch_size):
        batch_sig = significance_scores[i:i+batch_size]
        batch_gt = ground_truth[i:i+batch_size]

        # Update threshold
        new_threshold = controller.update_threshold(batch_sig, batch_gt)

        if i % 200 == 0:
            print(f"Batch {i//batch_size + 1}: Threshold = {new_threshold:.3f}")

    # Get final report
    report = controller.get_comprehensive_report()

    print("\nFinal Analysis:")
    print(f"Final threshold: {report['current_threshold']:.3f}")
    print(f"Average mutual information: {report['performance_summary']['avg_mutual_information']:.4f}")
    print(f"Average entropy: {report['performance_summary']['avg_entropy']:.4f}")
    print(f"Threshold stability (std): {report['performance_summary']['threshold_stability']:.4f}")
    print(f"Total adaptations: {report['performance_summary']['total_adaptations']}")

    print("\nInformation-theoretic threshold controller ready for integration!")
