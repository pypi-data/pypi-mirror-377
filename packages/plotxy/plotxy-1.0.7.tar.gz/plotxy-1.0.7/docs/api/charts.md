# Chart API Reference

Complete API documentation for all PlotX chart types.

## Basic Charts

### LineChart

High-performance line chart for continuous data visualization.

```python
class LineChart:
    """Line chart with advanced styling and performance optimization."""

    def __init__(self, width: int = 800, height: int = 600):
        """Initialize line chart.

        Args:
            width: Chart width in pixels
            height: Chart height in pixels
        """

    def plot(self, x: np.ndarray, y: np.ndarray,
             color: str = 'blue', linewidth: float = 2.0,
             label: str = None, style: str = '-') -> None:
        """Plot line data.

        Args:
            x: X-axis data points
            y: Y-axis data points
            color: Line color ('red', 'blue', '#FF0000', etc.)
            linewidth: Line thickness in pixels
            label: Legend label
            style: Line style ('-', '--', ':', '-.')

        Example:
            >>> chart = LineChart()
            >>> x = np.linspace(0, 10, 100)
            >>> y = np.sin(x)
            >>> chart.plot(x, y, color='red', linewidth=3, label='Sine')
        """

    def set_title(self, title: str) -> None:
        """Set chart title."""

    def set_labels(self, xlabel: str = None, ylabel: str = None) -> None:
        """Set axis labels."""

    def set_limits(self, xlim: tuple = None, ylim: tuple = None) -> None:
        """Set axis limits."""

    def add_grid(self, visible: bool = True, alpha: float = 0.3) -> None:
        """Add/remove grid lines."""

    def add_legend(self, location: str = 'best') -> None:
        """Add legend to chart."""

    def save(self, filename: str, dpi: int = 300) -> None:
        """Save chart to file."""

    def show(self) -> None:
        """Display chart interactively."""
```

**Example Usage:**

```python
import plotx
import numpy as np

# Create data
t = np.linspace(0, 2*np.pi, 1000)
sine = np.sin(t)
cosine = np.cos(t)

# Create chart
chart = plotx.LineChart(width=1000, height=600)

# Add multiple lines
chart.plot(t, sine, color='blue', linewidth=2, label='sin(x)')
chart.plot(t, cosine, color='red', linewidth=2, label='cos(x)')

# Styling
chart.set_title('Trigonometric Functions')
chart.set_labels(xlabel='Angle (radians)', ylabel='Amplitude')
chart.add_grid(visible=True, alpha=0.3)
chart.add_legend(location='upper right')

# Export
chart.save('trigonometric.png', dpi=300)
chart.show()
```

### ScatterChart

Advanced scatter plot with color mapping and size scaling.

```python
class ScatterChart:
    """Scatter plot with color mapping and variable sizing."""

    def plot(self, x: np.ndarray, y: np.ndarray,
             c: np.ndarray = None, s: np.ndarray = None,
             marker: str = 'o', alpha: float = 0.7,
             cmap: str = 'viridis', label: str = None) -> None:
        """Create scatter plot.

        Args:
            x: X-axis data
            y: Y-axis data
            c: Color values for each point
            s: Size values for each point
            marker: Marker style ('o', 's', '^', 'v', etc.)
            alpha: Transparency (0.0 to 1.0)
            cmap: Colormap name
            label: Legend label

        Example:
            >>> chart = ScatterChart()
            >>> x = np.random.randn(500)
            >>> y = np.random.randn(500)
            >>> colors = np.random.rand(500)
            >>> sizes = np.random.rand(500) * 100
            >>> chart.plot(x, y, c=colors, s=sizes, alpha=0.6)
        """

    def add_colorbar(self, label: str = None) -> None:
        """Add colorbar to chart."""

    def set_marker_style(self, marker: str, size: float = None) -> None:
        """Set default marker properties."""
```

**Example Usage:**

```python
import plotx
import numpy as np

# Generate sample data
np.random.seed(42)
n_points = 1000

x = np.random.normal(0, 1, n_points)
y = np.random.normal(0, 1, n_points)
colors = np.sqrt(x**2 + y**2)  # Distance from origin
sizes = np.random.uniform(10, 100, n_points)

# Create scatter plot
chart = plotx.ScatterChart()
chart.plot(x, y, c=colors, s=sizes, marker='o', alpha=0.6, cmap='plasma')

# Styling
chart.set_title('Random Scatter with Color and Size Mapping')
chart.set_labels(xlabel='X Values', ylabel='Y Values')
chart.add_colorbar(label='Distance from Origin')

chart.save('advanced_scatter.png')
```

### BarChart

Professional bar charts with multiple series support.

```python
class BarChart:
    """Bar chart with multiple series and styling options."""

    def bar(self, x: np.ndarray, height: np.ndarray,
            width: float = 0.8, color: str = None,
            label: str = None, alpha: float = 1.0) -> None:
        """Create bar chart.

        Args:
            x: X-axis positions
            height: Bar heights
            width: Bar width (0.0 to 1.0)
            color: Bar color
            label: Legend label
            alpha: Transparency
        """

    def barh(self, y: np.ndarray, width: np.ndarray, **kwargs) -> None:
        """Create horizontal bar chart."""

    def grouped_bar(self, categories: list, data: dict, **kwargs) -> None:
        """Create grouped bar chart."""

    def stacked_bar(self, categories: list, data: dict, **kwargs) -> None:
        """Create stacked bar chart."""
```

**Example Usage:**

```python
# Simple bar chart
categories = ['A', 'B', 'C', 'D', 'E']
values = [23, 45, 56, 78, 32]

chart = plotx.BarChart()
chart.bar(categories, values, color='steelblue', alpha=0.8)
chart.set_title('Sample Data')
chart.save('simple_bars.png')

# Grouped bar chart
categories = ['Q1', 'Q2', 'Q3', 'Q4']
data = {
    'Product A': [20, 35, 30, 35],
    'Product B': [25, 30, 15, 30],
    'Product C': [15, 20, 35, 20]
}

chart = plotx.BarChart()
chart.grouped_bar(categories, data)
chart.set_title('Quarterly Sales by Product')
chart.add_legend()
chart.save('grouped_bars.png')
```

### SurfaceChart

3D surface visualization with interactive capabilities.

```python
class SurfaceChart:
    """3D surface plot with interaction support."""

    def plot_surface(self, X: np.ndarray, Y: np.ndarray, Z: np.ndarray,
                    cmap: str = 'viridis', alpha: float = 1.0,
                    lighting: bool = True) -> None:
        """Plot 3D surface.

        Args:
            X: X-coordinate mesh
            Y: Y-coordinate mesh
            Z: Z-coordinate values
            cmap: Colormap
            alpha: Surface transparency
            lighting: Enable surface lighting
        """

    def plot_wireframe(self, X: np.ndarray, Y: np.ndarray, Z: np.ndarray,
                      color: str = 'black', linewidth: float = 1.0) -> None:
        """Plot wireframe surface."""

    def contour(self, X: np.ndarray, Y: np.ndarray, Z: np.ndarray,
               levels: int = 10, cmap: str = 'viridis') -> None:
        """Add contour lines."""
```

**Example Usage:**

```python
# Create 3D surface
x = np.linspace(-5, 5, 50)
y = np.linspace(-5, 5, 50)
X, Y = np.meshgrid(x, y)
Z = np.sin(np.sqrt(X**2 + Y**2))

chart = plotx.SurfaceChart()
chart.plot_surface(X, Y, Z, cmap='coolwarm', alpha=0.8)
chart.set_title('3D Surface: sin(sqrt(x² + y²))')
chart.save('3d_surface.png')
```

## Advanced Charts

### HeatmapChart

Correlation matrices and 2D data visualization.

```python
class HeatmapChart:
    """Heatmap for correlation matrices and 2D data."""

    def heatmap(self, data: np.ndarray,
                xticklabels: list = None, yticklabels: list = None,
                cmap: str = 'viridis', annot: bool = False,
                fmt: str = '.2f', cbar: bool = True) -> None:
        """Create heatmap.

        Args:
            data: 2D array of values
            xticklabels: X-axis labels
            yticklabels: Y-axis labels
            cmap: Colormap
            annot: Show values in cells
            fmt: Number format for annotations
            cbar: Show colorbar
        """
```

**Example Usage:**

```python
# Correlation matrix
import pandas as pd

# Sample data
data = np.random.randn(10, 12)
corr_matrix = np.corrcoef(data)

chart = plotx.HeatmapChart()
chart.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='RdBu_r')
chart.set_title('Correlation Matrix')
chart.save('correlation_heatmap.png')
```

### RadarChart

Multi-dimensional data visualization.

```python
class RadarChart:
    """Radar (spider) chart for multi-dimensional data."""

    def plot(self, categories: list, values: list,
             label: str = None, color: str = None,
             fill: bool = True, alpha: float = 0.3) -> None:
        """Plot radar chart.

        Args:
            categories: Category names
            values: Values for each category
            label: Data series label
            color: Line/fill color
            fill: Fill the area
            alpha: Fill transparency
        """
```

**Example Usage:**

```python
# Skills radar chart
categories = ['Python', 'JavaScript', 'SQL', 'Machine Learning',
              'Data Viz', 'Statistics']
developer_a = [9, 7, 8, 6, 9, 7]
developer_b = [7, 9, 6, 8, 7, 8]

chart = plotx.RadarChart()
chart.plot(categories, developer_a, label='Developer A', color='blue')
chart.plot(categories, developer_b, label='Developer B', color='red')
chart.set_title('Developer Skills Comparison')
chart.add_legend()
chart.save('skills_radar.png')
```

## Financial Charts

### CandlestickChart

Professional OHLC financial visualization.

```python
class CandlestickChart:
    """Candlestick chart for financial OHLC data."""

    def plot(self, dates: np.ndarray,
             open_prices: np.ndarray, high_prices: np.ndarray,
             low_prices: np.ndarray, close_prices: np.ndarray,
             volume: np.ndarray = None) -> None:
        """Plot candlestick chart.

        Args:
            dates: Date/time array
            open_prices: Opening prices
            high_prices: High prices
            low_prices: Low prices
            close_prices: Closing prices
            volume: Trading volume (optional)
        """

    def add_moving_average(self, window: int, color: str = 'blue') -> None:
        """Add moving average line."""

    def add_bollinger_bands(self, window: int = 20, num_std: float = 2) -> None:
        """Add Bollinger Bands."""

    def add_volume_bars(self, alpha: float = 0.3) -> None:
        """Add volume bars below chart."""
```

**Example Usage:**

```python
# Financial data
dates = pd.date_range('2023-01-01', periods=100, freq='D')
prices = 100 + np.cumsum(np.random.randn(100) * 0.5)

# OHLC data simulation
opens = prices + np.random.randn(100) * 0.2
highs = np.maximum(opens, prices) + np.random.rand(100) * 0.5
lows = np.minimum(opens, prices) - np.random.rand(100) * 0.5
closes = prices
volume = np.random.randint(1000000, 5000000, 100)

chart = plotx.CandlestickChart()
chart.plot(dates, opens, highs, lows, closes, volume)
chart.add_moving_average(window=20, color='blue')
chart.add_bollinger_bands(window=20, num_std=2)
chart.set_title('Stock Price Analysis')
chart.save('candlestick_analysis.png')
```

### RSIChart

Relative Strength Index technical indicator.

```python
class RSIChart:
    """RSI (Relative Strength Index) technical indicator."""

    def plot(self, prices: np.ndarray, window: int = 14) -> None:
        """Plot RSI indicator.

        Args:
            prices: Price data
            window: RSI calculation window
        """

    def add_overbought_line(self, level: float = 70) -> None:
        """Add overbought threshold line."""

    def add_oversold_line(self, level: float = 30) -> None:
        """Add oversold threshold line."""
```

### MACDChart

MACD (Moving Average Convergence Divergence) indicator.

```python
class MACDChart:
    """MACD technical indicator with histogram."""

    def plot(self, prices: np.ndarray,
             fast_period: int = 12, slow_period: int = 26,
             signal_period: int = 9) -> None:
        """Plot MACD indicator."""
```

## Chart Styling and Themes

### Themes

```python
# Available themes
THEMES = {
    'default': DefaultTheme(),
    'dark': DarkTheme(),
    'minimal': MinimalTheme(),
    'scientific': ScientificTheme(),
    'financial': FinancialTheme(),
    'presentation': PresentationTheme()
}

# Apply theme
plotx.set_theme('dark')

# Create custom theme
custom_theme = plotx.Theme(
    background_color='#f8f9fa',
    grid_color='#dee2e6',
    text_color='#212529',
    accent_colors=['#007bff', '#28a745', '#dc3545']
)
plotx.set_theme(custom_theme)
```

### Color Management

```python
# Color utilities
colors = plotx.Colors()

# Predefined palettes
colors.set_palette('viridis')
colors.set_palette('plasma')
colors.set_palette('coolwarm')

# Custom colors
colors.define_color('company_blue', '#1f77b4')
colors.create_gradient('sunset', ['#ff7f0e', '#d62728', '#9467bd'])
```

## Performance Optimization

### Large Datasets

```python
# Enable GPU acceleration
chart = plotx.LineChart(backend='gpu')

# Data sampling for large datasets
chart.enable_data_sampling(max_points=10000)

# Level-of-detail rendering
chart.enable_lod(distance_threshold=0.1)

# Streaming data
chart.enable_streaming_mode(buffer_size=1000)
```

### Memory Management

```python
# Memory-efficient plotting
with plotx.memory_managed():
    chart = plotx.ScatterChart()
    chart.plot(large_x_data, large_y_data)
    chart.save('large_scatter.png')
# Memory automatically freed

# Manual memory management
chart.clear_cache()
chart.optimize_memory()
```

## Integration Examples

### Jupyter Notebooks

```python
# Enable inline plotting
%matplotlib inline
import plotx
plotx.enable_notebook_mode()

# Interactive widgets
chart = plotx.LineChart()
chart.show_interactive()  # Creates interactive widget
```

### Web Applications

```python
# Flask integration
from flask import Flask
import plotx

app = Flask(__name__)

@app.route('/chart.png')
def generate_chart():
    chart = plotx.LineChart()
    # ... create chart ...
    return chart.to_response(format='png')
```

### Real-time Applications

```python
# Real-time data streaming
stream = plotx.DataStream()
chart = plotx.LineChart()

@stream.on_data
def update_chart(new_data):
    chart.append_data(new_data)
    chart.refresh()

stream.start()
```

---

This API reference covers all major chart types and features. For complete examples and tutorials, see the [Examples Gallery](../examples/gallery.md).