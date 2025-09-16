# src/sundew/monitoring.py
"""
Real-time monitoring and visualization tools for Sundew algorithms.
"""

from __future__ import annotations

import json
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

from .enhanced_core import EnhancedSundewAlgorithm


@dataclass
class MonitoringConfig:
    """Configuration for real-time monitoring."""

    # Data collection
    buffer_size: int = 10000
    sampling_interval: float = 0.1  # seconds
    metrics_window: int = 1000

    # Alerting
    enable_alerts: bool = True
    alert_thresholds: Dict[str, Tuple[float, float]] = field(default_factory=lambda: {
        "activation_rate": (0.05, 0.30),  # (min, max)
        "energy_level": (0.20, 1.00),
        "oscillation_index": (0.00, 0.15),
        "f1_score": (0.50, 1.00)
    })

    # Visualization
    enable_live_plots: bool = False  # Requires matplotlib
    plot_update_interval: float = 1.0
    max_plot_points: int = 1000

    # Logging
    log_to_file: bool = True
    log_file_path: str = "sundew_monitor.log"
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR

    # Performance profiling
    enable_profiling: bool = True
    profile_cpu_usage: bool = True
    profile_memory_usage: bool = True


@dataclass
class MetricSnapshot:
    """Snapshot of system metrics at a point in time."""

    timestamp: float

    # Core metrics
    activation_rate: float
    energy_level: float
    threshold: float
    significance: float

    # Performance metrics
    f1_score: float
    precision: float
    recall: float
    energy_efficiency: float

    # Stability metrics
    oscillation_index: float
    convergence_rate: float
    control_effort: float

    # System metrics
    processing_time: float
    memory_usage: float
    cpu_usage: float

    # Component-specific metrics
    component_metrics: Dict[str, Dict[str, float]] = field(default_factory=dict)


class AlertManager:
    """Manages alerting and anomaly detection."""

    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.alert_history: List[Dict[str, Any]] = []
        self.alert_callbacks: List[Callable[[str, Dict[str, Any]], None]] = []

        # Anomaly detection state
        self.metric_histories: Dict[str, deque] = {}
        self.baseline_stats: Dict[str, Dict[str, float]] = {}

    def register_alert_callback(self, callback: Callable[[str, Dict[str, Any]], None]):
        """Register callback function for alerts."""
        self.alert_callbacks.append(callback)

    def check_thresholds(self, snapshot: MetricSnapshot) -> List[Dict[str, Any]]:
        """Check metric thresholds and generate alerts."""
        alerts = []

        if not self.config.enable_alerts:
            return alerts

        # Check each configured threshold
        for metric_name, (min_val, max_val) in self.config.alert_thresholds.items():
            current_value = getattr(snapshot, metric_name, None)

            if current_value is None:
                continue

            alert_triggered = False
            alert_type = ""

            if current_value < min_val:
                alert_triggered = True
                alert_type = "below_threshold"
            elif current_value > max_val:
                alert_triggered = True
                alert_type = "above_threshold"

            if alert_triggered:
                alert = {
                    "timestamp": snapshot.timestamp,
                    "metric": metric_name,
                    "value": current_value,
                    "threshold": (min_val, max_val),
                    "type": alert_type,
                    "severity": self._compute_alert_severity(metric_name, current_value, min_val, max_val)
                }
                alerts.append(alert)
                self.alert_history.append(alert)

        # Check for anomalies using statistical methods
        anomaly_alerts = self._detect_anomalies(snapshot)
        alerts.extend(anomaly_alerts)

        # Trigger callbacks
        for alert in alerts:
            for callback in self.alert_callbacks:
                try:
                    callback(alert["type"], alert)
                except Exception as e:
                    print(f"Alert callback error: {e}")

        return alerts

    def _compute_alert_severity(
        self,
        metric_name: str,
        value: float,
        min_val: float,
        max_val: float
    ) -> str:
        """Compute alert severity based on how far outside bounds the value is."""

        if value < min_val:
            deviation = (min_val - value) / min_val if min_val > 0 else 1.0
        else:
            deviation = (value - max_val) / max_val if max_val > 0 else 1.0

        if deviation > 0.5:
            return "CRITICAL"
        elif deviation > 0.2:
            return "HIGH"
        elif deviation > 0.1:
            return "MEDIUM"
        else:
            return "LOW"

    def _detect_anomalies(self, snapshot: MetricSnapshot) -> List[Dict[str, Any]]:
        """Detect anomalies using statistical methods."""
        alerts = []

        # Key metrics to monitor for anomalies
        key_metrics = ["activation_rate", "energy_level", "oscillation_index", "processing_time"]

        for metric_name in key_metrics:
            value = getattr(snapshot, metric_name, None)
            if value is None:
                continue

            # Maintain rolling history
            if metric_name not in self.metric_histories:
                self.metric_histories[metric_name] = deque(maxlen=1000)

            history = self.metric_histories[metric_name]
            history.append(value)

            # Need sufficient history for anomaly detection
            if len(history) < 50:
                continue

            # Simple anomaly detection using z-score
            values = np.array(history)
            mean_val = np.mean(values[:-10])  # Exclude recent values for baseline
            std_val = np.std(values[:-10])

            if std_val > 0:
                z_score = abs(value - mean_val) / std_val

                if z_score > 3.0:  # 3-sigma rule
                    alert = {
                        "timestamp": snapshot.timestamp,
                        "metric": metric_name,
                        "value": value,
                        "type": "statistical_anomaly",
                        "z_score": z_score,
                        "severity": "HIGH" if z_score > 4.0 else "MEDIUM"
                    }
                    alerts.append(alert)

        return alerts


class PerformanceProfiler:
    """Profiles system performance and resource usage."""

    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.profile_data: Dict[str, deque] = {}

    def profile_step(self, algorithm: EnhancedSundewAlgorithm) -> Dict[str, float]:
        """Profile a single processing step."""
        metrics = {}

        if self.config.enable_profiling:
            # CPU usage (simplified - would use psutil in practice)
            cpu_usage = self._estimate_cpu_usage()
            metrics["cpu_usage"] = cpu_usage

            # Memory usage (simplified)
            memory_usage = self._estimate_memory_usage(algorithm)
            metrics["memory_usage"] = memory_usage

            # Component-specific profiling
            component_profiles = self._profile_components(algorithm)
            metrics.update(component_profiles)

        return metrics

    def _estimate_cpu_usage(self) -> float:
        """Estimate CPU usage (simplified implementation)."""
        # In practice, would use psutil.cpu_percent()
        # For now, return a placeholder based on system load
        return min(100.0, np.random.normal(25.0, 10.0))

    def _estimate_memory_usage(self, algorithm: EnhancedSundewAlgorithm) -> float:
        """Estimate memory usage in MB."""
        # Simplified memory estimation based on algorithm state
        base_memory = 10.0  # MB

        # Add memory for histories
        history_memory = len(algorithm.processing_history) * 0.001  # 1KB per item
        metrics_memory = len(algorithm.metrics.activation_rate_history) * 0.0001

        # Add memory for component models
        component_memory = 5.0  # Estimate for all components

        return base_memory + history_memory + metrics_memory + component_memory

    def _profile_components(self, algorithm: EnhancedSundewAlgorithm) -> Dict[str, float]:
        """Profile individual component performance."""
        profiles = {}

        # Significance model profiling
        sig_model_type = type(algorithm.significance_model).__name__
        if "Neural" in sig_model_type:
            profiles["neural_model_memory"] = 15.0  # MB estimate
            profiles["neural_model_compute"] = 5.0   # MFLOPS estimate
        else:
            profiles["linear_model_memory"] = 1.0
            profiles["linear_model_compute"] = 0.1

        # Control policy profiling
        control_type = type(algorithm.control_policy).__name__
        if "MPC" in control_type:
            profiles["mpc_controller_memory"] = 8.0
            profiles["mpc_controller_compute"] = 10.0
        else:
            profiles["pi_controller_memory"] = 0.5
            profiles["pi_controller_compute"] = 0.1

        return profiles


class RealTimeMonitor:
    """Main real-time monitoring system."""

    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.alert_manager = AlertManager(config)
        self.profiler = PerformanceProfiler(config)

        # Data storage
        self.metric_buffer: deque = deque(maxlen=config.buffer_size)
        self.alert_buffer: deque = deque(maxlen=1000)

        # State tracking
        self.monitoring_active = False
        self.last_update_time = 0.0

        # Performance tracking
        self.ground_truth_labels: Optional[List[int]] = None
        self.predictions: List[int] = []

        # Visualization state (if enabled)
        if config.enable_live_plots:
            self._init_live_plots()

    def _init_live_plots(self):
        """Initialize live plotting (requires matplotlib)."""
        try:
            import matplotlib.animation as animation
            import matplotlib.pyplot as plt

            self.fig, self.axes = plt.subplots(2, 2, figsize=(12, 8))
            self.fig.suptitle("Sundew Algorithm Real-Time Monitoring")

            # Configure subplots
            self.axes[0, 0].set_title("Activation Rate & Threshold")
            self.axes[0, 0].set_ylabel("Rate / Threshold")

            self.axes[0, 1].set_title("Energy Level")
            self.axes[0, 1].set_ylabel("Energy")

            self.axes[1, 0].set_title("Performance Metrics")
            self.axes[1, 0].set_ylabel("Score")

            self.axes[1, 1].set_title("Stability Metrics")
            self.axes[1, 1].set_ylabel("Index")

            # Initialize empty plots
            self.lines = {}
            for ax in self.axes.flat:
                ax.grid(True)

            self.animation = animation.FuncAnimation(
                self.fig, self._update_plots, interval=int(self.config.plot_update_interval * 1000)
            )

            self.plots_initialized = True

        except ImportError:
            print("Warning: matplotlib not available, live plots disabled")
            self.config.enable_live_plots = False
            self.plots_initialized = False

    def start_monitoring(self, algorithm: EnhancedSundewAlgorithm):
        """Start real-time monitoring of the algorithm."""
        self.monitoring_active = True
        self.algorithm = algorithm
        print("Real-time monitoring started")

    def stop_monitoring(self):
        """Stop real-time monitoring."""
        self.monitoring_active = False
        print("Real-time monitoring stopped")

    def update(
        self,
        algorithm: EnhancedSundewAlgorithm,
        ground_truth_label: Optional[int] = None,
        prediction: Optional[int] = None
    ):
        """Update monitoring with latest algorithm state."""

        if not self.monitoring_active:
            return

        current_time = time.time()

        # Rate limiting
        if current_time - self.last_update_time < self.config.sampling_interval:
            return

        # Collect metrics
        snapshot = self._collect_metrics(algorithm, current_time)

        # Store ground truth and predictions for evaluation
        if ground_truth_label is not None:
            if self.ground_truth_labels is None:
                self.ground_truth_labels = []
            self.ground_truth_labels.append(ground_truth_label)

        if prediction is not None:
            self.predictions.append(prediction)

        # Update performance metrics if we have both labels and predictions
        if (self.ground_truth_labels is not None and
            len(self.ground_truth_labels) == len(self.predictions) and
            len(self.predictions) > 0):

            performance_metrics = self._compute_performance_metrics()
            snapshot.f1_score = performance_metrics["f1_score"]
            snapshot.precision = performance_metrics["precision"]
            snapshot.recall = performance_metrics["recall"]

        # Store snapshot
        self.metric_buffer.append(snapshot)

        # Check for alerts
        alerts = self.alert_manager.check_thresholds(snapshot)
        self.alert_buffer.extend(alerts)

        # Log important events
        self._log_metrics(snapshot, alerts)

        self.last_update_time = current_time

    def _collect_metrics(self, algorithm: EnhancedSundewAlgorithm, timestamp: float) -> MetricSnapshot:
        """Collect comprehensive metrics from the algorithm."""

        # Get algorithm report
        report = algorithm.get_comprehensive_report()

        # Profile performance
        profile_data = self.profiler.profile_step(algorithm)

        # Extract significance from recent history
        recent_significance = 0.0
        if algorithm.metrics.significance_history:
            recent_significance = algorithm.metrics.significance_history[-1]

        # Create snapshot
        snapshot = MetricSnapshot(
            timestamp=timestamp,

            # Core metrics
            activation_rate=report["activation_rate"],
            energy_level=report["energy_remaining"],
            threshold=report["current_threshold"],
            significance=recent_significance,

            # Performance metrics (will be updated if ground truth available)
            f1_score=0.0,
            precision=0.0,
            recall=0.0,
            energy_efficiency=report["energy_efficiency"],

            # Stability metrics
            oscillation_index=report["stability_metrics"].get("oscillation", 0.0),
            convergence_rate=1.0 / max(1, report["stability_metrics"].get("settling_time", 1)),
            control_effort=report["stability_metrics"].get("control_effort", 0.0),

            # System metrics
            processing_time=report["avg_processing_time"],
            memory_usage=profile_data.get("memory_usage", 0.0),
            cpu_usage=profile_data.get("cpu_usage", 0.0),

            # Component metrics
            component_metrics=report["components"]
        )

        return snapshot

    def _compute_performance_metrics(self) -> Dict[str, float]:
        """Compute classification performance metrics."""

        if (self.ground_truth_labels is None or
            len(self.ground_truth_labels) != len(self.predictions) or
            len(self.predictions) == 0):
            return {"f1_score": 0.0, "precision": 0.0, "recall": 0.0}

        # Use recent window for performance calculation
        window_size = min(1000, len(self.predictions))
        recent_labels = self.ground_truth_labels[-window_size:]
        recent_preds = self.predictions[-window_size:]

        # Compute confusion matrix
        tp = sum(1 for pred, label in zip(recent_preds, recent_labels) if pred == 1 and label == 1)
        fp = sum(1 for pred, label in zip(recent_preds, recent_labels) if pred == 1 and label == 0)
        fn = sum(1 for pred, label in zip(recent_preds, recent_labels) if pred == 0 and label == 1)
        tn = sum(1 for pred, label in zip(recent_preds, recent_labels) if pred == 0 and label == 0)

        # Compute metrics
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        return {
            "f1_score": f1_score,
            "precision": precision,
            "recall": recall
        }

    def _log_metrics(self, snapshot: MetricSnapshot, alerts: List[Dict[str, Any]]):
        """Log metrics and alerts to file."""

        if not self.config.log_to_file:
            return

        # Log snapshot (simplified)
        if len(self.metric_buffer) % 100 == 0:  # Log every 100 samples
            log_entry = {
                "timestamp": snapshot.timestamp,
                "activation_rate": snapshot.activation_rate,
                "energy_level": snapshot.energy_level,
                "f1_score": snapshot.f1_score,
                "oscillation": snapshot.oscillation_index
            }

            # In practice, would use proper logging framework
            print(f"LOG: {json.dumps(log_entry)}")

        # Log alerts immediately
        for alert in alerts:
            print(f"ALERT [{alert['severity']}]: {alert['metric']} = {alert['value']:.3f}")

    def _update_plots(self, frame):
        """Update live plots (called by matplotlib animation)."""

        if not self.plots_initialized or len(self.metric_buffer) == 0:
            return

        # Extract recent data
        recent_data = list(self.metric_buffer)[-self.config.max_plot_points:]

        if len(recent_data) < 2:
            return

        timestamps = [s.timestamp - recent_data[0].timestamp for s in recent_data]

        # Clear axes
        for ax in self.axes.flat:
            ax.clear()
            ax.grid(True)

        # Plot 1: Activation Rate & Threshold
        activation_rates = [s.activation_rate for s in recent_data]
        thresholds = [s.threshold for s in recent_data]

        self.axes[0, 0].plot(timestamps, activation_rates, 'b-', label='Activation Rate')
        self.axes[0, 0].plot(timestamps, thresholds, 'r-', label='Threshold')
        self.axes[0, 0].set_title("Activation Rate & Threshold")
        self.axes[0, 0].set_ylabel("Rate / Threshold")
        self.axes[0, 0].legend()

        # Plot 2: Energy Level
        energy_levels = [s.energy_level for s in recent_data]

        self.axes[0, 1].plot(timestamps, energy_levels, 'g-', label='Energy Level')
        self.axes[0, 1].axhline(y=0.3, color='r', linestyle='--', alpha=0.5, label='Low Energy')
        self.axes[0, 1].set_title("Energy Level")
        self.axes[0, 1].set_ylabel("Energy")
        self.axes[0, 1].legend()

        # Plot 3: Performance Metrics
        f1_scores = [s.f1_score for s in recent_data]
        precisions = [s.precision for s in recent_data]
        recalls = [s.recall for s in recent_data]

        if any(f > 0 for f in f1_scores):  # Only plot if we have performance data
            self.axes[1, 0].plot(timestamps, f1_scores, 'b-', label='F1 Score')
            self.axes[1, 0].plot(timestamps, precisions, 'g-', label='Precision')
            self.axes[1, 0].plot(timestamps, recalls, 'orange', label='Recall')

        self.axes[1, 0].set_title("Performance Metrics")
        self.axes[1, 0].set_ylabel("Score")
        self.axes[1, 0].legend()

        # Plot 4: Stability Metrics
        oscillations = [s.oscillation_index for s in recent_data]
        convergence_rates = [s.convergence_rate for s in recent_data]

        self.axes[1, 1].plot(timestamps, oscillations, 'r-', label='Oscillation')
        self.axes[1, 1].plot(timestamps, convergence_rates, 'purple', label='Convergence Rate')
        self.axes[1, 1].axhline(y=0.1, color='r', linestyle='--', alpha=0.5, label='High Oscillation')
        self.axes[1, 1].set_title("Stability Metrics")
        self.axes[1, 1].set_ylabel("Index")
        self.axes[1, 1].legend()

        # Set common x-label
        for ax in self.axes[1, :]:
            ax.set_xlabel("Time (seconds)")

        plt.tight_layout()

    def get_monitoring_summary(self) -> Dict[str, Any]:
        """Get comprehensive monitoring summary."""

        if len(self.metric_buffer) == 0:
            return {"status": "no_data"}

        recent_snapshots = list(self.metric_buffer)[-100:]  # Last 100 samples

        # Compute statistics
        avg_activation_rate = np.mean([s.activation_rate for s in recent_snapshots])
        avg_energy_level = np.mean([s.energy_level for s in recent_snapshots])
        avg_f1_score = np.mean([s.f1_score for s in recent_snapshots])
        avg_oscillation = np.mean([s.oscillation_index for s in recent_snapshots])

        # Count recent alerts
        recent_alerts = [a for a in self.alert_buffer if time.time() - a["timestamp"] < 300]  # Last 5 minutes
        critical_alerts = [a for a in recent_alerts if a["severity"] == "CRITICAL"]

        # System health assessment
        health_score = self._compute_health_score(recent_snapshots)

        return {
            "status": "active" if self.monitoring_active else "inactive",
            "samples_collected": len(self.metric_buffer),
            "monitoring_duration": self.metric_buffer[-1].timestamp - self.metric_buffer[0].timestamp if len(self.metric_buffer) > 1 else 0,

            "current_metrics": {
                "activation_rate": avg_activation_rate,
                "energy_level": avg_energy_level,
                "f1_score": avg_f1_score,
                "oscillation_index": avg_oscillation
            },

            "alerts": {
                "total_recent": len(recent_alerts),
                "critical": len(critical_alerts),
                "recent_alerts": recent_alerts[-5:]  # Last 5 alerts
            },

            "system_health": {
                "overall_score": health_score,
                "status": self._health_status_from_score(health_score)
            }
        }

    def _compute_health_score(self, snapshots: List[MetricSnapshot]) -> float:
        """Compute overall system health score (0-100)."""

        if len(snapshots) == 0:
            return 0.0

        # Performance component (0-40 points)
        avg_f1 = np.mean([s.f1_score for s in snapshots])
        performance_score = min(40, avg_f1 * 40)

        # Stability component (0-30 points)
        avg_oscillation = np.mean([s.oscillation_index for s in snapshots])
        stability_score = max(0, 30 - avg_oscillation * 300)

        # Energy component (0-20 points)
        avg_energy = np.mean([s.energy_level for s in snapshots])
        energy_score = avg_energy * 20

        # Resource usage component (0-10 points)
        avg_cpu = np.mean([s.cpu_usage for s in snapshots])
        resource_score = max(0, 10 - avg_cpu * 0.1)

        total_score = performance_score + stability_score + energy_score + resource_score
        return min(100.0, total_score)

    def _health_status_from_score(self, score: float) -> str:
        """Convert health score to status string."""
        if score >= 80:
            return "EXCELLENT"
        elif score >= 60:
            return "GOOD"
        elif score >= 40:
            return "FAIR"
        elif score >= 20:
            return "POOR"
        else:
            return "CRITICAL"

    def export_data(self, filename: str):
        """Export monitoring data to file."""

        data = {
            "config": self.config.__dict__,
            "snapshots": [
                {
                    "timestamp": s.timestamp,
                    "activation_rate": s.activation_rate,
                    "energy_level": s.energy_level,
                    "threshold": s.threshold,
                    "f1_score": s.f1_score,
                    "oscillation_index": s.oscillation_index
                }
                for s in self.metric_buffer
            ],
            "alerts": list(self.alert_buffer),
            "summary": self.get_monitoring_summary()
        }

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Monitoring data exported to {filename}")


# Convenience functions for easy monitoring setup

def setup_basic_monitoring(algorithm: EnhancedSundewAlgorithm) -> RealTimeMonitor:
    """Set up basic monitoring with default configuration."""
    config = MonitoringConfig()
    monitor = RealTimeMonitor(config)
    monitor.start_monitoring(algorithm)
    return monitor


def setup_monitoring_with_alerts(
    algorithm: EnhancedSundewAlgorithm,
    alert_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None
) -> RealTimeMonitor:
    """Set up monitoring with custom alert handling."""
    config = MonitoringConfig(enable_alerts=True)
    monitor = RealTimeMonitor(config)

    if alert_callback:
        monitor.alert_manager.register_alert_callback(alert_callback)
    else:
        # Default alert handler
        def default_alert_handler(alert_type: str, alert_data: Dict[str, Any]):
            print(f"🚨 ALERT: {alert_type} - {alert_data['metric']} = {alert_data['value']:.3f}")

        monitor.alert_manager.register_alert_callback(default_alert_handler)

    monitor.start_monitoring(algorithm)
    return monitor


def setup_live_monitoring(algorithm: EnhancedSundewAlgorithm) -> RealTimeMonitor:
    """Set up monitoring with live visualization (requires matplotlib)."""
    config = MonitoringConfig(
        enable_live_plots=True,
        enable_alerts=True,
        plot_update_interval=0.5
    )
    monitor = RealTimeMonitor(config)
    monitor.start_monitoring(algorithm)
    return monitor
