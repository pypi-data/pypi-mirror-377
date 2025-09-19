"""
Core benchmarking functionality for mlbench-lite.
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')


def benchmark(X, y, test_size=0.2, random_state=42):
    """
    Benchmark multiple machine learning models on a dataset.
    
    Parameters
    ----------
    X : array-like of shape (n_samples, n_features)
        Training vectors, where n_samples is the number of samples
        and n_features is the number of features.
    y : array-like of shape (n_samples,)
        Target values (class labels).
    test_size : float, default=0.2
        Proportion of the dataset to include in the test split.
    random_state : int, default=42
        Controls the shuffling applied to the data before applying the split.
        
    Returns
    -------
    pandas.DataFrame
        A DataFrame containing the performance metrics for each model:
        - Model: Name of the model
        - Accuracy: Accuracy score
        - Precision: Precision score (macro-averaged)
        - Recall: Recall score (macro-averaged)
        - F1: F1 score (macro-averaged)
    """
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    # Define models to benchmark
    models = {
        'Logistic Regression': LogisticRegression(random_state=random_state, max_iter=1000),
        'Random Forest': RandomForestClassifier(random_state=random_state),
        'SVM': SVC(random_state=random_state)
    }
    
    # Store results
    results = []
    
    for model_name, model in models.items():
        try:
            # Train the model
            model.fit(X_train, y_train)
            
            # Make predictions
            y_pred = model.predict(X_test)
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, average='macro', zero_division=0)
            recall = recall_score(y_test, y_pred, average='macro', zero_division=0)
            f1 = f1_score(y_test, y_pred, average='macro', zero_division=0)
            
            results.append({
                'Model': model_name,
                'Accuracy': round(accuracy, 4),
                'Precision': round(precision, 4),
                'Recall': round(recall, 4),
                'F1': round(f1, 4)
            })
            
        except Exception as e:
            # If a model fails, add it with error values
            results.append({
                'Model': model_name,
                'Accuracy': 0.0,
                'Precision': 0.0,
                'Recall': 0.0,
                'F1': 0.0
            })
            print(f"Warning: {model_name} failed with error: {str(e)}")
    
    # Convert to DataFrame
    results_df = pd.DataFrame(results)
    
    # Sort by accuracy (descending)
    results_df = results_df.sort_values('Accuracy', ascending=False).reset_index(drop=True)
    
    return results_df
