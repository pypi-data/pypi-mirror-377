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
        expected_columns = ['Model', 'Category', 'Accuracy', 'Precision', 'Recall', 'F1']
        assert list(results.columns) == expected_columns
    
    def test_benchmark_dataframe_rows(self):
        """Test that the returned DataFrame has the expected number of rows."""
        results = benchmark(self.X, self.y)
        # Should have many models (20+)
        assert len(results) >= 20
    
    def test_benchmark_models_present(self):
        """Test that all expected models are present in results."""
        results = benchmark(self.X, self.y)
        expected_models = ['Logistic Regression', 'Random Forest', 'SVM (RBF)']
        # Check that at least the basic models are present
        model_names = set(results['Model'].tolist())
        for model in expected_models:
            assert model in model_names
    
    def test_benchmark_metrics_range(self):
        """Test that all metrics are between 0 and 1."""
        results = benchmark(self.X, self.y)
        for metric in ['Accuracy', 'Precision', 'Recall', 'F1']:
            assert all(0 <= val <= 1 for val in results[metric])
    
    def test_benchmark_custom_test_size(self):
        """Test benchmark with custom test size."""
        results = benchmark(self.X, self.y, test_size=0.3)
        assert isinstance(results, pd.DataFrame)
        assert len(results) >= 20
    
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
        assert len(results) >= 20
    
    def test_benchmark_specific_models(self):
        """Test benchmark with specific models."""
        results = benchmark(self.X, self.y, models=['Random Forest', 'Logistic Regression'])
        assert isinstance(results, pd.DataFrame)
        assert len(results) == 2
        model_names = set(results['Model'].tolist())
        assert 'Random Forest' in model_names
        assert 'Logistic Regression' in model_names
    
    def test_benchmark_model_categories(self):
        """Test benchmark with specific model categories."""
        results = benchmark(self.X, self.y, model_categories=['Linear Models'])
        assert isinstance(results, pd.DataFrame)
        assert len(results) >= 5  # Should have at least 5 linear models
        # All results should be from Linear Models category
        assert all(cat == 'Linear Models' for cat in results['Category'])
    
    def test_benchmark_exclude_models(self):
        """Test benchmark with excluded models."""
        results = benchmark(self.X, self.y, exclude_models=['Gaussian Process'])
        assert isinstance(results, pd.DataFrame)
        model_names = set(results['Model'].tolist())
        assert 'Gaussian Process' not in model_names
    
    def test_list_available_models(self):
        """Test list_available_models function."""
        from mlbench_lite import list_available_models
        models = list_available_models()
        assert isinstance(models, dict)
        assert 'Linear Models' in models
        assert 'Tree-based Models' in models
        assert 'Random Forest' in models['Tree-based Models']
    
    def test_get_model_info(self):
        """Test get_model_info function."""
        from mlbench_lite import get_model_info
        info = get_model_info()
        assert isinstance(info, pd.DataFrame)
        assert 'Category' in info.columns
        assert 'Model' in info.columns
        assert 'Description' in info.columns
        assert len(info) >= 20
