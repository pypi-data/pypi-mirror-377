"""Generate a gallery of PlotX charts for consumption by a frontend."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List

import numpy as np

from plotx import (
    BarChart,
    BodePlot,
    InteractiveSurfaceChart,
    LineChart,
    PlotXFigure,
    ScatterChart,
    StressStrainChart,
)
from plotx.charts.surface import SurfaceChart


BuilderFn = Callable[[], PlotXFigure | tuple[PlotXFigure, dict[str, object]]]


@dataclass
class ChartExample:
    """Metadata describing a single demo chart."""

    key: str
    title: str
    description: str
    kind: str
    builder: BuilderFn
    tags: tuple[str, ...] = ()


def _build_line_chart() -> PlotXFigure:
    fig = PlotXFigure(style="extraordinary")
    time = np.linspace(0, 2 * np.pi, 300)
    response = np.sin(time) * np.exp(-0.25 * time)
    line = LineChart(fig, label="Damped response")
    line.plot(time, response, xlabel="Time (s)", ylabel="Amplitude", glow=True)
    return fig


def _build_line_comparison() -> PlotXFigure:
    fig = PlotXFigure(style="light", width=11, height=6)
    time = np.linspace(0, 12, 240)
    baseline = np.sin(time)
    damped = baseline * np.exp(-0.1 * time)
    noisy = baseline + np.random.default_rng(12).normal(0, 0.15, baseline.size)
    chart = LineChart(fig)
    chart.plot_multiple(
        {
            "Baseline": (time, baseline),
            "Damped": (time, damped),
            "Noisy": (time, noisy),
        },
        xlabel="Time (s)",
        ylabel="Amplitude",
    )
    chart.axes.set_title("Signal Comparison")
    return fig


def _build_scatter_chart() -> PlotXFigure:
    rng = np.random.default_rng(7)
    x = rng.normal(0, 1, 400)
    y = 0.75 * x + rng.normal(0, 0.45, 400)
    fig = PlotXFigure(style="light")
    scatter = ScatterChart(fig, label="Samples")
    scatter.plot(x, y, xlabel="Speed (m/s)", ylabel="Efficiency (%)", alpha=0.65)
    return fig


def _build_bar_chart() -> PlotXFigure:
    projects = ["A", "B", "C", "D"]
    output = [120, 165, 150, 190]
    fig = PlotXFigure(style="engineering")
    BarChart(fig, label="Throughput").plot(
        projects,
        output,
        ylabel="Production (units)",
        xlabel="Project",
    )
    return fig


def _build_grouped_bar() -> PlotXFigure:
    regions = ["North", "South", "East", "West"]
    rng = np.random.default_rng(23)
    value_map = {
        "2019": rng.uniform(80, 120, len(regions)),
        "2020": rng.uniform(90, 130, len(regions)),
        "2021": rng.uniform(110, 150, len(regions)),
    }
    fig = PlotXFigure(style="dark", width=9, height=6)
    chart = BarChart(fig)
    chart.plot_grouped(
        regions,
        {k: [float(v) for v in vals] for k, vals in value_map.items()},
        xlabel="Region",
        ylabel="Output (units)",
        width=0.22,
    )
    chart.axes.set_title("Regional Throughput by Year")
    return fig


def _build_surface_chart() -> PlotXFigure:
    x = np.linspace(-2, 2, 60)
    y = np.linspace(-2, 2, 60)
    x_grid, y_grid = np.meshgrid(x, y)
    r = np.sqrt(x_grid**2 + y_grid**2)
    z = np.sin(r)
    fig = PlotXFigure(width=8, height=6, style="light")
    surface = SurfaceChart(fig)
    surface.plot(x_grid, y_grid, z, cmap="plasma")
    return fig


def _build_interactive_surface() -> tuple[PlotXFigure, dict[str, object]]:
    x = np.linspace(-3, 3, 80)
    y = np.linspace(-3, 3, 80)
    x_grid, y_grid = np.meshgrid(x, y)
    z_grid = np.sin(x_grid) * np.cos(y_grid) + 0.2 * np.sin(2 * x_grid)
    fig = PlotXFigure(width=8, height=6, style="dark")
    chart = InteractiveSurfaceChart(fig)
    chart.plot(
        x_grid,
        y_grid,
        z_grid,
        cmap="magma",
        linewidth=0.05,
        enable_interaction=False,
    )
    chart.axes.set_title("Interactive Wave Surface")
    chart.axes.set_box_aspect((1, 1, 0.6))
    mesh_payload = chart.export_mesh().copy()
    mesh_payload["title"] = "Interactive Wave Surface"
    return fig, {"interactive": {"type": "mesh3d", "payload": mesh_payload}}


def _build_bode_plot() -> PlotXFigure:
    bode = BodePlot()
    numerator = [10]
    denominator = [1, 0.8, 10]
    return bode.plot(numerator, denominator, units="rad/s")


def _build_stress_strain() -> PlotXFigure:
    strain = np.linspace(0, 0.12, 80)
    stress = 210e3 * strain - 220e3 * strain**2
    fig = PlotXFigure(style="engineering")
    chart = StressStrainChart(fig)
    chart.plot(
        strain,
        stress / 1e6,
        yield_point=(0.02, (210e3 * 0.02 - 220e3 * 0.02**2) / 1e6),
        ultimate_point=(0.085, stress.max() / 1e6),
        xlabel="Strain",
        ylabel="Stress (MPa)",
    )
    return fig


EXAMPLES: List[ChartExample] = [
    ChartExample(
        key="line",
        title="Damped Oscillation",
        description="Line chart showcasing theming, grid control, and legends.",
        kind="line",
        builder=_build_line_chart,
        tags=("line", "time-series", "analytics"),
    ),
    ChartExample(
        key="line-multi",
        title="Signal Comparison",
        description="Multiple series plotted together using PlotX line helpers.",
        kind="line",
        builder=_build_line_comparison,
        tags=("line", "multi-series", "analytics"),
    ),
    ChartExample(
        key="scatter",
        title="Efficiency vs Speed",
        description="Scatter chart with transparency for dense data clouds.",
        kind="scatter",
        builder=_build_scatter_chart,
        tags=("scatter", "statistics"),
    ),
    ChartExample(
        key="bar",
        title="Production Output",
        description="Categorical bar chart with axis labeling and grouping.",
        kind="bar",
        builder=_build_bar_chart,
        tags=("bar", "categorical"),
    ),
    ChartExample(
        key="bar-grouped",
        title="Regional Throughput",
        description="Grouped bars comparing multiple years per region.",
        kind="bar",
        builder=_build_grouped_bar,
        tags=("bar", "grouped", "comparison"),
    ),
    ChartExample(
        key="surface",
        title="Ripple Surface",
        description="3D surface rendering using Matplotlib's mplot3d toolkit.",
        kind="surface",
        builder=_build_surface_chart,
        tags=("surface", "3d", "mesh"),
    ),
    ChartExample(
        key="surface-interactive",
        title="Interactive Wave Surface",
        description="High-resolution surface exported for browser-based interaction.",
        kind="surface-interactive",
        builder=_build_interactive_surface,
        tags=("surface", "3d", "interactive"),
    ),
    ChartExample(
        key="bode",
        title="Second-Order System",
        description="Engineering-focused Bode magnitude and phase plots.",
        kind="bode",
        builder=_build_bode_plot,
        tags=("engineering", "frequency-response"),
    ),
    ChartExample(
        key="stress",
        title="Stress-Strain Curve",
        description="Materials chart with automatic annotations for yield and ultimate points.",
        kind="stress-strain",
        builder=_build_stress_strain,
        tags=("engineering", "materials"),
    ),
]


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def _summarize_single_axes(axes) -> Dict[str, object]:
    summary: Dict[str, object] = {
        "xlabel": getattr(axes, "get_xlabel", lambda: None)(),
        "ylabel": getattr(axes, "get_ylabel", lambda: None)(),
        "title": getattr(axes, "get_title", lambda: None)(),
        "type": type(axes).__name__,
    }
    if hasattr(axes, "get_zlabel"):
        summary["zlabel"] = axes.get_zlabel()

    series = []
    if hasattr(axes, "lines") and axes.lines:
        for line in axes.lines:
            label = line.get_label()
            if label == "_nolegend_":
                label = "series"
            x_data = line.get_xdata()
            y_data = line.get_ydata()
            sample = list(zip(x_data[:6], y_data[:6]))
            series.append(
                {
                    "label": label,
                    "sample": [
                        [float(round(x, 4)), float(round(y, 4))] for x, y in sample
                    ],
                }
            )
    if series:
        summary["series"] = series

    scatter_points: List[Dict[str, object]] = []
    if hasattr(axes, "collections") and axes.collections:
        for collection in axes.collections:
            offsets = collection.get_offsets()
            if offsets.size == 0:
                continue
            sample = offsets[:6]
            scatter_points.append(
                {
                    "size": (
                        float(collection.get_sizes()[0])
                        if collection.get_sizes().size
                        else None
                    ),
                    "sample": [
                        [float(round(x, 4)), float(round(y, 4))] for x, y in sample
                    ],
                }
            )
    if scatter_points:
        summary["scatter"] = scatter_points

    bar_heights: List[Dict[str, object]] = []
    if hasattr(axes, "containers"):
        for container in axes.containers:
            for patch in container:
                if hasattr(patch, "get_x") and hasattr(patch, "get_height"):
                    bar_heights.append(
                        {
                            "x": float(round(patch.get_x(), 4)),
                            "width": float(round(patch.get_width(), 4)),
                            "height": float(round(patch.get_height(), 4)),
                        }
                    )
    if bar_heights:
        summary["bars"] = bar_heights

    lims: Dict[str, List[float]] = {}
    if hasattr(axes, "get_xlim"):
        lims["xlim"] = [float(v) for v in axes.get_xlim()]
    if hasattr(axes, "get_ylim"):
        lims["ylim"] = [float(v) for v in axes.get_ylim()]
    if lims:
        summary["limits"] = lims

    return summary


def _summarize_axes(fig: PlotXFigure) -> Dict[str, object]:
    axes = fig.axes if isinstance(fig.axes, list) else [fig.axes]
    summaries = []
    for idx, ax in enumerate(axes):
        meta = _summarize_single_axes(ax)
        meta["index"] = idx
        summaries.append(meta)

    if len(summaries) == 1:
        return summaries[0]

    return {
        "count": len(summaries),
        "primary": summaries[0],
        "additional": summaries[1:],
    }


def render_gallery(output_dir: Path) -> dict:
    output_dir = _ensure_dir(output_dir)
    images_dir = _ensure_dir(output_dir / "images")

    manifest = []
    interactive_dir = _ensure_dir(output_dir / "interactive")

    for example in EXAMPLES:
        built = example.builder()
        if isinstance(built, tuple):
            fig, extras = built
        else:
            fig, extras = built, {}

        image_path = images_dir / f"{example.key}.png"
        fig.save(image_path, dpi=200)
        metadata = _summarize_axes(fig)
        fig.close()

        interactive_meta: dict[str, object] | None = None
        if isinstance(extras, dict):
            interactive_payload = extras.get("interactive")
            if isinstance(interactive_payload, dict):
                payload_type = interactive_payload.get("type")
                payload_body = interactive_payload.get("payload")
                if payload_type == "mesh3d" and isinstance(payload_body, dict):
                    mesh_path = interactive_dir / f"{example.key}.json"
                    with mesh_path.open("w", encoding="utf-8") as mesh_handle:
                        json.dump(payload_body, mesh_handle)
                    interactive_meta = {
                        "type": "mesh3d",
                        "mesh": f"interactive/{mesh_path.name}",
                    }

        manifest.append(
            {
                "key": example.key,
                "title": example.title,
                "description": example.description,
                "kind": example.kind,
                "theme": fig.style,
                "tags": list(example.tags),
                "image": f"images/{image_path.name}",
                "axes": metadata,
                "interactive": interactive_meta,
            }
        )

    gallery = {
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "count": len(manifest),
        "charts": manifest,
    }

    with (output_dir / "gallery.json").open("w", encoding="utf-8") as handle:
        json.dump(gallery, handle, indent=2)

    return gallery


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("examples/react-gallery/public/gallery"),
        help="Directory where images and gallery.json will be written.",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print a JSON summary to stdout after rendering.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    gallery = render_gallery(args.output_dir)
    print(f"Generated {gallery['count']} charts in {args.output_dir!s}")
    if args.summary:
        print(json.dumps(gallery, indent=2))


if __name__ == "__main__":
    main()
