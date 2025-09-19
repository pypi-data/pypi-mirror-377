"""Histogram chart helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np

from .base import BaseChart


@dataclass
class HistogramChart(BaseChart):
    """Convenience wrapper for histogram plots."""

    def hist(
        self,
        data: Sequence[float] | Iterable[float],
        bins: int = 30,
        alpha: float = 0.7,
        color: str = 'blue',
        density: bool = False,
        label: str | None = None,
    ) -> None:
        """Create a histogram."""
        data_array = np.asarray(list(data), dtype=float)

        self.axes.hist(
            data_array,
            bins=bins,
            alpha=alpha,
            color=color,
            density=density,
            label=label
        )

        if label:
            self.axes.legend()

    def plot(self, x, y, color: str = 'red', linewidth: float = 2, label: str | None = None) -> None:
        """Add a line plot (for overlaying curves on histograms)."""
        self.axes.plot(x, y, color=color, linewidth=linewidth, label=label)
        if label:
            self.axes.legend()