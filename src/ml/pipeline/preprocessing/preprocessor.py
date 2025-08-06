import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from typing import List, Tuple, Optional, Union
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataPreprocessor:
    def __init__(self):
        """
        Initialize the DataPreprocessor with feature configurations.
        """
        self.preprocessor = None
        
        # Define selected features
        self.selected_features = [
            'logged_in', 'count', 'serror_rate', 'srv_serror_rate', 'same_srv_rate',
            'dst_host_srv_count', 'dst_host_same_srv_rate', 'dst_host_serror_rate',
            'dst_host_srv_serror_rate', 'flag'
        ]
        
        # Define feature types
        self.categorical_features = ['flag']
        self.numerical_features = [f for f in self.selected_features if f not in self.categorical_features]
        
        logger.info(f"Initialized preprocessor with {len(self.numerical_features)} numerical and "
                   f"{len(self.categorical_features)} categorical features")
        
    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> 'DataPreprocessor':
        """
        Fit the preprocessor on training data.
        
        Args:
            X (pd.DataFrame): Input features
            y (pd.Series, optional): Target variable (not used)
            
        Returns:
            self: The fitted preprocessor
            
        Raises:
            ValueError: If required features are missing
        """
        # Validate input features
        missing_features = set(self.selected_features) - set(X.columns)
        if missing_features:
            raise ValueError(f"Missing required features: {missing_features}")
        
        # Create preprocessing pipelines
        numeric_transformer = Pipeline(steps=[
            ('scaler', StandardScaler())
        ])
        
        categorical_transformer = Pipeline(steps=[
            ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
        ])
        
        # Combine transformers
        self.preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, self.numerical_features),
                ('cat', categorical_transformer, self.categorical_features)
            ],
            remainder='drop'  # Drop any columns not specified in transformers
        )
        
        # Fit preprocessor
        self.preprocessor.fit(X)
        logger.info("Successfully fitted preprocessor")
            
        return self
        
    def transform(self, X: pd.DataFrame) -> np.ndarray:
        """
        Transform data using fitted preprocessor.
        
        Args:
            X (pd.DataFrame): Input features to transform
            
        Returns:
            np.ndarray: Transformed features
            
        Raises:
            ValueError: If preprocessor is not fitted
        """
        if self.preprocessor is None:
            raise ValueError("Preprocessor has not been fitted yet")
            
        # Transform the data
        X_transformed = self.preprocessor.transform(X)
        
        # For the flag feature, we only need one column (since it's binary)
        # If we have both S0 and SF columns, we'll keep only one
        if 'flag_SF' in self.get_feature_names():
            # Get the index of the flag_SF column
            feature_names = self.get_feature_names()
            sf_idx = feature_names.index('flag_SF')
            # Keep only the flag_SF column and all numerical features
            X_transformed = np.hstack([X_transformed[:, :len(self.numerical_features)], 
                                     X_transformed[:, sf_idx:sf_idx+1]])
            
        return X_transformed
    
    def fit_transform(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> np.ndarray:
        """
        Fit preprocessor and transform data in one step.
        
        Args:
            X (pd.DataFrame): Input features
            y (pd.Series, optional): Target variable (not used)
            
        Returns:
            np.ndarray: Transformed features
        """
        return self.fit(X, y).transform(X)
    
    def get_feature_names(self) -> List[str]:
        """
        Get names of features after preprocessing.
        
        Returns:
            list: List of feature names
            
        Raises:
            ValueError: If preprocessor is not fitted
        """
        if self.preprocessor is None:
            raise ValueError("Preprocessor has not been fitted yet")
            
        # Get feature names after preprocessing
        feature_names = []
        for name, transformer, features in self.preprocessor.transformers_:
            if name == 'num':
                feature_names.extend(features)
            elif name == 'cat':
                # Get one-hot encoded feature names
                encoder = transformer.named_steps['onehot']
                encoded_features = []
                for i, feature in enumerate(features):
                    # Only keep the SF flag feature
                    if feature == 'flag':
                        encoded_features.append('flag_SF')
                    else:
                        encoded_features.extend([f"{feature}_{val}" for val in encoder.categories_[i]])
                feature_names.extend(encoded_features)
            
        return feature_names



