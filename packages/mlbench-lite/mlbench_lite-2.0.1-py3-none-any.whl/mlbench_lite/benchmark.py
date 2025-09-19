"""
Core benchmarking functionality for mlbench-lite.
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Import all available models
try:
    from sklearn.linear_model import LogisticRegression, RidgeClassifier, SGDClassifier
    from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, GradientBoostingClassifier, AdaBoostClassifier, BaggingClassifier
    from sklearn.svm import SVC, LinearSVC
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.naive_bayes import GaussianNB, MultinomialNB, BernoulliNB
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
    from sklearn.neural_network import MLPClassifier
    from sklearn.gaussian_process import GaussianProcessClassifier
    from sklearn.linear_model import Perceptron, PassiveAggressiveClassifier
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False

try:
    import catboost as cb
    CATBOOST_AVAILABLE = True
except ImportError:
    CATBOOST_AVAILABLE = False


def get_available_models():
    """
    Get all available models with their categories.
    
    Returns
    -------
    dict
        Dictionary with model categories as keys and lists of (name, model_class) tuples as values
    """
    models = {}
    
    if SKLEARN_AVAILABLE:
        models['Linear Models'] = [
            ('Logistic Regression', LogisticRegression(random_state=42, max_iter=1000)),
            ('Ridge Classifier', RidgeClassifier(random_state=42)),
            ('SGD Classifier', SGDClassifier(random_state=42)),
            ('Perceptron', Perceptron(random_state=42)),
            ('Passive Aggressive', PassiveAggressiveClassifier(random_state=42)),
        ]
        
        models['Tree-based Models'] = [
            ('Decision Tree', DecisionTreeClassifier(random_state=42)),
            ('Random Forest', RandomForestClassifier(random_state=42)),
            ('Extra Trees', ExtraTreesClassifier(random_state=42)),
            ('Gradient Boosting', GradientBoostingClassifier(random_state=42)),
            ('AdaBoost', AdaBoostClassifier(random_state=42)),
            ('Bagging Classifier', BaggingClassifier(random_state=42)),
        ]
        
        models['SVM Models'] = [
            ('SVM (RBF)', SVC(random_state=42)),
            ('SVM (Linear)', LinearSVC(random_state=42)),
        ]
        
        models['Neighbors'] = [
            ('K-Nearest Neighbors', KNeighborsClassifier()),
        ]
        
        models['Naive Bayes'] = [
            ('Gaussian Naive Bayes', GaussianNB()),
            ('Multinomial Naive Bayes', MultinomialNB()),
            ('Bernoulli Naive Bayes', BernoulliNB()),
        ]
        
        models['Discriminant Analysis'] = [
            ('Linear Discriminant Analysis', LinearDiscriminantAnalysis()),
            ('Quadratic Discriminant Analysis', QuadraticDiscriminantAnalysis()),
        ]
        
        models['Neural Networks'] = [
            ('Multi-layer Perceptron', MLPClassifier(random_state=42, max_iter=1000)),
        ]
        
        models['Gaussian Process'] = [
            ('Gaussian Process', GaussianProcessClassifier(random_state=42)),
        ]
    
    if XGBOOST_AVAILABLE:
        models['XGBoost'] = [
            ('XGBoost', xgb.XGBClassifier(random_state=42, eval_metric='logloss')),
        ]
    
    if LIGHTGBM_AVAILABLE:
        models['LightGBM'] = [
            ('LightGBM', lgb.LGBMClassifier(random_state=42, verbose=-1)),
        ]
    
    if CATBOOST_AVAILABLE:
        models['CatBoost'] = [
            ('CatBoost', cb.CatBoostClassifier(random_state=42, verbose=False)),
        ]
    
    return models


def benchmark(X, y, test_size=0.2, random_state=42, models=None, model_categories=None, exclude_models=None):
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
    models : list of str, optional
        Specific models to use. If None, uses all available models.
        Examples: ['Logistic Regression', 'Random Forest', 'XGBoost']
    model_categories : list of str, optional
        Categories of models to use. If None, uses all categories.
        Examples: ['Linear Models', 'Tree-based Models', 'XGBoost']
    exclude_models : list of str, optional
        Models to exclude from benchmarking.
        Examples: ['SVM (RBF)', 'Gaussian Process']
        
    Returns
    -------
    pandas.DataFrame
        A DataFrame containing the performance metrics for each model:
        - Model: Name of the model
        - Category: Category of the model
        - Accuracy: Accuracy score
        - Precision: Precision score (macro-averaged)
        - Recall: Recall score (macro-averaged)
        - F1: F1 score (macro-averaged)
    """
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    # Get available models
    available_models = get_available_models()
    
    # Filter models based on user selection
    selected_models = {}
    
    if models is not None:
        # User specified specific models
        for category, model_list in available_models.items():
            for name, model in model_list:
                if name in models:
                    if category not in selected_models:
                        selected_models[category] = []
                    selected_models[category].append((name, model))
    elif model_categories is not None:
        # User specified categories
        for category in model_categories:
            if category in available_models:
                selected_models[category] = available_models[category]
    else:
        # Use all available models
        selected_models = available_models.copy()
    
    # Remove excluded models
    if exclude_models is not None:
        for category in list(selected_models.keys()):
            selected_models[category] = [
                (name, model) for name, model in selected_models[category]
                if name not in exclude_models
            ]
            if not selected_models[category]:
                del selected_models[category]
    
    # Store results
    results = []
    
    for category, model_list in selected_models.items():
        for model_name, model in model_list:
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
                    'Category': category,
                    'Accuracy': round(accuracy, 4),
                    'Precision': round(precision, 4),
                    'Recall': round(recall, 4),
                    'F1': round(f1, 4)
                })
                
            except Exception as e:
                # If a model fails, add it with error values
                results.append({
                    'Model': model_name,
                    'Category': category,
                    'Accuracy': 0.0,
                    'Precision': 0.0,
                    'Recall': 0.0,
                    'F1': 0.0
                })
                print(f"Warning: {model_name} failed with error: {str(e)}")
    
    # Convert to DataFrame
    results_df = pd.DataFrame(results)
    
    if results_df.empty:
        print("No models were successfully trained. Please check your data and model selection.")
        return results_df
    
    # Sort by accuracy (descending)
    results_df = results_df.sort_values('Accuracy', ascending=False).reset_index(drop=True)
    
    return results_df


def list_available_models():
    """
    List all available models and their categories.
    
    Returns
    -------
    dict
        Dictionary with model categories as keys and lists of model names as values
    """
    available_models = get_available_models()
    model_list = {}
    
    for category, models in available_models.items():
        model_list[category] = [name for name, _ in models]
    
    return model_list


def get_model_info():
    """
    Get detailed information about available models.
    
    Returns
    -------
    pandas.DataFrame
        DataFrame with model information including category, name, and description
    """
    model_info = []
    
    model_info.append({
        'Category': 'Linear Models',
        'Model': 'Logistic Regression',
        'Description': 'Linear model for classification using logistic function'
    })
    model_info.append({
        'Category': 'Linear Models',
        'Model': 'Ridge Classifier',
        'Description': 'Linear classifier with L2 regularization'
    })
    model_info.append({
        'Category': 'Linear Models',
        'Model': 'SGD Classifier',
        'Description': 'Linear classifier using Stochastic Gradient Descent'
    })
    model_info.append({
        'Category': 'Linear Models',
        'Model': 'Perceptron',
        'Description': 'Simple linear classifier'
    })
    model_info.append({
        'Category': 'Linear Models',
        'Model': 'Passive Aggressive',
        'Description': 'Online learning algorithm for classification'
    })
    
    model_info.append({
        'Category': 'Tree-based Models',
        'Model': 'Decision Tree',
        'Description': 'Non-parametric supervised learning method'
    })
    model_info.append({
        'Category': 'Tree-based Models',
        'Model': 'Random Forest',
        'Description': 'Ensemble of decision trees with bagging'
    })
    model_info.append({
        'Category': 'Tree-based Models',
        'Model': 'Extra Trees',
        'Description': 'Extremely randomized trees ensemble'
    })
    model_info.append({
        'Category': 'Tree-based Models',
        'Model': 'Gradient Boosting',
        'Description': 'Boosting ensemble method using gradient descent'
    })
    model_info.append({
        'Category': 'Tree-based Models',
        'Model': 'AdaBoost',
        'Description': 'Adaptive boosting ensemble method'
    })
    model_info.append({
        'Category': 'Tree-based Models',
        'Model': 'Bagging Classifier',
        'Description': 'Bootstrap aggregating ensemble method'
    })
    
    model_info.append({
        'Category': 'SVM Models',
        'Model': 'SVM (RBF)',
        'Description': 'Support Vector Machine with RBF kernel'
    })
    model_info.append({
        'Category': 'SVM Models',
        'Model': 'SVM (Linear)',
        'Description': 'Support Vector Machine with linear kernel'
    })
    
    model_info.append({
        'Category': 'Neighbors',
        'Model': 'K-Nearest Neighbors',
        'Description': 'Instance-based learning algorithm'
    })
    
    model_info.append({
        'Category': 'Naive Bayes',
        'Model': 'Gaussian Naive Bayes',
        'Description': 'Naive Bayes classifier for Gaussian features'
    })
    model_info.append({
        'Category': 'Naive Bayes',
        'Model': 'Multinomial Naive Bayes',
        'Description': 'Naive Bayes classifier for multinomial features'
    })
    model_info.append({
        'Category': 'Naive Bayes',
        'Model': 'Bernoulli Naive Bayes',
        'Description': 'Naive Bayes classifier for binary features'
    })
    
    model_info.append({
        'Category': 'Discriminant Analysis',
        'Model': 'Linear Discriminant Analysis',
        'Description': 'Linear dimensionality reduction and classification'
    })
    model_info.append({
        'Category': 'Discriminant Analysis',
        'Model': 'Quadratic Discriminant Analysis',
        'Description': 'Quadratic classifier with Gaussian assumptions'
    })
    
    model_info.append({
        'Category': 'Neural Networks',
        'Model': 'Multi-layer Perceptron',
        'Description': 'Feedforward artificial neural network'
    })
    
    model_info.append({
        'Category': 'Gaussian Process',
        'Model': 'Gaussian Process',
        'Description': 'Probabilistic classifier using Gaussian processes'
    })
    
    if XGBOOST_AVAILABLE:
        model_info.append({
            'Category': 'XGBoost',
            'Model': 'XGBoost',
            'Description': 'Extreme gradient boosting framework'
        })
    
    if LIGHTGBM_AVAILABLE:
        model_info.append({
            'Category': 'LightGBM',
            'Model': 'LightGBM',
            'Description': 'Light gradient boosting machine'
        })
    
    if CATBOOST_AVAILABLE:
        model_info.append({
            'Category': 'CatBoost',
            'Model': 'CatBoost',
            'Description': 'Categorical boosting framework'
        })
    
    return pd.DataFrame(model_info)