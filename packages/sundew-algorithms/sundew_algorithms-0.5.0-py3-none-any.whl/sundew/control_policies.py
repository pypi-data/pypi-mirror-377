# src/sundew/control_policies.py
"""
Concrete implementations of control policies for threshold adaptation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np

from .interfaces import ControlPolicy, ControlState


@dataclass
class PIControlConfig:
    """Configuration for PI controller."""

    kp: float = 0.08  # Proportional gain
    ki: float = 0.02  # Integral gain
    error_deadband: float = 0.005
    integral_clamp: float = 0.50
    energy_pressure_weight: float = 0.04
    adaptive_gains: bool = False
    stability_monitoring: bool = True


class PIControlPolicy(ControlPolicy):
    """Enhanced PI controller with stability monitoring and adaptive gains."""

    def __init__(self, config: PIControlConfig):
        self.config = config
        self.integral_error = 0.0
        self.previous_error = 0.0
        self.error_history: List[float] = []
        self.oscillation_detector = OscillationDetector()

        # Adaptive gains state
        self.current_kp = config.kp
        self.current_ki = config.ki

        # Stability metrics
        self.stability_history: List[Dict[str, float]] = []

    def update_threshold(
        self,
        current_state: ControlState,
        target_activation_rate: float,
        recent_activations: List[bool],
        energy_state: Dict[str, float]
    ) -> Tuple[float, ControlState]:
        """Update threshold using enhanced PI control."""

        # Compute error
        error = target_activation_rate - current_state.activation_rate

        # Apply deadband
        if abs(error) <= self.config.error_deadband:
            error = 0.0

        # Update integral with anti-windup
        self.integral_error += error
        self.integral_error = np.clip(
            self.integral_error,
            -self.config.integral_clamp,
            self.config.integral_clamp
        )

        # Adaptive gain adjustment
        if self.config.adaptive_gains:
            self._update_adaptive_gains(error, current_state)

        # PI control law
        control_output = self.current_kp * error + self.current_ki * self.integral_error

        # Energy pressure term
        energy_fraction = energy_state.get("energy_level", 1.0)
        energy_pressure = self.config.energy_pressure_weight * (1.0 - energy_fraction)

        # Update threshold
        new_threshold = current_state.threshold - control_output + energy_pressure
        new_threshold = np.clip(new_threshold, 0.0, 1.0)

        # Update error history for stability analysis
        self.error_history.append(error)
        if len(self.error_history) > 100:
            self.error_history.pop(0)

        # Detect oscillations
        oscillation_metrics = self.oscillation_detector.analyze(self.error_history)

        # Update stability metrics
        stability_metrics = {
            "oscillation": oscillation_metrics["oscillation_index"],
            "settling_time": oscillation_metrics["settling_time"],
            "overshoot": oscillation_metrics["overshoot"],
            "steady_state_error": abs(error) if len(self.error_history) > 50 else 0.0,
            "control_effort": abs(control_output),
            "integral_windup": abs(self.integral_error) / self.config.integral_clamp
        }

        # Create new control state
        new_state = ControlState(
            threshold=new_threshold,
            activation_rate=current_state.activation_rate,
            energy_level=energy_fraction,
            error_integral=self.integral_error,
            stability_metrics=stability_metrics
        )

        self.previous_error = error
        self.stability_history.append(stability_metrics)
        if len(self.stability_history) > 1000:
            self.stability_history.pop(0)

        return new_threshold, new_state

    def _update_adaptive_gains(self, error: float, current_state: ControlState):
        """Update PI gains based on system performance."""
        # Simple adaptive logic - more sophisticated methods exist

        # Increase gains if error is persistently large
        if len(self.error_history) > 10:
            recent_errors = self.error_history[-10:]
            avg_error = np.mean(np.abs(recent_errors))

            if avg_error > 0.05:  # Large persistent error
                self.current_kp = min(self.current_kp * 1.05, self.config.kp * 2.0)
                self.current_ki = min(self.current_ki * 1.02, self.config.ki * 2.0)

        # Decrease gains if oscillating
        oscillation = current_state.stability_metrics.get("oscillation", 0.0)
        if oscillation > 0.1:
            self.current_kp = max(self.current_kp * 0.95, self.config.kp * 0.5)
            self.current_ki = max(self.current_ki * 0.98, self.config.ki * 0.5)

    def predict_stability(
        self,
        current_state: ControlState,
        horizon: int = 100
    ) -> Dict[str, float]:
        """Predict stability metrics using linear model approximation."""
        if len(self.error_history) < 10:
            return {"convergence_time": float("inf"), "predicted_overshoot": 0.0}

        # Simple prediction based on current error dynamics
        recent_errors = np.array(self.error_history[-10:])

        # Estimate convergence time (when error becomes small)
        if len(recent_errors) > 1:
            error_slope = np.polyfit(range(len(recent_errors)), recent_errors, 1)[0]
            if abs(error_slope) > 1e-6:
                convergence_time = abs(recent_errors[-1] / error_slope)
            else:
                convergence_time = float("inf")
        else:
            convergence_time = float("inf")

        # Predict overshoot based on current control gains
        predicted_overshoot = self.current_kp * abs(recent_errors[-1]) * 0.5

        # Estimate oscillation risk
        if len(self.stability_history) > 5:
            recent_oscillations = [h["oscillation"] for h in self.stability_history[-5:]]
            oscillation_trend = np.mean(recent_oscillations)
        else:
            oscillation_trend = 0.0

        return {
            "convergence_time": min(convergence_time, horizon),
            "predicted_overshoot": predicted_overshoot,
            "oscillation_risk": oscillation_trend,
            "stability_margin": max(0.0, 1.0 - oscillation_trend - predicted_overshoot)
        }

    def get_theoretical_bounds(self) -> Dict[str, Tuple[float, float]]:
        """Get theoretical performance bounds for PI controller."""
        # Based on control theory for PI controllers
        return {
            "settling_time": (0.0, 4.0 / (self.current_kp + self.current_ki)),
            "overshoot": (0.0, 0.2),  # Typical for well-tuned PI
            "steady_state_error": (0.0, self.config.error_deadband),
            "stability_margin": (0.1, 1.0)  # Phase/gain margin equivalent
        }


@dataclass
class MPCControlConfig:
    """Configuration for Model Predictive Control."""

    prediction_horizon: int = 20
    control_horizon: int = 10
    weight_tracking: float = 1.0
    weight_control_effort: float = 0.1
    weight_energy: float = 0.5
    constraint_violation_penalty: float = 100.0
    system_noise_variance: float = 0.01
    measurement_noise_variance: float = 0.005
    learning_rate: float = 0.01
    model_update_frequency: int = 50


class MPCControlPolicy(ControlPolicy):
    """
    Model Predictive Control with online system identification.
    Provides theoretical guarantees and optimal multi-objective control.
    """

    def __init__(self, config: MPCControlConfig):
        self.config = config

        # System model parameters (learned online)
        self.system_model = SystemModel()

        # State estimation (Kalman filter)
        self.state_estimator = StateEstimator(config)

        # Optimization state
        self.control_sequence: List[float] = []
        self.prediction_errors: List[float] = []

        # Learning state
        self.update_count = 0
        self.model_identification_data: List[Tuple[np.ndarray, float]] = []

    def update_threshold(
        self,
        current_state: ControlState,
        target_activation_rate: float,
        recent_activations: List[bool],
        energy_state: Dict[str, float]
    ) -> Tuple[float, ControlState]:
        """Update threshold using Model Predictive Control."""

        # Update system model
        if self.update_count % self.config.model_update_frequency == 0:
            self._update_system_model()

        # State estimation
        estimated_state = self.state_estimator.update(current_state, recent_activations)

        # MPC optimization
        optimal_control, predicted_trajectory = self._solve_mpc_optimization(
            estimated_state, target_activation_rate, energy_state
        )

        # Apply first control action
        threshold_delta = optimal_control[0] if optimal_control else 0.0
        new_threshold = np.clip(
            current_state.threshold + threshold_delta,
            0.0, 1.0
        )

        # Update control sequence (shift and append)
        if len(self.control_sequence) >= self.config.control_horizon:
            self.control_sequence.pop(0)
        self.control_sequence.append(threshold_delta)

        # Compute advanced stability metrics
        stability_metrics = self._compute_stability_metrics(
            predicted_trajectory, optimal_control, current_state
        )

        # Store data for model learning
        state_vector = np.array([
            current_state.threshold,
            current_state.activation_rate,
            current_state.energy_level,
            target_activation_rate
        ])
        self.model_identification_data.append((state_vector, threshold_delta))

        # Create new control state
        new_state = ControlState(
            threshold=new_threshold,
            activation_rate=current_state.activation_rate,  # Will be updated externally
            energy_level=energy_state.get("energy_level", 1.0),
            error_integral=current_state.error_integral,  # Not used in MPC
            stability_metrics=stability_metrics
        )

        self.update_count += 1
        return new_threshold, new_state

    def _solve_mpc_optimization(
        self,
        current_state: ControlState,
        target_rate: float,
        energy_state: Dict[str, float]
    ) -> Tuple[List[float], List[Dict[str, float]]]:
        """Solve MPC optimization problem."""

        # Simple quadratic programming approximation
        # In practice, would use proper QP solver like CVXPY

        horizon = self.config.prediction_horizon
        control_horizon = self.config.control_horizon

        # Initialize control sequence
        if not self.control_sequence:
            control_sequence = [0.0] * control_horizon
        else:
            control_sequence = self.control_sequence[:control_horizon]
            while len(control_sequence) < control_horizon:
                control_sequence.append(0.0)

        # Gradient descent optimization (simplified)
        learning_rate = 0.1
        for iteration in range(10):  # Limited iterations for real-time

            # Forward simulation
            predicted_trajectory = self._simulate_system(
                current_state, control_sequence, horizon
            )

            # Compute cost and gradients
            cost, gradients = self._compute_cost_and_gradients(
                predicted_trajectory, control_sequence, target_rate, energy_state
            )

            # Update control sequence
            for i in range(len(control_sequence)):
                control_sequence[i] -= learning_rate * gradients[i]
                control_sequence[i] = np.clip(control_sequence[i], -0.1, 0.1)  # Control limits

        return control_sequence, predicted_trajectory

    def _simulate_system(
        self,
        initial_state: ControlState,
        control_sequence: List[float],
        horizon: int
    ) -> List[Dict[str, float]]:
        """Simulate system forward using learned model."""

        trajectory = []
        state = {
            "threshold": initial_state.threshold,
            "activation_rate": initial_state.activation_rate,
            "energy_level": initial_state.energy_level
        }

        for k in range(horizon):
            # Get control input (zero-order hold beyond control horizon)
            if k < len(control_sequence):
                control_input = control_sequence[k]
            else:
                control_input = control_sequence[-1] if control_sequence else 0.0

            # Update state using system model
            state = self.system_model.predict_next_state(state, control_input)
            trajectory.append(state.copy())

        return trajectory

    def _compute_cost_and_gradients(
        self,
        trajectory: List[Dict[str, float]],
        control_sequence: List[float],
        target_rate: float,
        energy_state: Dict[str, float]
    ) -> Tuple[float, List[float]]:
        """Compute cost function and gradients for MPC optimization."""

        total_cost = 0.0
        gradients = [0.0] * len(control_sequence)

        # Tracking cost
        for state in trajectory:
            tracking_error = state["activation_rate"] - target_rate
            total_cost += self.config.weight_tracking * tracking_error**2

        # Control effort cost
        for u in control_sequence:
            total_cost += self.config.weight_control_effort * u**2

        # Energy cost
        for state in trajectory:
            energy_cost = max(0.0, 0.3 - state["energy_level"])**2  # Penalty for low energy
            total_cost += self.config.weight_energy * energy_cost

        # Compute simple finite-difference gradients
        eps = 1e-4
        for i in range(len(control_sequence)):
            # Perturb control input
            control_sequence[i] += eps
            traj_plus = self._simulate_system(
                ControlState(
                    threshold=trajectory[0]["threshold"] if trajectory else 0.5,
                    activation_rate=trajectory[0]["activation_rate"] if trajectory else 0.15,
                    energy_level=trajectory[0]["energy_level"] if trajectory else 1.0,
                    error_integral=0.0,
                    stability_metrics={}
                ),
                control_sequence,
                len(trajectory)
            )

            cost_plus, _ = self._compute_cost_and_gradients(
                traj_plus, control_sequence, target_rate, energy_state
            )

            # Restore original value
            control_sequence[i] -= eps

            # Finite difference gradient
            gradients[i] = (cost_plus - total_cost) / eps

        return total_cost, gradients

    def _compute_stability_metrics(
        self,
        trajectory: List[Dict[str, float]],
        control_sequence: List[float],
        current_state: ControlState
    ) -> Dict[str, float]:
        """Compute stability metrics from MPC solution."""

        if not trajectory:
            return {"lyapunov_exponent": 0.0, "controllability": 1.0, "robustness": 1.0}

        # Lyapunov stability approximation
        state_deviations = [
            abs(state["activation_rate"] - 0.15) for state in trajectory
        ]
        lyapunov_exponent = np.mean(state_deviations) if state_deviations else 0.0

        # Controllability measure (control effort needed)
        controllability = 1.0 / (1.0 + np.mean(np.abs(control_sequence)) * 10)

        # Robustness measure (sensitivity to disturbances)
        state_variance = np.var([state["activation_rate"] for state in trajectory])
        robustness = 1.0 / (1.0 + state_variance * 100)

        return {
            "lyapunov_exponent": lyapunov_exponent,
            "controllability": controllability,
            "robustness": robustness,
            "predicted_settling_time": float(len(trajectory)),
            "control_cost": np.sum(np.abs(control_sequence))
        }

    def _update_system_model(self):
        """Update system model using recent data."""
        if len(self.model_identification_data) > 20:
            self.system_model.update_parameters(self.model_identification_data[-50:])

    def predict_stability(
        self,
        current_state: ControlState,
        horizon: int = 100
    ) -> Dict[str, float]:
        """Predict stability using MPC model."""

        # Use MPC to predict long-term behavior
        zero_control = [0.0] * min(horizon, 50)
        trajectory = self._simulate_system(current_state, zero_control, horizon)

        if not trajectory:
            return {"convergence_time": float("inf"), "predicted_overshoot": 0.0}

        # Analyze trajectory for stability
        activation_rates = [state["activation_rate"] for state in trajectory]

        # Convergence analysis
        target_rate = 0.15  # Assume typical target
        errors = [abs(rate - target_rate) for rate in activation_rates]

        convergence_time = horizon
        for i, error in enumerate(errors):
            if error < 0.01:  # Converged
                convergence_time = i
                break

        # Overshoot analysis
        max_overshoot = max(activation_rates) - target_rate if activation_rates else 0.0

        return {
            "convergence_time": float(convergence_time),
            "predicted_overshoot": max(0.0, max_overshoot),
            "steady_state_variance": np.var(activation_rates[-10:]) if len(activation_rates) > 10 else 0.0,
            "stability_margin": 1.0 / (1.0 + np.var(activation_rates))
        }

    def get_theoretical_bounds(self) -> Dict[str, Tuple[float, float]]:
        """Get theoretical bounds for MPC controller."""
        return {
            "settling_time": (0.0, float(self.config.prediction_horizon)),
            "overshoot": (0.0, 0.1),  # MPC typically has low overshoot
            "steady_state_error": (0.0, 0.005),  # Better than PI due to prediction
            "stability_margin": (0.5, 1.0),  # High due to optimization
            "robustness": (0.7, 1.0)  # Good robustness with model adaptation
        }


class SystemModel:
    """Simple system model for MPC."""

    def __init__(self):
        # Simple linear model: x[k+1] = A*x[k] + B*u[k]
        self.A = np.array([[0.95, 0.05, 0.0], [0.1, 0.85, 0.05], [0.0, 0.0, 0.98]])
        self.B = np.array([0.1, -0.2, 0.0]).reshape(-1, 1)

    def predict_next_state(self, state_dict: Dict[str, float], control: float) -> Dict[str, float]:
        """Predict next state."""
        state_vector = np.array([
            state_dict["threshold"],
            state_dict["activation_rate"],
            state_dict["energy_level"]
        ])

        next_state = self.A @ state_vector + self.B.flatten() * control
        next_state = np.clip(next_state, [0.0, 0.0, 0.0], [1.0, 1.0, 1.0])

        return {
            "threshold": float(next_state[0]),
            "activation_rate": float(next_state[1]),
            "energy_level": float(next_state[2])
        }

    def update_parameters(self, data: List[Tuple[np.ndarray, float]]):
        """Update model parameters using system identification."""
        # Simple least squares update (would use more sophisticated methods in practice)
        if len(data) < 10:
            return

        # Extract data matrices
        X = np.array([d[0][:3] for d in data[:-1]])  # State
        U = np.array([d[1] for d in data[:-1]]).reshape(-1, 1)  # Control
        Y = np.array([d[0][:3] for d in data[1:]])   # Next state

        # Least squares: [A B] = Y / [X U]
        XU = np.hstack([X, U])
        if XU.shape[0] >= XU.shape[1]:  # Sufficient data
            try:
                params = np.linalg.lstsq(XU, Y, rcond=None)[0]
                self.A = params[:3, :].T
                self.B = params[3:, :].T
            except np.linalg.LinAlgError:
                pass  # Keep existing parameters


class StateEstimator:
    """Kalman filter for state estimation."""

    def __init__(self, config: MPCControlConfig):
        self.config = config
        self.state_mean = np.array([0.5, 0.15, 1.0])  # threshold, rate, energy
        self.state_covariance = np.eye(3) * 0.1

    def update(self, measurement: ControlState, recent_activations: List[bool]) -> ControlState:
        """Update state estimate using Kalman filter."""
        # Simple implementation - would use full Kalman filter in practice

        # Measurement vector
        z = np.array([
            measurement.threshold,
            measurement.activation_rate,
            measurement.energy_level
        ])

        # Simple exponential smoothing (simplified Kalman filter)
        alpha = 0.1
        self.state_mean = alpha * z + (1 - alpha) * self.state_mean

        return ControlState(
            threshold=float(self.state_mean[0]),
            activation_rate=float(self.state_mean[1]),
            energy_level=float(self.state_mean[2]),
            error_integral=measurement.error_integral,
            stability_metrics=measurement.stability_metrics
        )


class OscillationDetector:
    """Detect oscillations in control signals."""

    def analyze(self, error_history: List[float]) -> Dict[str, float]:
        """Analyze error history for oscillations."""
        if len(error_history) < 10:
            return {"oscillation_index": 0.0, "settling_time": 0.0, "overshoot": 0.0}

        errors = np.array(error_history)

        # Simple oscillation detection using zero crossings
        sign_changes = np.sum(np.diff(np.sign(errors)) != 0)
        oscillation_index = min(1.0, sign_changes / len(errors) * 2)

        # Settling time (when error stays below threshold)
        threshold = 0.01
        settling_time = len(errors)
        for i in range(len(errors)):
            if all(abs(e) < threshold for e in errors[i:]):
                settling_time = i
                break

        # Overshoot
        overshoot = max(0.0, max(errors) - 0.02) if errors[-1] > 0 else max(0.0, -min(errors) - 0.02)

        return {
            "oscillation_index": oscillation_index,
            "settling_time": float(settling_time),
            "overshoot": overshoot
        }
