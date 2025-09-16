# src/sundew/energy_models.py
"""
Concrete implementations of energy models for different hardware platforms.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Dict, List

import numpy as np

from .interfaces import EnergyModel, ProcessingContext


@dataclass
class SimpleEnergyConfig:
    """Configuration for simple energy model."""

    max_energy: float = 100.0
    eval_cost: float = 0.6
    base_processing_cost: float = 10.0
    dormant_tick_cost: float = 0.5
    regen_min: float = 1.0
    regen_max: float = 3.0
    energy_pressure_factor: float = 0.04


class SimpleEnergyModel(EnergyModel):
    """Simple energy model (current Sundew approach) with random regeneration."""

    def __init__(self, config: SimpleEnergyConfig):
        self.config = config
        self.current_energy = config.max_energy

    def compute_processing_cost(
        self,
        significance: float,
        processing_type: str,
        context: ProcessingContext
    ) -> float:
        """Compute energy cost based on significance and processing type."""
        base_cost = self.config.base_processing_cost
        eval_cost = self.config.eval_cost

        # Scale cost by significance (more significant = more processing)
        significance_factor = 0.8 + 0.4 * significance

        # Add fixed evaluation cost
        total_cost = eval_cost + base_cost * significance_factor

        # Type-specific adjustments
        if processing_type == "training":
            total_cost *= 2.0  # Training is more expensive
        elif processing_type == "inference_complex":
            total_cost *= 1.5  # Complex inference

        return float(total_cost)

    def compute_idle_cost(self, duration: float) -> float:
        """Compute energy cost for idle period."""
        return self.config.dormant_tick_cost * duration

    def update_energy_state(
        self,
        current_energy: float,
        cost: float,
        regeneration: float = 0.0
    ) -> float:
        """Update energy state with consumption and regeneration."""
        # Apply cost
        new_energy = current_energy - cost

        # Add regeneration (random if not specified)
        if regeneration == 0.0:
            regeneration = random.uniform(self.config.regen_min, self.config.regen_max)

        new_energy += regeneration

        # Clamp to valid range
        return float(np.clip(new_energy, 0.0, self.config.max_energy))

    def predict_energy_trajectory(
        self,
        current_energy: float,
        predicted_activations: List[float],
        horizon: int
    ) -> List[float]:
        """Predict energy levels over time."""
        trajectory = [current_energy]
        energy = current_energy

        for i in range(horizon):
            if i < len(predicted_activations):
                activation_prob = predicted_activations[i]
            else:
                activation_prob = predicted_activations[-1] if predicted_activations else 0.15

            # Expected energy cost
            expected_processing_cost = self.config.base_processing_cost * activation_prob
            idle_cost = self.config.dormant_tick_cost * (1.0 - activation_prob)
            expected_cost = expected_processing_cost + idle_cost

            # Expected regeneration
            expected_regen = (self.config.regen_min + self.config.regen_max) / 2.0

            # Update energy
            energy = energy - expected_cost + expected_regen
            energy = np.clip(energy, 0.0, self.config.max_energy)
            trajectory.append(float(energy))

        return trajectory

    def get_energy_pressure(self, current_energy: float, max_energy: float) -> float:
        """Compute energy pressure term."""
        energy_fraction = current_energy / max_energy
        pressure = self.config.energy_pressure_factor * (1.0 - energy_fraction)
        return float(np.clip(pressure, 0.0, 1.0))


@dataclass
class RealisticEnergyConfig:
    """Configuration for realistic hardware energy model."""

    # Hardware platform
    platform: str = "cortex_m4"  # cortex_m4, cortex_a7, jetson_nano, etc.

    # Power consumption (mW)
    idle_power: float = 5.0
    cpu_active_power: float = 50.0
    memory_access_power: float = 10.0
    computation_power_per_mflop: float = 2.0

    # Battery characteristics
    battery_capacity_mah: float = 1000.0
    voltage: float = 3.3
    discharge_efficiency: float = 0.95
    self_discharge_rate: float = 0.001  # Per hour

    # Thermal model
    thermal_resistance: float = 10.0  # K/W
    ambient_temperature: float = 25.0  # Celsius
    max_temperature: float = 85.0
    thermal_throttling_threshold: float = 75.0

    # Performance scaling
    dvfs_enabled: bool = True  # Dynamic Voltage/Frequency Scaling
    min_frequency_ratio: float = 0.3
    max_frequency_ratio: float = 1.0

    # Energy harvesting (optional)
    harvesting_enabled: bool = False
    max_harvest_power: float = 10.0  # mW
    harvest_efficiency: float = 0.8


class RealisticEnergyModel(EnergyModel):
    """
    Realistic hardware-based energy model considering:
    - Actual power consumption patterns
    - Battery dynamics and thermal effects
    - Dynamic voltage/frequency scaling
    - Energy harvesting capabilities
    """

    def __init__(self, config: RealisticEnergyConfig):
        self.config = config

        # Initialize hardware model
        self.hardware_profile = self._get_hardware_profile(config.platform)

        # Battery state
        self.battery_energy_mwh = config.battery_capacity_mah * config.voltage
        self.current_temperature = config.ambient_temperature

        # Performance state
        self.current_frequency_ratio = 1.0
        self.thermal_throttling_active = False

        # Energy accounting
        self.cumulative_energy_consumed = 0.0
        self.energy_history: List[Dict[str, float]] = []

        # Power estimation models
        self.operation_costs = self._calibrate_operation_costs()

    def _get_hardware_profile(self, platform: str) -> Dict[str, Any]:
        """Get hardware-specific parameters."""
        profiles = {
            "cortex_m4": {
                "mips": 100,
                "cache_size_kb": 64,
                "memory_bandwidth_mbps": 100,
                "typical_frequency_mhz": 168,
                "power_efficiency_mips_per_mw": 20
            },
            "cortex_a7": {
                "mips": 2500,
                "cache_size_kb": 512,
                "memory_bandwidth_mbps": 800,
                "typical_frequency_mhz": 1000,
                "power_efficiency_mips_per_mw": 10
            },
            "jetson_nano": {
                "mips": 20000,
                "cache_size_kb": 2048,
                "memory_bandwidth_mbps": 25600,
                "typical_frequency_mhz": 1430,
                "power_efficiency_mips_per_mw": 5
            }
        }
        return profiles.get(platform, profiles["cortex_m4"])

    def _calibrate_operation_costs(self) -> Dict[str, float]:
        """Calibrate energy costs for different operations."""
        # Based on hardware profiling data
        return {
            "feature_extraction": 0.5,  # mJ per sample
            "linear_computation": 0.1,  # mJ per operation
            "neural_forward_pass": 2.0,  # mJ per pass
            "attention_computation": 1.5,  # mJ per attention head
            "memory_access": 0.01,  # mJ per KB accessed
            "control_computation": 0.05,  # mJ per control update
            "communication": 0.8  # mJ per transmission
        }

    def compute_processing_cost(
        self,
        significance: float,
        processing_type: str,
        context: ProcessingContext
    ) -> float:
        """Compute realistic energy cost based on actual operations."""

        # Base computational cost
        base_cost = self._estimate_computational_cost(significance, processing_type, context)

        # Memory access cost
        memory_cost = self._estimate_memory_cost(significance, processing_type)

        # Thermal and frequency scaling effects
        scaling_factor = self._get_performance_scaling_factor()

        # Total cost in mJ
        total_cost_mj = (base_cost + memory_cost) * scaling_factor

        # Update thermal state
        self._update_thermal_state(total_cost_mj)

        # Convert to energy units (normalized to 0-100 scale)
        normalized_cost = total_cost_mj / (self.battery_energy_mwh / 100.0)

        return float(normalized_cost)

    def _estimate_computational_cost(
        self,
        significance: float,
        processing_type: str,
        context: ProcessingContext
    ) -> float:
        """Estimate computational energy cost in mJ."""

        costs = self.operation_costs

        if processing_type == "neural_inference":
            # Neural network forward pass
            complexity_factor = 1.0 + significance  # More significant = more computation
            return costs["neural_forward_pass"] * complexity_factor

        elif processing_type == "attention_gating":
            # Attention mechanism computation
            num_heads = context.metadata.get("attention_heads", 4)
            return costs["attention_computation"] * num_heads

        elif processing_type == "linear_significance":
            # Simple linear combination
            return costs["linear_computation"]

        elif processing_type == "control_update":
            # Control algorithm computation
            return costs["control_computation"]

        else:
            # Default processing
            return costs["feature_extraction"] * (1.0 + significance * 0.5)

    def _estimate_memory_cost(self, significance: float, processing_type: str) -> float:
        """Estimate memory access energy cost in mJ."""

        # Memory footprint based on processing type
        memory_footprints = {
            "neural_inference": 50,  # KB
            "attention_gating": 20,  # KB
            "linear_significance": 2,  # KB
            "control_update": 5,  # KB
            "default": 10  # KB
        }

        memory_kb = memory_footprints.get(processing_type, memory_footprints["default"])

        # Scale by significance (more significant = more data)
        memory_kb *= (1.0 + significance * 0.3)

        return memory_kb * self.operation_costs["memory_access"]

    def _get_performance_scaling_factor(self) -> float:
        """Get current performance scaling due to DVFS and thermal throttling."""

        scaling = self.current_frequency_ratio

        # Thermal throttling
        if self.thermal_throttling_active:
            scaling *= 0.7  # Reduce performance to cool down

        # Power scaling (higher frequency = higher power)
        power_scaling = scaling ** 2.5  # Approximate power-frequency relationship

        return power_scaling

    def _update_thermal_state(self, power_mw: float):
        """Update thermal state based on power consumption."""

        # Simple thermal model: T = T_ambient + P * R_thermal
        power_increase = power_mw - self.config.idle_power
        temperature_rise = power_increase * self.config.thermal_resistance / 1000.0  # W to mW
        self.current_temperature = self.config.ambient_temperature + temperature_rise

        # Thermal throttling logic
        if self.current_temperature > self.config.thermal_throttling_threshold:
            self.thermal_throttling_active = True
            # Reduce frequency to cool down
            self.current_frequency_ratio = max(
                self.current_frequency_ratio * 0.9,
                self.config.min_frequency_ratio
            )
        else:
            self.thermal_throttling_active = False
            # Gradually increase frequency back to maximum
            self.current_frequency_ratio = min(
                self.current_frequency_ratio * 1.05,
                self.config.max_frequency_ratio
            )

    def compute_idle_cost(self, duration: float) -> float:
        """Compute realistic idle energy cost."""

        # Idle power consumption
        idle_cost_mj = self.config.idle_power * duration  # Assume duration in ms

        # Self-discharge
        if duration > 1000:  # For long idle periods
            hours = duration / 3600000  # Convert ms to hours
            self_discharge_mj = (
                self.battery_energy_mwh * self.config.self_discharge_rate * hours
            )
            idle_cost_mj += self_discharge_mj

        # Energy harvesting (if enabled)
        if self.config.harvesting_enabled:
            harvest_energy = min(
                self.config.max_harvest_power * duration,
                self.config.max_harvest_power * self.config.harvest_efficiency * duration
            )
            idle_cost_mj -= harvest_energy

        # Convert to normalized units
        normalized_cost = idle_cost_mj / (self.battery_energy_mwh / 100.0)
        return max(0.0, float(normalized_cost))

    def update_energy_state(
        self,
        current_energy: float,
        cost: float,
        regeneration: float = 0.0
    ) -> float:
        """Update energy state with realistic battery dynamics."""

        # Apply discharge efficiency
        actual_cost = cost / self.config.discharge_efficiency

        # Update energy
        new_energy = current_energy - actual_cost + regeneration

        # Battery capacity limits
        max_energy = 100.0  # Normalized scale
        new_energy = np.clip(new_energy, 0.0, max_energy)

        # Update cumulative consumption
        self.cumulative_energy_consumed += actual_cost

        # Store history for analysis
        self.energy_history.append({
            "timestamp": len(self.energy_history),
            "energy_level": new_energy,
            "cost": actual_cost,
            "temperature": self.current_temperature,
            "frequency_ratio": self.current_frequency_ratio,
            "thermal_throttling": self.thermal_throttling_active
        })

        # Limit history size
        if len(self.energy_history) > 10000:
            self.energy_history.pop(0)

        return float(new_energy)

    def predict_energy_trajectory(
        self,
        current_energy: float,
        predicted_activations: List[float],
        horizon: int
    ) -> List[float]:
        """Predict energy trajectory considering thermal and battery dynamics."""

        trajectory = [current_energy]
        energy = current_energy
        temperature = self.current_temperature
        frequency_ratio = self.current_frequency_ratio

        for i in range(horizon):
            # Get predicted activation
            if i < len(predicted_activations):
                activation_prob = predicted_activations[i]
            else:
                activation_prob = 0.15  # Default activation rate

            # Estimate power consumption
            if activation_prob > random.random():
                # Processing step
                processing_power = self._estimate_step_power_consumption("processing")
                step_cost = processing_power * frequency_ratio ** 2.5  # Power scaling
            else:
                # Idle step
                step_cost = self.config.idle_power

            # Update thermal state (simplified)
            temp_change = (step_cost - self.config.idle_power) * 0.01
            temperature = min(temperature + temp_change, self.config.max_temperature)

            # Thermal throttling
            if temperature > self.config.thermal_throttling_threshold:
                frequency_ratio = max(frequency_ratio * 0.95, self.config.min_frequency_ratio)
            else:
                frequency_ratio = min(frequency_ratio * 1.01, self.config.max_frequency_ratio)

            # Energy harvesting
            harvest_energy = 0.0
            if self.config.harvesting_enabled:
                harvest_energy = self.config.max_harvest_power * self.config.harvest_efficiency

            # Update energy
            net_cost = step_cost - harvest_energy
            normalized_cost = net_cost / (self.battery_energy_mwh / 100.0)
            energy = max(0.0, energy - normalized_cost)

            trajectory.append(float(energy))

        return trajectory

    def _estimate_step_power_consumption(self, operation_type: str) -> float:
        """Estimate power consumption for a single time step."""

        base_power = self.config.cpu_active_power

        if operation_type == "processing":
            # Add computational and memory power
            comp_power = self.config.computation_power_per_mflop * 10  # Assume 10 MFLOPS
            mem_power = self.config.memory_access_power
            return base_power + comp_power + mem_power
        else:
            return self.config.idle_power

    def get_energy_pressure(self, current_energy: float, max_energy: float) -> float:
        """Compute energy pressure considering battery characteristics."""

        energy_fraction = current_energy / max_energy

        # Non-linear pressure based on battery discharge curve
        if energy_fraction > 0.8:
            pressure = 0.0
        elif energy_fraction > 0.5:
            pressure = 0.1 * (0.8 - energy_fraction) / 0.3
        elif energy_fraction > 0.2:
            pressure = 0.1 + 0.2 * (0.5 - energy_fraction) / 0.3
        else:
            pressure = 0.3 + 0.7 * (0.2 - energy_fraction) / 0.2

        # Increase pressure if thermal throttling is active
        if self.thermal_throttling_active:
            pressure *= 1.5

        return float(np.clip(pressure, 0.0, 1.0))

    def get_hardware_metrics(self) -> Dict[str, Any]:
        """Get current hardware state metrics."""
        return {
            "temperature_celsius": self.current_temperature,
            "frequency_ratio": self.current_frequency_ratio,
            "thermal_throttling_active": self.thermal_throttling_active,
            "cumulative_energy_consumed_mj": self.cumulative_energy_consumed,
            "power_efficiency_mips_per_mw": self.hardware_profile["power_efficiency_mips_per_mw"],
            "estimated_battery_life_hours": (
                (self.battery_energy_mwh - self.cumulative_energy_consumed) /
                (self.config.idle_power * 1000 / 3600)
            ) if self.cumulative_energy_consumed > 0 else float("inf")
        }
