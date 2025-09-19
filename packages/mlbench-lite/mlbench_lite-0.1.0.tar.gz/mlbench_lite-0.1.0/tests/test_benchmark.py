"""
Unit tests for mlbench-lite benchmark functionality.
"""

import pytest
import pandas as pd
import numpy as np
from sklearn.datasets import make_classification
from mlbench_lite.benchmark import benchmark


class TestBenchmark:
    """Test cases for the benchmark function."""
    
    def setup_method(self):
        """Set up test data before each test method."""
        # Create a simple classification dataset
        self.X, self.y = make_classification(
            n_samples=1000,
            n_features=10,
            n_informative=8,
            n_redundant=2,
            n_classes=3,
            random_state=42
        )
    
    def test_benchmark_returns_dataframe(self):
        """Test that benchmark returns a pandas DataFrame."""
        results = benchmark(self.X, self.y)
        assert isinstance(results, pd.DataFrame)
    
    def test_benchmark_dataframe_columns(self):
        """Test that the returned DataFrame has the expected columns."""
        results = benchmark(self.X, self.y)
        expected_columns = ['Model', 'Accuracy', 'Precision', 'Recall', 'F1']
        assert list(results.columns) == expected_columns
    
    def test_benchmark_dataframe_rows(self):
        """Test that the returned DataFrame has the expected number of rows."""
        results = benchmark(self.X, self.y)
        # Should have 3 models: Logistic Regression, Random Forest, SVM
        assert len(results) == 3
    
    def test_benchmark_models_present(self):
        """Test that all expected models are present in results."""
        results = benchmark(self.X, self.y)
        expected_models = ['Logistic Regression', 'Random Forest', 'SVM']
        assert set(results['Model'].tolist()) == set(expected_models)
    
    def test_benchmark_metrics_range(self):
        """Test that all metrics are between 0 and 1."""
        results = benchmark(self.X, self.y)
        for metric in ['Accuracy', 'Precision', 'Recall', 'F1']:
            assert all(0 <= val <= 1 for val in results[metric])
    
    def test_benchmark_custom_test_size(self):
        """Test benchmark with custom test size."""
        results = benchmark(self.X, self.y, test_size=0.3)
        assert isinstance(results, pd.DataFrame)
        assert len(results) == 3
    
    def test_benchmark_custom_random_state(self):
        """Test benchmark with custom random state."""
        results1 = benchmark(self.X, self.y, random_state=123)
        results2 = benchmark(self.X, self.y, random_state=123)
        # Results should be identical with same random state
        pd.testing.assert_frame_equal(results1, results2)
    
    def test_benchmark_different_random_states(self):
        """Test that different random states produce different results."""
        results1 = benchmark(self.X, self.y, random_state=123)
        results2 = benchmark(self.X, self.y, random_state=456)
        # Results should be different with different random states
        assert not results1.equals(results2)
    
    def test_benchmark_sorted_by_accuracy(self):
        """Test that results are sorted by accuracy in descending order."""
        results = benchmark(self.X, self.y)
        accuracies = results['Accuracy'].tolist()
        assert accuracies == sorted(accuracies, reverse=True)
    
    def test_benchmark_with_small_dataset(self):
        """Test benchmark with a very small dataset."""
        X_small, y_small = make_classification(
            n_samples=50,
            n_features=5,
            n_classes=2,
            random_state=42
        )
        results = benchmark(X_small, y_small)
        assert isinstance(results, pd.DataFrame)
        assert len(results) == 3
