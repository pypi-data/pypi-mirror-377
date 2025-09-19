"""Scatter plot helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from .base import BaseChart


@dataclass
class ScatterChart(BaseChart):
    """Create high-density scatter plots with sensible defaults."""

    def plot(
        self,
        x_values: Sequence[float] | Iterable[float],
        y_values: Sequence[float] | Iterable[float],
        *,
        label: str | None = None,
        color: str | None = None,
        c: Sequence[float] | Iterable[float] | None = None,
        size: int = 40,
        s: int | None = None,
        alpha: float = 0.9,
        style: str = "o",
        xlabel: str | None = None,
        ylabel: str | None = None,
        grid: bool = True,
    ) -> None:
        x, y = self._validate_xy(x_values, y_values)

        # Handle size parameter (s takes precedence over size)
        point_size = s if s is not None else size

        self.axes.scatter(
            x,
            y,
            label=label or self.label,
            color=color,
            c=c,
            s=point_size,
            alpha=alpha,
            marker=style,
        )
        if grid:
            self.axes.grid(True, linestyle=":")
        if label or self.label:
            self.axes.legend()
        self._maybe_set_labels(xlabel, ylabel)
