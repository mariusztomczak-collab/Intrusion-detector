import logging
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from preprocessing.preprocessor import DataPreprocessor

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_selected_features(data_path: str, n_features_to_select: int = 10) -> list:
    """
    Get the selected features from the training process.

    Args:
        data_path (str): Path to the dataset
        n_features_to_select (int): Number of features to select

    Returns:
        list: List of selected feature names
    """
    try:
        # Load data
        df = pd.read_csv(data_path)
        if df.empty:
            raise ValueError("Data file is empty")

        # Initialize preprocessor
        preprocessor = DataPreprocessor(n_features_to_select=n_features_to_select)

        # Prepare data
        df = preprocessor.prepare_data(df)

        # Separate features and target
        y = df["kind_of_activity"]
        X = df.drop(["kind_of_activity", "level"], axis=1)

        # Fit preprocessor
        preprocessor.fit(X, y)

        # Get selected features
        selected_features = preprocessor.get_feature_names()
        logger.info(f"Selected {len(selected_features)} features: {selected_features}")

        return selected_features

    except Exception as e:
        logger.error(f"Error getting selected features: {str(e)}")
        raise


if __name__ == "__main__":
    # Path to the dataset
    data_path = "data/processed/train.csv"  # Update this path as needed

    # Get selected features
    selected_features = get_selected_features(data_path)

    # Print selected features
    print("\nSelected Features:")
    for i, feature in enumerate(selected_features, 1):
        print(f"{i}. {feature}")
