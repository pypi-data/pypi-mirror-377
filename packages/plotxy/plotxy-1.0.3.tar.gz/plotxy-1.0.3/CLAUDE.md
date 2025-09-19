# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Development Dependencies
```bash
pip install -e .[dev]
```

### Testing
```bash
pytest                    # Run all tests
pytest tests/core -k <pattern>  # Run targeted tests
pytest --maxfail=1 --disable-warnings  # Full suite with early exit
```

### Code Quality
```bash
ruff check src tests      # Lint checking
black --check src tests   # Format checking
```

### Gallery Demo
```bash
python sample.py          # Generate chart gallery
cd examples/react-gallery
npm install
npm run dev              # Start React gallery server
```

## Project Architecture

PlotX is a declarative plotting library built on Matplotlib with the following key architectural components:

### Core Components
- **PlotXFigure** (`src/plotx/figure.py`): Central figure management class that wraps Matplotlib figures with theming, layout helpers, and export utilities
- **BaseChart** (`src/plotx/charts/base.py`): Abstract base class providing common chart scaffolding, validation, and axes binding
- **PlotXTheme** (`src/plotx/theme.py`): Theming system for consistent styling across chart types

### Chart Types
- **LineChart** (`src/plotx/charts/line.py`): Line and curve plotting
- **ScatterChart** (`src/plotx/charts/scatter.py`): Scatter plot implementations
- **BarChart** (`src/plotx/charts/bar.py`): Bar and column charts
- **SurfaceChart** (`src/plotx/charts/surface.py`): 3D surface plots with mesh export

### Engineering Utilities
- **BodePlot** (`src/plotx/engineering/bode.py`): Frequency response analysis
- **StressStrainChart** (`src/plotx/engineering/stress.py`): Material testing visualization

### Gallery System
The `sample.py` script generates a comprehensive gallery of charts with metadata that feeds into a React-based viewer in `examples/react-gallery/`. The React app provides interactive exploration with search, filtering, and 3D surface interaction.

## Code Conventions

### Python Style
- Follow PEP 8 with Black formatting (≤88 characters)
- Use type hints for all function signatures and class members
- Prefer `pathlib.Path` for filesystem operations
- Export public APIs through module-level `__all__` lists

### Chart Implementation Patterns
- All charts inherit from `BaseChart` and use its validation helpers
- Chart constructors accept a `PlotXFigure` instance or create one automatically
- Use `_validate_xy()` for input validation and `_maybe_set_labels()` for automatic labeling
- Support both standalone usage and subplot integration via `bind_axes()`

### Dependencies
- Core: `matplotlib>=3.7`, `numpy>=1.24`
- Engineering features: `scipy>=1.11` (optional)
- Development: `pytest`, `ruff`, `black`

## Testing Strategy

Tests are organized to mirror the source structure:
- `tests/test_charts.py`: Chart functionality and validation
- `tests/test_engineering.py`: Engineering-specific utilities
- Maintain ≥90% coverage across `src/plotx/`
- Use descriptive test names like `test_loader_handles_missing_files`

## Development Workflow

1. Make changes following the established patterns in existing chart implementations
2. Run `ruff check src tests` and `black --check src tests` before committing
3. Execute tests with `pytest --maxfail=1 --disable-warnings`
4. Test gallery generation with `python sample.py` to verify visual output
5. Use conventional commit prefixes (`feat:`, `fix:`, etc.)