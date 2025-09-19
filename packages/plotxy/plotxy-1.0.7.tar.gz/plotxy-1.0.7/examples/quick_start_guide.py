#!/usr/bin/env python3
"""
PlotX Quick Start Guide
Step-by-step introduction to PlotX visualization library.
"""

import numpy as np
import sys
import os

# Add src to path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import plotxy


def step_1_hello_plotx():
    """Step 1: Your first PlotX chart."""
    print("📈 Step 1: Creating your first PlotX chart")

    # Simple data
    x = [1, 2, 3, 4, 5]
    y = [2, 4, 6, 8, 10]

    # Create chart
    chart = plotxy.LineChart()
    chart.plot(x, y, color='blue', linewidth=2)
    chart.set_title('My First PlotX Chart')
    chart.save('examples/outputs/step1_first_chart.png')

    print("✓ First chart created! Check step1_first_chart.png")
    print("  This demonstrates basic line plotting with PlotX\n")


def step_2_customization():
    """Step 2: Customizing your charts."""
    print("🎨 Step 2: Customizing charts")

    # Generate sample data
    x = np.linspace(0, 2*np.pi, 50)
    y = np.sin(x)

    # Create and customize chart
    chart = plotxy.LineChart(width=800, height=600)
    chart.plot(x, y, color='red', linewidth=3, label='sin(x)')

    # Add customization
    chart.set_title('Customized Sine Wave', fontsize=16, fontweight='bold')
    chart.set_labels(xlabel='Angle (radians)', ylabel='Amplitude')
    chart.add_grid(visible=True, alpha=0.3)
    chart.add_legend(location='upper right')
    chart.set_limits(xlim=(0, 2*np.pi), ylim=(-1.2, 1.2))

    chart.save('examples/outputs/step2_customized.png', dpi=300)

    print("✓ Customized chart created! Check step2_customized.png")
    print("  This shows titles, labels, grids, legends, and limits\n")


def step_3_multiple_series():
    """Step 3: Multiple data series."""
    print("📊 Step 3: Multiple data series")

    # Create multiple datasets
    x = np.linspace(0, 4*np.pi, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)
    y3 = np.sin(x) * np.cos(x/2)

    # Plot multiple series
    chart = plotxy.LineChart(width=1000, height=600)
    chart.plot(x, y1, color='blue', linewidth=2, label='sin(x)')
    chart.plot(x, y2, color='red', linewidth=2, label='cos(x)')
    chart.plot(x, y3, color='green', linewidth=2, label='sin(x)·cos(x/2)')

    # Styling
    chart.set_title('Multiple Data Series')
    chart.set_labels('X Values', 'Y Values')
    chart.add_legend()
    chart.add_grid(alpha=0.3)

    chart.save('examples/outputs/step3_multiple_series.png', dpi=300)

    print("✓ Multiple series chart created! Check step3_multiple_series.png")
    print("  This demonstrates plotting multiple datasets on one chart\n")


def step_4_different_chart_types():
    """Step 4: Different chart types."""
    print("📈 Step 4: Exploring different chart types")

    # Scatter plot
    np.random.seed(42)
    x = np.random.randn(100)
    y = np.random.randn(100)
    colors = np.random.rand(100)

    scatter_chart = plotxy.ScatterChart()
    scatter_chart.plot(x, y, c=colors, s=60, alpha=0.7, cmap='viridis')
    scatter_chart.set_title('Scatter Plot Example')
    scatter_chart.set_labels('X Values', 'Y Values')
    scatter_chart.add_colorbar(label='Color Scale')
    scatter_chart.save('examples/outputs/step4a_scatter.png')

    # Bar chart
    categories = ['A', 'B', 'C', 'D', 'E']
    values = [23, 45, 56, 78, 32]

    bar_chart = plotxy.BarChart()
    bar_chart.bar(categories, values, color='orange', alpha=0.8)
    bar_chart.set_title('Bar Chart Example')
    bar_chart.set_labels('Categories', 'Values')
    bar_chart.add_grid(axis='y', alpha=0.3)
    bar_chart.save('examples/outputs/step4b_bar.png')

    # Histogram
    data = np.random.normal(50, 15, 1000)
    hist_chart = plotxy.HistogramChart()
    hist_chart.hist(data, bins=30, color='skyblue', alpha=0.7)
    hist_chart.set_title('Histogram Example')
    hist_chart.set_labels('Values', 'Frequency')
    hist_chart.add_grid(alpha=0.3)
    hist_chart.save('examples/outputs/step4c_histogram.png')

    print("✓ Different chart types created!")
    print("  - Scatter plot: step4a_scatter.png")
    print("  - Bar chart: step4b_bar.png")
    print("  - Histogram: step4c_histogram.png\n")


def step_5_3d_visualization():
    """Step 5: 3D visualization."""
    print("🌄 Step 5: 3D visualization")

    # Create 3D surface data
    x = np.linspace(-2, 2, 30)
    y = np.linspace(-2, 2, 30)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y) * np.exp(-(X**2 + Y**2)/4)

    # Create 3D surface
    surface_chart = plotxy.SurfaceChart()
    surface_chart.plot_surface(X, Y, Z, cmap='coolwarm', alpha=0.8)
    surface_chart.set_title('3D Surface Visualization')
    surface_chart.set_labels('X', 'Y', 'Z')
    surface_chart.save('examples/outputs/step5_3d_surface.png')

    print("✓ 3D surface created! Check step5_3d_surface.png")
    print("  This demonstrates 3D plotting capabilities\n")


def step_6_real_world_example():
    """Step 6: Real-world data example."""
    print("🌍 Step 6: Real-world data example")

    # Simulate monthly temperature data
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    # Temperature data for three cities
    city_data = {
        'New York': [32, 35, 45, 55, 65, 75, 80, 78, 70, 60, 50, 38],
        'Los Angeles': [65, 67, 70, 73, 75, 78, 82, 83, 80, 76, 71, 66],
        'Chicago': [25, 30, 40, 52, 63, 73, 78, 76, 68, 56, 45, 32]
    }

    # Create comparison chart
    chart = plotxy.LineChart(width=1000, height=600)

    colors = ['blue', 'red', 'green']
    for i, (city, temps) in enumerate(city_data.items()):
        chart.plot(months, temps, color=colors[i], linewidth=3,
                  marker='o', markersize=6, label=city)

    # Professional styling
    chart.set_title('Monthly Temperature Comparison', fontsize=16, fontweight='bold')
    chart.set_labels('Month', 'Temperature (°F)')
    chart.add_legend(location='upper left')
    chart.add_grid(alpha=0.3)

    # Add average line
    all_temps = [temp for temps in city_data.values() for temp in temps]
    avg_temp = np.mean(all_temps)
    chart.add_horizontal_line(avg_temp, color='black', linestyle='--',
                             alpha=0.7, label=f'Average: {avg_temp:.1f}°F')

    chart.save('examples/outputs/step6_real_world.png', dpi=300)

    print("✓ Real-world example created! Check step6_real_world.png")
    print("  This shows temperature comparison with professional styling\n")


def step_7_interactive_features():
    """Step 7: Interactive features preview."""
    print("🎮 Step 7: Interactive features preview")

    # Create data for interactive demonstration
    x = np.linspace(0, 10, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)
    y3 = np.sin(x) * np.exp(-x/10)

    # Create interactive-ready chart
    chart = plotxy.LineChart(width=1200, height=700)
    chart.plot(x, y1, color='blue', linewidth=2, label='sin(x)')
    chart.plot(x, y2, color='red', linewidth=2, label='cos(x)')
    chart.plot(x, y3, color='green', linewidth=2, label='Damped sine')

    # Prepare for interaction
    chart.enable_zoom_pan()
    chart.enable_selection()
    chart.enable_hover_tooltips()

    chart.set_title('Interactive Chart (Zoom, Pan, Hover)', fontsize=16)
    chart.set_labels('X Values', 'Y Values')
    chart.add_legend()
    chart.add_grid(alpha=0.3)

    # Save static version
    chart.save('examples/outputs/step7_interactive_preview.png', dpi=300)

    # Export interactive version
    chart.save_html('examples/outputs/step7_interactive.html')

    print("✓ Interactive features demonstrated!")
    print("  - Static preview: step7_interactive_preview.png")
    print("  - Interactive HTML: step7_interactive.html")
    print("  Features: zoom, pan, hover tooltips\n")


def step_8_themes_and_styling():
    """Step 8: Themes and advanced styling."""
    print("🎨 Step 8: Themes and advanced styling")

    # Sample data
    x = np.linspace(0, 6, 50)
    y = np.exp(-x/2) * np.sin(2*x)

    # Dark theme example
    chart_dark = plotxy.LineChart(width=800, height=600)
    chart_dark.set_theme('dark')
    chart_dark.plot(x, y, color='cyan', linewidth=3, label='Exponential decay')
    chart_dark.set_title('Dark Theme Example', color='white')
    chart_dark.set_labels('Time', 'Amplitude', color='white')
    chart_dark.add_legend()
    chart_dark.add_grid(alpha=0.3, color='gray')
    chart_dark.save('examples/outputs/step8a_dark_theme.png')

    # Scientific theme example
    chart_sci = plotxy.LineChart(width=800, height=600)
    chart_sci.set_theme('scientific')
    chart_sci.plot(x, y, color='darkblue', linewidth=2, label='Exponential decay')
    chart_sci.set_title('Scientific Theme Example')
    chart_sci.set_labels('Time (s)', 'Amplitude (V)')
    chart_sci.add_legend()
    chart_sci.add_grid(alpha=0.5)
    chart_sci.save('examples/outputs/step8b_scientific_theme.png')

    # Custom styling
    chart_custom = plotxy.LineChart(width=800, height=600)
    chart_custom.set_background_color('#F8F9FA')
    chart_custom.plot(x, y, color='#E74C3C', linewidth=3, label='Custom style')
    chart_custom.set_title('Custom Styling Example',
                          fontsize=18, color='#2C3E50', fontweight='bold')
    chart_custom.set_labels('Time', 'Amplitude', fontsize=14, color='#34495E')
    chart_custom.add_legend(fancybox=True, shadow=True)
    chart_custom.add_grid(alpha=0.4, color='#BDC3C7')
    chart_custom.save('examples/outputs/step8c_custom_style.png')

    print("✓ Theme examples created!")
    print("  - Dark theme: step8a_dark_theme.png")
    print("  - Scientific theme: step8b_scientific_theme.png")
    print("  - Custom styling: step8c_custom_style.png\n")


def step_9_performance_tips():
    """Step 9: Performance optimization tips."""
    print("⚡ Step 9: Performance optimization")

    # Large dataset example
    print("  Creating large dataset visualization...")

    # Generate large dataset
    n_points = 10000
    x = np.linspace(0, 100, n_points)
    y = np.sin(x/5) + 0.1 * np.random.randn(n_points)

    # Optimized chart for large data
    chart = plotxy.LineChart(width=1000, height=600)

    # Enable performance optimizations
    chart.enable_data_sampling(max_points=5000)  # Downsample for display
    chart.enable_fast_rendering()                # Use fast rendering mode

    chart.plot(x, y, color='blue', linewidth=1, alpha=0.7)
    chart.set_title(f'Large Dataset Visualization ({n_points:,} points)')
    chart.set_labels('X Values', 'Y Values')
    chart.add_grid(alpha=0.3)

    # Add performance info
    chart.add_text(0.02, 0.98, f'Original: {n_points:,} points\nDisplayed: ~5,000 points',
                  transform='axes', fontsize=10, verticalalignment='top',
                  bbox={'boxstyle': 'round', 'facecolor': 'yellow', 'alpha': 0.8})

    chart.save('examples/outputs/step9_performance.png', dpi=300)

    print("✓ Performance example created! Check step9_performance.png")
    print("  This demonstrates handling large datasets efficiently\n")


def step_10_next_steps():
    """Step 10: What's next."""
    print("🚀 Step 10: What's next with PlotX")

    # Create a summary showcase
    fig = plotxy.Figure(figsize=(16, 10))

    # Multiple subplots showing different capabilities
    # Subplot 1: Basic line plot
    ax1 = fig.add_subplot(2, 3, 1)
    x = np.linspace(0, 2*np.pi, 50)
    ax1.plot(x, np.sin(x), 'b-', linewidth=2)
    ax1.set_title('Line Plots')
    ax1.grid(True, alpha=0.3)

    # Subplot 2: Scatter plot
    ax2 = fig.add_subplot(2, 3, 2)
    x = np.random.randn(100)
    y = np.random.randn(100)
    ax2.scatter(x, y, c=x+y, cmap='viridis', alpha=0.7)
    ax2.set_title('Scatter Plots')

    # Subplot 3: Bar chart
    ax3 = fig.add_subplot(2, 3, 3)
    categories = ['A', 'B', 'C', 'D']
    values = [23, 45, 56, 78]
    ax3.bar(categories, values, color='orange', alpha=0.8)
    ax3.set_title('Bar Charts')

    # Subplot 4: Histogram
    ax4 = fig.add_subplot(2, 3, 4)
    data = np.random.normal(0, 1, 1000)
    ax4.hist(data, bins=30, color='lightgreen', alpha=0.7)
    ax4.set_title('Histograms')

    # Subplot 5: Heatmap
    ax5 = fig.add_subplot(2, 3, 5)
    data = np.random.randn(10, 10)
    ax5.imshow(data, cmap='coolwarm', aspect='auto')
    ax5.set_title('Heatmaps')

    # Subplot 6: 3D surface (represented as contour)
    ax6 = fig.add_subplot(2, 3, 6)
    x = np.linspace(-2, 2, 20)
    y = np.linspace(-2, 2, 20)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y)
    ax6.contour(X, Y, Z, levels=10)
    ax6.set_title('3D & Contours')

    # Main title
    fig.suptitle('PlotX Capabilities Overview', fontsize=20, fontweight='bold')
    fig.tight_layout()
    fig.savefig('examples/outputs/step10_overview.png', dpi=300)

    # Create next steps guide
    next_steps_text = """
🎉 Congratulations! You've completed the PlotX Quick Start Guide!

📚 What you've learned:
  ✓ Creating basic charts
  ✓ Customizing appearance
  ✓ Multiple data series
  ✓ Different chart types
  ✓ 3D visualization
  ✓ Real-world examples
  ✓ Interactive features
  ✓ Themes and styling
  ✓ Performance optimization

🚀 Next steps:
  1. Explore advanced tutorials in docs/tutorials/
  2. Check out the examples gallery
  3. Learn about 3D interaction features
  4. Try financial chart analysis
  5. Build real-time dashboards
  6. Create interactive web visualizations

📖 Documentation:
  - API Reference: docs/api/
  - Tutorials: docs/tutorials/
  - Examples: examples/
  - 3D Features: docs/api/interaction3d.md

💡 Tips for success:
  - Start with simple charts and build complexity gradually
  - Use appropriate chart types for your data
  - Focus on clarity and readability
  - Leverage themes for consistent styling
  - Optimize for performance with large datasets

Happy visualizing with PlotX! 📊✨
"""

    with open('examples/outputs/step10_next_steps.txt', 'w') as f:
        f.write(next_steps_text.strip())

    print("✓ Overview showcase created! Check step10_overview.png")
    print("✓ Next steps guide saved: step10_next_steps.txt")
    print("\n🎉 Quick Start Guide Complete!")


def create_output_directory():
    """Ensure output directory exists."""
    output_dir = 'examples/outputs'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 Created output directory: {output_dir}")


def main():
    """Run the complete quick start guide."""
    print("🚀 PlotX Quick Start Guide")
    print("=" * 50)
    print("Welcome to PlotX! This guide will walk you through")
    print("the essential features step by step.\n")

    # Create output directory
    create_output_directory()

    try:
        # Run all steps
        step_1_hello_plotx()
        step_2_customization()
        step_3_multiple_series()
        step_4_different_chart_types()
        step_5_3d_visualization()
        step_6_real_world_example()
        step_7_interactive_features()
        step_8_themes_and_styling()
        step_9_performance_tips()
        step_10_next_steps()

        print("\n" + "=" * 50)
        print("🎉 Quick Start Guide Completed Successfully!")
        print("\nAll examples have been saved to examples/outputs/")
        print("\nYou're now ready to create amazing visualizations with PlotX!")
        print("Check out the advanced tutorials and API documentation for more features.")

    except Exception as e:
        print(f"\n❌ Quick start guide failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()