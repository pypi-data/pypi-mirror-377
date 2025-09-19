"""Performance monitoring and optimization utilities for PlotX."""

from __future__ import annotations

import psutil
import threading
import time
import logging
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple
import weakref

import numpy as np

try:
    import cupy as cp
    HAS_CUPY = True
except ImportError:
    HAS_CUPY = False

try:
    import pynvml
    pynvml.nvmlInit()
    HAS_NVML = True
except (ImportError, Exception):
    HAS_NVML = False


logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics container."""
    timestamp: float
    cpu_usage: float
    memory_usage: float
    gpu_usage: Optional[float] = None
    gpu_memory_usage: Optional[float] = None
    render_fps: Optional[float] = None
    frame_time: Optional[float] = None
    data_throughput: Optional[float] = None  # MB/s


@dataclass
class BufferStats:
    """Buffer usage statistics."""
    total_size: int
    used_size: int
    free_size: int
    allocation_count: int
    deallocation_count: int
    peak_usage: int


class PerformanceMonitor:
    """System performance monitoring for PlotX applications."""

    def __init__(self, sample_interval: float = 1.0, history_size: int = 300) -> None:
        self.sample_interval = sample_interval
        self.history_size = history_size
        self.metrics_history: deque[PerformanceMetrics] = deque(maxlen=history_size)

        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._callbacks: List[Callable[[PerformanceMetrics], None]] = []

        # GPU monitoring setup
        self._gpu_available = HAS_NVML
        self._gpu_handles: List[Any] = []

        if self._gpu_available:
            try:
                device_count = pynvml.nvmlDeviceGetCount()
                for i in range(device_count):
                    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                    self._gpu_handles.append(handle)
                logger.info(f"GPU monitoring enabled for {device_count} device(s)")
            except Exception as e:
                logger.warning(f"Failed to initialize GPU monitoring: {e}")
                self._gpu_available = False

    def start_monitoring(self) -> None:
        """Start performance monitoring."""
        if self._monitoring:
            return

        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        logger.info("Performance monitoring started")

    def stop_monitoring(self) -> None:
        """Stop performance monitoring."""
        if not self._monitoring:
            return

        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2.0)
        logger.info("Performance monitoring stopped")

    def add_callback(self, callback: Callable[[PerformanceMetrics], None]) -> None:
        """Add callback for performance metric updates."""
        self._callbacks.append(callback)

    def remove_callback(self, callback: Callable[[PerformanceMetrics], None]) -> None:
        """Remove performance metric callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self._monitoring:
            start_time = time.time()

            # Collect metrics
            metrics = self._collect_metrics()
            self.metrics_history.append(metrics)

            # Notify callbacks
            for callback in self._callbacks:
                try:
                    callback(metrics)
                except Exception as e:
                    logger.error(f"Error in performance callback: {e}")

            # Sleep for remaining interval
            elapsed = time.time() - start_time
            sleep_time = max(0, self.sample_interval - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)

    def _collect_metrics(self) -> PerformanceMetrics:
        """Collect current performance metrics."""
        timestamp = time.time()

        # CPU and memory usage
        cpu_usage = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        memory_usage = memory.percent

        # GPU metrics
        gpu_usage = None
        gpu_memory_usage = None

        if self._gpu_available and self._gpu_handles:
            try:
                # Use first GPU for now
                handle = self._gpu_handles[0]
                utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
                gpu_usage = utilization.gpu

                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpu_memory_usage = (memory_info.used / memory_info.total) * 100

            except Exception as e:
                logger.debug(f"Failed to get GPU metrics: {e}")

        return PerformanceMetrics(
            timestamp=timestamp,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            gpu_usage=gpu_usage,
            gpu_memory_usage=gpu_memory_usage
        )

    def get_current_metrics(self) -> Optional[PerformanceMetrics]:
        """Get the most recent performance metrics."""
        return self.metrics_history[-1] if self.metrics_history else None

    def get_average_metrics(self, duration: float = 60.0) -> Optional[PerformanceMetrics]:
        """Get average metrics over the specified duration (seconds)."""
        if not self.metrics_history:
            return None

        current_time = time.time()
        cutoff_time = current_time - duration

        recent_metrics = [m for m in self.metrics_history if m.timestamp >= cutoff_time]
        if not recent_metrics:
            return None

        # Calculate averages
        avg_cpu = np.mean([m.cpu_usage for m in recent_metrics])
        avg_memory = np.mean([m.memory_usage for m in recent_metrics])

        avg_gpu = None
        avg_gpu_memory = None
        if any(m.gpu_usage is not None for m in recent_metrics):
            gpu_values = [m.gpu_usage for m in recent_metrics if m.gpu_usage is not None]
            avg_gpu = np.mean(gpu_values) if gpu_values else None

        if any(m.gpu_memory_usage is not None for m in recent_metrics):
            gpu_mem_values = [m.gpu_memory_usage for m in recent_metrics if m.gpu_memory_usage is not None]
            avg_gpu_memory = np.mean(gpu_mem_values) if gpu_mem_values else None

        return PerformanceMetrics(
            timestamp=current_time,
            cpu_usage=avg_cpu,
            memory_usage=avg_memory,
            gpu_usage=avg_gpu,
            gpu_memory_usage=avg_gpu_memory
        )

    def detect_performance_issues(self) -> List[str]:
        """Detect potential performance issues."""
        issues = []

        if not self.metrics_history:
            return issues

        recent_metrics = list(self.metrics_history)[-10:]  # Last 10 samples

        # High CPU usage
        avg_cpu = np.mean([m.cpu_usage for m in recent_metrics])
        if avg_cpu > 90:
            issues.append(f"High CPU usage: {avg_cpu:.1f}%")

        # High memory usage
        avg_memory = np.mean([m.memory_usage for m in recent_metrics])
        if avg_memory > 90:
            issues.append(f"High memory usage: {avg_memory:.1f}%")

        # GPU issues
        if any(m.gpu_usage is not None for m in recent_metrics):
            gpu_values = [m.gpu_usage for m in recent_metrics if m.gpu_usage is not None]
            if gpu_values:
                avg_gpu = np.mean(gpu_values)
                if avg_gpu > 95:
                    issues.append(f"High GPU usage: {avg_gpu:.1f}%")

        if any(m.gpu_memory_usage is not None for m in recent_metrics):
            gpu_mem_values = [m.gpu_memory_usage for m in recent_metrics if m.gpu_memory_usage is not None]
            if gpu_mem_values:
                avg_gpu_mem = np.mean(gpu_mem_values)
                if avg_gpu_mem > 95:
                    issues.append(f"High GPU memory usage: {avg_gpu_mem:.1f}%")

        # Frame rate issues
        fps_values = [m.render_fps for m in recent_metrics if m.render_fps is not None]
        if fps_values:
            avg_fps = np.mean(fps_values)
            if avg_fps < 30:
                issues.append(f"Low rendering FPS: {avg_fps:.1f}")

        return issues


class BufferManager:
    """Memory buffer management with GPU acceleration support."""

    def __init__(self, max_cpu_memory: int = 1024 * 1024 * 1024,  # 1GB
                 max_gpu_memory: Optional[int] = None,
                 enable_compression: bool = False) -> None:
        self.max_cpu_memory = max_cpu_memory
        self.max_gpu_memory = max_gpu_memory
        self.enable_compression = enable_compression

        # Buffer storage
        self._cpu_buffers: Dict[str, np.ndarray] = {}
        self._gpu_buffers: Dict[str, Any] = {}  # CuPy arrays
        self._buffer_metadata: Dict[str, Dict[str, Any]] = {}

        # Usage tracking
        self._cpu_usage = 0
        self._gpu_usage = 0
        self._allocation_count = 0
        self._deallocation_count = 0
        self._peak_cpu_usage = 0
        self._peak_gpu_usage = 0

        # GPU availability
        self._gpu_enabled = HAS_CUPY

        if self._gpu_enabled and max_gpu_memory is None:
            try:
                # Auto-detect GPU memory
                mempool = cp.get_default_memory_pool()
                gpu_memory = cp.cuda.Device().mem_info[1]  # Total memory
                self.max_gpu_memory = int(gpu_memory * 0.8)  # Use 80% of available
                logger.info(f"GPU buffer manager initialized with {self.max_gpu_memory // (1024**2)} MB")
            except Exception as e:
                logger.warning(f"Failed to initialize GPU buffers: {e}")
                self._gpu_enabled = False

    def allocate_cpu_buffer(self, name: str, shape: Tuple[int, ...], dtype: np.dtype = np.float32) -> bool:
        """Allocate CPU buffer."""
        if name in self._cpu_buffers:
            logger.warning(f"Buffer {name} already exists")
            return False

        # Calculate required memory
        required_memory = np.prod(shape) * np.dtype(dtype).itemsize

        if self._cpu_usage + required_memory > self.max_cpu_memory:
            # Try to free some buffers
            if not self._free_least_used_buffers(required_memory, prefer_cpu=True):
                logger.error(f"Cannot allocate {required_memory} bytes: insufficient CPU memory")
                return False

        try:
            buffer = np.zeros(shape, dtype=dtype)
            self._cpu_buffers[name] = buffer
            self._buffer_metadata[name] = {
                "type": "cpu",
                "shape": shape,
                "dtype": dtype,
                "size": required_memory,
                "created": time.time(),
                "last_accessed": time.time(),
                "access_count": 0
            }

            self._cpu_usage += required_memory
            self._allocation_count += 1
            self._peak_cpu_usage = max(self._peak_cpu_usage, self._cpu_usage)

            logger.debug(f"Allocated CPU buffer {name}: {shape} {dtype}")
            return True

        except Exception as e:
            logger.error(f"Failed to allocate CPU buffer {name}: {e}")
            return False

    def allocate_gpu_buffer(self, name: str, shape: Tuple[int, ...], dtype: np.dtype = np.float32) -> bool:
        """Allocate GPU buffer."""
        if not self._gpu_enabled:
            logger.warning("GPU buffers not available")
            return False

        if name in self._gpu_buffers:
            logger.warning(f"GPU buffer {name} already exists")
            return False

        # Calculate required memory
        required_memory = np.prod(shape) * np.dtype(dtype).itemsize

        if self.max_gpu_memory and self._gpu_usage + required_memory > self.max_gpu_memory:
            # Try to free some GPU buffers
            if not self._free_least_used_buffers(required_memory, prefer_cpu=False):
                logger.error(f"Cannot allocate {required_memory} bytes: insufficient GPU memory")
                return False

        try:
            buffer = cp.zeros(shape, dtype=dtype)
            self._gpu_buffers[name] = buffer
            self._buffer_metadata[name] = {
                "type": "gpu",
                "shape": shape,
                "dtype": dtype,
                "size": required_memory,
                "created": time.time(),
                "last_accessed": time.time(),
                "access_count": 0
            }

            self._gpu_usage += required_memory
            self._allocation_count += 1
            self._peak_gpu_usage = max(self._peak_gpu_usage, self._gpu_usage)

            logger.debug(f"Allocated GPU buffer {name}: {shape} {dtype}")
            return True

        except Exception as e:
            logger.error(f"Failed to allocate GPU buffer {name}: {e}")
            return False

    def get_buffer(self, name: str) -> Optional[Union[np.ndarray, Any]]:
        """Get buffer by name."""
        if name in self._cpu_buffers:
            self._update_access_stats(name)
            return self._cpu_buffers[name]
        elif name in self._gpu_buffers:
            self._update_access_stats(name)
            return self._gpu_buffers[name]
        else:
            return None

    def copy_to_gpu(self, name: str) -> bool:
        """Copy CPU buffer to GPU."""
        if not self._gpu_enabled:
            return False

        if name not in self._cpu_buffers:
            logger.error(f"CPU buffer {name} not found")
            return False

        if name in self._gpu_buffers:
            logger.warning(f"GPU buffer {name} already exists")
            return True

        try:
            cpu_buffer = self._cpu_buffers[name]
            gpu_buffer = cp.asarray(cpu_buffer)

            # Calculate memory usage
            required_memory = cpu_buffer.nbytes

            self._gpu_buffers[name] = gpu_buffer
            self._buffer_metadata[f"{name}_gpu"] = {
                "type": "gpu",
                "shape": cpu_buffer.shape,
                "dtype": cpu_buffer.dtype,
                "size": required_memory,
                "created": time.time(),
                "last_accessed": time.time(),
                "access_count": 0
            }

            self._gpu_usage += required_memory
            logger.debug(f"Copied buffer {name} to GPU")
            return True

        except Exception as e:
            logger.error(f"Failed to copy buffer {name} to GPU: {e}")
            return False

    def copy_to_cpu(self, name: str) -> bool:
        """Copy GPU buffer to CPU."""
        if name not in self._gpu_buffers:
            logger.error(f"GPU buffer {name} not found")
            return False

        if name in self._cpu_buffers:
            logger.warning(f"CPU buffer {name} already exists")
            return True

        try:
            gpu_buffer = self._gpu_buffers[name]
            cpu_buffer = cp.asnumpy(gpu_buffer)

            # Calculate memory usage
            required_memory = cpu_buffer.nbytes

            if self._cpu_usage + required_memory > self.max_cpu_memory:
                if not self._free_least_used_buffers(required_memory, prefer_cpu=True):
                    logger.error(f"Cannot copy buffer {name}: insufficient CPU memory")
                    return False

            self._cpu_buffers[name] = cpu_buffer
            self._buffer_metadata[f"{name}_cpu"] = {
                "type": "cpu",
                "shape": cpu_buffer.shape,
                "dtype": cpu_buffer.dtype,
                "size": required_memory,
                "created": time.time(),
                "last_accessed": time.time(),
                "access_count": 0
            }

            self._cpu_usage += required_memory
            logger.debug(f"Copied buffer {name} to CPU")
            return True

        except Exception as e:
            logger.error(f"Failed to copy buffer {name} to CPU: {e}")
            return False

    def free_buffer(self, name: str) -> bool:
        """Free a named buffer."""
        freed = False

        if name in self._cpu_buffers:
            buffer = self._cpu_buffers[name]
            self._cpu_usage -= buffer.nbytes
            del self._cpu_buffers[name]
            freed = True

        if name in self._gpu_buffers:
            buffer = self._gpu_buffers[name]
            if hasattr(buffer, 'nbytes'):
                self._gpu_usage -= buffer.nbytes
            del self._gpu_buffers[name]
            freed = True

        if name in self._buffer_metadata:
            del self._buffer_metadata[name]

        if freed:
            self._deallocation_count += 1
            logger.debug(f"Freed buffer {name}")

        return freed

    def _update_access_stats(self, name: str) -> None:
        """Update buffer access statistics."""
        if name in self._buffer_metadata:
            self._buffer_metadata[name]["last_accessed"] = time.time()
            self._buffer_metadata[name]["access_count"] += 1

    def _free_least_used_buffers(self, required_memory: int, prefer_cpu: bool = True) -> bool:
        """Free least recently used buffers to make space."""
        # Sort buffers by last access time
        candidates = []

        target_buffers = self._cpu_buffers if prefer_cpu else self._gpu_buffers
        target_usage = self._cpu_usage if prefer_cpu else self._gpu_usage
        target_max = self.max_cpu_memory if prefer_cpu else (self.max_gpu_memory or float('inf'))

        for name in target_buffers:
            if name in self._buffer_metadata:
                metadata = self._buffer_metadata[name]
                candidates.append((metadata["last_accessed"], name, metadata["size"]))

        candidates.sort()  # Sort by access time (oldest first)

        freed_memory = 0
        for _, name, size in candidates:
            if target_usage - freed_memory + required_memory <= target_max:
                break

            self.free_buffer(name)
            freed_memory += size

        return target_usage - freed_memory + required_memory <= target_max

    def get_stats(self) -> BufferStats:
        """Get buffer usage statistics."""
        cpu_stats = BufferStats(
            total_size=self.max_cpu_memory,
            used_size=self._cpu_usage,
            free_size=self.max_cpu_memory - self._cpu_usage,
            allocation_count=self._allocation_count,
            deallocation_count=self._deallocation_count,
            peak_usage=self._peak_cpu_usage
        )

        return cpu_stats

    def cleanup(self) -> None:
        """Clean up all buffers."""
        buffer_names = list(self._cpu_buffers.keys()) + list(self._gpu_buffers.keys())
        for name in buffer_names:
            self.free_buffer(name)

        logger.info("Buffer manager cleanup complete")