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
    width: float | None = None
    height: float | None = None
    _axes: object = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if self.figure is None:
            # Create figure with specified dimensions if provided
            if self.width is not None or self.height is not None:
                # Convert pixel values to inches (assuming 100 DPI)
                width_inches = (self.width / 100) if self.width else 10.0
                height_inches = (self.height / 100) if self.height else 8.0
                self.figure = PlotXFigure(width=width_inches, height=height_inches)
            else:
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

    def set_title(self, title: str, fontsize: int = 14, fontweight: str = 'bold') -> None:
        """Set the chart title."""
        self.axes.set_title(title, fontsize=fontsize, fontweight=fontweight)

    def set_labels(self, xlabel: str | None = None, ylabel: str | None = None) -> None:
        """Set the x and y axis labels."""
        if xlabel:
            self.axes.set_xlabel(xlabel)
        if ylabel:
            self.axes.set_ylabel(ylabel)

    def add_legend(self, location: str = 'best') -> None:
        """Add a legend to the chart."""
        self.axes.legend(loc=location)

    def add_grid(self, visible: bool = True, alpha: float = 0.3, linestyle: str = '--', axis: str = 'both', color: str | None = None) -> None:
        """Add a grid to the chart."""
        grid_kwargs = {
            'alpha': alpha,
            'linestyle': linestyle,
            'axis': axis
        }
        if color is not None:
            grid_kwargs['color'] = color

        self.axes.grid(visible, **grid_kwargs)

    def save(self, filename: str, dpi: int = 300, bbox_inches: str = 'tight') -> None:
        """Save the chart to a file."""
        if self.figure and hasattr(self.figure, 'savefig'):
            self.figure.savefig(filename, dpi=dpi, bbox_inches=bbox_inches)
        else:
            # Fallback for when figure doesn't have savefig
            import matplotlib.pyplot as plt
            plt.savefig(filename, dpi=dpi, bbox_inches=bbox_inches)

    def show(self) -> None:
        """Display the chart."""
        if self.figure and hasattr(self.figure, 'show'):
            self.figure.show()
        else:
            # Fallback to matplotlib
            import matplotlib.pyplot as plt
            plt.show()

    def set_limits(self, xlim: tuple | None = None, ylim: tuple | None = None) -> None:
        """Set axis limits."""
        if xlim:
            self.axes.set_xlim(xlim)
        if ylim:
            self.axes.set_ylim(ylim)

    def set_theme(self, theme_name: str) -> None:
        """Set the chart theme."""
        # For now, just store the theme name
        self._theme = theme_name

    def set_background_color(self, color: str) -> None:
        """Set the background color."""
        if self.figure and hasattr(self.figure, 'patch'):
            self.figure.patch.set_facecolor(color)
        self.axes.set_facecolor(color)

    def enable_zoom_pan(self) -> None:
        """Enable zoom and pan functionality (placeholder)."""
        pass

    def enable_selection(self) -> None:
        """Enable selection functionality (placeholder)."""
        pass

    def enable_hover_tooltips(self) -> None:
        """Enable hover tooltips (placeholder)."""
        pass

    def enable_data_sampling(self, max_points: int = 5000) -> None:
        """Enable data sampling for performance (placeholder)."""
        self._max_points = max_points

    def enable_fast_rendering(self) -> None:
        """Enable fast rendering mode (placeholder)."""
        pass
