# Basic Usage Tutorial

A complete guide to getting started with PlotX visualization.

## Installation

PlotX requires only Python 3.7+ and NumPy:

```bash
pip install numpy
```

Then clone and install PlotX:

```bash
git clone https://github.com/your-repo/plotx.git
cd plotx
pip install -e .
```

## Your First Chart

Let's create a simple line chart:

```python
import plotx
import numpy as np

# Create data
x = np.linspace(0, 2*np.pi, 100)
y = np.sin(x)

# Create and customize chart
chart = plotx.LineChart()
chart.plot(x, y, color='blue', linewidth=2, label='sin(x)')
chart.set_title('My First PlotX Chart')
chart.set_labels(xlabel='Angle (radians)', ylabel='Amplitude')
chart.add_grid(visible=True)
chart.add_legend()

# Save or display
chart.save('first_chart.png', dpi=300)
chart.show()
```

## Basic Chart Types

### Line Charts

Perfect for continuous data and time series:

```python
import plotx
import numpy as np

# Time series data
t = np.linspace(0, 10, 1000)
signal1 = np.sin(2*np.pi*t)
signal2 = np.cos(2*np.pi*t) * np.exp(-t/5)

chart = plotx.LineChart(width=1000, height=600)
chart.plot(t, signal1, color='blue', linewidth=2, label='Sine wave')
chart.plot(t, signal2, color='red', linewidth=2, label='Damped cosine')

chart.set_title('Signal Analysis')
chart.set_labels('Time (s)', 'Amplitude')
chart.add_grid(alpha=0.3)
chart.add_legend()
chart.save('signals.png')
```

### Scatter Plots

Ideal for correlation analysis:

```python
# Generate correlated data
np.random.seed(42)
n = 200
x = np.random.normal(0, 1, n)
y = x + 0.5 * np.random.normal(0, 1, n)
colors = x + y  # Color by sum

chart = plotx.ScatterChart()
chart.plot(x, y, c=colors, s=50, alpha=0.7, cmap='viridis')
chart.set_title('Correlation Analysis')
chart.set_labels('Variable X', 'Variable Y')
chart.add_colorbar(label='X + Y')
chart.save('correlation.png')
```

### Bar Charts

Great for categorical data:

```python
# Sales data
categories = ['Q1', 'Q2', 'Q3', 'Q4']
values = [23500, 35200, 28100, 42300]

chart = plotx.BarChart()
chart.bar(categories, values, color='steelblue', alpha=0.8)
chart.set_title('Quarterly Sales')
chart.set_labels('Quarter', 'Sales ($)')
chart.save('sales.png')
```

## Styling and Themes

### Applying Themes

```python
# Set global theme
plotx.set_theme('dark')

# Or use specific theme for one chart
chart = plotx.LineChart()
chart.apply_theme(plotx.themes.scientific)
```

### Custom Colors

```python
# Custom color palette
colors = plotx.Colors()
colors.set_palette(['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])

chart = plotx.LineChart()
# Colors will automatically cycle through palette
```

### Professional Styling

```python
chart = plotx.LineChart(width=1200, height=800)

# Data
x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)

# Plot with professional styling
chart.plot(x, y1, color='#2E86AB', linewidth=3, label='sin(x)')
chart.plot(x, y2, color='#A23B72', linewidth=3, label='cos(x)')

# Professional formatting
chart.set_title('Trigonometric Functions', fontsize=16, fontweight='bold')
chart.set_labels('X Values', 'Y Values', fontsize=14)
chart.add_grid(visible=True, alpha=0.3, linestyle='--')
chart.add_legend(location='upper right', fontsize=12)

# High-quality export
chart.save('professional_chart.png', dpi=300)
```

## Working with Real Data

### CSV Data

```python
import pandas as pd  # Optional for data loading
import plotx

# Load data (or use NumPy arrays)
# data = pd.read_csv('sales_data.csv')
# x, y = data['month'].values, data['sales'].values

# Example with synthetic data
months = np.arange(1, 13)
sales = np.array([12, 15, 18, 22, 25, 28, 32, 30, 27, 24, 20, 16]) * 1000

chart = plotx.LineChart()
chart.plot(months, sales, color='green', linewidth=3, marker='o')
chart.set_title('Monthly Sales Trends')
chart.set_labels('Month', 'Sales ($)')
chart.set_limits(xlim=(1, 12), ylim=(10000, 35000))
chart.add_grid()
chart.save('monthly_sales.png')
```

### Multiple Data Series

```python
# Compare different products
months = np.arange(1, 13)
product_a = np.array([12, 15, 18, 22, 25, 28, 32, 30, 27, 24, 20, 16]) * 1000
product_b = np.array([8, 12, 16, 20, 23, 26, 29, 31, 28, 25, 22, 18]) * 1000
product_c = np.array([5, 8, 11, 15, 18, 21, 25, 27, 24, 21, 18, 15]) * 1000

chart = plotx.LineChart()
chart.plot(months, product_a, color='blue', linewidth=2, label='Product A')
chart.plot(months, product_b, color='red', linewidth=2, label='Product B')
chart.plot(months, product_c, color='green', linewidth=2, label='Product C')

chart.set_title('Product Sales Comparison')
chart.set_labels('Month', 'Sales ($)')
chart.add_legend()
chart.add_grid()
chart.save('product_comparison.png')
```

## Interactive Features

### Basic Interactivity

```python
chart = plotx.LineChart()
chart.plot(x, y, color='blue')

# Enable interactive mode
chart.show_interactive()  # Opens interactive window
```

### Web Integration

```python
# Create chart for web
chart = plotx.LineChart()
chart.plot(x, y, color='blue')

# Export for web
chart.save_html('interactive_chart.html')
```

## Performance Tips

### Large Datasets

```python
# For datasets with >10,000 points
chart = plotx.LineChart()

# Enable data sampling
chart.enable_data_sampling(max_points=5000)

# Or use GPU acceleration
chart = plotx.LineChart(backend='gpu')
```

### Memory Management

```python
# For multiple charts
with plotx.memory_managed():
    for i in range(100):
        chart = plotx.ScatterChart()
        chart.plot(data_x[i], data_y[i])
        chart.save(f'chart_{i}.png')
# Memory automatically freed
```

## Exporting Charts

### High-Quality Images

```python
# Publication quality
chart.save('figure.png', dpi=300)     # High resolution PNG
chart.save('figure.svg')             # Vector graphics
chart.save('figure.pdf')             # PDF for publications
```

### Different Formats

```python
# Multiple formats
formats = ['png', 'svg', 'pdf']
for fmt in formats:
    chart.save(f'chart.{fmt}')
```

## Common Patterns

### Dashboard Layout

```python
# Create multiple charts for dashboard
charts = []

# Chart 1: Line plot
chart1 = plotx.LineChart()
chart1.plot(time_data, values1, color='blue')
chart1.set_title('Metric 1')
charts.append(chart1)

# Chart 2: Bar chart
chart2 = plotx.BarChart()
chart2.bar(categories, values2, color='green')
chart2.set_title('Metric 2')
charts.append(chart2)

# Save all charts
for i, chart in enumerate(charts):
    chart.save(f'dashboard_chart_{i}.png')
```

### Animated Sequences

```python
# Create animation frames
for frame in range(100):
    x = np.linspace(0, 2*np.pi, 100)
    y = np.sin(x + frame * 0.1)

    chart = plotx.LineChart()
    chart.plot(x, y, color='blue')
    chart.set_title(f'Animation Frame {frame}')
    chart.set_limits(ylim=(-1.2, 1.2))
    chart.save(f'frame_{frame:03d}.png')

# Combine frames into animation (external tool)
# ffmpeg -r 30 -i frame_%03d.png -c:v libx264 animation.mp4
```

## Next Steps

- Explore [3D Visualization Tutorial](3d-visualization.md)
- Learn about [Financial Charts](financial-charts.md)
- Check out [Advanced Features](advanced-features.md)
- Browse the [Examples Gallery](../examples/gallery.md)

---

Ready to create more advanced visualizations? Continue with our specialized tutorials!