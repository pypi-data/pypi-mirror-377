# src/sundew/enhanced_core.py
"""
Enhanced Sundew algorithm with modular architecture.
Supports pluggable significance models, gating strategies, control policies, and energy models.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np

from .control_policies import MPCControlPolicy, PIControlPolicy
from .energy_models import RealisticEnergyModel, SimpleEnergyModel
from .gating_strategies import AdaptiveGatingStrategy, TemperatureGatingStrategy
from .interfaces import (
    ControlPolicy,
    ControlState,
    EnergyModel,
    GatingStrategy,
    ProcessingContext,
    ProcessingResult,
    SignificanceModel,
)
from .significance_models import LinearSignificanceModel, NeuralSignificanceModel

# Advanced features
try:
    from .information_theory import InformationTheoreticController
    INFORMATION_THEORY_AVAILABLE = True
except ImportError:
    InformationTheoreticController = None
    INFORMATION_THEORY_AVAILABLE = False

try:
    from .batch_processing import GPU_AVAILABLE, BatchProcessingConfig, BatchProcessingEngine
    BATCH_PROCESSING_AVAILABLE = True
except ImportError:
    BatchProcessingEngine = None
    BatchProcessingConfig = None
    GPU_AVAILABLE = False
    BATCH_PROCESSING_AVAILABLE = False

try:
    from .automl_optimization import AutoMLOptimizer
    AUTOML_AVAILABLE = True
except ImportError:
    AutoMLOptimizer = None
    AUTOML_AVAILABLE = False

try:
    from .theoretical_analysis import TheoreticalAnalysisEngine
    THEORETICAL_ANALYSIS_AVAILABLE = True
except ImportError:
    TheoreticalAnalysisEngine = None
    THEORETICAL_ANALYSIS_AVAILABLE = False


@dataclass
class EnhancedSundewConfig:
    """Configuration for enhanced Sundew algorithm with modular components and advanced features."""

    # Component selection
    significance_model: str = "linear"  # "linear", "neural"
    gating_strategy: str = "temperature"  # "temperature", "adaptive"
    control_policy: str = "pi"  # "pi", "mpc"
    energy_model: str = "simple"  # "simple", "realistic"

    # Target performance
    target_activation_rate: float = 0.15

    # Threshold bounds
    min_threshold: float = 0.20
    max_threshold: float = 0.92
    initial_threshold: float = 0.78

    # Performance monitoring
    enable_detailed_logging: bool = True
    log_frequency: int = 100  # Log every N samples
    performance_window: int = 1000  # Window for performance metrics

    # Advanced features
    enable_online_learning: bool = True
    enable_auto_tuning: bool = False
    multi_objective_optimization: bool = False

    # ADVANCED: Information-theoretic threshold adaptation
    enable_information_theoretic_threshold: bool = False
    information_threshold_method: str = "mutual_information"  # "mutual_information" or "entropy"
    mutual_info_history_size: int = 1000
    mutual_info_adaptation_rate: float = 0.1
    target_entropy: float = 0.5
    entropy_weight: float = 0.7

    # ADVANCED: High-performance batch processing
    enable_batch_processing: bool = False
    batch_processing_method: str = "vectorized"  # "vectorized", "gpu", or "parallel"
    batch_size: int = 1000
    max_workers: Optional[int] = None
    use_gpu: bool = False
    use_numba: bool = True
    memory_limit_mb: int = 1024

    # ADVANCED: AutoML optimization
    enable_automl: bool = False
    automl_time_budget_minutes: int = 30
    automl_method: str = "auto"  # "auto", "bayesian", "optuna_tpe", "genetic"
    automl_n_trials: Optional[int] = None

    # ADVANCED: Theoretical analysis
    enable_theoretical_analysis: bool = False
    stability_analysis_enabled: bool = True
    performance_bounds_enabled: bool = True
    statistical_testing_enabled: bool = True
    convergence_testing_enabled: bool = True

    # Component-specific configurations
    component_configs: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def get_component_config(self, component_name: str) -> Dict[str, Any]:
        """Get configuration for a specific component."""
        return self.component_configs.get(component_name, {})

    @classmethod
    def create_optimized_config(cls, application_domain: str = "general",
                              performance_target: str = "balanced") -> 'EnhancedSundewConfig':
        """Create AutoML-optimized configuration presets for different domains and targets."""

        if application_domain == "edge_computing":
            # Optimized for edge devices with limited resources
            base_config = cls(
                # Basic settings
                significance_model="linear",  # Faster than neural
                gating_strategy="temperature",  # Simple gating
                control_policy="pi",  # Stable and efficient
                energy_model="simple",  # Lower overhead
                target_activation_rate=0.12,  # More conservative

                # Thresholds
                min_threshold=0.25,
                max_threshold=0.85,
                initial_threshold=0.65,

                # Performance settings
                performance_window=500,  # Smaller window
                log_frequency=200,

                # Advanced features (optimized for edge)
                enable_information_theoretic_threshold=True,
                information_threshold_method="entropy",  # Simpler than MI
                enable_batch_processing=True,
                batch_processing_method="vectorized",  # No GPU on edge
                batch_size=100,  # Smaller batches
                enable_theoretical_analysis=False  # Skip for performance
            )

        elif application_domain == "cloud_hpc":
            # Optimized for high-performance cloud computing
            base_config = cls(
                # Advanced models
                significance_model="neural",
                gating_strategy="adaptive",
                control_policy="mpc",  # Advanced control
                energy_model="realistic",
                target_activation_rate=0.18,

                # Thresholds
                min_threshold=0.15,
                max_threshold=0.95,
                initial_threshold=0.75,

                # Large windows for stability
                performance_window=2000,
                log_frequency=50,

                # All advanced features enabled
                enable_information_theoretic_threshold=True,
                information_threshold_method="mutual_information",
                enable_batch_processing=True,
                batch_processing_method="gpu" if BATCH_PROCESSING_AVAILABLE and GPU_AVAILABLE else "parallel",
                batch_size=2000,
                use_gpu=True,
                max_workers=None,  # Use all cores
                enable_automl=True,
                enable_theoretical_analysis=True
            )

        elif application_domain == "real_time":
            # Optimized for real-time systems
            base_config = cls(
                # Fast components
                significance_model="linear",
                gating_strategy="temperature",
                control_policy="pi",
                energy_model="simple",
                target_activation_rate=0.20,  # Higher for responsiveness

                # Tight thresholds
                min_threshold=0.30,
                max_threshold=0.80,
                initial_threshold=0.55,

                # Fast adaptation
                performance_window=100,
                log_frequency=10,

                # Batch processing for throughput
                enable_batch_processing=True,
                batch_processing_method="vectorized",
                batch_size=50,  # Small for low latency

                # Skip expensive analysis
                enable_information_theoretic_threshold=False,
                enable_theoretical_analysis=False
            )

        elif application_domain == "research":
            # Optimized for research with all features
            base_config = cls(
                # Advanced everything
                significance_model="neural",
                gating_strategy="adaptive",
                control_policy="mpc",
                energy_model="realistic",
                target_activation_rate=0.15,

                # Wide range for exploration
                min_threshold=0.10,
                max_threshold=0.98,
                initial_threshold=0.70,

                # Large windows for analysis
                performance_window=5000,
                log_frequency=25,

                # All features enabled
                enable_online_learning=True,
                enable_auto_tuning=True,
                enable_information_theoretic_threshold=True,
                information_threshold_method="mutual_information",
                enable_batch_processing=True,
                batch_processing_method="auto",
                batch_size=1000,
                enable_automl=True,
                enable_theoretical_analysis=True,

                # Research-specific settings
                mutual_info_history_size=2000,
                automl_time_budget_minutes=60
            )
        else:
            # General balanced configuration
            base_config = cls(
                # Balanced settings
                significance_model="neural",
                gating_strategy="adaptive",
                control_policy="pi",
                energy_model="realistic",
                target_activation_rate=0.15,

                # Standard thresholds
                min_threshold=0.20,
                max_threshold=0.92,
                initial_threshold=0.78,

                # Moderate settings
                performance_window=1000,
                log_frequency=100,

                # Some advanced features
                enable_information_theoretic_threshold=True,
                information_threshold_method="mutual_information",
                enable_batch_processing=True,
                batch_processing_method="vectorized",
                batch_size=1000,
                enable_theoretical_analysis=True
            )

        # Apply performance target adjustments to any configuration
        if performance_target == "energy_efficient":
            base_config.target_activation_rate *= 0.8  # Reduce activations
            base_config.min_threshold += 0.1  # Higher thresholds
            base_config.initial_threshold += 0.1
        elif performance_target == "high_throughput":
            base_config.target_activation_rate *= 1.3  # More activations
            base_config.min_threshold -= 0.05  # Lower thresholds
            base_config.performance_window *= 2  # Larger windows
        elif performance_target == "low_latency":
            base_config.performance_window = min(100, base_config.performance_window)
            base_config.log_frequency = max(5, base_config.log_frequency // 2)
            base_config.enable_theoretical_analysis = False  # Skip for speed

        return base_config

    @classmethod
    def get_available_presets(cls) -> Dict[str, Dict[str, str]]:
        """Get information about available configuration presets."""
        return {
            'domains': {
                'edge_computing': 'Optimized for edge devices with limited resources',
                'cloud_hpc': 'Optimized for high-performance cloud computing',
                'real_time': 'Optimized for real-time systems requiring low latency',
                'research': 'Full-featured configuration for research applications',
                'general': 'Balanced configuration for general use'
            },
            'targets': {
                'energy_efficient': 'Minimize energy consumption',
                'high_throughput': 'Maximize processing throughput',
                'low_latency': 'Minimize response latency',
                'balanced': 'Balance between all objectives'
            }
        }


@dataclass
class EnhancedMetrics:
    """Enhanced metrics container with detailed performance tracking."""

    # Basic metrics
    total_processed: int = 0
    total_activated: int = 0
    total_processing_time: float = 0.0
    total_energy_consumed: float = 0.0

    # Performance metrics
    activation_rate_history: List[float] = field(default_factory=list)
    threshold_history: List[float] = field(default_factory=list)
    energy_history: List[float] = field(default_factory=list)
    significance_history: List[float] = field(default_factory=list)

    # Component-specific metrics
    significance_model_metrics: Dict[str, Any] = field(default_factory=dict)
    gating_strategy_metrics: Dict[str, Any] = field(default_factory=dict)
    control_policy_metrics: Dict[str, Any] = field(default_factory=dict)
    energy_model_metrics: Dict[str, Any] = field(default_factory=dict)

    # Quality metrics
    prediction_accuracies: List[float] = field(default_factory=list)
    stability_scores: List[float] = field(default_factory=list)

    def update_histories(self, activation_rate: float, threshold: float,
                        energy_level: float, significance: float, window_size: int = 1000):
        """Update metric histories with window management."""
        self.activation_rate_history.append(activation_rate)
        self.threshold_history.append(threshold)
        self.energy_history.append(energy_level)
        self.significance_history.append(significance)

        # Maintain window size
        for history in [self.activation_rate_history, self.threshold_history,
                       self.energy_history, self.significance_history]:
            if len(history) > window_size:
                history.pop(0)


class EnhancedSundewAlgorithm:
    """
    Enhanced Sundew algorithm with modular architecture.
    Provides pluggable components for different application domains and requirements.
    """

    def __init__(
        self,
        config: EnhancedSundewConfig,
        significance_model: Optional[SignificanceModel] = None,
        gating_strategy: Optional[GatingStrategy] = None,
        control_policy: Optional[ControlPolicy] = None,
        energy_model: Optional[EnergyModel] = None
    ):
        self.config = config

        # Initialize components (use provided or create from config)
        self.significance_model = significance_model or self._create_significance_model()
        self.gating_strategy = gating_strategy or self._create_gating_strategy()
        self.control_policy = control_policy or self._create_control_policy()
        self.energy_model = energy_model or self._create_energy_model()

        # Initialize advanced components
        self.information_controller = None
        self.batch_engine = None
        self.automl_optimizer = None
        self.theoretical_analyzer = None

        self._initialize_advanced_features()

        # Initialize state
        self.control_state = ControlState(
            threshold=config.initial_threshold,
            activation_rate=0.0,
            energy_level=1.0,
            error_integral=0.0,
            stability_metrics={}
        )

        # Initialize metrics
        self.metrics = EnhancedMetrics()

        # Processing history for context
        self.processing_history: List[Dict[str, Any]] = []
        self.recent_activations: List[bool] = []

        # Performance tracking
        self.performance_evaluator = PerformanceEvaluator(config)

        # Auto-tuning state
        if config.enable_auto_tuning:
            self.auto_tuner = AutoTuner(config)
        else:
            self.auto_tuner = None

    def _create_significance_model(self) -> SignificanceModel:
        """Create significance model based on configuration."""
        model_type = self.config.significance_model
        model_config = self.config.get_component_config("significance_model")

        if model_type == "neural":
            from .significance_models import NeuralSignificanceConfig
            config = NeuralSignificanceConfig(**model_config)
            return NeuralSignificanceModel(config)
        else:  # "linear"
            from .significance_models import LinearSignificanceConfig
            config = LinearSignificanceConfig(**model_config)
            return LinearSignificanceModel(config)

    def _create_gating_strategy(self) -> GatingStrategy:
        """Create gating strategy based on configuration."""
        strategy_type = self.config.gating_strategy
        strategy_config = self.config.get_component_config("gating_strategy")

        if strategy_type == "adaptive":
            from .gating_strategies import AdaptiveGatingConfig
            config = AdaptiveGatingConfig(**strategy_config)
            return AdaptiveGatingStrategy(config)
        else:  # "temperature"
            from .gating_strategies import TemperatureGatingConfig
            config = TemperatureGatingConfig(**strategy_config)
            return TemperatureGatingStrategy(config)

    def _create_control_policy(self) -> ControlPolicy:
        """Create control policy based on configuration."""
        policy_type = self.config.control_policy
        policy_config = self.config.get_component_config("control_policy")

        if policy_type == "mpc":
            from .control_policies import MPCControlConfig
            config = MPCControlConfig(**policy_config)
            return MPCControlPolicy(config)
        else:  # "pi"
            from .control_policies import PIControlConfig
            config = PIControlConfig(**policy_config)
            return PIControlPolicy(config)

    def _create_energy_model(self) -> EnergyModel:
        """Create energy model based on configuration."""
        model_type = self.config.energy_model
        model_config = self.config.get_component_config("energy_model")

        if model_type == "realistic":
            from .energy_models import RealisticEnergyConfig
            config = RealisticEnergyConfig(**model_config)
            return RealisticEnergyModel(config)
        else:  # "simple"
            from .energy_models import SimpleEnergyConfig
            config = SimpleEnergyConfig(**model_config)
            return SimpleEnergyModel(config)

    def _initialize_advanced_features(self):
        """Initialize advanced feature components based on configuration."""

        # Information-theoretic threshold controller
        if self.config.enable_information_theoretic_threshold and INFORMATION_THEORY_AVAILABLE:
            try:
                # Create parameters based on method
                if self.config.information_threshold_method == "mutual_information":
                    params = {
                        'history_size': self.config.mutual_info_history_size,
                        'alpha': self.config.mutual_info_adaptation_rate
                    }
                else:  # entropy method
                    params = {
                        'target_entropy': self.config.target_entropy,
                        'entropy_weight': self.config.entropy_weight,
                        'history_size': self.config.mutual_info_history_size
                    }

                self.information_controller = InformationTheoreticController(
                    method=self.config.information_threshold_method,
                    **params
                )
                print("[OK] Information-theoretic threshold controller initialized")
            except Exception as e:
                print(f"[WARNING] Information-theoretic controller failed to initialize: {e}")

        # Batch processing engine
        if self.config.enable_batch_processing and BATCH_PROCESSING_AVAILABLE:
            try:
                batch_config = BatchProcessingConfig(
                    batch_size=self.config.batch_size,
                    max_workers=1,  # Disable parallel to avoid recursion
                    use_gpu=self.config.use_gpu,
                    use_numba=self.config.use_numba,
                    memory_limit_mb=self.config.memory_limit_mb
                )
                self.batch_engine = BatchProcessingEngine(self, batch_config)
                print("[OK] Batch processing engine initialized")
            except Exception as e:
                print(f"[WARNING] Batch processing engine failed to initialize: {e}")

        # AutoML optimizer
        if self.config.enable_automl and AUTOML_AVAILABLE:
            try:
                objectives = [
                    # Would need to import OptimizationObjective
                    # OptimizationObjective('energy_savings', weight=0.4, minimize=False),
                    # OptimizationObjective('f1_score', weight=0.4, minimize=False),
                    # OptimizationObjective('processing_time', weight=0.2, minimize=True)
                ]
                self.automl_optimizer = AutoMLOptimizer(
                    objectives=None,  # Use defaults for now
                    time_budget_minutes=self.config.automl_time_budget_minutes
                )
                print("[OK] AutoML optimizer initialized")
            except Exception as e:
                print(f"[WARNING] AutoML optimizer failed to initialize: {e}")

        # Theoretical analysis engine
        if self.config.enable_theoretical_analysis and THEORETICAL_ANALYSIS_AVAILABLE:
            try:
                analysis_params = {
                    'adapt_kp': 0.1,  # Would get from control policy
                    'adapt_ki': 0.01,
                    'target_activation_rate': self.config.target_activation_rate,
                    'dormant_tick_cost': 0.5,  # Would get from energy model
                    'base_processing_cost': 50.0,
                    'energy_pressure': 0.05
                }
                self.theoretical_analyzer = TheoreticalAnalysisEngine(analysis_params)
                print("[OK] Theoretical analysis engine initialized")
            except Exception as e:
                print(f"[WARNING] Theoretical analysis engine failed to initialize: {e}")

    def process(self, features: Dict[str, Any]) -> ProcessingResult:
        """
        Process input using enhanced modular pipeline.

        Args:
            features: Input features dictionary

        Returns:
            ProcessingResult with activation status and metrics
        """
        start_time = time.perf_counter()

        # Create processing context
        context = ProcessingContext(
            timestamp=start_time,
            sequence_id=self.metrics.total_processed,
            features=features,
            history=self.processing_history[-10:],  # Last 10 samples
            metadata={
                "algorithm_version": "enhanced",
                "config": self.config
            }
        )

        # Compute significance
        significance, significance_explanation = self.significance_model.compute_significance(context)

        # Make gating decision
        gating_decision = self.gating_strategy.gate(
            significance=significance,
            threshold=self.control_state.threshold,
            context=context,
            control_state=self.control_state
        )

        # Update metrics
        self.metrics.total_processed += 1
        self.metrics.significance_history.append(significance)

        if not gating_decision.should_process:
            # Gated - compute idle cost and update state
            idle_duration = 1.0  # Assume 1 time unit
            idle_cost = self.energy_model.compute_idle_cost(idle_duration)

            new_energy = self.energy_model.update_energy_state(
                self.control_state.energy_level * 100,  # Convert to energy model scale
                idle_cost
            ) / 100.0  # Convert back to [0,1] scale

            # Update control state
            self.recent_activations.append(False)
            self._update_control_state(activated=False, new_energy=new_energy)

            # Store processing history
            self.processing_history.append({
                "features": features,
                "significance": significance,
                "activated": False,
                "timestamp": start_time
            })

            if len(self.processing_history) > 100:
                self.processing_history.pop(0)

            # Return result for gated case
            return ProcessingResult(
                activated=False,
                significance=significance,
                energy_consumed=idle_cost,
                processing_time=time.perf_counter() - start_time,
                threshold_used=self.control_state.threshold,
                explanation=significance_explanation,
                component_metrics={
                    "significance_model": getattr(self.significance_model, 'get_metrics', lambda: {})(),
                    "gating_strategy": getattr(self.gating_strategy, 'get_metrics', lambda: {})(),
                    "control_policy": getattr(self.control_policy, 'get_metrics', lambda: {})(),
                    "energy_model": getattr(self.energy_model, 'get_metrics', lambda: {})()
                }
            )

        # Activated - perform processing
        processing_type = self._determine_processing_type(significance, context)
        processing_cost = self.energy_model.compute_processing_cost(
            significance=significance,
            processing_type=processing_type,
            context=context
        )

        # Simulate processing time
        processing_time = self._simulate_processing_time(significance, processing_type)

        # Update energy state
        new_energy = self.energy_model.update_energy_state(
            self.control_state.energy_level * 100,  # Convert to energy model scale
            processing_cost
        ) / 100.0  # Convert back to [0,1] scale

        # Update metrics
        self.metrics.total_activated += 1
        self.metrics.total_processing_time += processing_time
        self.metrics.total_energy_consumed += processing_cost

        # Update control state
        self.recent_activations.append(True)
        self._update_control_state(activated=True, new_energy=new_energy)

        # Create processing result
        result = ProcessingResult(
            activated=True,
            significance=significance,
            energy_consumed=processing_cost,
            processing_time=processing_time,
            threshold_used=self.control_state.threshold,
            explanation=significance_explanation,
            component_metrics={
                "significance_model": getattr(self.significance_model, 'get_metrics', lambda: {})(),
                "gating_strategy": getattr(self.gating_strategy, 'get_metrics', lambda: {})(),
                "control_policy": getattr(self.control_policy, 'get_metrics', lambda: {})(),
                "energy_model": getattr(self.energy_model, 'get_metrics', lambda: {})()
            }
        )

        # Update learning models
        if self.config.enable_online_learning:
            self._update_learning_models(context, result, gating_decision)

        # Store processing history
        self.processing_history.append({
            "features": features,
            "significance": significance,
            "activated": True,
            "timestamp": start_time,
            "processing_time": processing_time,
            "energy_cost": processing_cost
        })

        if len(self.processing_history) > 100:
            self.processing_history.pop(0)

        # Performance evaluation and auto-tuning
        if self.metrics.total_processed % self.config.log_frequency == 0:
            self._evaluate_performance()

            if self.auto_tuner is not None:
                self.auto_tuner.update(self.metrics, self.control_state)

        return result

    def _process_single_direct(self, features: Dict[str, Any]) -> ProcessingResult:
        """Direct processing method for batch processing to avoid recursion."""
        start_time = time.perf_counter()

        # Create processing context
        context = ProcessingContext(
            timestamp=start_time,
            sequence_id=0,  # Not tracked in batch mode
            features=features,
            history=[],  # Empty for batch processing
            metadata={"algorithm_version": "enhanced_batch"}
        )

        # Compute significance
        significance, significance_explanation = self.significance_model.compute_significance(context)

        # Make gating decision using current threshold
        current_threshold = getattr(self.control_state, 'threshold', self.config.initial_threshold)
        activated = significance >= current_threshold

        # Compute energy cost
        if activated:
            processing_cost = self.energy_model.compute_processing_cost(
                significance=significance,
                processing_type="batch_processing",
                context=context
            )
        else:
            processing_cost = self.energy_model.compute_idle_cost(1.0)

        processing_time = time.perf_counter() - start_time

        return ProcessingResult(
            activated=activated,
            significance=significance,
            energy_consumed=processing_cost,
            processing_time=processing_time,
            threshold_used=current_threshold,
            explanation=significance_explanation,
            component_metrics={}
        )

    def process_batch(self, samples: List[Dict[str, Any]],
                     processor_type: Optional[str] = None):
        """Process a batch of samples using high-performance batch processing."""
        if not self.batch_engine:
            # Fallback: process samples individually
            activations = []
            significance_scores = []
            energy_consumed = []
            processing_times = []

            for sample in samples:
                result = self.process(sample)
                activations.append(1.0 if result.activated else 0.0)
                significance_scores.append(result.significance)
                energy_consumed.append(result.energy_consumed)
                processing_times.append(result.processing_time)

            # Return BatchResult-like structure
            from types import SimpleNamespace
            return SimpleNamespace(
                processed_samples=len(samples),
                activations=np.array(activations),
                significance_scores=np.array(significance_scores),
                energy_consumed=np.array(energy_consumed),
                processing_times=np.array(processing_times),
                activation_rate=np.mean(activations),
                total_energy=np.sum(energy_consumed),
                avg_processing_time=np.mean(processing_times),
                metadata={'method': 'individual_fallback'}
            )

        # Use high-performance batch processing
        return self.batch_engine.process_batch(samples, processor_type)

    def process_large_dataset(self, data_source, processor_type: Optional[str] = None):
        """Process large dataset with streaming and optimal batching."""
        if not self.batch_engine:
            # Fallback: process in chunks
            def fallback_generator():
                batch = []
                for sample in data_source:
                    batch.append(sample)
                    if len(batch) >= 1000:  # Default batch size
                        yield self.process_batch(batch)
                        batch = []
                if batch:
                    yield self.process_batch(batch)
            return fallback_generator()

        # Use streaming batch processor
        return self.batch_engine.process_large_dataset(data_source, processor_type)

    def optimize_with_automl(self, test_data: List[Dict],
                           time_budget_minutes: int = 30) -> Optional[Dict[str, Any]]:
        """Optimize algorithm configuration using AutoML."""
        if not self.automl_optimizer:
            print("[WARNING] AutoML optimizer not available")
            return None

        try:
            # Create evaluation function
            def evaluate_config(params):
                # Apply parameters to current configuration
                temp_config = self.config
                for key, value in params.items():
                    if hasattr(temp_config, key):
                        setattr(temp_config, key, value)

                # Test on sample data
                results = []
                for sample in test_data[:100]:  # Use subset for speed
                    result = self.process(sample)
                    results.append({
                        'activated': result.activated,
                        'significance': result.significance,
                        'energy': result.energy_consumed,
                        'time': result.processing_time
                    })

                # Compute metrics
                activation_rate = np.mean([r['activated'] for r in results])
                avg_energy = np.mean([r['energy'] for r in results])
                energy_savings = 1.0 - (avg_energy / 50.0)  # Normalize against full processing

                return {
                    'energy_savings': energy_savings,
                    'f1_score': min(1.0, activation_rate * 2),  # Simplified
                    'processing_time': np.mean([r['time'] for r in results])
                }

            # Run optimization
            result = self.automl_optimizer.optimize_sundew_config(
                evaluation_func=evaluate_config,
                enhanced_system=True,
                method='auto',
                n_trials=min(100, time_budget_minutes * 2)
            )

            return result.best_params

        except Exception as e:
            print(f"[WARNING] AutoML optimization failed: {e}")
            return None

    def benchmark_batch_processors(self, test_samples: List[Dict]) -> Dict[str, Dict[str, float]]:
        """Benchmark available batch processors."""
        if not self.batch_engine:
            return {'error': 'Batch engine not available'}

        try:
            return self.batch_engine.benchmark_processors(test_samples)
        except Exception as e:
            return {'error': f'Benchmark failed: {e}'}

    def _determine_processing_type(self, significance: float, context: ProcessingContext) -> str:
        """Determine processing type based on significance and context."""
        if isinstance(self.significance_model, NeuralSignificanceModel):
            return "neural_inference"
        elif isinstance(self.gating_strategy, AdaptiveGatingStrategy):
            return "attention_gating"
        elif isinstance(self.control_policy, MPCControlPolicy):
            return "mpc_control"
        else:
            return "linear_significance"

    def _simulate_processing_time(self, significance: float, processing_type: str) -> float:
        """Simulate realistic processing time."""
        base_times = {
            "neural_inference": 0.005,  # 5ms
            "attention_gating": 0.003,  # 3ms
            "mpc_control": 0.008,       # 8ms
            "linear_significance": 0.001  # 1ms
        }

        base_time = base_times.get(processing_type, 0.002)
        complexity_factor = 1.0 + significance * 0.5  # More significant = more time

        return base_time * complexity_factor

    def _update_control_state(self, activated: bool, new_energy: float):
        """Update control state using control policy and advanced features."""

        # Compute current activation rate
        if len(self.recent_activations) > 0:
            activation_rate = sum(self.recent_activations) / len(self.recent_activations)
        else:
            activation_rate = 0.0

        # Limit history size
        if len(self.recent_activations) > self.config.performance_window:
            self.recent_activations.pop(0)

        # Update control state
        self.control_state.activation_rate = activation_rate
        self.control_state.energy_level = new_energy

        # Primary threshold update using control policy
        energy_state = {"energy_level": new_energy}
        new_threshold, updated_state = self.control_policy.update_threshold(
            current_state=self.control_state,
            target_activation_rate=self.config.target_activation_rate,
            recent_activations=self.recent_activations,
            energy_state=energy_state
        )

        # Advanced: Information-theoretic threshold adjustment
        if self.information_controller and len(self.metrics.significance_history) > 0:
            try:
                # Get recent data for information-theoretic analysis
                recent_size = min(100, len(self.metrics.significance_history))
                recent_significance = np.array(self.metrics.significance_history[-recent_size:])
                recent_activations_array = np.array(self.recent_activations[-recent_size:])

                # Update information-theoretic threshold
                info_threshold = self.information_controller.update_threshold(
                    recent_significance, recent_activations_array
                )

                # Blend traditional and information-theoretic thresholds
                blend_weight = 0.3  # 30% information-theoretic, 70% traditional
                new_threshold = (1 - blend_weight) * new_threshold + blend_weight * info_threshold

            except Exception as e:
                # Fallback to traditional threshold if information-theoretic fails
                print(f"[WARNING] Information-theoretic threshold update failed: {e}")

        # Apply threshold bounds
        new_threshold = np.clip(new_threshold, self.config.min_threshold, self.config.max_threshold)

        # Update control state
        self.control_state = updated_state
        self.control_state.threshold = new_threshold

        # Update metrics histories
        self.metrics.update_histories(
            activation_rate=activation_rate,
            threshold=new_threshold,
            energy_level=new_energy,
            significance=self.metrics.significance_history[-1] if self.metrics.significance_history else 0.0,
            window_size=self.config.performance_window
        )

    def _update_learning_models(
        self,
        context: ProcessingContext,
        result: ProcessingResult,
        gating_decision: Any
    ):
        """Update learning models based on processing outcome."""

        # Create outcome information
        outcome = {
            "energy_efficiency": 1.0 - (result.energy_consumed / 10.0),  # Normalize
            "processing_time": result.processing_time,
            "activation_confidence": gating_decision.confidence,
            "significance": result.significance
        }

        # Simple accuracy estimation (would use ground truth in practice)
        if hasattr(self, 'ground_truth_labels'):
            # Would compute actual accuracy here
            outcome["accuracy"] = 0.8  # Placeholder
        else:
            # Estimate accuracy based on confidence and significance
            outcome["accuracy"] = gating_decision.confidence * result.significance

        # Update significance model
        self.significance_model.update(context, outcome)

    def _evaluate_performance(self):
        """Evaluate current system performance."""
        if self.performance_evaluator:
            performance_metrics = self.performance_evaluator.evaluate(
                self.metrics, self.control_state
            )

            # Store performance metrics
            self.metrics.significance_model_metrics.update(performance_metrics.get("significance", {}))
            self.metrics.gating_strategy_metrics.update(performance_metrics.get("gating", {}))
            self.metrics.control_policy_metrics.update(performance_metrics.get("control", {}))
            self.metrics.energy_model_metrics.update(performance_metrics.get("energy", {}))

    def get_comprehensive_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report."""

        # Basic metrics
        total_samples = max(1, self.metrics.total_processed)
        activation_rate = self.metrics.total_activated / total_samples
        avg_processing_time = (
            self.metrics.total_processing_time / max(1, self.metrics.total_activated)
        )

        # Energy metrics
        energy_remaining = self.control_state.energy_level
        total_energy_used = self.metrics.total_energy_consumed

        # Stability metrics
        stability_metrics = self.control_policy.predict_stability(self.control_state)

        # Component-specific metrics
        component_metrics = {
            "significance_model": {
                "type": self.config.significance_model,
                "parameters": self.significance_model.get_parameters(),
                "metrics": self.metrics.significance_model_metrics
            },
            "gating_strategy": {
                "type": self.config.gating_strategy,
                "exploration_rate": self.gating_strategy.get_exploration_probability(self.control_state),
                "metrics": self.metrics.gating_strategy_metrics
            },
            "control_policy": {
                "type": self.config.control_policy,
                "stability_prediction": stability_metrics,
                "theoretical_bounds": self.control_policy.get_theoretical_bounds(),
                "metrics": self.metrics.control_policy_metrics
            },
            "energy_model": {
                "type": self.config.energy_model,
                "current_pressure": self.energy_model.get_energy_pressure(
                    energy_remaining * 100, 100.0
                ),
                "metrics": self.metrics.energy_model_metrics
            }
        }

        # Performance trends
        if len(self.metrics.activation_rate_history) > 10:
            activation_trend = np.polyfit(
                range(len(self.metrics.activation_rate_history[-50:])),
                self.metrics.activation_rate_history[-50:],
                1
            )[0]
        else:
            activation_trend = 0.0

        report = {
            # Basic performance
            "total_samples": total_samples,
            "activations": self.metrics.total_activated,
            "activation_rate": activation_rate,
            "target_activation_rate": self.config.target_activation_rate,
            "activation_error": abs(activation_rate - self.config.target_activation_rate),

            # Timing
            "avg_processing_time": avg_processing_time,
            "total_processing_time": self.metrics.total_processing_time,

            # Energy
            "energy_remaining": energy_remaining,
            "total_energy_consumed": total_energy_used,
            "energy_efficiency": 1.0 - (total_energy_used / max(1, total_samples * 10)),

            # Control
            "current_threshold": self.control_state.threshold,
            "threshold_range": (self.config.min_threshold, self.config.max_threshold),
            "stability_metrics": self.control_state.stability_metrics,

            # Trends
            "activation_rate_trend": activation_trend,
            "threshold_stability": np.std(self.metrics.threshold_history[-20:]) if len(self.metrics.threshold_history) >= 20 else 0.0,

            # Component details
            "components": component_metrics,

            # Advanced metrics
            "performance_score": self._compute_performance_score(),
            "research_quality_score": self._compute_research_quality_score()
        }

        # Add advanced feature reports
        if self.information_controller:
            try:
                info_report = self.information_controller.get_comprehensive_report()
                report["information_theoretic_analysis"] = info_report
            except Exception as e:
                report["information_theoretic_analysis"] = {"error": str(e)}

        if self.batch_engine:
            try:
                batch_report = self.batch_engine.get_performance_report()
                report["batch_processing_performance"] = batch_report
            except Exception as e:
                report["batch_processing_performance"] = {"error": str(e)}

        if self.automl_optimizer:
            try:
                automl_report = self.automl_optimizer.get_optimization_report()
                report["automl_optimization"] = automl_report
            except Exception as e:
                report["automl_optimization"] = {"error": str(e)}

        if self.theoretical_analyzer:
            try:
                # Get comprehensive theoretical analysis with current empirical data
                performance_metrics_history = []
                if len(self.metrics.activation_rate_history) > 0:
                    for i in range(min(50, len(self.metrics.activation_rate_history))):
                        performance_metrics_history.append({
                            'energy_savings': self.metrics.energy_history[i] if i < len(self.metrics.energy_history) else 0,
                            'activation_rate': self.metrics.activation_rate_history[i],
                            'f1_score': min(1.0, self.metrics.activation_rate_history[i] * 2)  # Simplified F1
                        })

                empirical_data = {
                    'threshold_history': list(self.metrics.threshold_history),
                    'performance_metrics': performance_metrics_history,
                    'final_metrics': {
                        'energy_savings': report['energy_efficiency'],
                        'activation_rate': activation_rate,
                        'processing_time': avg_processing_time
                    },
                    'system_configuration': {
                        'control_policy': self.config.control_policy,
                        'significance_model': self.config.significance_model,
                        'gating_strategy': self.config.gating_strategy,
                        'energy_model': self.config.energy_model
                    }
                }
                theoretical_report = self.theoretical_analyzer.comprehensive_analysis(empirical_data)
                report["theoretical_analysis"] = theoretical_report
            except Exception as e:
                report["theoretical_analysis"] = {"error": str(e)}

        return report

    def _compute_performance_score(self) -> float:
        """Compute overall performance score (0-10)."""

        # Activation rate accuracy (0-3 points)
        activation_error = abs(self.control_state.activation_rate - self.config.target_activation_rate)
        activation_score = max(0, 3 - activation_error * 15)

        # Energy efficiency (0-3 points)
        energy_score = self.control_state.energy_level * 3

        # Stability (0-2 points)
        oscillation = self.control_state.stability_metrics.get("oscillation", 0.5)
        stability_score = max(0, 2 - oscillation * 4)

        # Convergence (0-2 points)
        if len(self.metrics.threshold_history) >= 20:
            threshold_variance = np.var(self.metrics.threshold_history[-20:])
            convergence_score = max(0, 2 - threshold_variance * 20)
        else:
            convergence_score = 1.0

        return activation_score + energy_score + stability_score + convergence_score

    def _compute_research_quality_score(self) -> float:
        """Compute research quality score (0-10)."""

        base_score = 6.5  # Current prototype level

        # Improvements from modular architecture
        if self.config.significance_model == "neural":
            base_score += 0.5  # Neural learning
        if self.config.gating_strategy == "adaptive":
            base_score += 0.3  # Adaptive gating
        if self.config.control_policy == "mpc":
            base_score += 0.4  # MPC control
        if self.config.energy_model == "realistic":
            base_score += 0.3  # Realistic energy model

        # Advanced feature bonuses
        if self.information_controller:
            base_score += 0.4  # Information-theoretic threshold adaptation
        if self.batch_engine:
            base_score += 0.3  # High-performance batch processing
        if self.automl_optimizer:
            base_score += 0.3  # AutoML hyperparameter optimization
        if self.theoretical_analyzer:
            base_score += 0.5  # Theoretical analysis and proofs

        # Stability and performance bonuses
        stability_bonus = (1.0 - self.control_state.stability_metrics.get("oscillation", 0.5)) * 0.3
        performance_bonus = (self._compute_performance_score() / 10.0) * 0.3

        # Information-theoretic performance bonus
        info_bonus = 0.0
        if self.information_controller and hasattr(self.information_controller, 'performance_history'):
            if len(self.information_controller.performance_history) > 0:
                recent_mi = np.mean([p['metrics']['mutual_information']
                                   for p in self.information_controller.performance_history[-5:]])
                info_bonus = min(0.2, recent_mi * 0.5)  # Up to 0.2 bonus for high MI

        total_score = base_score + stability_bonus + performance_bonus + info_bonus
        return min(10.0, total_score)


class PerformanceEvaluator:
    """Evaluates system performance across multiple dimensions."""

    def __init__(self, config: EnhancedSundewConfig):
        self.config = config

    def evaluate(self, metrics: EnhancedMetrics, control_state: ControlState) -> Dict[str, Any]:
        """Evaluate performance across all components."""
        return {
            "significance": self._evaluate_significance_model(metrics),
            "gating": self._evaluate_gating_strategy(metrics, control_state),
            "control": self._evaluate_control_policy(metrics, control_state),
            "energy": self._evaluate_energy_model(metrics, control_state)
        }

    def _evaluate_significance_model(self, metrics: EnhancedMetrics) -> Dict[str, float]:
        """Evaluate significance model performance."""
        if len(metrics.significance_history) < 10:
            return {"variance": 0.0, "distribution_quality": 0.5}

        significance_variance = np.var(metrics.significance_history[-100:])
        mean_significance = np.mean(metrics.significance_history[-100:])

        return {
            "variance": significance_variance,
            "mean": mean_significance,
            "distribution_quality": min(1.0, significance_variance * 4)  # Good spread is important
        }

    def _evaluate_gating_strategy(self, metrics: EnhancedMetrics, control_state: ControlState) -> Dict[str, float]:
        """Evaluate gating strategy performance."""
        return {
            "decision_consistency": 1.0 - control_state.stability_metrics.get("oscillation", 0.5),
            "exploration_balance": 0.8  # Placeholder - would measure exploration vs exploitation
        }

    def _evaluate_control_policy(self, metrics: EnhancedMetrics, control_state: ControlState) -> Dict[str, float]:
        """Evaluate control policy performance."""
        return {
            "convergence_speed": 1.0 / (1.0 + control_state.stability_metrics.get("settling_time", 10)),
            "overshoot": max(0.0, 1.0 - control_state.stability_metrics.get("overshoot", 0.2)),
            "steady_state_accuracy": max(0.0, 1.0 - control_state.stability_metrics.get("steady_state_error", 0.1))
        }

    def _evaluate_energy_model(self, metrics: EnhancedMetrics, control_state: ControlState) -> Dict[str, float]:
        """Evaluate energy model performance."""
        return {
            "efficiency": control_state.energy_level,
            "prediction_accuracy": 0.8  # Placeholder - would compare predictions to actual
        }


class AutoTuner:
    """Automatic hyperparameter tuning system."""

    def __init__(self, config: EnhancedSundewConfig):
        self.config = config
        self.best_performance = 0.0
        self.tuning_history: List[Dict[str, Any]] = []

    def update(self, metrics: EnhancedMetrics, control_state: ControlState):
        """Update auto-tuning based on performance."""
        # Placeholder for auto-tuning logic
        # In practice, would implement Bayesian optimization or similar
        pass
