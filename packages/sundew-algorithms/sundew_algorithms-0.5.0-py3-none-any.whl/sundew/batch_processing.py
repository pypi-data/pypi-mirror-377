#!/usr/bin/env python3
# type: ignore
"""
High-performance vectorized batch processing engine for Sundew algorithm.

This module provides optimized batch processing capabilities with:
- Vectorized operations using NumPy and optional GPU acceleration
- Parallel processing for multi-core systems
- Memory-efficient streaming for large datasets
- Performance profiling and optimization
"""

import multiprocessing as mp
import queue
import threading
import time
import warnings
from abc import ABC, abstractmethod
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple, Union

import numpy as np

try:
    import cupy as cp
    GPU_AVAILABLE = True
except ImportError:
    import numpy as cp  # Use numpy as fallback for type hints
    GPU_AVAILABLE = False

try:
    from numba import cuda, jit
    NUMBA_AVAILABLE = True
except ImportError:
    def jit(x):  # No-op decorator
        return x
    cuda = None
    NUMBA_AVAILABLE = False


@dataclass
class BatchProcessingConfig:
    """Configuration for batch processing engine."""
    batch_size: int = 1000
    max_workers: int = None  # Auto-detect
    use_gpu: bool = False
    use_numba: bool = True
    memory_limit_mb: int = 1024
    prefetch_batches: int = 2
    enable_profiling: bool = True
    chunk_size: int = 10000  # For large dataset streaming


@dataclass
class BatchResult:
    """Result from batch processing."""
    processed_samples: int
    activations: np.ndarray
    significance_scores: np.ndarray
    energy_consumed: np.ndarray
    processing_times: np.ndarray
    metadata: Dict[str, Any]

    @property
    def activation_rate(self) -> float:
        return np.mean(self.activations) if len(self.activations) > 0 else 0.0

    @property
    def total_energy(self) -> float:
        return np.sum(self.energy_consumed) if len(self.energy_consumed) > 0 else 0.0

    @property
    def avg_processing_time(self) -> float:
        return np.mean(self.processing_times) if len(self.processing_times) > 0 else 0.0


class BatchProcessor(ABC):
    """Abstract base class for batch processors."""

    @abstractmethod
    def process_batch(self, samples: np.ndarray) -> BatchResult:
        """Process a batch of samples."""
        pass


class VectorizedProcessor(BatchProcessor):
    """High-performance vectorized processor using NumPy operations."""

    def __init__(self,
                 algorithm,
                 config: BatchProcessingConfig = None):
        self.algorithm = algorithm
        self.config = config or BatchProcessingConfig()
        self.performance_stats = {
            'batches_processed': 0,
            'total_samples': 0,
            'total_time': 0.0,
            'memory_usage': []
        }

    @jit if NUMBA_AVAILABLE else lambda x: x
    def _vectorized_significance(self, features: np.ndarray) -> np.ndarray:
        """Vectorized significance computation."""
        # Extract feature columns
        magnitude = features[:, 0]
        anomaly = features[:, 1]
        context = features[:, 2]
        urgency = features[:, 3]

        # Vectorized weighted combination
        weights = np.array([0.3, 0.3, 0.2, 0.2])  # Default weights
        significance = (magnitude * weights[0] +
                       anomaly * weights[1] +
                       context * weights[2] +
                       urgency * weights[3])

        return np.clip(significance / 100.0, 0.0, 1.0)  # Normalize

    @jit if NUMBA_AVAILABLE else lambda x: x
    def _vectorized_gating(self, significance: np.ndarray, threshold: float) -> np.ndarray:
        """Vectorized gating decisions."""
        return (significance >= threshold).astype(np.float32)

    @jit if NUMBA_AVAILABLE else lambda x: x
    def _vectorized_energy(self, activations: np.ndarray) -> np.ndarray:
        """Vectorized energy consumption calculation."""
        base_cost = 0.5  # Dormant cost
        active_cost = 50.0  # Full processing cost

        return base_cost + activations * (active_cost - base_cost)

    def process_batch(self, samples: np.ndarray) -> BatchResult:
        """Process batch using vectorized operations."""
        start_time = time.time()

        # Convert samples to feature matrix
        if isinstance(samples, list):
            # Convert list of dicts to numpy array
            features = np.array([[
                s.get('magnitude', 0),
                s.get('anomaly_score', 0),
                s.get('context_relevance', 0),
                s.get('urgency', 0)
            ] for s in samples])
        else:
            features = samples

        batch_size = len(features)

        # Vectorized computation pipeline
        significance_scores = self._vectorized_significance(features)

        # Get current threshold from algorithm
        current_threshold = getattr(self.algorithm, 'threshold', 0.5)

        # Vectorized gating
        activations = self._vectorized_gating(significance_scores, current_threshold)

        # Vectorized energy calculation
        energy_consumed = self._vectorized_energy(activations)

        # Processing times (simulated for vectorized operations)
        processing_times = np.full(batch_size, time.time() - start_time)

        # Update performance stats
        processing_time = time.time() - start_time
        self.performance_stats['batches_processed'] += 1
        self.performance_stats['total_samples'] += batch_size
        self.performance_stats['total_time'] += processing_time

        return BatchResult(
            processed_samples=batch_size,
            activations=activations,
            significance_scores=significance_scores,
            energy_consumed=energy_consumed,
            processing_times=processing_times,
            metadata={
                'processing_time': processing_time,
                'throughput': batch_size / processing_time,
                'threshold_used': current_threshold,
                'vectorized': True
            }
        )


class GPUProcessor(BatchProcessor):
    """GPU-accelerated batch processor using CuPy."""

    def __init__(self, algorithm, config: BatchProcessingConfig = None):
        if not GPU_AVAILABLE:
            raise RuntimeError("GPU processing requires CuPy to be installed")

        self.algorithm = algorithm
        self.config = config or BatchProcessingConfig()
        if GPU_AVAILABLE:
            self.device = cp.cuda.Device(0)  # Use first GPU
        else:
            self.device = None

    def _gpu_significance(self, features_gpu: cp.ndarray) -> cp.ndarray:
        """GPU-accelerated significance computation."""
        weights = cp.array([0.3, 0.3, 0.2, 0.2])
        significance = cp.sum(features_gpu * weights, axis=1)
        return cp.clip(significance / 100.0, 0.0, 1.0)

    def _gpu_gating(self, significance_gpu: cp.ndarray, threshold: float) -> cp.ndarray:
        """GPU-accelerated gating decisions."""
        return (significance_gpu >= threshold).astype(cp.float32)

    def process_batch(self, samples: np.ndarray) -> BatchResult:
        """Process batch on GPU."""
        start_time = time.time()

        if self.device:
            with self.device:
                # Transfer data to GPU
                if isinstance(samples, list):
                    features = np.array([[
                        s.get('magnitude', 0),
                        s.get('anomaly_score', 0),
                        s.get('context_relevance', 0),
                        s.get('urgency', 0)
                    ] for s in samples])
                else:
                    features = samples

                features_gpu = cp.asarray(features)

                # GPU computations
                significance_gpu = self._gpu_significance(features_gpu)
                current_threshold = getattr(self.algorithm, 'threshold', 0.5)
                activations_gpu = self._gpu_gating(significance_gpu, current_threshold)

                # Energy calculation on GPU
                base_cost = 0.5
                active_cost = 50.0
                energy_gpu = base_cost + activations_gpu * (active_cost - base_cost)

                # Transfer results back to CPU
                significance_scores = cp.asnumpy(significance_gpu)
                activations = cp.asnumpy(activations_gpu)
                energy_consumed = cp.asnumpy(energy_gpu)
        else:
            # Fallback to CPU processing
            raise RuntimeError("GPU device not available")

        processing_time = time.time() - start_time
        batch_size = len(samples)
        processing_times = np.full(batch_size, processing_time)

        return BatchResult(
            processed_samples=batch_size,
            activations=activations,
            significance_scores=significance_scores,
            energy_consumed=energy_consumed,
            processing_times=processing_times,
            metadata={
                'processing_time': processing_time,
                'throughput': batch_size / processing_time,
                'threshold_used': current_threshold,
                'gpu_accelerated': True
            }
        )


class ParallelProcessor(BatchProcessor):
    """Multi-core parallel batch processor."""

    def __init__(self,
                 algorithm,
                 config: BatchProcessingConfig = None,
                 use_processes: bool = True):
        self.algorithm = algorithm
        self.config = config or BatchProcessingConfig()
        self.use_processes = use_processes

        if self.config.max_workers is None:
            self.config.max_workers = mp.cpu_count()

    def _process_chunk(self, chunk: List[Dict]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Process a chunk of samples in a worker."""
        activations = []
        significance_scores = []
        energy_consumed = []

        for sample in chunk:
            # Use direct processing to avoid recursion
            if hasattr(self.algorithm, '_process_single_direct'):
                result = self.algorithm._process_single_direct(sample)
            else:
                result = self.algorithm.process(sample)

            if result:
                activations.append(1.0)
                significance_scores.append(result.significance)
                energy_consumed.append(result.energy_consumed)
            else:
                activations.append(0.0)
                significance_scores.append(0.0)  # Unknown for gated samples
                energy_consumed.append(0.5)  # Dormant cost

        return (np.array(activations),
                np.array(significance_scores),
                np.array(energy_consumed))

    def process_batch(self, samples: List[Dict]) -> BatchResult:
        """Process batch using parallel workers."""
        start_time = time.time()

        # Split samples into chunks for workers
        chunk_size = max(1, len(samples) // self.config.max_workers)
        chunks = [samples[i:i + chunk_size]
                 for i in range(0, len(samples), chunk_size)]

        # Process chunks in parallel
        if self.use_processes:
            with ProcessPoolExecutor(max_workers=self.config.max_workers) as executor:
                results = list(executor.map(self._process_chunk, chunks))
        else:
            with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
                results = list(executor.map(self._process_chunk, chunks))

        # Combine results
        all_activations = np.concatenate([r[0] for r in results])
        all_significance = np.concatenate([r[1] for r in results])
        all_energy = np.concatenate([r[2] for r in results])

        processing_time = time.time() - start_time
        processing_times = np.full(len(samples), processing_time)

        return BatchResult(
            processed_samples=len(samples),
            activations=all_activations,
            significance_scores=all_significance,
            energy_consumed=all_energy,
            processing_times=processing_times,
            metadata={
                'processing_time': processing_time,
                'throughput': len(samples) / processing_time,
                'parallel_workers': self.config.max_workers,
                'chunks_processed': len(chunks)
            }
        )


class StreamingProcessor:
    """Memory-efficient streaming processor for large datasets."""

    def __init__(self,
                 processor: BatchProcessor,
                 config: BatchProcessingConfig = None):
        self.processor = processor
        self.config = config or BatchProcessingConfig()
        self.results_queue = queue.Queue(maxsize=self.config.prefetch_batches)
        self.processing_thread = None
        self.stop_signal = threading.Event()

    def _background_processor(self, data_stream: Iterator):
        """Background processing thread."""
        try:
            batch = []
            for sample in data_stream:
                batch.append(sample)

                if len(batch) >= self.config.batch_size:
                    # Process batch
                    result = self.processor.process_batch(batch)
                    self.results_queue.put(result)
                    batch = []

                    if self.stop_signal.is_set():
                        break

            # Process remaining samples
            if batch:
                result = self.processor.process_batch(batch)
                self.results_queue.put(result)

        except Exception as e:
            self.results_queue.put(('ERROR', e))
        finally:
            self.results_queue.put('DONE')

    def process_stream(self, data_stream: Iterator) -> Iterator[BatchResult]:
        """Process data stream with background batching."""
        # Start background processing
        self.processing_thread = threading.Thread(
            target=self._background_processor,
            args=(data_stream,)
        )
        self.processing_thread.start()

        # Yield results as they become available
        while True:
            try:
                result = self.results_queue.get(timeout=10.0)

                if result == 'DONE':
                    break
                elif isinstance(result, tuple) and result[0] == 'ERROR':
                    raise result[1]
                else:
                    yield result

            except queue.Empty:
                warnings.warn("Processing timeout - stream may be slow")
                break

        # Clean up
        self.stop_signal.set()
        if self.processing_thread.is_alive():
            self.processing_thread.join(timeout=5.0)


class BatchProcessingEngine:
    """
    Master batch processing engine with automatic optimization.

    Automatically selects the best processing strategy based on:
    - Hardware capabilities (CPU cores, GPU availability)
    - Dataset characteristics (size, complexity)
    - Performance requirements (latency vs throughput)
    """

    def __init__(self,
                 algorithm,
                 config: BatchProcessingConfig = None,
                 auto_optimize: bool = True):
        self.algorithm = algorithm
        self.config = config or BatchProcessingConfig()
        self.auto_optimize = auto_optimize

        # Available processors
        self.processors = {}
        self._initialize_processors()

        # Performance tracking
        self.benchmark_results = {}
        self.optimal_processor = None

    def _initialize_processors(self):
        """Initialize available processors based on capabilities."""
        # Always available: vectorized
        self.processors['vectorized'] = VectorizedProcessor(
            self.algorithm, self.config
        )

        # GPU if available
        if GPU_AVAILABLE and self.config.use_gpu:
            try:
                self.processors['gpu'] = GPUProcessor(self.algorithm, self.config)
            except Exception as e:
                warnings.warn(f"GPU processor initialization failed: {e}")

        # Parallel processing
        if self.config.max_workers != 1:
            self.processors['parallel'] = ParallelProcessor(
                self.algorithm, self.config
            )

    def benchmark_processors(self, test_samples: List[Dict],
                           iterations: int = 3) -> Dict[str, Dict[str, float]]:
        """Benchmark all available processors."""
        print("Benchmarking processors...")

        for processor_name, processor in self.processors.items():
            print(f"  Testing {processor_name}...")

            times = []
            throughputs = []

            for i in range(iterations):
                start_time = time.time()
                processor.process_batch(test_samples)
                processing_time = time.time() - start_time

                times.append(processing_time)
                throughputs.append(len(test_samples) / processing_time)

            self.benchmark_results[processor_name] = {
                'avg_time': np.mean(times),
                'std_time': np.std(times),
                'avg_throughput': np.mean(throughputs),
                'std_throughput': np.std(throughputs)
            }

            print(f"    Throughput: {np.mean(throughputs):.0f} ± {np.std(throughputs):.0f} samples/sec")

        # Select optimal processor
        if self.auto_optimize:
            best_processor = max(self.benchmark_results.keys(),
                               key=lambda x: self.benchmark_results[x]['avg_throughput'])
            self.optimal_processor = best_processor
            print(f"  Selected optimal processor: {best_processor}")

        return self.benchmark_results

    def process_batch(self, samples: List[Dict],
                     processor_type: Optional[str] = None) -> BatchResult:
        """Process batch using specified or optimal processor."""
        if processor_type is None:
            processor_type = self.optimal_processor or 'vectorized'

        if processor_type not in self.processors:
            raise ValueError(f"Processor {processor_type} not available")

        return self.processors[processor_type].process_batch(samples)

    def process_large_dataset(self,
                            data_source: Union[List[Dict], Iterator],
                            processor_type: Optional[str] = None) -> Iterator[BatchResult]:
        """Process large dataset with streaming and optimal batching."""
        processor_type = processor_type or self.optimal_processor or 'vectorized'
        processor = self.processors[processor_type]

        # Use streaming processor for large datasets
        streaming_processor = StreamingProcessor(processor, self.config)

        if isinstance(data_source, list):
            data_source = iter(data_source)

        yield from streaming_processor.process_stream(data_source)

    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report."""
        report = {
            'config': {
                'batch_size': self.config.batch_size,
                'max_workers': self.config.max_workers,
                'use_gpu': self.config.use_gpu,
                'use_numba': self.config.use_numba
            },
            'available_processors': list(self.processors.keys()),
            'optimal_processor': self.optimal_processor,
            'benchmark_results': self.benchmark_results,
            'hardware_info': {
                'cpu_count': mp.cpu_count(),
                'gpu_available': GPU_AVAILABLE,
                'numba_available': NUMBA_AVAILABLE
            }
        }

        # Add processor-specific stats
        for name, processor in self.processors.items():
            if hasattr(processor, 'performance_stats'):
                report[f'{name}_stats'] = processor.performance_stats

        return report


# Utility functions for batch processing optimization

def estimate_optimal_batch_size(sample_processor: Callable,
                               test_samples: List[Dict],
                               max_batch_size: int = 10000) -> int:
    """Estimate optimal batch size for given processor."""
    batch_sizes = [10, 50, 100, 500, 1000, 2000, 5000]
    if max_batch_size > 5000:
        batch_sizes.extend([10000, 20000])

    best_throughput = 0
    best_batch_size = 100

    for batch_size in batch_sizes:
        if batch_size > len(test_samples):
            break

        test_batch = test_samples[:batch_size]

        start_time = time.time()
        sample_processor(test_batch)
        processing_time = time.time() - start_time

        throughput = batch_size / processing_time

        if throughput > best_throughput:
            best_throughput = throughput
            best_batch_size = batch_size

    return best_batch_size


def memory_usage_monitor():
    """Monitor memory usage during batch processing."""
    import psutil
    process = psutil.Process()

    def get_memory_mb():
        return process.memory_info().rss / 1024 / 1024

    return get_memory_mb


if __name__ == "__main__":
    # Example usage and testing
    print("High-Performance Batch Processing Engine")
    print("=" * 50)

    # Mock algorithm for testing
    class MockAlgorithm:
        def __init__(self):
            self.threshold = 0.6

        def process(self, sample):
            # Simple mock processing
            significance = (sample.get('magnitude', 0) * 0.3 +
                          sample.get('anomaly_score', 0) * 0.7)

            if significance >= self.threshold * 100:
                from types import SimpleNamespace
                return SimpleNamespace(
                    significance=significance / 100,
                    energy_consumed=50.0
                )
            return None

    # Create test data
    np.random.seed(42)
    test_samples = []
    for i in range(1000):
        test_samples.append({
            'magnitude': np.random.uniform(0, 100),
            'anomaly_score': np.random.uniform(0, 1),
            'context_relevance': np.random.uniform(0, 1),
            'urgency': np.random.uniform(0, 1)
        })

    # Initialize engine
    algorithm = MockAlgorithm()
    config = BatchProcessingConfig(
        batch_size=500,
        use_gpu=False,  # Set to True if you have CuPy installed
        use_numba=NUMBA_AVAILABLE
    )

    engine = BatchProcessingEngine(algorithm, config)

    # Benchmark processors
    benchmark_results = engine.benchmark_processors(test_samples[:100])

    # Process full batch
    print(f"\nProcessing {len(test_samples)} samples...")
    result = engine.process_batch(test_samples)

    print("Results:")
    print(f"  Activation rate: {result.activation_rate:.1%}")
    print(f"  Total energy: {result.total_energy:.1f}")
    print(f"  Throughput: {result.metadata.get('throughput', 0):.0f} samples/sec")

    # Performance report
    report = engine.get_performance_report()
    print(f"\nOptimal processor: {report['optimal_processor']}")
    print(f"Available processors: {report['available_processors']}")

    print("\nBatch processing engine ready for integration!")
