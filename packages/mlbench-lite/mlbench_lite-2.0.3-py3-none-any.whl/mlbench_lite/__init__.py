"""
mlbench-lite: A Pypi machine learning benchmarking library to make life easier.

This library provides a simple ways to benchmark multiple machine learning models
on a dataset using scikit-learn.
"""

from .benchmark import benchmark, list_available_models, get_model_info
from .datasets import load_clover

__version__ = "2.0.3"
__author__ = "Arefin Amin"
__email__ = "arefinamin994@gmail.com"

__all__ = ["benchmark", "load_clover", "list_available_models", "get_model_info"]
