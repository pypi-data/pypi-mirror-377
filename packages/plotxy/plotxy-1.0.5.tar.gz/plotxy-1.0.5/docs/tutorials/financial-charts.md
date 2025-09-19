# Financial Charts Tutorial

Complete guide to creating professional financial visualizations with technical analysis.

## Stock Price Visualization

### Basic Candlestick Chart

```python
import plotx
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Generate sample OHLC data
def generate_stock_data(days=100, start_price=100):
    dates = pd.date_range(start='2023-01-01', periods=days, freq='D')

    # Random walk for price simulation
    returns = np.random.normal(0.001, 0.02, days)
    prices = start_price * np.exp(np.cumsum(returns))

    # Generate OHLC from prices
    opens = prices * (1 + np.random.normal(0, 0.005, days))
    highs = np.maximum(opens, prices) * (1 + np.random.uniform(0, 0.01, days))
    lows = np.minimum(opens, prices) * (1 - np.random.uniform(0, 0.01, days))
    closes = prices

    # Trading volume
    volume = np.random.randint(1000000, 10000000, days)

    return dates, opens, highs, lows, closes, volume

# Create sample data
dates, opens, highs, lows, closes, volume = generate_stock_data(100, 150)

# Create candlestick chart
chart = plotx.CandlestickChart(width=1200, height=800)
chart.plot(dates, opens, highs, lows, closes, volume)

# Styling
chart.set_title('AAPL Stock Price Analysis', fontsize=16)
chart.set_labels('Date', 'Price ($)')
chart.add_volume_bars(alpha=0.3)

# Save high-quality chart
chart.save('candlestick_basic.png', dpi=300)
```

### Advanced Candlestick with Indicators

```python
# Advanced candlestick with technical indicators
chart = plotx.CandlestickChart(width=1400, height=900)

# Plot OHLC data
chart.plot(dates, opens, highs, lows, closes, volume)

# Add moving averages
chart.add_moving_average(window=20, color='blue', label='SMA 20')
chart.add_moving_average(window=50, color='orange', label='SMA 50')

# Add Bollinger Bands
chart.add_bollinger_bands(window=20, num_std=2, alpha=0.2)

# Add volume analysis
chart.add_volume_bars(alpha=0.4)
chart.add_volume_sma(window=20, color='purple')

# Professional styling
chart.set_title('Advanced Technical Analysis', fontsize=18, fontweight='bold')
chart.set_theme('financial')  # Use financial theme
chart.add_legend(location='upper left')
chart.add_grid(alpha=0.3)

chart.save('candlestick_advanced.png', dpi=300)
```

## Technical Indicators

### RSI (Relative Strength Index)

```python
# RSI implementation and visualization
class RSICalculator:
    @staticmethod
    def calculate_rsi(prices, window=14):
        """Calculate RSI indicator."""
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)

        avg_gains = np.convolve(gains, np.ones(window)/window, mode='valid')
        avg_losses = np.convolve(losses, np.ones(window)/window, mode='valid')

        rs = avg_gains / (avg_losses + 1e-10)  # Avoid division by zero
        rsi = 100 - (100 / (1 + rs))

        return rsi

# Calculate RSI
rsi_values = RSICalculator.calculate_rsi(closes, window=14)
rsi_dates = dates[14:]  # Skip first 14 values

# Create RSI chart
rsi_chart = plotx.RSIChart(width=1200, height=400)
rsi_chart.plot(rsi_dates, rsi_values, window=14)

# Add threshold lines
rsi_chart.add_overbought_line(level=70)
rsi_chart.add_oversold_line(level=30)

# Styling
rsi_chart.set_title('RSI Technical Indicator', fontsize=14)
rsi_chart.set_labels('Date', 'RSI')
rsi_chart.add_grid(alpha=0.3)

rsi_chart.save('rsi_indicator.png', dpi=300)
```

### MACD Analysis

```python
# MACD implementation
class MACDCalculator:
    @staticmethod
    def calculate_ema(prices, span):
        """Calculate Exponential Moving Average."""
        alpha = 2 / (span + 1)
        ema = np.zeros_like(prices)
        ema[0] = prices[0]

        for i in range(1, len(prices)):
            ema[i] = alpha * prices[i] + (1 - alpha) * ema[i-1]

        return ema

    @staticmethod
    def calculate_macd(prices, fast=12, slow=26, signal=9):
        """Calculate MACD indicator."""
        ema_fast = MACDCalculator.calculate_ema(prices, fast)
        ema_slow = MACDCalculator.calculate_ema(prices, slow)

        macd_line = ema_fast - ema_slow
        signal_line = MACDCalculator.calculate_ema(macd_line, signal)
        histogram = macd_line - signal_line

        return macd_line, signal_line, histogram

# Calculate MACD
macd, signal, histogram = MACDCalculator.calculate_macd(closes)

# Create MACD chart
macd_chart = plotx.MACDChart(width=1200, height=500)
macd_chart.plot(dates, macd, signal, histogram)

# Styling
macd_chart.set_title('MACD Analysis', fontsize=14)
macd_chart.set_labels('Date', 'MACD')
macd_chart.add_zero_line()
macd_chart.add_legend()

macd_chart.save('macd_analysis.png', dpi=300)
```

### Support and Resistance Levels

```python
# Support and Resistance Detection
class SupportResistance:
    @staticmethod
    def find_support_resistance(highs, lows, window=10, threshold=0.02):
        """Find support and resistance levels."""
        # Local maxima (resistance)
        resistance_levels = []
        for i in range(window, len(highs) - window):
            if highs[i] == max(highs[i-window:i+window]):
                resistance_levels.append((i, highs[i]))

        # Local minima (support)
        support_levels = []
        for i in range(window, len(lows) - window):
            if lows[i] == min(lows[i-window:i+window]):
                support_levels.append((i, lows[i]))

        return support_levels, resistance_levels

# Find levels
support_levels, resistance_levels = SupportResistance.find_support_resistance(highs, lows)

# Create chart with S/R levels
chart = plotx.CandlestickChart(width=1200, height=800)
chart.plot(dates, opens, highs, lows, closes)

# Add support levels
for idx, level in support_levels:
    chart.add_horizontal_line(level, color='green', linestyle='--',
                             label=f'Support {level:.2f}' if idx == support_levels[0][0] else None)

# Add resistance levels
for idx, level in resistance_levels:
    chart.add_horizontal_line(level, color='red', linestyle='--',
                             label=f'Resistance {level:.2f}' if idx == resistance_levels[0][0] else None)

chart.set_title('Support and Resistance Analysis')
chart.add_legend()
chart.save('support_resistance.png', dpi=300)
```

## Portfolio Analysis

### Portfolio Performance

```python
# Portfolio visualization
class PortfolioAnalyzer:
    def __init__(self, stocks_data):
        self.stocks_data = stocks_data

    def calculate_returns(self):
        """Calculate portfolio returns."""
        returns = {}
        for stock, prices in self.stocks_data.items():
            daily_returns = np.diff(prices) / prices[:-1]
            returns[stock] = daily_returns
        return returns

    def calculate_cumulative_returns(self, weights=None):
        """Calculate cumulative portfolio returns."""
        returns = self.calculate_returns()

        if weights is None:
            weights = {stock: 1/len(returns) for stock in returns.keys()}

        # Portfolio returns
        portfolio_returns = np.zeros(len(list(returns.values())[0]))
        for stock, weight in weights.items():
            portfolio_returns += weight * returns[stock]

        cumulative_returns = np.cumprod(1 + portfolio_returns) - 1
        return cumulative_returns

# Sample portfolio data
portfolio_stocks = {
    'AAPL': closes * np.random.uniform(0.8, 1.2),
    'GOOGL': closes * np.random.uniform(0.9, 1.1) + np.random.normal(0, 5, len(closes)),
    'MSFT': closes * np.random.uniform(0.85, 1.15) + np.random.normal(0, 3, len(closes)),
    'TSLA': closes * np.random.uniform(0.7, 1.3) + np.random.normal(0, 10, len(closes))
}

analyzer = PortfolioAnalyzer(portfolio_stocks)

# Equal weight portfolio
portfolio_returns = analyzer.calculate_cumulative_returns()

# Create portfolio chart
portfolio_chart = plotx.LineChart(width=1200, height=600)

# Plot individual stocks
colors = ['blue', 'red', 'green', 'orange']
for i, (stock, prices) in enumerate(portfolio_stocks.items()):
    returns = (prices - prices[0]) / prices[0]
    portfolio_chart.plot(dates, returns, color=colors[i], label=stock, alpha=0.7)

# Plot portfolio
portfolio_chart.plot(dates[1:], portfolio_returns, color='black', linewidth=3, label='Portfolio')

portfolio_chart.set_title('Portfolio Performance Comparison')
portfolio_chart.set_labels('Date', 'Cumulative Returns')
portfolio_chart.add_legend()
portfolio_chart.add_grid(alpha=0.3)
portfolio_chart.save('portfolio_performance.png', dpi=300)
```

### Risk Analysis

```python
# Risk metrics visualization
class RiskAnalyzer:
    @staticmethod
    def calculate_var(returns, confidence=0.95):
        """Calculate Value at Risk."""
        return np.percentile(returns, (1 - confidence) * 100)

    @staticmethod
    def calculate_sharpe_ratio(returns, risk_free_rate=0.02):
        """Calculate Sharpe ratio."""
        excess_returns = np.mean(returns) - risk_free_rate/252  # Daily risk-free rate
        return excess_returns / np.std(returns) * np.sqrt(252)  # Annualized

    @staticmethod
    def calculate_max_drawdown(prices):
        """Calculate maximum drawdown."""
        cumulative = np.cumprod(1 + np.diff(prices) / prices[:-1])
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        return np.min(drawdown)

# Calculate risk metrics
risk_analyzer = RiskAnalyzer()
returns = np.diff(closes) / closes[:-1]

var_95 = risk_analyzer.calculate_var(returns, 0.95)
sharpe_ratio = risk_analyzer.calculate_sharpe_ratio(returns)
max_drawdown = risk_analyzer.calculate_max_drawdown(closes)

# Risk histogram
risk_chart = plotx.HistogramChart(width=800, height=600)
risk_chart.hist(returns * 100, bins=50, alpha=0.7, color='skyblue', density=True)

# Add VaR line
risk_chart.add_vertical_line(var_95 * 100, color='red', linestyle='--',
                            label=f'VaR 95%: {var_95*100:.2f}%')

risk_chart.set_title(f'Risk Analysis\nSharpe Ratio: {sharpe_ratio:.2f}, Max Drawdown: {max_drawdown*100:.2f}%')
risk_chart.set_labels('Daily Returns (%)', 'Density')
risk_chart.add_legend()
risk_chart.save('risk_analysis.png', dpi=300)
```

## Real-Time Financial Data

### Live Trading Dashboard

```python
# Real-time trading dashboard
class TradingDashboard:
    def __init__(self):
        self.charts = {}
        self.setup_charts()

    def setup_charts(self):
        """Setup dashboard charts."""
        # Main price chart
        self.charts['price'] = plotx.CandlestickChart(width=800, height=400)

        # Volume chart
        self.charts['volume'] = plotx.BarChart(width=800, height=200)

        # RSI chart
        self.charts['rsi'] = plotx.RSIChart(width=800, height=200)

        # MACD chart
        self.charts['macd'] = plotx.MACDChart(width=800, height=200)

    def update_data(self, new_data):
        """Update charts with new data."""
        # Update price chart
        self.charts['price'].append_data(new_data['ohlcv'])

        # Update indicators
        if len(new_data['rsi']) > 0:
            self.charts['rsi'].update_data(new_data['rsi'])

        if len(new_data['macd']) > 0:
            self.charts['macd'].update_data(new_data['macd'])

        # Refresh displays
        for chart in self.charts.values():
            chart.refresh()

    def save_dashboard(self, filename):
        """Save complete dashboard."""
        # Create combined image
        dashboard = plotx.DashboardLayout(2, 2)
        dashboard.add_chart(self.charts['price'], 0, 0, colspan=2)
        dashboard.add_chart(self.charts['volume'], 1, 0)
        dashboard.add_chart(self.charts['rsi'], 1, 1)
        dashboard.save(filename)

# Usage
dashboard = TradingDashboard()

# Simulate real-time updates
for i in range(10):
    new_data = {
        'ohlcv': generate_stock_data(1),  # One new candle
        'rsi': [RSICalculator.calculate_rsi(closes[-15:])[-1]],
        'macd': MACDCalculator.calculate_macd(closes[-27:])
    }
    dashboard.update_data(new_data)
    dashboard.save_dashboard(f'dashboard_frame_{i}.png')
```

### Market Comparison

```python
# Market sector comparison
def create_market_comparison():
    # Sample sector data
    sectors = {
        'Technology': {'return': 0.15, 'volatility': 0.25, 'market_cap': 5000},
        'Healthcare': {'return': 0.12, 'volatility': 0.18, 'market_cap': 3500},
        'Financials': {'return': 0.08, 'volatility': 0.22, 'market_cap': 4200},
        'Energy': {'return': -0.05, 'volatility': 0.35, 'market_cap': 1800},
        'Consumer': {'return': 0.10, 'volatility': 0.20, 'market_cap': 2800}
    }

    # Extract data
    returns = [data['return'] * 100 for data in sectors.values()]
    volatilities = [data['volatility'] * 100 for data in sectors.values()]
    market_caps = [data['market_cap'] for data in sectors.values()]
    sector_names = list(sectors.keys())

    # Risk-Return scatter plot
    chart = plotx.ScatterChart(width=1000, height=700)
    chart.plot(volatilities, returns, s=market_caps, alpha=0.7,
              c=range(len(sectors)), cmap='Set1')

    # Add sector labels
    for i, sector in enumerate(sector_names):
        chart.add_annotation(volatilities[i], returns[i], sector,
                           fontsize=10, ha='center')

    # Add quadrant lines
    chart.add_vertical_line(np.mean(volatilities), color='gray',
                           linestyle='--', alpha=0.5)
    chart.add_horizontal_line(np.mean(returns), color='gray',
                             linestyle='--', alpha=0.5)

    chart.set_title('Market Sector Analysis: Risk vs Return')
    chart.set_labels('Volatility (%)', 'Annual Return (%)')
    chart.add_grid(alpha=0.3)
    chart.save('market_comparison.png', dpi=300)

create_market_comparison()
```

## Advanced Financial Analysis

### Options Analysis

```python
# Black-Scholes option pricing visualization
class OptionsAnalyzer:
    @staticmethod
    def black_scholes_call(S, K, T, r, sigma):
        """Black-Scholes call option price."""
        from scipy.stats import norm

        d1 = (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
        d2 = d1 - sigma*np.sqrt(T)

        call_price = S*norm.cdf(d1) - K*np.exp(-r*T)*norm.cdf(d2)
        return call_price

    @staticmethod
    def calculate_greeks(S, K, T, r, sigma):
        """Calculate option Greeks."""
        from scipy.stats import norm

        d1 = (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
        d2 = d1 - sigma*np.sqrt(T)

        # Greeks
        delta = norm.cdf(d1)
        gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
        theta = (-S*norm.pdf(d1)*sigma/(2*np.sqrt(T)) -
                r*K*np.exp(-r*T)*norm.cdf(d2)) / 365
        vega = S * norm.pdf(d1) * np.sqrt(T) / 100

        return {'delta': delta, 'gamma': gamma, 'theta': theta, 'vega': vega}

# Option price surface
S_range = np.linspace(80, 120, 50)
T_range = np.linspace(0.1, 1, 50)
S_grid, T_grid = np.meshgrid(S_range, T_range)

K = 100  # Strike price
r = 0.05  # Risk-free rate
sigma = 0.2  # Volatility

# Calculate option prices
option_prices = OptionsAnalyzer.black_scholes_call(S_grid, K, T_grid, r, sigma)

# Create 3D surface
surface_chart = plotx.SurfaceChart(width=1000, height=700)
surface_chart.plot_surface(S_grid, T_grid, option_prices,
                          cmap='viridis', alpha=0.8)

surface_chart.set_title('Option Price Surface (Black-Scholes)')
surface_chart.set_labels('Stock Price ($)', 'Time to Expiry (years)', 'Option Price ($)')
surface_chart.save('option_surface.png', dpi=300)
```

### Correlation Analysis

```python
# Stock correlation heatmap
def create_correlation_matrix():
    # Calculate correlation matrix
    price_data = np.array(list(portfolio_stocks.values())).T
    correlation_matrix = np.corrcoef(price_data.T)

    # Create heatmap
    heatmap_chart = plotx.HeatmapChart(width=600, height=600)
    heatmap_chart.heatmap(correlation_matrix,
                         xticklabels=list(portfolio_stocks.keys()),
                         yticklabels=list(portfolio_stocks.keys()),
                         annot=True, fmt='.2f', cmap='RdBu_r',
                         center=0, vmin=-1, vmax=1)

    heatmap_chart.set_title('Stock Correlation Matrix')
    heatmap_chart.save('correlation_matrix.png', dpi=300)

create_correlation_matrix()
```

## Best Practices

### Professional Styling

```python
# Financial chart styling guidelines
def apply_financial_theme(chart):
    """Apply professional financial styling."""
    chart.set_theme('financial')
    chart.set_background_color('#FFFFFF')
    chart.set_grid_style(color='#E0E0E0', alpha=0.5)
    chart.set_title_style(fontsize=16, fontweight='bold', color='#2E2E2E')
    chart.set_axis_style(labelsize=12, color='#4E4E4E')
    chart.set_legend_style(frameon=True, fancybox=True, shadow=True)

# Color schemes for financial data
FINANCIAL_COLORS = {
    'bullish': '#26A69A',  # Green for up moves
    'bearish': '#EF5350',  # Red for down moves
    'volume': '#78909C',   # Gray for volume
    'ma_short': '#2196F3', # Blue for short MA
    'ma_long': '#FF9800',  # Orange for long MA
    'support': '#4CAF50',  # Green for support
    'resistance': '#F44336' # Red for resistance
}
```

### Performance Optimization

```python
# Optimize for real-time financial data
class OptimizedFinancialChart:
    def __init__(self, max_candles=1000):
        self.max_candles = max_candles
        self.chart = plotx.CandlestickChart()
        self.chart.enable_data_sampling(max_points=max_candles)
        self.chart.enable_streaming_mode(buffer_size=100)

    def update_realtime(self, new_ohlcv):
        """Efficiently update with new data."""
        self.chart.append_candle(new_ohlcv)
        if self.chart.candle_count > self.max_candles:
            self.chart.trim_data(keep_last=self.max_candles)

        self.chart.refresh_display()
```

### Error Handling

```python
# Robust financial data handling
class FinancialDataValidator:
    @staticmethod
    def validate_ohlcv(open_price, high, low, close, volume):
        """Validate OHLCV data integrity."""
        errors = []

        if high < max(open_price, close):
            errors.append("High price is less than open/close")

        if low > min(open_price, close):
            errors.append("Low price is greater than open/close")

        if volume < 0:
            errors.append("Volume cannot be negative")

        return len(errors) == 0, errors

    @staticmethod
    def clean_financial_data(data):
        """Clean and prepare financial data."""
        # Remove NaN values
        data = data.dropna()

        # Remove outliers (beyond 3 standard deviations)
        for col in ['open', 'high', 'low', 'close']:
            mean = data[col].mean()
            std = data[col].std()
            data = data[abs(data[col] - mean) <= 3 * std]

        return data
```

## Next Steps

- Explore [Real-time Applications](real-time-applications.md)
- Learn about [Portfolio Optimization](portfolio-optimization.md)
- Check out [Financial Examples Gallery](../examples/financial-gallery.md)

---

Master financial visualization with PlotX's comprehensive toolkit!