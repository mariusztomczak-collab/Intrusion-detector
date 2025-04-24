from typing import Any, Dict, List, Union
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator

class IntrusionDetectionModel:
    def __init__(self, model: BaseEstimator):
        self.model = model

    def predict(self, data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]]) -> np.ndarray:
        """
        Predict whether network traffic is malicious or normal.
        
        Args:
            data: Input data in various formats (DataFrame, dict, or list of dicts)
        
        Returns:
            numpy.ndarray: Predictions (1 for malicious, 0 for normal)
        """
        if isinstance(data, dict):
            data = pd.DataFrame([data])
        elif isinstance(data, list):
            data = pd.DataFrame(data)
        
        return self.model.predict(data)

    def predict_proba(self, data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]]) -> np.ndarray:
        """
        Predict probability of network traffic being malicious.
        
        Args:
            data: Input data in various formats (DataFrame, dict, or list of dicts)
        
        Returns:
            numpy.ndarray: Probability predictions
        """
        if isinstance(data, dict):
            data = pd.DataFrame([data])
        elif isinstance(data, list):
            data = pd.DataFrame(data)
        
        return self.model.predict_proba(data) 