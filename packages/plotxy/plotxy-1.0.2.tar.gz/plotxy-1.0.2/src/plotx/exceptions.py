"""Custom exceptions for the PlotX library."""

from __future__ import annotations


class PlotXError(Exception):
    """Base exception for PlotX-related errors."""


class ThemeNotFoundError(PlotXError):
    """Raised when a requested theme key is not registered."""


class ChartValidationError(PlotXError):
    """Raised when chart inputs fail validation."""
