"""
Custom datasets for mlbench-lite.
"""

import numpy as np
from sklearn.datasets import make_classification


def load_clover(return_X_y=False):
    """
    Load the clover dataset.
    
    This is a synthetic classification dataset with 4 classes representing
    different types of clover leaves.
    
    Parameters
    ----------
    return_X_y : bool, default=False
        If True, returns (data, target) instead of a Bunch object.
        
    Returns
    -------
    data : Bunch
        Dictionary-like object with the following attributes:
        - data : ndarray of shape (400, 4)
            The data matrix.
        - target : ndarray of shape (400,)
            The classification target.
        - feature_names : list of length 4
            The names of the dataset columns.
        - target_names : list of length 4
            The names of target classes.
        - DESCR : str
            The full description of the dataset.
    (data, target) : tuple if return_X_y is True
        A tuple of two ndarrays. The first containing a 2D array of shape
        (400, 4) with each row representing one sample, and the second
        containing the class labels (integers from 0 to 3) for each sample.
    """
    
    # Create synthetic clover dataset
    X, y = make_classification(
        n_samples=400,
        n_features=4,
        n_informative=4,
        n_redundant=0,
        n_classes=4,
        n_clusters_per_class=1,
        class_sep=1.5,
        random_state=42
    )
    
    # Feature names representing clover leaf characteristics
    feature_names = [
        'leaf_length',
        'leaf_width', 
        'petiole_length',
        'leaflet_count'
    ]
    
    # Target names representing different clover types
    target_names = [
        'white_clover',
        'red_clover', 
        'crimson_clover',
        'alsike_clover'
    ]
    
    # Create description
    DESCR = """
    Clover Dataset
    ==============
    
    A synthetic dataset representing different types of clover leaves.
    
    Features:
    - leaf_length: Length of the leaf in cm
    - leaf_width: Width of the leaf in cm  
    - petiole_length: Length of the petiole in cm
    - leaflet_count: Number of leaflets per leaf
    
    Classes:
    - white_clover: Trifolium repens
    - red_clover: Trifolium pratense
    - crimson_clover: Trifolium incarnatum
    - alsike_clover: Trifolium hybridum
    
    Samples: 400
    Features: 4
    Classes: 4
    """
    
    if return_X_y:
        return X, y
    
    from sklearn.utils import Bunch
    
    return Bunch(
        data=X,
        target=y,
        feature_names=feature_names,
        target_names=target_names,
        DESCR=DESCR
    )
