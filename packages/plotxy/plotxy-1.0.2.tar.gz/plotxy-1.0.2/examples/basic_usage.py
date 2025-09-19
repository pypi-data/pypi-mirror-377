"""Demonstrates the core capabilities of PlotX."""

import numpy as np

from plotx import (
    BarChart,
    BodePlot,
    LineChart,
    PlotXFigure,
    ScatterChart,
    StressStrainChart,
)


def demo_line() -> None:
    time = np.linspace(0, 2 * np.pi, 200)
    response = np.sin(time) * np.exp(-0.2 * time)

    fig = PlotXFigure(style="dark")
    chart = LineChart(fig, label="Damped response")
    chart.plot(time, response, xlabel="Time (s)", ylabel="Amplitude")
    fig.save("examples/output/damped_line.png")
    fig.close()


def demo_scatter() -> None:
    rng = np.random.default_rng(42)
    x = rng.normal(0, 1, 500)
    y = 0.7 * x + rng.normal(0, 0.5, 500)

    fig = PlotXFigure(style="light")
    chart = ScatterChart(fig)
    chart.plot(x, y, xlabel="Speed (m/s)", ylabel="Efficiency (%)", alpha=0.6)
    fig.save("examples/output/scatter.png")
    fig.close()


def demo_bar() -> None:
    categories = ["Q1", "Q2", "Q3", "Q4"]
    values = [120, 150, 170, 160]

    fig = PlotXFigure()
    BarChart(fig).plot(categories, values, ylabel="Production (units)")
    fig.save("examples/output/bars.png")
    fig.close()


def demo_bode() -> None:
    numerator = [10]
    denominator = [1, 0.5, 10]

    bode = BodePlot()
    fig = bode.plot(numerator, denominator)
    fig.save("examples/output/bode.png")
    fig.close()


def demo_stress_strain() -> None:
    strain = np.linspace(0, 0.12, 80)
    stress = 210e3 * strain - 200e3 * strain**2

    fig = PlotXFigure(style="engineering")
    chart = StressStrainChart(fig)
    chart.plot(
        strain,
        stress / 1e6,
        yield_point=(0.02, (210e3 * 0.02 - 200e3 * 0.02**2) / 1e6),
        ultimate_point=(0.08, stress.max() / 1e6),
    )
    fig.save("examples/output/stress_strain.png")
    fig.close()


if __name__ == "__main__":
    demo_line()
    demo_scatter()
    demo_bar()
    demo_bode()
    demo_stress_strain()
