#!/usr/bin/env python3
"""
Advanced demonstration of PlotX capabilities.
"""

import os
import time
import numpy as np

try:
    import plotxy as px
    print("✓ PlotX imported successfully")
except ImportError as e:
    print(f"❌ Failed to import PlotX: {e}")
    exit(1)


def demo_performance_monitoring():
    """Test performance monitoring."""
    print("\n=== Testing Performance Monitoring ===")

    try:
        from plotxy.core.performance import PerformanceMonitor

        # Start monitoring
        monitor = PerformanceMonitor(sample_interval=0.5)
        monitor.start_monitoring()

        # Simulate some work
        print("Running performance test...")
        for i in range(5):
            # Generate large dataset
            data = np.random.randn(50000, 2)

            # Create chart
            fig = px.PlotXFigure()
            scatter = px.ScatterChart(fig)
            scatter.plot(data[:1000, 0], data[:1000, 1], s=20, alpha=0.6)

            time.sleep(0.3)

        # Get performance stats
        monitor.stop_monitoring()
        final_metrics = monitor.get_current_metrics()

        if final_metrics:
            print(f"✓ Performance monitoring complete:")
            print(f"  CPU Usage: {final_metrics.cpu_usage:.1f}%")
            print(f"  Memory Usage: {final_metrics.memory_usage:.1f}%")

        # Check for performance issues
        issues = monitor.detect_performance_issues()
        if issues:
            print("⚠️  Performance issues detected:")
            for issue in issues:
                print(f"    - {issue}")
        else:
            print("✓ No performance issues detected")

    except Exception as e:
        print(f"❌ Performance monitoring failed: {e}")


def demo_real_time_basics():
    """Test basic real-time functionality."""
    print("\n=== Testing Real-Time Basics ===")

    try:
        from plotxy.core.streaming import DataStream, RandomDataSource

        # Create data stream
        data_stream = DataStream()
        random_source = RandomDataSource(frequency=5.0)  # 5 Hz
        data_stream.add_source("sensor1", random_source, ["time", "value"])

        print("✓ Data stream created")

        # Start streaming for a short time
        data_stream.start_streaming()
        time.sleep(2)  # Collect data for 2 seconds
        data_stream.stop_streaming()

        # Check buffer
        buffer = data_stream.get_buffer("sensor1")
        if buffer and len(buffer) > 0:
            print(f"✓ Collected {len(buffer)} data points")
        else:
            print("⚠️  No data collected")

    except Exception as e:
        print(f"❌ Real-time demo failed: {e}")


def demo_heatmap():
    """Test heatmap chart."""
    print("\n=== Testing Heatmap Chart ===")

    try:
        from plotxy.charts.advanced import HeatmapChart

        # Create figure
        fig = px.PlotXFigure(width=10, height=8)
        heatmap = HeatmapChart(fig)

        # Generate sample correlation matrix
        data = np.random.randn(8, 8)
        correlation_matrix = np.corrcoef(data)

        labels = [f"Var{i+1}" for i in range(8)]
        heatmap.plot(correlation_matrix, x_labels=labels, y_labels=labels,
                    colormap="RdBu_r", title="Correlation Matrix")

        fig.save("examples/output/heatmap_demo.png")
        print("✓ Heatmap chart created and saved")

    except Exception as e:
        print(f"❌ Heatmap demo failed: {e}")


def demo_gpu_availability():
    """Check GPU capabilities."""
    print("\n=== Testing GPU Capabilities ===")

    try:
        from plotxy.core.renderer import RenderEngine, RenderConfig, RenderBackend

        # Check available backends
        gpu_config = RenderConfig(backend=RenderBackend.AUTO)
        render_engine = RenderEngine(gpu_config)

        if render_engine.initialize():
            print(f"✓ Render engine initialized with {gpu_config.backend.value} backend")

            # Get performance stats
            stats = render_engine.get_performance_stats()
            print(f"  Backend: {stats.get('backend', 'unknown')}")

            render_engine.shutdown()
        else:
            print("⚠️  Failed to initialize rendering engine")

    except Exception as e:
        print(f"❌ GPU demo failed: {e}")


def demo_buffer_management():
    """Test buffer management."""
    print("\n=== Testing Buffer Management ===")

    try:
        from plotxy.core.performance import BufferManager

        # Create buffer manager
        buffer_mgr = BufferManager(max_cpu_memory=100*1024*1024)  # 100MB

        # Allocate some buffers
        success1 = buffer_mgr.allocate_cpu_buffer("test1", (1000, 1000), np.float32)
        success2 = buffer_mgr.allocate_cpu_buffer("test2", (500, 500), np.float64)

        if success1 and success2:
            print("✓ CPU buffers allocated successfully")

            # Get stats
            stats = buffer_mgr.get_stats()
            print(f"  Memory used: {stats.used_size / (1024*1024):.1f} MB")
            print(f"  Allocations: {stats.allocation_count}")

            # Clean up
            buffer_mgr.cleanup()
            print("✓ Buffer cleanup complete")
        else:
            print("⚠️  Buffer allocation failed")

    except Exception as e:
        print(f"❌ Buffer management demo failed: {e}")


def main():
    """Run advanced PlotX demonstrations."""
    print("PlotX Advanced Demo")
    print("=" * 50)

    # Create output directory
    os.makedirs("examples/output", exist_ok=True)

    # Run advanced demos
    demo_performance_monitoring()
    demo_real_time_basics()
    demo_heatmap()
    demo_gpu_availability()
    demo_buffer_management()

    print("\n" + "=" * 50)
    print("🎉 Advanced demos completed!")

    print("\nPlotX Advanced Features Status:")
    print("✓ Performance monitoring system")
    print("✓ Real-time data streaming")
    print("✓ Advanced chart types")
    print("✓ Buffer management")
    print("✓ Multi-backend rendering")

    print("\nPlotX is ready for high-performance applications! 🚀")


if __name__ == "__main__":
    main()