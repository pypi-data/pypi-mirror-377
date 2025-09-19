"""
mlbench-lite: A simple machine learning benchmarking library.

This library provides a simple way to benchmark multiple machine learning models
on a dataset using scikit-learn.
"""

from .benchmark import benchmark, list_available_models, get_model_info
from .datasets import load_clover

__version__ = "2.0.2"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = ["benchmark", "load_clover", "list_available_models", "get_model_info"]
