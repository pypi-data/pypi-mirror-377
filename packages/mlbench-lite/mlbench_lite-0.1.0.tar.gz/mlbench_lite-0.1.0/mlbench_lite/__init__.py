"""
mlbench-lite: A simple machine learning benchmarking library.

This library provides a simple way to benchmark multiple machine learning models
on a dataset using scikit-learn.
"""

from .benchmark import benchmark
from .datasets import load_clover

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = ["benchmark", "load_clover"]
