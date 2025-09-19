#!/usr/bin/env python3
"""
Basic Chart Examples for PlotX
Demonstrates fundamental chart types and usage patterns.
"""

import numpy as np
import sys
import os

# Add src to path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import plotxy
from plotxy.rendering.export import pyplot


def line_chart_example():
    """Create a basic line chart."""
    print("📈 Creating line chart example...")

    # Generate sample data
    x = np.linspace(0, 4*np.pi, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)
    y3 = np.sin(x + np.pi/4)

    # Create chart
    chart = plotxy.LineChart(width=1000, height=600)

    # Add multiple data series
    chart.plot(x, y1, color='blue', linewidth=2, label='sin(x)')
    chart.plot(x, y2, color='red', linewidth=2, label='cos(x)')
    chart.plot(x, y3, color='green', linewidth=2, label='sin(x + π/4)')

    # Styling
    chart.set_title('Trigonometric Functions')
    chart.set_labels(xlabel='Angle (radians)', ylabel='Amplitude')
    chart.add_grid(visible=True, alpha=0.3)
    chart.add_legend(location='upper right')

    # Save
    chart.save('examples/outputs/line_chart_basic.png', dpi=300)
    print("✓ Line chart saved: examples/outputs/line_chart_basic.png")


def scatter_plot_example():
    """Create a scatter plot with color mapping."""
    print("📊 Creating scatter plot example...")

    # Generate random data
    np.random.seed(42)
    n_points = 500

    # Create clusters
    cluster1 = np.random.multivariate_normal([2, 2], [[1, 0.5], [0.5, 1]], n_points//3)
    cluster2 = np.random.multivariate_normal([-2, -1], [[1.5, -0.3], [-0.3, 0.8]], n_points//3)
    cluster3 = np.random.multivariate_normal([0, -2], [[0.8, 0], [0, 1.2]], n_points//3)

    # Combine data
    x = np.concatenate([cluster1[:, 0], cluster2[:, 0], cluster3[:, 0]])
    y = np.concatenate([cluster1[:, 1], cluster2[:, 1], cluster3[:, 1]])

    # Color by distance from origin
    colors = np.sqrt(x**2 + y**2)
    sizes = np.random.uniform(20, 100, len(x))

    # Create chart
    chart = plotxy.ScatterChart(width=800, height=800)
    chart.plot(x, y, c=colors, s=sizes, alpha=0.6, cmap='viridis')

    # Styling
    chart.set_title('Clustered Data Visualization')
    chart.set_labels('X Coordinate', 'Y Coordinate')
    chart.add_colorbar(label='Distance from Origin')
    chart.add_grid(alpha=0.3)

    # Save
    chart.save('examples/outputs/scatter_plot_clusters.png', dpi=300)
    print("✓ Scatter plot saved: examples/outputs/scatter_plot_clusters.png")


def bar_chart_example():
    """Create bar charts with different styles."""
    print("📊 Creating bar chart examples...")

    # Simple bar chart
    categories = ['Product A', 'Product B', 'Product C', 'Product D', 'Product E']
    values = [23, 45, 56, 78, 32]

    chart = plotxy.BarChart(width=800, height=600)
    chart.bar(categories, values, color='steelblue', alpha=0.8)
    chart.set_title('Product Sales Comparison')
    chart.set_labels('Products', 'Sales (units)')
    chart.add_grid(axis='y', alpha=0.3)

    chart.save('examples/outputs/bar_chart_simple.png', dpi=300)
    print("✓ Simple bar chart saved: examples/outputs/bar_chart_simple.png")

    # Grouped bar chart
    quarters = ['Q1', 'Q2', 'Q3', 'Q4']
    data = {
        'Product A': [20, 35, 30, 35],
        'Product B': [25, 30, 15, 30],
        'Product C': [15, 20, 35, 20]
    }

    grouped_chart = plotxy.BarChart(width=1000, height=600)
    grouped_chart.grouped_bar(quarters, data)
    grouped_chart.set_title('Quarterly Sales by Product')
    grouped_chart.set_labels('Quarter', 'Sales (K units)')
    grouped_chart.add_legend()
    grouped_chart.add_grid(axis='y', alpha=0.3)

    grouped_chart.save('examples/outputs/bar_chart_grouped.png', dpi=300)
    print("✓ Grouped bar chart saved: examples/outputs/bar_chart_grouped.png")


def surface_plot_example():
    """Create a 3D surface plot."""
    print("🌄 Creating 3D surface plot example...")

    # Generate 3D data
    x = np.linspace(-3, 3, 50)
    y = np.linspace(-3, 3, 50)
    X, Y = np.meshgrid(x, y)

    # Mathematical surface: Peaks function
    Z = 3 * (1 - X)**2 * np.exp(-(X**2) - (Y + 1)**2) \
        - 10 * (X/5 - X**3 - Y**5) * np.exp(-X**2 - Y**2) \
        - 1/3 * np.exp(-(X + 1)**2 - Y**2)

    # Create surface chart
    chart = plotxy.SurfaceChart(width=1000, height=800)
    chart.plot_surface(X, Y, Z, cmap='viridis', alpha=0.9, lighting=True)

    # Add contour lines
    chart.contour(X, Y, Z, levels=10, cmap='hot', alpha=0.6)

    # Styling
    chart.set_title('3D Peaks Function')
    chart.set_labels('X', 'Y', 'Z')

    # Save
    chart.save('examples/outputs/surface_plot_peaks.png', dpi=300)
    print("✓ Surface plot saved: examples/outputs/surface_plot_peaks.png")


def heatmap_example():
    """Create correlation heatmap."""
    print("🔥 Creating heatmap example...")

    # Generate correlated data
    np.random.seed(123)
    variables = ['Temperature', 'Humidity', 'Pressure', 'Wind Speed', 'Visibility']
    n_samples = 100

    # Create correlated data
    data = np.random.randn(n_samples, len(variables))
    data[:, 1] = -0.7 * data[:, 0] + 0.5 * np.random.randn(n_samples)  # Humidity vs Temp
    data[:, 2] = 0.6 * data[:, 0] + 0.3 * data[:, 1] + 0.5 * np.random.randn(n_samples)  # Pressure

    # Calculate correlation matrix
    correlation_matrix = np.corrcoef(data.T)

    # Create heatmap
    chart = plotxy.HeatmapChart(width=700, height=700)
    chart.heatmap(correlation_matrix,
                  xticklabels=variables,
                  yticklabels=variables,
                  annot=True, fmt='.2f',
                  cmap='RdBu_r', center=0)

    chart.set_title('Weather Variables Correlation Matrix')

    # Save
    chart.save('examples/outputs/heatmap_correlation.png', dpi=300)
    print("✓ Heatmap saved: examples/outputs/heatmap_correlation.png")


def radar_chart_example():
    """Create radar chart for multi-dimensional comparison."""
    print("🕸️ Creating radar chart example...")

    # Performance metrics
    categories = ['Speed', 'Reliability', 'Security', 'Usability', 'Scalability', 'Cost']

    # Product comparisons
    product_a = [8, 9, 7, 8, 6, 5]  # Strong in reliability, weak in cost
    product_b = [6, 7, 9, 6, 8, 8]  # Strong in security and scalability
    product_c = [9, 6, 6, 9, 7, 9]  # Fast and user-friendly, affordable

    # Create radar chart
    chart = plotxy.RadarChart(width=800, height=800)

    chart.plot(categories, product_a, label='Product A', color='blue', fill=True, alpha=0.3)
    chart.plot(categories, product_b, label='Product B', color='red', fill=True, alpha=0.3)
    chart.plot(categories, product_c, label='Product C', color='green', fill=True, alpha=0.3)

    chart.set_title('Product Performance Comparison')
    chart.add_legend()

    # Save
    chart.save('examples/outputs/radar_chart_products.png', dpi=300)
    print("✓ Radar chart saved: examples/outputs/radar_chart_products.png")


def pyplot_interface_example():
    """Demonstrate matplotlib-like pyplot interface."""
    print("🎭 Creating pyplot interface example...")

    # Get pyplot interface
    plt = pyplot()

    # Create figure
    plt.figure(figsize=(10, 6))

    # Generate data
    t = np.linspace(0, 2*np.pi, 100)
    signal = np.sin(3*t) * np.exp(-t/3)
    noise = 0.1 * np.random.randn(100)
    noisy_signal = signal + noise

    # Plot data
    plt.plot(t, signal, color='blue', linewidth=2, label='Clean Signal')
    plt.plot(t, noisy_signal, color='red', alpha=0.7, label='Noisy Signal')

    # Styling
    plt.title('Signal Processing Example')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.grid(True)
    plt.legend()

    # Save
    plt.savefig('examples/outputs/pyplot_interface.png', dpi=300)
    print("✓ Pyplot interface example saved: examples/outputs/pyplot_interface.png")


def statistical_plots_example():
    """Create statistical visualization examples."""
    print("📊 Creating statistical plots...")

    # Histogram with normal distribution fit
    np.random.seed(42)
    data = np.random.normal(100, 15, 1000)

    hist_chart = plotxy.HistogramChart(width=800, height=600)
    hist_chart.hist(data, bins=50, alpha=0.7, color='skyblue', density=True)

    # Add normal distribution curve
    x_fit = np.linspace(data.min(), data.max(), 100)
    y_fit = (1/(15*np.sqrt(2*np.pi))) * np.exp(-0.5*((x_fit-100)/15)**2)
    hist_chart.plot(x_fit, y_fit, color='red', linewidth=2, label='Normal Distribution')

    hist_chart.set_title('Sample Distribution with Normal Fit')
    hist_chart.set_labels('Value', 'Density')
    hist_chart.add_legend()
    hist_chart.add_grid(alpha=0.3)

    hist_chart.save('examples/outputs/histogram_normal_fit.png', dpi=300)
    print("✓ Histogram saved: examples/outputs/histogram_normal_fit.png")

    # Box plot for comparing distributions
    groups = ['Group A', 'Group B', 'Group C', 'Group D']
    group_data = [
        np.random.normal(100, 10, 100),
        np.random.normal(110, 15, 100),
        np.random.normal(95, 8, 100),
        np.random.normal(105, 12, 100)
    ]

    box_chart = plotxy.BoxChart(width=800, height=600)
    box_chart.boxplot(group_data, labels=groups)
    box_chart.set_title('Distribution Comparison Across Groups')
    box_chart.set_labels('Groups', 'Values')
    box_chart.add_grid(axis='y', alpha=0.3)

    box_chart.save('examples/outputs/box_plot_comparison.png', dpi=300)
    print("✓ Box plot saved: examples/outputs/box_plot_comparison.png")


def real_world_example():
    """Create a real-world data analysis example."""
    print("🌍 Creating real-world analysis example...")

    # Simulate monthly sales data for a year
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    # Different product lines
    products = {
        'Electronics': [120, 115, 130, 125, 140, 160, 180, 175, 155, 145, 200, 220],
        'Clothing': [80, 85, 95, 110, 115, 90, 85, 88, 105, 120, 140, 160],
        'Home & Garden': [60, 65, 85, 95, 110, 125, 130, 120, 100, 85, 70, 75],
        'Sports': [70, 75, 90, 100, 120, 140, 150, 145, 130, 110, 95, 85]
    }

    # Create multi-panel dashboard
    fig = plotxy.Figure(figsize=(16, 12))

    # Panel 1: Line chart showing trends
    ax1 = fig.add_subplot(2, 2, 1)
    colors = ['blue', 'red', 'green', 'orange']
    for i, (product, sales) in enumerate(products.items()):
        ax1.plot(months, sales, color=colors[i], linewidth=2, marker='o', label=product)

    ax1.set_title('Monthly Sales Trends by Product Category')
    ax1.set_xlabel('Month')
    ax1.set_ylabel('Sales (K units)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Panel 2: Total sales bar chart
    ax2 = fig.add_subplot(2, 2, 2)
    total_sales = [sum(products[p][i] for p in products) for i in range(12)]
    ax2.bar(months, total_sales, color='purple', alpha=0.7)
    ax2.set_title('Total Monthly Sales')
    ax2.set_xlabel('Month')
    ax2.set_ylabel('Total Sales (K units)')
    ax2.grid(True, alpha=0.3, axis='y')

    # Panel 3: Product share pie chart
    ax3 = fig.add_subplot(2, 2, 3)
    annual_totals = [sum(sales) for sales in products.values()]
    ax3.pie(annual_totals, labels=list(products.keys()), autopct='%1.1f%%',
            colors=colors, startangle=90)
    ax3.set_title('Annual Sales Share by Product')

    # Panel 4: Growth rate analysis
    ax4 = fig.add_subplot(2, 2, 4)
    for i, (product, sales) in enumerate(products.items()):
        growth_rates = [(sales[j+1] - sales[j])/sales[j]*100 for j in range(11)]
        ax4.plot(months[1:], growth_rates, color=colors[i], linewidth=2,
                marker='s', label=product)

    ax4.set_title('Month-over-Month Growth Rates')
    ax4.set_xlabel('Month')
    ax4.set_ylabel('Growth Rate (%)')
    ax4.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    # Save complete dashboard
    fig.suptitle('Sales Analysis Dashboard - 2023', fontsize=16, fontweight='bold')
    fig.tight_layout()
    fig.savefig('examples/outputs/dashboard_sales_analysis.png', dpi=300)
    print("✓ Sales dashboard saved: examples/outputs/dashboard_sales_analysis.png")


def create_output_directory():
    """Ensure output directory exists."""
    output_dir = 'examples/outputs'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 Created output directory: {output_dir}")


def main():
    """Run all basic chart examples."""
    print("🎨 PlotX Basic Charts Examples")
    print("=" * 50)

    # Create output directory
    create_output_directory()

    try:
        # Run all examples
        line_chart_example()
        scatter_plot_example()
        bar_chart_example()
        surface_plot_example()
        heatmap_example()
        radar_chart_example()
        pyplot_interface_example()
        statistical_plots_example()
        real_world_example()

        print("\n🎉 All examples completed successfully!")
        print("\nGenerated files:")
        print("  📈 examples/outputs/line_chart_basic.png")
        print("  📊 examples/outputs/scatter_plot_clusters.png")
        print("  📊 examples/outputs/bar_chart_simple.png")
        print("  📊 examples/outputs/bar_chart_grouped.png")
        print("  🌄 examples/outputs/surface_plot_peaks.png")
        print("  🔥 examples/outputs/heatmap_correlation.png")
        print("  🕸️ examples/outputs/radar_chart_products.png")
        print("  🎭 examples/outputs/pyplot_interface.png")
        print("  📊 examples/outputs/histogram_normal_fit.png")
        print("  📊 examples/outputs/box_plot_comparison.png")
        print("  🌍 examples/outputs/dashboard_sales_analysis.png")

        print(f"\n✅ Basic charts demonstration complete!")
        print(f"🎯 Ready for production use!")

    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()