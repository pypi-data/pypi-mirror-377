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
        cmap: str = 'viridis',
        xlabel: str | None = None,
        ylabel: str | None = None,
        grid: bool = True,
    ) -> None:
        x, y = self._validate_xy(x_values, y_values)

        # Handle size parameter (s takes precedence over size)
        point_size = s if s is not None else size

        scatter = self.axes.scatter(
            x,
            y,
            label=label or self.label,
            color=color,
            c=c,
            s=point_size,
            alpha=alpha,
            marker=style,
            cmap=cmap,
        )
        if grid:
            self.axes.grid(True, linestyle=":")
        if label or self.label:
            self.axes.legend()
        self._maybe_set_labels(xlabel, ylabel)

        # Store scatter object for colorbar
        self._scatter = scatter

    def add_colorbar(self, label: str | None = None) -> None:
        """Add a colorbar to the scatter plot."""
        if hasattr(self, '_scatter') and self.figure:
            # Access the matplotlib figure from PlotXFigure
            if hasattr(self.figure, 'fig'):
                cbar = self.figure.fig.colorbar(self._scatter, ax=self.axes)
            elif hasattr(self.figure, 'colorbar'):
                cbar = self.figure.colorbar(self._scatter, ax=self.axes)
            else:
                # Fallback to matplotlib
                import matplotlib.pyplot as plt
                cbar = plt.colorbar(self._scatter, ax=self.axes)

            if label:
                cbar.set_label(label)
