#!/usr/bin/env python3
"""
AutoML hyperparameter optimization for Sundew algorithm.

This module provides automated hyperparameter tuning using:
- Bayesian optimization for efficient search
- Multi-objective optimization (energy vs accuracy)
- Population-based methods (genetic algorithms)
- Neural architecture search for significance models
- Automated configuration selection and validation
"""

import json
import random
import time
import warnings
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import numpy as np

# Optional dependencies for advanced optimization
try:
    from sklearn.gaussian_process import GaussianProcessRegressor
    from sklearn.gaussian_process.kernels import RBF, ConstantKernel, Matern
    from sklearn.model_selection import cross_val_score
    SKLEARN_AVAILABLE = True
except ImportError:
    # Fallback classes for type hints when sklearn not available
    class GaussianProcessRegressor:
        pass
    class Matern:
        pass
    class RBF:
        pass
    class ConstantKernel:
        pass
    SKLEARN_AVAILABLE = False

try:
    import optuna
    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False


@dataclass
class OptimizationObjective:
    """Define optimization objectives with weights and constraints."""
    name: str
    weight: float = 1.0
    minimize: bool = True
    constraint_min: Optional[float] = None
    constraint_max: Optional[float] = None

    def evaluate_constraint(self, value: float) -> bool:
        """Check if value satisfies constraints."""
        if self.constraint_min is not None and value < self.constraint_min:
            return False
        if self.constraint_max is not None and value > self.constraint_max:
            return False
        return True


@dataclass
class HyperparameterSpace:
    """Define hyperparameter search space."""
    name: str
    param_type: str  # 'float', 'int', 'categorical', 'boolean'
    low: Optional[Union[float, int]] = None
    high: Optional[Union[float, int]] = None
    choices: Optional[List[Any]] = None
    log_scale: bool = False

    def sample(self, random_state: Optional[int] = None) -> Any:
        """Sample a value from this hyperparameter space."""
        if random_state is not None:
            np.random.seed(random_state)

        if self.param_type == 'float':
            if self.log_scale:
                return np.random.lognormal(np.log(self.low),
                                         np.log(self.high / self.low))
            return np.random.uniform(self.low, self.high)

        elif self.param_type == 'int':
            return np.random.randint(self.low, self.high + 1)

        elif self.param_type == 'categorical':
            return np.random.choice(self.choices)

        elif self.param_type == 'boolean':
            return np.random.choice([True, False])

        else:
            raise ValueError(f"Unknown parameter type: {self.param_type}")


@dataclass
class OptimizationResult:
    """Result from hyperparameter optimization."""
    best_params: Dict[str, Any]
    best_score: float
    all_trials: List[Dict[str, Any]]
    optimization_time: float
    convergence_history: List[float]
    method_used: str
    validation_metrics: Dict[str, float]

    def save(self, filepath: str):
        """Save optimization result to file."""
        with open(filepath, 'w') as f:
            json.dump(asdict(self), f, indent=2, default=str)

    @classmethod
    def load(cls, filepath: str):
        """Load optimization result from file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls(**data)


class BaseOptimizer(ABC):
    """Abstract base class for hyperparameter optimizers."""

    @abstractmethod
    def optimize(self,
                objective_func: Callable,
                param_space: List[HyperparameterSpace],
                n_trials: int = 100) -> OptimizationResult:
        """Run hyperparameter optimization."""
        pass


class BayesianOptimizer(BaseOptimizer):
    """Bayesian optimization using Gaussian Process surrogate models."""

    def __init__(self,
                 acquisition_function: str = 'expected_improvement',
                 n_initial_points: int = 10,
                 kernel: str = 'matern',
                 random_state: int = 42):

        if not SKLEARN_AVAILABLE:
            raise ImportError("Bayesian optimization requires scikit-learn")

        self.acquisition_function = acquisition_function
        self.n_initial_points = n_initial_points
        self.kernel_name = kernel
        self.random_state = random_state

        # Initialize GP kernel
        if kernel == 'matern':
            self.kernel = ConstantKernel() * Matern(nu=2.5)
        elif kernel == 'rbf':
            self.kernel = ConstantKernel() * RBF()
        else:
            raise ValueError(f"Unknown kernel: {kernel}")

    def _acquisition_function(self, X: np.ndarray, gp: GaussianProcessRegressor,
                            best_score: float) -> np.ndarray:
        """Compute acquisition function values."""
        mu, sigma = gp.predict(X, return_std=True)

        if self.acquisition_function == 'expected_improvement':
            # Expected Improvement
            improvement = best_score - mu
            z = improvement / (sigma + 1e-9)

            from scipy.stats import norm
            ei = improvement * norm.cdf(z) + sigma * norm.pdf(z)
            return ei

        elif self.acquisition_function == 'upper_confidence_bound':
            # Upper Confidence Bound
            beta = 2.0  # Exploration parameter
            return mu + beta * sigma

        else:
            raise ValueError(f"Unknown acquisition function: {self.acquisition_function}")

    def optimize(self,
                objective_func: Callable,
                param_space: List[HyperparameterSpace],
                n_trials: int = 100) -> OptimizationResult:
        """Run Bayesian optimization."""

        start_time = time.time()

        # Initialize with random points
        X_trials = []
        y_trials = []
        all_trials = []

        print(f"Bayesian optimization: {n_trials} trials")
        print("Initial random exploration...")

        # Random initialization
        for i in range(min(self.n_initial_points, n_trials)):
            params = {space.name: space.sample(self.random_state + i)
                     for space in param_space}

            score = objective_func(params)

            # Convert params to feature vector
            X_trials.append([params[space.name] if space.param_type in ['float', 'int']
                           else hash(str(params[space.name])) % 1000
                           for space in param_space])
            y_trials.append(score)

            all_trials.append({
                'trial_id': i,
                'params': params.copy(),
                'score': score,
                'method': 'random_init'
            })

            if (i + 1) % 5 == 0:
                print(f"  Trial {i+1}/{self.n_initial_points}: score = {score:.4f}")

        X_trials = np.array(X_trials)
        y_trials = np.array(y_trials)

        # Bayesian optimization loop
        gp = GaussianProcessRegressor(
            kernel=self.kernel,
            alpha=1e-6,
            normalize_y=True,
            random_state=self.random_state
        )

        convergence_history = []
        best_score = np.min(y_trials)

        print("Bayesian optimization...")

        for trial in range(self.n_initial_points, n_trials):
            # Fit GP on all trials so far
            gp.fit(X_trials, y_trials)

            # Find next point using acquisition function
            best_x = None
            best_acq = -np.inf

            # Sample candidate points
            n_candidates = 1000
            for _ in range(n_candidates):
                candidate_params = {space.name: space.sample() for space in param_space}
                candidate_x = np.array([[candidate_params[space.name]
                                       if space.param_type in ['float', 'int']
                                       else hash(str(candidate_params[space.name])) % 1000
                                       for space in param_space]])

                acq_value = self._acquisition_function(candidate_x, gp, best_score)[0]

                if acq_value > best_acq:
                    best_acq = acq_value
                    best_x = candidate_x[0]
                    best_params = candidate_params

            # Evaluate objective at best point
            score = objective_func(best_params)

            # Update data
            X_trials = np.vstack([X_trials, best_x])
            y_trials = np.append(y_trials, score)

            if score < best_score:
                best_score = score

            convergence_history.append(best_score)

            all_trials.append({
                'trial_id': trial,
                'params': best_params.copy(),
                'score': score,
                'method': 'bayesian',
                'acquisition_value': best_acq
            })

            if trial % 10 == 0:
                print(f"  Trial {trial+1}/{n_trials}: score = {score:.4f}, best = {best_score:.4f}")

        # Find best parameters
        best_idx = np.argmin(y_trials)
        best_params = all_trials[best_idx]['params']

        optimization_time = time.time() - start_time

        return OptimizationResult(
            best_params=best_params,
            best_score=best_score,
            all_trials=all_trials,
            optimization_time=optimization_time,
            convergence_history=convergence_history,
            method_used='bayesian_optimization',
            validation_metrics={'final_gp_score': gp.score(X_trials, y_trials)}
        )


class OptunaOptimizer(BaseOptimizer):
    """Optuna-based optimization with advanced pruning and multi-objective support."""

    def __init__(self,
                 sampler: str = 'tpe',
                 pruner: str = 'median',
                 n_startup_trials: int = 10):

        if not OPTUNA_AVAILABLE:
            raise ImportError("OptunaOptimizer requires optuna to be installed")

        self.sampler_name = sampler
        self.pruner_name = pruner
        self.n_startup_trials = n_startup_trials

    def _create_sampler(self):
        """Create Optuna sampler."""
        if self.sampler_name == 'tpe':
            return optuna.samplers.TPESampler(n_startup_trials=self.n_startup_trials)
        elif self.sampler_name == 'random':
            return optuna.samplers.RandomSampler()
        elif self.sampler_name == 'cmaes':
            return optuna.samplers.CmaEsSampler(n_startup_trials=self.n_startup_trials)
        else:
            raise ValueError(f"Unknown sampler: {self.sampler_name}")

    def _create_pruner(self):
        """Create Optuna pruner."""
        if self.pruner_name == 'median':
            return optuna.pruners.MedianPruner()
        elif self.pruner_name == 'hyperband':
            return optuna.pruners.HyperbandPruner()
        elif self.pruner_name == 'none':
            return optuna.pruners.NopPruner()
        else:
            raise ValueError(f"Unknown pruner: {self.pruner_name}")

    def optimize(self,
                objective_func: Callable,
                param_space: List[HyperparameterSpace],
                n_trials: int = 100) -> OptimizationResult:
        """Run Optuna optimization."""

        start_time = time.time()

        # Create study
        study = optuna.create_study(
            direction='minimize',
            sampler=self._create_sampler(),
            pruner=self._create_pruner()
        )

        # Define Optuna objective
        def optuna_objective(trial):
            params = {}

            for space in param_space:
                if space.param_type == 'float':
                    if space.log_scale:
                        params[space.name] = trial.suggest_loguniform(
                            space.name, space.low, space.high
                        )
                    else:
                        params[space.name] = trial.suggest_uniform(
                            space.name, space.low, space.high
                        )
                elif space.param_type == 'int':
                    params[space.name] = trial.suggest_int(
                        space.name, space.low, space.high
                    )
                elif space.param_type == 'categorical':
                    params[space.name] = trial.suggest_categorical(
                        space.name, space.choices
                    )
                elif space.param_type == 'boolean':
                    params[space.name] = trial.suggest_categorical(
                        space.name, [True, False]
                    )

            return objective_func(params)

        # Optimize
        print(f"Optuna optimization: {n_trials} trials")
        study.optimize(optuna_objective, n_trials=n_trials, show_progress_bar=True)

        # Extract results
        all_trials = []
        convergence_history = []
        best_score_so_far = float('inf')

        for i, trial in enumerate(study.trials):
            score = trial.value if trial.value is not None else float('inf')

            if score < best_score_so_far:
                best_score_so_far = score
            convergence_history.append(best_score_so_far)

            all_trials.append({
                'trial_id': i,
                'params': trial.params,
                'score': score,
                'method': 'optuna',
                'state': trial.state.name
            })

        optimization_time = time.time() - start_time

        return OptimizationResult(
            best_params=study.best_params,
            best_score=study.best_value,
            all_trials=all_trials,
            optimization_time=optimization_time,
            convergence_history=convergence_history,
            method_used=f'optuna_{self.sampler_name}',
            validation_metrics={
                'n_complete_trials': len([t for t in study.trials if t.state == optuna.trial.TrialState.COMPLETE]),
                'n_pruned_trials': len([t for t in study.trials if t.state == optuna.trial.TrialState.PRUNED])
            }
        )


class GeneticAlgorithmOptimizer(BaseOptimizer):
    """Genetic algorithm for hyperparameter optimization."""

    def __init__(self,
                 population_size: int = 50,
                 mutation_rate: float = 0.1,
                 crossover_rate: float = 0.8,
                 tournament_size: int = 3,
                 elitism_ratio: float = 0.1):

        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.tournament_size = tournament_size
        self.elitism_ratio = elitism_ratio

    def _create_individual(self, param_space: List[HyperparameterSpace]) -> Dict[str, Any]:
        """Create random individual."""
        return {space.name: space.sample() for space in param_space}

    def _mutate(self, individual: Dict[str, Any],
               param_space: List[HyperparameterSpace]) -> Dict[str, Any]:
        """Mutate an individual."""
        mutated = individual.copy()

        for space in param_space:
            if np.random.random() < self.mutation_rate:
                mutated[space.name] = space.sample()

        return mutated

    def _crossover(self, parent1: Dict[str, Any], parent2: Dict[str, Any]) -> Dict[str, Any]:
        """Create offspring through crossover."""
        offspring = {}

        for key in parent1:
            if np.random.random() < 0.5:
                offspring[key] = parent1[key]
            else:
                offspring[key] = parent2[key]

        return offspring

    def _tournament_selection(self, population: List[Tuple[Dict, float]]) -> Dict[str, Any]:
        """Select individual using tournament selection."""
        tournament = random.sample(population, self.tournament_size)
        winner = min(tournament, key=lambda x: x[1])  # Minimize
        return winner[0]

    def optimize(self,
                objective_func: Callable,
                param_space: List[HyperparameterSpace],
                n_trials: int = 100) -> OptimizationResult:
        """Run genetic algorithm optimization."""

        start_time = time.time()
        n_generations = n_trials // self.population_size

        print(f"Genetic algorithm: {n_generations} generations, {self.population_size} individuals")

        # Initialize population
        population = []
        for i in range(self.population_size):
            individual = self._create_individual(param_space)
            fitness = objective_func(individual)
            population.append((individual, fitness))

        all_trials = []
        convergence_history = []
        best_score = min(pop[1] for pop in population)

        for gen in range(n_generations):
            # Sort population by fitness
            population.sort(key=lambda x: x[1])

            # Track best score
            current_best = population[0][1]
            if current_best < best_score:
                best_score = current_best
            convergence_history.append(best_score)

            # Record trials
            for i, (individual, fitness) in enumerate(population):
                all_trials.append({
                    'trial_id': gen * self.population_size + i,
                    'params': individual.copy(),
                    'score': fitness,
                    'method': 'genetic_algorithm',
                    'generation': gen
                })

            # Elite selection
            n_elite = int(self.elitism_ratio * self.population_size)
            new_population = population[:n_elite]

            # Generate offspring
            while len(new_population) < self.population_size:
                parent1 = self._tournament_selection(population)
                parent2 = self._tournament_selection(population)

                # Crossover
                if np.random.random() < self.crossover_rate:
                    offspring = self._crossover(parent1, parent2)
                else:
                    offspring = parent1.copy()

                # Mutation
                offspring = self._mutate(offspring, param_space)

                # Evaluate offspring
                fitness = objective_func(offspring)
                new_population.append((offspring, fitness))

            population = new_population

            if gen % 10 == 0:
                print(f"  Generation {gen+1}/{n_generations}: best = {best_score:.4f}")

        # Find best individual
        population.sort(key=lambda x: x[1])
        best_params, best_score = population[0]

        optimization_time = time.time() - start_time

        return OptimizationResult(
            best_params=best_params,
            best_score=best_score,
            all_trials=all_trials,
            optimization_time=optimization_time,
            convergence_history=convergence_history,
            method_used='genetic_algorithm',
            validation_metrics={'final_population_diversity': len(set(str(p[0]) for p in population[-10:]))}
        )


class AutoMLOptimizer:
    """
    Master AutoML optimizer with automatic method selection and multi-objective optimization.
    """

    def __init__(self,
                 objectives: List[OptimizationObjective] = None,
                 time_budget_minutes: int = 60,
                 auto_select_method: bool = True):

        self.objectives = objectives or [
            OptimizationObjective('energy_savings', weight=0.4, minimize=False),
            OptimizationObjective('f1_score', weight=0.4, minimize=False),
            OptimizationObjective('processing_time', weight=0.2, minimize=True)
        ]

        self.time_budget_minutes = time_budget_minutes
        self.auto_select_method = auto_select_method

        # Available optimizers
        self.optimizers = {}
        self._initialize_optimizers()

        # Results tracking
        self.optimization_history = []

    def _initialize_optimizers(self):
        """Initialize available optimizers."""
        # Always available
        self.optimizers['genetic'] = GeneticAlgorithmOptimizer()

        # Optional optimizers
        if SKLEARN_AVAILABLE:
            self.optimizers['bayesian'] = BayesianOptimizer()

        if OPTUNA_AVAILABLE:
            self.optimizers['optuna_tpe'] = OptunaOptimizer(sampler='tpe')
            self.optimizers['optuna_cmaes'] = OptunaOptimizer(sampler='cmaes')

    def _compute_multi_objective_score(self, metrics: Dict[str, float]) -> float:
        """Compute weighted multi-objective score."""
        total_score = 0
        total_weight = 0

        for objective in self.objectives:
            if objective.name in metrics:
                value = metrics[objective.name]

                # Check constraints
                if not objective.evaluate_constraint(value):
                    return float('inf')  # Constraint violation

                # Normalize and weight
                if objective.minimize:
                    score = value * objective.weight
                else:
                    score = (1 - value) * objective.weight if value <= 1 else -value * objective.weight

                total_score += score
                total_weight += objective.weight

        return total_score / total_weight if total_weight > 0 else float('inf')

    def create_sundew_param_space(self) -> List[HyperparameterSpace]:
        """Create comprehensive parameter space for Sundew algorithm."""
        return [
            # Threshold parameters
            HyperparameterSpace('activation_threshold', 'float', 0.1, 0.95),
            HyperparameterSpace('target_activation_rate', 'float', 0.05, 0.5),
            HyperparameterSpace('gate_temperature', 'float', 0.001, 0.5, log_scale=True),
            HyperparameterSpace('max_threshold', 'float', 0.7, 0.99),
            HyperparameterSpace('min_threshold', 'float', 0.01, 0.3),

            # Control parameters
            HyperparameterSpace('adapt_kp', 'float', 0.001, 1.0, log_scale=True),
            HyperparameterSpace('adapt_ki', 'float', 0.0001, 0.1, log_scale=True),
            HyperparameterSpace('error_deadband', 'float', 0.001, 0.1),
            HyperparameterSpace('integral_clamp', 'float', 0.1, 2.0),

            # Energy parameters
            HyperparameterSpace('energy_pressure', 'float', 0.001, 0.2),
            HyperparameterSpace('max_energy', 'float', 50, 200),
            HyperparameterSpace('dormant_tick_cost', 'float', 0.1, 2.0),
            HyperparameterSpace('eval_cost', 'float', 0.5, 5.0),
            HyperparameterSpace('base_processing_cost', 'float', 10, 100),

            # Significance weights (must sum to 1)
            HyperparameterSpace('w_magnitude', 'float', 0.1, 0.7),
            HyperparameterSpace('w_anomaly', 'float', 0.1, 0.7),
            HyperparameterSpace('w_context', 'float', 0.05, 0.5),
            HyperparameterSpace('w_urgency', 'float', 0.05, 0.5),

            # Algorithm parameters
            HyperparameterSpace('ema_alpha', 'float', 0.01, 0.5),
            HyperparameterSpace('refractory', 'int', 0, 10),
            HyperparameterSpace('probe_every', 'int', 1, 20),
        ]

    def create_enhanced_param_space(self) -> List[HyperparameterSpace]:
        """Create parameter space for enhanced Sundew system."""
        base_space = self.create_sundew_param_space()

        enhanced_params = [
            # Model selection
            HyperparameterSpace('significance_model', 'categorical',
                              choices=['linear', 'neural']),
            HyperparameterSpace('gating_strategy', 'categorical',
                              choices=['temperature', 'adaptive']),
            HyperparameterSpace('control_policy', 'categorical',
                              choices=['pi', 'mpc']),
            HyperparameterSpace('energy_model', 'categorical',
                              choices=['simple', 'realistic']),

            # Neural model parameters
            HyperparameterSpace('hidden_size', 'int', 16, 128),
            HyperparameterSpace('learning_rate', 'float', 1e-4, 1e-2, log_scale=True),
            HyperparameterSpace('attention_heads', 'int', 1, 8),
            HyperparameterSpace('history_window', 'int', 5, 50),

            # MPC parameters
            HyperparameterSpace('prediction_horizon', 'int', 3, 20),
            HyperparameterSpace('control_horizon', 'int', 1, 10),
            HyperparameterSpace('mpc_weight_rate', 'float', 0.1, 2.0),
            HyperparameterSpace('mpc_weight_energy', 'float', 0.1, 2.0),
            HyperparameterSpace('mpc_weight_stability', 'float', 0.01, 1.0),
        ]

        return base_space + enhanced_params

    def optimize_sundew_config(self,
                             evaluation_func: Callable,
                             enhanced_system: bool = True,
                             method: str = 'auto',
                             n_trials: int = None) -> OptimizationResult:
        """Optimize Sundew algorithm configuration."""

        # Determine trials based on time budget
        if n_trials is None:
            n_trials = min(200, max(50, self.time_budget_minutes * 2))

        # Select parameter space
        if enhanced_system:
            param_space = self.create_enhanced_param_space()
        else:
            param_space = self.create_sundew_param_space()

        # Auto-select method
        if method == 'auto':
            if OPTUNA_AVAILABLE and n_trials > 100:
                method = 'optuna_tpe'
            elif SKLEARN_AVAILABLE and n_trials > 50:
                method = 'bayesian'
            else:
                method = 'genetic'

        print(f"AutoML optimization using {method}")
        print(f"Search space: {len(param_space)} parameters")
        print(f"Objectives: {[obj.name for obj in self.objectives]}")

        # Create multi-objective wrapper
        def multi_objective_func(params):
            # Normalize significance weights to sum to 1
            if all(f'w_{key}' in params for key in ['magnitude', 'anomaly', 'context', 'urgency']):
                weight_sum = sum(params[f'w_{key}'] for key in ['magnitude', 'anomaly', 'context', 'urgency'])
                if weight_sum > 0:
                    for key in ['magnitude', 'anomaly', 'context', 'urgency']:
                        params[f'w_{key}'] /= weight_sum

            # Evaluate with user function
            try:
                metrics = evaluation_func(params)
                return self._compute_multi_objective_score(metrics)
            except Exception as e:
                warnings.warn(f"Evaluation failed: {e}")
                return float('inf')

        # Run optimization
        optimizer = self.optimizers[method]
        result = optimizer.optimize(multi_objective_func, param_space, n_trials)

        # Store in history
        self.optimization_history.append({
            'timestamp': time.time(),
            'method': method,
            'enhanced_system': enhanced_system,
            'n_trials': n_trials,
            'result': result
        })

        return result

    def get_optimization_report(self) -> Dict[str, Any]:
        """Get comprehensive optimization report."""
        if not self.optimization_history:
            return {'status': 'no_optimizations'}

        latest = self.optimization_history[-1]

        return {
            'latest_optimization': {
                'method': latest['method'],
                'enhanced_system': latest['enhanced_system'],
                'best_score': latest['result'].best_score,
                'best_params': latest['result'].best_params,
                'optimization_time': latest['result'].optimization_time,
                'convergence_achieved': len(latest['result'].convergence_history) > 10 and
                                     np.std(latest['result'].convergence_history[-10:]) < 0.001
            },
            'objectives': [asdict(obj) for obj in self.objectives],
            'available_methods': list(self.optimizers.keys()),
            'optimization_history': [
                {
                    'method': h['method'],
                    'best_score': h['result'].best_score,
                    'time': h['result'].optimization_time
                } for h in self.optimization_history
            ]
        }


# Utility functions for AutoML integration

def create_evaluation_function(sundew_algorithm_class, test_data: List[Dict]) -> Callable:
    """Create evaluation function for hyperparameter optimization."""

    def evaluate_config(params: Dict[str, Any]) -> Dict[str, float]:
        """Evaluate algorithm configuration on test data."""
        try:
            # Create algorithm with parameters
            if 'significance_model' in params:
                # Enhanced system
                from sundew.enhanced_core import EnhancedSundewAlgorithm, EnhancedSundewConfig
                config = EnhancedSundewConfig(**{k: v for k, v in params.items()
                                               if hasattr(EnhancedSundewConfig, k)})
                algorithm = EnhancedSundewAlgorithm(config)
            else:
                # Original system
                from sundew.config import SundewConfig
                config = SundewConfig(**{k: v for k, v in params.items()
                                       if hasattr(SundewConfig, k)})
                algorithm = sundew_algorithm_class(config)

            # Process test data
            start_time = time.time()
            activations = []
            significance_scores = []

            for sample in test_data:
                result = algorithm.process(sample)
                if result:
                    activations.append(1)
                    significance_scores.append(result.significance)
                else:
                    activations.append(0)
                    significance_scores.append(0)

            processing_time = time.time() - start_time

            # Compute metrics
            activation_rate = np.mean(activations)
            avg_significance = np.mean(significance_scores)

            # Get energy metrics
            if hasattr(algorithm, 'get_comprehensive_report'):
                report = algorithm.get_comprehensive_report()
                energy_savings = report.get('energy_efficiency', 0) * 100
            else:
                final_report = algorithm.report()
                energy_savings = final_report.get('estimated_energy_savings_pct', 0)

            # Simulate F1 score (in real usage, compare with ground truth)
            f1_score = min(1.0, avg_significance * 2)  # Simplified metric

            return {
                'energy_savings': energy_savings / 100,  # Normalized
                'f1_score': f1_score,
                'processing_time': processing_time,
                'activation_rate': activation_rate,
                'avg_significance': avg_significance
            }

        except Exception:
            # Return poor metrics for failed configurations
            return {
                'energy_savings': 0.0,
                'f1_score': 0.0,
                'processing_time': 999.0,
                'activation_rate': 0.0,
                'avg_significance': 0.0
            }

    return evaluate_config


if __name__ == "__main__":
    # Example usage and testing
    print("AutoML Hyperparameter Optimization for Sundew")
    print("=" * 50)

    # Mock evaluation function
    def mock_evaluation(params):
        """Mock evaluation function for testing."""
        # Simulate realistic metrics based on parameters
        threshold = params.get('activation_threshold', 0.5)
        energy_pressure = params.get('energy_pressure', 0.05)

        # Simple heuristics for demonstration
        energy_savings = 0.8 + energy_pressure * 2  # Higher pressure = more savings
        f1_score = 0.7 - abs(threshold - 0.6)  # Optimal around 0.6
        processing_time = 1.0 + np.random.normal(0, 0.1)  # Add noise

        return {
            'energy_savings': min(1.0, energy_savings),
            'f1_score': max(0.0, min(1.0, f1_score)),
            'processing_time': max(0.1, processing_time)
        }

    # Initialize AutoML optimizer
    objectives = [
        OptimizationObjective('energy_savings', weight=0.4, minimize=False,
                            constraint_min=0.8),  # Must save at least 80% energy
        OptimizationObjective('f1_score', weight=0.4, minimize=False,
                            constraint_min=0.6),  # Must achieve at least 0.6 F1
        OptimizationObjective('processing_time', weight=0.2, minimize=True,
                            constraint_max=2.0)  # Must process within 2 seconds
    ]

    automl = AutoMLOptimizer(
        objectives=objectives,
        time_budget_minutes=5  # Short for demo
    )

    print(f"Available optimizers: {list(automl.optimizers.keys())}")

    # Run optimization
    result = automl.optimize_sundew_config(
        evaluation_func=mock_evaluation,
        enhanced_system=False,
        method='auto',
        n_trials=30  # Small for demo
    )

    print("\nOptimization completed!")
    print(f"Best score: {result.best_score:.4f}")
    print("Best parameters:")
    for key, value in result.best_params.items():
        print(f"  {key}: {value}")

    print(f"\nOptimization time: {result.optimization_time:.2f} seconds")
    print(f"Method used: {result.method_used}")

    # Get report
    report = automl.get_optimization_report()
    print(f"Convergence achieved: {report['latest_optimization']['convergence_achieved']}")

    print("\nAutoML optimization system ready for integration!")
