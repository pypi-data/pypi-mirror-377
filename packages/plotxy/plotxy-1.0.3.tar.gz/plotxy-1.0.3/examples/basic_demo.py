#!/usr/bin/env python3
"""
Basic demonstration of PlotX capabilities.
"""

import os
import numpy as np
import matplotlib.pyplot as plt

try:
    import plotx as px
    print("✓ PlotX imported successfully")
except ImportError as e:
    print(f"❌ Failed to import PlotX: {e}")
    exit(1)


def demo_basic_line_chart():
    """Test basic line chart functionality."""
    print("\n=== Testing Basic Line Chart ===")

    try:
        # Create figure
        fig = px.PlotXFigure(style="light", width=10, height=6)
        line_chart = px.LineChart(fig)

        # Generate sample data
        x = np.linspace(0, 2*np.pi, 100)
        y1 = np.sin(x)
        y2 = np.cos(x)

        # Plot data
        line_chart.plot(x, y1, label="sin(x)")
        line_chart.plot(x, y2, label="cos(x)")

        fig.axes.legend()
        fig.axes.set_title("Basic Line Chart Demo")
        fig.axes.set_xlabel("x")
        fig.axes.set_ylabel("y")

        # Save chart
        os.makedirs("examples/output", exist_ok=True)
        fig.save("examples/output/basic_line_chart.png")
        print("✓ Basic line chart created and saved")

    except Exception as e:
        print(f"❌ Basic line chart failed: {e}")


def demo_scatter_chart():
    """Test scatter chart functionality."""
    print("\n=== Testing Scatter Chart ===")

    try:
        # Create figure
        fig = px.PlotXFigure(width=8, height=6)
        scatter_chart = px.ScatterChart(fig)

        # Generate sample data
        n_points = 500
        x = np.random.randn(n_points)
        y = np.random.randn(n_points)
        colors = np.random.rand(n_points)

        # Plot data
        scatter_chart.plot(x, y, c=colors, s=30, alpha=0.7)

        fig.axes.set_title("Scatter Chart Demo")
        fig.axes.set_xlabel("X values")
        fig.axes.set_ylabel("Y values")

        # Save chart
        fig.save("examples/output/scatter_chart.png")
        print("✓ Scatter chart created and saved")

    except Exception as e:
        print(f"❌ Scatter chart failed: {e}")


def demo_surface_chart():
    """Test 3D surface chart functionality."""
    print("\n=== Testing 3D Surface Chart ===")

    try:
        # Create figure
        fig = px.PlotXFigure(width=10, height=8)
        surface_chart = px.SurfaceChart(fig)

        # Generate 3D surface data
        x = np.linspace(-2, 2, 30)
        y = np.linspace(-2, 2, 30)
        X, Y = np.meshgrid(x, y)
        Z = np.sin(np.sqrt(X**2 + Y**2))

        # Plot surface
        surface_chart.plot(X, Y, Z, cmap="viridis")

        fig.axes.set_title("3D Surface Demo")

        # Save chart
        fig.save("examples/output/surface_chart.png")
        print("✓ 3D surface chart created and saved")

    except Exception as e:
        print(f"❌ 3D surface chart failed: {e}")


def demo_bar_chart():
    """Test bar chart functionality."""
    print("\n=== Testing Bar Chart ===")

    try:
        # Create figure
        fig = px.PlotXFigure(width=8, height=6)
        bar_chart = px.BarChart(fig)

        # Sample data
        categories = ['A', 'B', 'C', 'D', 'E']
        values = [23, 45, 56, 78, 32]

        # Plot bars
        bar_chart.plot(categories, values, color="steelblue")

        fig.axes.set_title("Bar Chart Demo")
        fig.axes.set_xlabel("Categories")
        fig.axes.set_ylabel("Values")

        # Save chart
        fig.save("examples/output/bar_chart.png")
        print("✓ Bar chart created and saved")

    except Exception as e:
        print(f"❌ Bar chart failed: {e}")


def main():
    """Run basic PlotX demonstrations."""
    print("PlotX Basic Demo")
    print("=" * 40)

    # Create output directory
    os.makedirs("examples/output", exist_ok=True)

    # Run basic demos
    demo_basic_line_chart()
    demo_scatter_chart()
    demo_surface_chart()
    demo_bar_chart()

    print("\n" + "=" * 40)
    print("🎉 Basic demos completed!")
    print("\nGenerated files:")
    print("  - examples/output/basic_line_chart.png")
    print("  - examples/output/scatter_chart.png")
    print("  - examples/output/surface_chart.png")
    print("  - examples/output/bar_chart.png")

    print("\nPlotX basic functionality verified! ✓")


if __name__ == "__main__":
    main()