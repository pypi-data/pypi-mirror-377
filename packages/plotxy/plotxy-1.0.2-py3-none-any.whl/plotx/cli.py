#!/usr/bin/env python3
"""
PlotX Command Line Interface
Provides command-line tools for PlotX demonstration and utilities.
"""

import argparse
import sys
import os
import subprocess
from pathlib import Path


def demo_command():
    """Run PlotX demonstration."""
    print("🚀 PlotX Demonstration")
    print("=" * 30)

    try:
        import plotx
        import numpy as np

        # Check dependencies
        print("Checking dependencies...")
        if not plotx.check_dependencies():
            return 1

        print("Creating demonstration charts...")

        # Basic line chart
        x = np.linspace(0, 2*np.pi, 100)
        y1 = np.sin(x)
        y2 = np.cos(x)

        chart = plotx.LineChart()
        chart.plot(x, y1, color='blue', linewidth=2, label='sin(x)')
        chart.plot(x, y2, color='red', linewidth=2, label='cos(x)')
        chart.set_title("PlotX Demo - Trigonometric Functions")
        chart.set_labels("X", "Y")
        chart.add_legend()
        chart.add_grid(alpha=0.3)
        chart.save("plotx_demo_trig.png")

        # Scatter plot
        np.random.seed(42)
        x_scatter = np.random.randn(200)
        y_scatter = np.random.randn(200)
        colors = x_scatter + y_scatter

        scatter_chart = plotx.ScatterChart()
        scatter_chart.plot(x_scatter, y_scatter, c=colors, s=50, alpha=0.7, cmap='viridis')
        scatter_chart.set_title("PlotX Demo - Scatter Plot")
        scatter_chart.set_labels("X Values", "Y Values")
        scatter_chart.add_colorbar(label="Color Scale")
        scatter_chart.save("plotx_demo_scatter.png")

        # 3D Surface
        x_3d = np.linspace(-2, 2, 30)
        y_3d = np.linspace(-2, 2, 30)
        X, Y = np.meshgrid(x_3d, y_3d)
        Z = np.sin(X) * np.cos(Y)

        surface_chart = plotx.SurfaceChart()
        surface_chart.plot_surface(X, Y, Z, cmap='coolwarm', alpha=0.8)
        surface_chart.set_title("PlotX Demo - 3D Surface")
        surface_chart.save("plotx_demo_3d.png")

        print("\n✅ Demo completed successfully!")
        print("Generated files:")
        print("  📈 plotx_demo_trig.png")
        print("  📊 plotx_demo_scatter.png")
        print("  🌄 plotx_demo_3d.png")
        print("\n🎉 PlotX is working correctly!")

        return 0

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please install PlotX: pip install plotx")
        return 1
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return 1


def gallery_command():
    """Launch PlotX gallery."""
    print("🎨 Launching PlotX Gallery...")

    try:
        # Try to find gallery script
        gallery_paths = [
            "examples/web_start.py",
            "plotx/examples/web_start.py",
            os.path.join(os.path.dirname(__file__), "..", "..", "examples", "web_start.py")
        ]

        gallery_script = None
        for path in gallery_paths:
            if os.path.exists(path):
                gallery_script = path
                break

        if gallery_script:
            print(f"Starting gallery from: {gallery_script}")
            subprocess.run([sys.executable, gallery_script])
        else:
            print("❌ Gallery script not found")
            print("Please run from PlotX repository directory or install complete package")
            return 1

        return 0

    except Exception as e:
        print(f"❌ Gallery launch failed: {e}")
        return 1


def server_command():
    """Start PlotX web server."""
    print("🌐 Starting PlotX Web Server...")

    try:
        import plotx.web
        server = plotx.web.PlotXServer()
        server.start(port=8888)
        return 0

    except ImportError:
        print("❌ Web components not available")
        print("Install with web support: pip install plotx[web]")
        return 1
    except Exception as e:
        print(f"❌ Server start failed: {e}")
        return 1


def info_command():
    """Show PlotX information."""
    print("📊 PlotX Information")
    print("=" * 30)

    try:
        import plotx
        info = plotx.get_info()

        print(f"Version: {info['version']}")
        print(f"Description: {info['description']}")
        print(f"Author: {info['author']}")
        print(f"License: {info['license']}")
        print(f"Python Requirements: {info['python_requires']}")
        print(f"Dependencies: {', '.join(info['dependencies'])}")

        print(f"\nFeatures ({len(info['features'])}):")
        for feature in info['features']:
            print(f"  ✓ {feature}")

        print(f"\nChart Types ({len(info['chart_types'])}):")
        for chart_type in info['chart_types']:
            print(f"  📊 {chart_type}")

        # Check if installed correctly
        print(f"\nInstallation Check:")
        if plotx.check_dependencies():
            print("  ✅ All dependencies satisfied")
        else:
            print("  ❌ Missing dependencies")

        return 0

    except Exception as e:
        print(f"❌ Info command failed: {e}")
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="PlotX Command Line Interface",
        prog="plotx"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Demo command
    demo_parser = subparsers.add_parser("demo", help="Run PlotX demonstration")
    demo_parser.set_defaults(func=demo_command)

    # Gallery command
    gallery_parser = subparsers.add_parser("gallery", help="Launch interactive gallery")
    gallery_parser.set_defaults(func=gallery_command)

    # Server command
    server_parser = subparsers.add_parser("server", help="Start web server")
    server_parser.add_argument("--port", type=int, default=8888, help="Port number (default: 8888)")
    server_parser.set_defaults(func=server_command)

    # Info command
    info_parser = subparsers.add_parser("info", help="Show PlotX information")
    info_parser.set_defaults(func=info_command)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Execute command
    try:
        return args.func()
    except KeyboardInterrupt:
        print("\n⏹️  Interrupted by user")
        return 130
    except Exception as e:
        print(f"❌ Command failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())