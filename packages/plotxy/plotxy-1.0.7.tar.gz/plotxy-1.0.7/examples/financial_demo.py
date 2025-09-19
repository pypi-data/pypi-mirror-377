#!/usr/bin/env python3
"""
Financial charts demonstration of PlotX capabilities.
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

try:
    import plotxy as px
    print("✓ PlotX imported successfully")
except ImportError as e:
    print(f"❌ Failed to import PlotX: {e}")
    exit(1)


def generate_sample_financial_data():
    """Generate realistic financial data."""
    # Generate dates
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    n_days = len(dates)

    # Simulate price with realistic movements
    np.random.seed(42)
    returns = np.random.normal(0.0005, 0.02, n_days)  # Daily returns
    price = 100 * np.exp(np.cumsum(returns))

    # Create OHLC data with realistic spreads
    daily_volatility = np.abs(np.random.normal(0, 0.015, n_days))

    open_price = np.roll(price, 1)
    open_price[0] = price[0]

    high = price * (1 + daily_volatility)
    low = price * (1 - daily_volatility)
    close_price = price

    # Generate volume with correlation to price changes
    price_change = np.abs(np.diff(np.concatenate([[100], price])))
    base_volume = np.random.lognormal(mean=9, sigma=0.8, size=n_days)
    volume = base_volume * (1 + price_change * 0.1)

    return dates, open_price, high, low, close_price, volume


def demo_candlestick_chart():
    """Test candlestick chart functionality."""
    print("\n=== Testing Candlestick Chart ===")

    try:
        from plotxy.charts.financial import CandlestickChart

        # Generate sample data
        dates, open_price, high, low, close_price, volume = generate_sample_financial_data()

        # Use last 60 days for better visualization
        end_idx = len(dates)
        start_idx = max(0, end_idx - 60)

        subset_dates = dates[start_idx:end_idx]
        subset_open = open_price[start_idx:end_idx]
        subset_high = high[start_idx:end_idx]
        subset_low = low[start_idx:end_idx]
        subset_close = close_price[start_idx:end_idx]
        subset_volume = volume[start_idx:end_idx]

        # Create candlestick chart
        fig = px.PlotXFigure(width=14, height=10)
        candlestick = CandlestickChart(fig)

        candlestick.plot(subset_dates, subset_open, subset_high, subset_low, subset_close,
                        volume=subset_volume, up_color='green', down_color='red')

        # Add moving averages
        candlestick.add_moving_average(subset_dates, subset_close, period=10,
                                     color="blue", label="10-day MA")
        candlestick.add_moving_average(subset_dates, subset_close, period=20,
                                     color="orange", label="20-day MA")

        fig.save("examples/output/candlestick_demo.png", dpi=150)
        print("✓ Candlestick chart created and saved")

    except Exception as e:
        print(f"❌ Candlestick chart failed: {e}")


def demo_rsi_chart():
    """Test RSI chart functionality."""
    print("\n=== Testing RSI Chart ===")

    try:
        from plotxy.charts.financial import RSIChart

        # Generate sample data
        dates, _, _, _, close_price, _ = generate_sample_financial_data()

        # Create RSI chart
        fig = px.PlotXFigure(width=12, height=6)
        rsi_chart = RSIChart(fig)

        rsi_chart.plot(dates, close_price, period=14)

        fig.save("examples/output/rsi_demo.png")
        print("✓ RSI chart created and saved")

    except Exception as e:
        print(f"❌ RSI chart failed: {e}")


def demo_volume_profile():
    """Test volume profile chart."""
    print("\n=== Testing Volume Profile Chart ===")

    try:
        from plotxy.charts.financial import VolumeProfileChart

        # Generate sample data
        _, _, _, _, close_price, volume = generate_sample_financial_data()

        # Create volume profile chart
        fig = px.PlotXFigure(width=8, height=10)
        volume_profile = VolumeProfileChart(fig)

        volume_profile.plot(close_price, volume, price_bins=30,
                          orientation='horizontal', color='steelblue')

        fig.save("examples/output/volume_profile_demo.png")
        print("✓ Volume profile chart created and saved")

    except Exception as e:
        print(f"❌ Volume profile chart failed: {e}")


def demo_macd_chart():
    """Test MACD chart functionality."""
    print("\n=== Testing MACD Chart ===")

    try:
        from plotxy.charts.financial import MACDChart

        # Generate sample data
        dates, _, _, _, close_price, _ = generate_sample_financial_data()

        # Create MACD chart
        fig = px.PlotXFigure(width=12, height=6)
        macd_chart = MACDChart(fig)

        macd_chart.plot(dates, close_price, fast_period=12, slow_period=26, signal_period=9)

        fig.save("examples/output/macd_demo.png")
        print("✓ MACD chart created and saved")

    except Exception as e:
        print(f"❌ MACD chart failed: {e}")


def main():
    """Run financial chart demonstrations."""
    print("PlotX Financial Charts Demo")
    print("=" * 50)

    # Create output directory
    os.makedirs("examples/output", exist_ok=True)

    # Run financial demos
    demo_candlestick_chart()
    demo_rsi_chart()
    demo_volume_profile()
    demo_macd_chart()

    print("\n" + "=" * 50)
    print("🎉 Financial charts demos completed!")

    print("\nGenerated financial charts:")
    print("  - examples/output/candlestick_demo.png")
    print("  - examples/output/rsi_demo.png")
    print("  - examples/output/volume_profile_demo.png")
    print("  - examples/output/macd_demo.png")

    print("\nPlotX Financial Features:")
    print("✓ Professional candlestick charts")
    print("✓ Technical indicators (RSI, MACD)")
    print("✓ Volume analysis tools")
    print("✓ Moving averages and overlays")
    print("✓ Publication-quality styling")

    print("\nPlotX is ready for financial analysis! 📈")


if __name__ == "__main__":
    main()