"""Common chart scaffolding for PlotX."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Sequence

import numpy as np

from ..exceptions import ChartValidationError
from ..figure import PlotXFigure


def _to_numpy(sequence: Sequence[float] | Iterable[float]) -> np.ndarray:
    return np.asarray(list(sequence), dtype=float)


@dataclass
class BaseChart:
    """Base class for all PlotX charts."""

    figure: PlotXFigure | None = None
    label: str | None = None
    autoset_labels: bool = True
    _axes: object = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if self.figure is None:
            self.figure = PlotXFigure()
        self._axes = self.figure.axes

    @property
    def axes(self):  # type: ignore[override]
        return self._axes

    def _validate_xy(
        self,
        x_values: Sequence[float] | Iterable[float],
        y_values: Sequence[float] | Iterable[float],
    ) -> tuple[np.ndarray, np.ndarray]:
        x = _to_numpy(x_values)
        y = _to_numpy(y_values)
        if x.size != y.size:
            raise ChartValidationError("x and y must be the same length")
        if not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)):
            raise ChartValidationError("x and y must contain finite numeric values")
        return x, y

    def _maybe_set_labels(self, xlabel: str | None, ylabel: str | None) -> None:
        if not self.autoset_labels:
            return
        if xlabel:
            self.axes.set_xlabel(xlabel)
        if ylabel:
            self.axes.set_ylabel(ylabel)

    def bind_axes(self, axes) -> None:
        """Bind operations to a different axes instance."""
        self._axes = axes
