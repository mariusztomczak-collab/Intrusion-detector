import logging
from pathlib import Path

import mlflow
import numpy as np
import pandas as pd
from preprocessing.preprocessor import DataPreprocessor
from sklearn.model_selection import train_test_split
from training.trainer import ModelTrainer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_data():
    """Load and prepare the dataset."""
    # For demonstration, we'll create a sample dataset
    # In production, you would load your actual dataset here
    data = pd.DataFrame(
        {
            "logged_in": [True, False, True, False, True],
            "count": [1, 2, 3, 4, 5],
            "serror_rate": [0.1, 0.2, 0.3, 0.4, 0.5],
            "srv_serror_rate": [0.1, 0.2, 0.3, 0.4, 0.5],
            "same_srv_rate": [0.8, 0.7, 0.9, 0.6, 0.8],
            "dst_host_srv_count": [10, 20, 30, 40, 50],
            "dst_host_same_srv_rate": [0.8, 0.7, 0.9, 0.6, 0.8],
            "dst_host_serror_rate": [0.1, 0.2, 0.3, 0.4, 0.5],
            "dst_host_srv_serror_rate": [0.1, 0.2, 0.3, 0.4, 0.5],
            "flag": ["SF", "S0", "SF", "S0", "SF"],
        }
    )

    # Create labels (0 for normal, 1 for malicious)
    labels = np.array([0, 1, 0, 1, 0])

    return data, labels


def main():
    # Set MLflow tracking URI
    mlflow.set_tracking_uri("http://localhost:5000")

    # Load data
    logger.info("Loading data...")
    X, y = load_data()

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Preprocess data
    logger.info("Preprocessing data...")
    preprocessor = DataPreprocessor()
    X_train_processed = preprocessor.fit_transform(X_train)
    X_test_processed = preprocessor.transform(X_test)

    # Train models
    logger.info("Training models...")
    trainer = ModelTrainer(random_state=42)
    results = trainer.train_and_evaluate(
        X_train_processed,
        X_test_processed,
        y_train,
        y_test,
        experiment_name="Intrusion Detection",
    )

    # Log results
    logger.info("Training results:")
    for model_name, metrics in results.items():
        logger.info(f"{model_name}:")
        for metric_name, value in metrics.items():
            logger.info(f"  {metric_name}: {value:.4f}")

    logger.info(f"Best model: {trainer.best_model_name} (F1: {trainer.best_score:.4f})")


if __name__ == "__main__":
    main()
