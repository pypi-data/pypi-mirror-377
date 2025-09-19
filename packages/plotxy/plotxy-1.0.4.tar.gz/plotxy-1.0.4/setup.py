#!/usr/bin/env python3
"""
PlotX Setup Configuration
High-performance visualization library with zero dependencies.
"""

from setuptools import setup, find_packages
import os

# Read long description from README
def read_long_description():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "PlotX: High-performance visualization library with zero dependencies"

# Read version from __init__.py
def read_version():
    version_file = os.path.join(os.path.dirname(__file__), 'src', 'plotx', '__init__.py')
    with open(version_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"\'')
    return "1.0.0"

setup(
    # Package metadata
    name="plotxy",
    version="1.0.4",
    author="Infinidatum Development Team",
    author_email="durai@infinidatum.net",
    description="High-performance visualization library with zero dependencies",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/plotx/plotxy",
    project_urls={
        "Bug Tracker": "https://github.com/plotx/plotxy/issues",
        "Documentation": "https://plotxy.readthedocs.io/",
        "Source Code": "https://github.com/plotx/plotxy",
        "Examples": "https://github.com/plotx/plotxy/tree/main/examples",
    },

    # Package configuration
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,

    # Dependencies
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.19.0",
    ],

    # Optional dependencies
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
            "mypy>=0.800",
        ],
        "web": [
            "tornado>=6.0.0",
        ],
        "jupyter": [
            "jupyter>=1.0.0",
            "ipywidgets>=7.0.0",
        ],
        "complete": [
            "tornado>=6.0.0",
            "jupyter>=1.0.0",
            "ipywidgets>=7.0.0",
        ],
    },

    # Package classification
    classifiers=[
        # Development status
        "Development Status :: 5 - Production/Stable",

        # Intended audience
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Education",

        # Topic classification
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Software Development :: Libraries :: Python Modules",

        # License
        "License :: OSI Approved :: MIT License",

        # Programming language
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",

        # Operating systems
        "Operating System :: OS Independent",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",

        # Environment
        "Environment :: Console",
        "Environment :: Web Environment",
        "Environment :: X11 Applications",
    ],

    # Keywords for discoverability
    keywords=[
        "visualization", "plotting", "charts", "graphs", "data-science",
        "matplotlib-alternative", "plotly-alternative", "zero-dependencies",
        "3d-visualization", "interactive-charts", "financial-charts",
        "real-time-plotting", "high-performance", "pure-python",
        "scientific-visualization", "engineering-plots", "dashboard",
        "webgl", "vr", "ar", "immersive-visualization"
    ],

    # Entry points
    entry_points={
        "console_scripts": [
            "plotxy-demo=plotx.cli:demo_command",
            "plotxy-gallery=plotx.cli:gallery_command",
            "plotxy-server=plotx.cli:server_command",
        ],
    },

    # Package data
    package_data={
        "plotx": [
            "templates/*.html",
            "static/*.js",
            "static/*.css",
            "themes/*.json",
            "examples/*.py",
        ],
    },

    # Zip safety
    zip_safe=False,
)