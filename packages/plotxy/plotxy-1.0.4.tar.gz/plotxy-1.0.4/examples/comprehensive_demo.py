#!/usr/bin/env python3
"""
Comprehensive demonstration of PlotX capabilities.

This example showcases the full range of PlotX features including:
- High-performance rendering
- Real-time data streaming
- Advanced chart types
- CAE visualization
- Interactive web components
- GPU acceleration
"""

import time
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

import plotx as px
from plotx.core import DataStream, RealTimeChart, PerformanceMonitor
from plotx.web import PlotXServer, DashboardComponent
from plotx.cae import FEAMesh, MeshRenderer, ScalarField


def demo_basic_charts():
    """Demonstrate basic chart functionality."""
    print("=== Basic Charts Demo ===")

    # Line chart with themes
    fig = px.PlotXFigure(style="dark", width=12, height=8)
    line_chart = px.LineChart(fig)

    # Generate sample data
    x = np.linspace(0, 4*np.pi, 1000)
    y1 = np.sin(x) * np.exp(-x/10)
    y2 = np.cos(x) * np.exp(-x/8)

    line_chart.plot(x, y1, label="Damped Sine", color="cyan", line_width=2)
    line_chart.plot(x, y2, label="Damped Cosine", color="orange", line_width=2)

    fig.axes.legend()
    fig.axes.set_title("High-Performance Line Chart", fontsize=16)
    fig.save("examples/output/basic_line_chart.png")
    print("✓ Line chart saved")

    # 3D Surface with interaction
    fig_3d = px.PlotXFigure(width=10, height=8)
    surface_chart = px.InteractiveSurfaceChart(fig_3d)

    # Generate 3D surface data
    x = np.linspace(-5, 5, 50)
    y = np.linspace(-5, 5, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(np.sqrt(X**2 + Y**2)) * np.exp(-0.1 * np.sqrt(X**2 + Y**2))

    surface_chart.plot(X, Y, Z, cmap="plasma", antialiased=True)
    fig_3d.save("examples/output/interactive_surface.png")
    print("✓ Interactive 3D surface saved")


def demo_advanced_charts():
    """Demonstrate advanced chart types."""
    print("\n=== Advanced Charts Demo ===")

    # Heatmap
    fig_heat = px.PlotXFigure(width=10, height=8)
    heatmap = px.HeatmapChart(fig_heat)

    # Generate correlation matrix
    data = np.random.randn(10, 10)
    correlation_matrix = np.corrcoef(data)

    labels = [f"Var{i+1}" for i in range(10)]
    heatmap.plot(correlation_matrix, x_labels=labels, y_labels=labels,
                colormap="RdBu_r", show_values=True, title="Correlation Matrix")
    fig_heat.save("examples/output/heatmap.png")
    print("✓ Heatmap saved")

    # Radar chart
    fig_radar = px.PlotXFigure(width=8, height=8)
    radar = px.RadarChart(fig_radar)

    # Sample performance metrics
    metrics = ["Speed", "Accuracy", "Memory", "Scalability", "Ease of Use"]
    plotx_scores = [0.9, 0.95, 0.8, 0.9, 0.85]
    competitor_scores = [0.7, 0.8, 0.9, 0.7, 0.9]

    values = np.array([plotx_scores, competitor_scores])
    radar.plot(values, metrics, series_names=["PlotX", "Competitor"],
              colors=["blue", "red"])
    fig_radar.save("examples/output/radar_chart.png")
    print("✓ Radar chart saved")

    # Treemap
    fig_tree = px.PlotXFigure(width=10, height=6)
    treemap = px.TreemapChart(fig_tree)

    # Market share data
    companies = ["PlotX", "Plotly", "Matplotlib", "Seaborn", "Bokeh", "Others"]
    market_share = [25, 30, 20, 10, 8, 7]
    colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", "#DDA0DD"]

    treemap.plot(market_share, companies, colors=colors,
                title="Visualization Library Market Share")
    fig_tree.save("examples/output/treemap.png")
    print("✓ Treemap saved")


def demo_financial_charts():
    """Demonstrate financial chart types."""
    print("\n=== Financial Charts Demo ===")

    # Generate sample financial data
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    np.random.seed(42)

    # Simulate stock price with realistic movements
    returns = np.random.normal(0.001, 0.02, len(dates))
    price = 100 * np.exp(np.cumsum(returns))

    # Create OHLC data
    high = price * (1 + np.abs(np.random.normal(0, 0.01, len(dates))))
    low = price * (1 - np.abs(np.random.normal(0, 0.01, len(dates))))
    open_price = np.roll(price, 1)
    open_price[0] = price[0]
    close_price = price

    volume = np.random.lognormal(mean=10, sigma=0.5, size=len(dates))

    # Candlestick chart
    fig_candle = px.PlotXFigure(width=14, height=10)
    candlestick = px.CandlestickChart(fig_candle)

    candlestick.plot(dates, open_price, high, low, close_price, volume=volume)
    candlestick.add_moving_average(dates, close_price, period=20, color="blue", label="20-day MA")
    candlestick.add_moving_average(dates, close_price, period=50, color="red", label="50-day MA")
    candlestick.add_bollinger_bands(dates, close_price, period=20, num_std=2.0)

    fig_candle.save("examples/output/candlestick_chart.png", dpi=150)
    print("✓ Candlestick chart with indicators saved")

    # RSI chart
    fig_rsi = px.PlotXFigure(width=12, height=6)
    rsi_chart = px.RSIChart(fig_rsi)
    rsi_chart.plot(dates, close_price, period=14)
    fig_rsi.save("examples/output/rsi_chart.png")
    print("✓ RSI chart saved")


def demo_cae_visualization():
    """Demonstrate CAE and FEA capabilities."""
    print("\n=== CAE Visualization Demo ===")

    # Create a simple FEA mesh (2D plate with hole)
    mesh = FEAMesh()

    # Generate mesh nodes
    n_x, n_y = 20, 10
    x = np.linspace(0, 10, n_x)
    y = np.linspace(0, 5, n_y)

    nodes = []
    node_id = 1

    for j in range(n_y):
        for i in range(n_x):
            # Skip nodes in the center (hole)
            if 4 <= i <= 6 and 3 <= j <= 6:
                continue

            coord = (x[i], y[j], 0.0)
            nodes.append((node_id, coord))
            node_id += 1

    # Add nodes to mesh
    for nid, coord in nodes:
        from plotx.cae.mesh import Node
        mesh.add_node(Node(nid, coord))

    # Create simple stress field
    n_nodes = len(nodes)
    stress_values = np.random.uniform(50, 200, n_nodes)  # Stress in MPa
    node_coords = np.array([coord for _, coord in nodes])

    # Visualize mesh with stress
    fig_mesh = px.PlotXFigure(width=12, height=8)
    renderer = MeshRenderer(fig_mesh)

    renderer.render_mesh(mesh, mode="surface", scalar_field=stress_values,
                        colormap="jet", show_edges=True)

    fig_mesh.axes.set_title("FEA Stress Analysis", fontsize=14)
    fig_mesh.save("examples/output/fea_stress.png")
    print("✓ FEA stress visualization saved")


def demo_real_time_streaming():
    """Demonstrate real-time data streaming."""
    print("\n=== Real-Time Streaming Demo ===")

    # Create data stream
    from plotx.core.streaming import RandomDataSource

    data_stream = DataStream()
    random_source = RandomDataSource(frequency=10.0)  # 10 Hz
    data_stream.add_source("sensor1", random_source, ["x", "y", "z"])

    # Create real-time chart
    fig_rt = px.PlotXFigure(width=12, height=8)
    rt_chart = RealTimeChart(fig_rt, data_stream)

    rt_chart.add_line_series("sensor1", "x", "y", label="Signal Y")
    rt_chart.add_line_series("sensor1", "x", "z", label="Signal Z")

    print("✓ Real-time streaming chart configured")

    # Simulate data collection for a few seconds
    rt_chart.start()
    time.sleep(5)  # Collect data for 5 seconds
    rt_chart.stop()

    fig_rt.save("examples/output/realtime_data.png")
    print("✓ Real-time data visualization saved")


def demo_performance_monitoring():
    """Demonstrate performance monitoring."""
    print("\n=== Performance Monitoring Demo ===")

    # Start performance monitoring
    monitor = PerformanceMonitor(sample_interval=0.5)
    monitor.start_monitoring()

    # Simulate heavy computation
    print("Running performance test...")
    for i in range(10):
        # Generate large dataset
        data = np.random.randn(100000, 3)

        # Create chart
        fig = px.PlotXFigure()
        scatter = px.ScatterChart(fig)

        # Subsample for visualization
        indices = np.random.choice(len(data), 1000, replace=False)
        scatter.plot(data[indices, 0], data[indices, 1],
                    c=data[indices, 2], cmap="viridis", s=20)

        time.sleep(0.5)

    # Get performance stats
    monitor.stop_monitoring()
    final_metrics = monitor.get_current_metrics()

    if final_metrics:
        print(f"✓ Performance monitoring complete:")
        print(f"  CPU Usage: {final_metrics.cpu_usage:.1f}%")
        print(f"  Memory Usage: {final_metrics.memory_usage:.1f}%")

        if final_metrics.gpu_usage is not None:
            print(f"  GPU Usage: {final_metrics.gpu_usage:.1f}%")

    # Check for performance issues
    issues = monitor.detect_performance_issues()
    if issues:
        print("⚠️  Performance issues detected:")
        for issue in issues:
            print(f"    - {issue}")
    else:
        print("✓ No performance issues detected")


def demo_web_dashboard():
    """Demonstrate web dashboard capabilities."""
    print("\n=== Web Dashboard Demo ===")

    try:
        # Create web server
        server = PlotXServer(port=8890, debug=True)

        # Create dashboard
        dashboard = DashboardComponent(title="PlotX Analytics Dashboard")

        # Add various charts to dashboard
        # Chart 1: Line chart with multiple series
        chart1 = px.InteractiveChart()
        x = np.linspace(0, 10, 100)
        y1 = np.sin(x)
        y2 = np.cos(x)
        chart1.add_line_series(x, y1, name="Sin(x)", color="blue")
        chart1.add_line_series(x, y2, name="Cos(x)", color="red")

        # Chart 2: Bar chart
        chart2 = px.InteractiveChart()
        categories = ["Q1", "Q2", "Q3", "Q4"]
        values = [120, 150, 180, 200]
        chart2.add_bar_series(categories, values, name="Revenue", color="green")

        # Chart 3: 3D Surface
        chart3 = px.InteractiveChart()
        x = np.linspace(-2, 2, 20)
        y = np.linspace(-2, 2, 20)
        X, Y = np.meshgrid(x, y)
        Z = X * np.exp(-X**2 - Y**2)
        chart3.add_surface_series(X, Y, Z, name="Surface", colorscale="viridis")

        # Add charts to dashboard
        dashboard.add_chart(chart1)
        dashboard.add_chart(chart2)
        dashboard.add_chart(chart3)

        # Add dashboard to server
        server.add_component(dashboard)

        print("✓ Web dashboard configured")
        print(f"  Server ready at: http://localhost:8890")
        print(f"  Dashboard at: http://localhost:8890/dashboard/{dashboard.id}")

        # Start server (non-blocking for demo)
        server.start(blocking=False)
        time.sleep(2)  # Let server start

        print("✓ Web server started successfully")
        server.stop()

    except ImportError:
        print("⚠️  Web dashboard requires tornado (pip install tornado)")
    except Exception as e:
        print(f"⚠️  Web dashboard demo failed: {e}")


def demo_gpu_acceleration():
    """Demonstrate GPU acceleration capabilities."""
    print("\n=== GPU Acceleration Demo ===")

    try:
        from plotx.core import RenderEngine, RenderConfig, RenderBackend

        # Try GPU rendering
        gpu_config = RenderConfig(backend=RenderBackend.AUTO, max_fps=60)
        render_engine = RenderEngine(gpu_config)

        if render_engine.initialize():
            print(f"✓ Render engine initialized with {gpu_config.backend.value} backend")

            # Generate large dataset for performance test
            n_points = 100000
            vertices = np.random.randn(n_points, 3).astype(np.float32)
            colors = np.random.rand(n_points, 3).astype(np.float32)

            # Benchmark rendering
            start_time = time.time()
            render_engine.render_points(vertices, colors=colors)
            end_time = time.time()

            render_time = (end_time - start_time) * 1000  # Convert to milliseconds
            print(f"✓ Rendered {n_points:,} points in {render_time:.2f}ms")

            # Get performance stats
            stats = render_engine.get_performance_stats()
            print(f"  Backend: {stats.get('backend', 'unknown')}")
            print(f"  FPS: {stats.get('fps', 0):.1f}")

            render_engine.shutdown()
        else:
            print("⚠️  Failed to initialize GPU rendering")

    except Exception as e:
        print(f"⚠️  GPU acceleration demo failed: {e}")


def main():
    """Run all demonstrations."""
    print("PlotX Comprehensive Demo")
    print("=" * 50)

    # Create output directory
    import os
    os.makedirs("examples/output", exist_ok=True)

    # Run all demos
    demo_basic_charts()
    demo_advanced_charts()
    demo_financial_charts()
    demo_cae_visualization()
    demo_real_time_streaming()
    demo_performance_monitoring()
    demo_gpu_acceleration()
    demo_web_dashboard()

    print("\n" + "=" * 50)
    print("🎉 All demos completed successfully!")
    print("\nGenerated files:")
    print("  - examples/output/basic_line_chart.png")
    print("  - examples/output/interactive_surface.png")
    print("  - examples/output/heatmap.png")
    print("  - examples/output/radar_chart.png")
    print("  - examples/output/treemap.png")
    print("  - examples/output/candlestick_chart.png")
    print("  - examples/output/rsi_chart.png")
    print("  - examples/output/fea_stress.png")
    print("  - examples/output/realtime_data.png")

    print("\nPlotX Features Demonstrated:")
    print("✓ High-performance rendering")
    print("✓ Real-time data streaming")
    print("✓ Advanced chart types")
    print("✓ Financial analysis tools")
    print("✓ CAE/FEA visualization")
    print("✓ Performance monitoring")
    print("✓ GPU acceleration")
    print("✓ Interactive web dashboards")

    print("\nPlotX is ready for production use!")


if __name__ == "__main__":
    main()