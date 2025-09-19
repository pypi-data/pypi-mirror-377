"""Line chart helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from matplotlib.lines import Line2D

from .base import BaseChart


@dataclass
class LineChart(BaseChart):
    """Convenience wrapper for standard line plots."""

    def plot(
        self,
        x_values: Sequence[float] | Iterable[float],
        y_values: Sequence[float] | Iterable[float],
        *,
        label: str | None = None,
        color: str | None = None,
        linewidth: float = 2.0,
        marker: str | None = None,
        xlabel: str | None = None,
        ylabel: str | None = None,
        grid: bool = True,
        glow: bool = False,
    ) -> Line2D:
        x, y = self._validate_xy(x_values, y_values)
        if glow:
            for i in range(1, 10):
                self.axes.plot(
                    x,
                    y,
                    color=color,
                    linewidth=linewidth + i * 2,
                    alpha=0.1 - i * 0.01,
                    marker=marker,
                )
        (line,) = self.axes.plot(
            x,
            y,
            label=label or self.label,
            color=color,
            linewidth=linewidth,
            marker=marker,
        )
        if grid:
            self.axes.grid(True)
        if label or self.label:
            self.axes.legend()
        self._maybe_set_labels(xlabel, ylabel)
        return line

    def plot_multiple(
        self,
        series: dict[
            str,
            tuple[Sequence[float] | Iterable[float], Sequence[float] | Iterable[float]],
        ],
        *,
        xlabel: str | None = None,
        ylabel: str | None = None,
    ) -> None:
        for label, (xs, ys) in series.items():
            self.plot(xs, ys, label=label, grid=False)
        self.axes.grid(True)
        self._maybe_set_labels(xlabel, ylabel)
