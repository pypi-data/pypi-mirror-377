"""Engineering chart types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence, Tuple

import numpy as np
from scipy import signal

from .base import BaseChart


@dataclass
class BodePlot(BaseChart):
    """Convenience wrapper for Bode plots."""

    def plot(
        self,
        numerator: Sequence[float],
        denominator: Sequence[float],
        frequencies: Sequence[float] | None = None,
    ) -> 'PlotXFigure':
        """Create a Bode plot."""
        # Create transfer function
        system = signal.TransferFunction(numerator, denominator)

        # Generate frequency range if not provided
        if frequencies is None:
            w = np.logspace(-2, 3, 1000)
        else:
            w = np.asarray(frequencies)

        # Calculate frequency response
        w_rad, h = signal.freqresp(system, w)

        # Magnitude plot (top subplot)
        mag_db = 20 * np.log10(np.abs(h))
        self.axes.semilogx(w_rad, mag_db)
        self.axes.set_ylabel('Magnitude (dB)')
        self.axes.grid(True, which='both', alpha=0.3)

        # Phase plot would typically be a second subplot
        # For now, just return the figure
        return self.figure


@dataclass
class StressStrainChart(BaseChart):
    """Convenience wrapper for stress-strain curves."""

    def plot(
        self,
        strain: Sequence[float] | Iterable[float],
        stress: Sequence[float] | Iterable[float],
        yield_point: Tuple[float, float] | None = None,
        ultimate_point: Tuple[float, float] | None = None,
    ) -> None:
        """Create a stress-strain curve."""
        strain_array = np.asarray(list(strain), dtype=float)
        stress_array = np.asarray(list(stress), dtype=float)

        # Main curve
        self.axes.plot(strain_array, stress_array, 'b-', linewidth=2, label='Stress-Strain')

        # Mark special points
        if yield_point:
            self.axes.plot(yield_point[0], yield_point[1], 'ro', markersize=8, label='Yield Point')

        if ultimate_point:
            self.axes.plot(ultimate_point[0], ultimate_point[1], 'rs', markersize=8, label='Ultimate Strength')

        self.axes.set_xlabel('Strain')
        self.axes.set_ylabel('Stress (MPa)')
        self.axes.grid(True, alpha=0.3)
        self.axes.legend()