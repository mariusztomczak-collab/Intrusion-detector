import logging
import os
from typing import Any, Dict, Optional

import mlflow
import mlflow.sklearn
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import cross_val_score
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ModelTrainer:
    def __init__(self, random_state: int = 42):
        """
        Initialize the ModelTrainer with model configurations.

        Args:
            random_state (int): Random seed for reproducibility
        """
        self.random_state = random_state
        self.models = {
            "logistic": LogisticRegression(
                random_state=random_state, max_iter=1000, class_weight="balanced"
            ),
            "decision_tree": DecisionTreeClassifier(
                random_state=random_state, class_weight="balanced"
            ),
            "xgboost": XGBClassifier(
                random_state=random_state,
                scale_pos_weight=1,
                use_label_encoder=False,
                eval_metric="logloss",
            ),
        }
        self.best_model = None
        self.best_model_name = None
        self.best_score = -np.inf

        # Log model configurations
        logger.info("Initialized models with configurations:")
        for name, model in self.models.items():
            logger.info(f"{name}: {model.get_params()}")

    def train_and_evaluate(
        self,
        X_train: np.ndarray,
        X_test: np.ndarray,
        y_train: np.ndarray,
        y_test: np.ndarray,
        experiment_name: str = "Intrusion Detection",
    ) -> Dict[str, Dict[str, float]]:
        """
        Train and evaluate multiple models, tracking results with MLflow.

        Args:
            X_train (np.ndarray): Training features
            X_test (np.ndarray): Test features
            y_train (np.ndarray): Training labels
            y_test (np.ndarray): Test labels
            experiment_name (str): Name of the MLflow experiment

        Returns:
            dict: Dictionary containing evaluation metrics for all models

        Raises:
            ValueError: If input data shapes are invalid
        """
        # Validate input shapes
        if X_train.shape[1] != X_test.shape[1]:
            raise ValueError(
                f"Feature dimension mismatch: train {X_train.shape[1]} != test {X_test.shape[1]}"
            )
        if len(y_train) != X_train.shape[0]:
            raise ValueError(
                f"Train data length mismatch: X {X_train.shape[0]} != y {len(y_train)}"
            )
        if len(y_test) != X_test.shape[0]:
            raise ValueError(
                f"Test data length mismatch: X {X_test.shape[0]} != y {len(y_test)}"
            )

        # Set MLflow tracking URI if specified
        if os.getenv("MLFLOW_TRACKING_URI"):
            mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))

        mlflow.set_experiment(experiment_name)
        results = {}

        for model_name, model in self.models.items():
            logger.info(f"Training {model_name}...")

            try:
                with mlflow.start_run(run_name=model_name):
                    # Train the model
                    model.fit(X_train, y_train)

                    # Make predictions
                    y_pred = model.predict(X_test)
                    y_pred_proba = model.predict_proba(X_test)[:, 1]

                    # Calculate metrics
                    metrics = {
                        "accuracy": accuracy_score(y_test, y_pred),
                        "precision": precision_score(y_test, y_pred),
                        "recall": recall_score(y_test, y_pred),
                        "f1": f1_score(y_test, y_pred),
                        "roc_auc": roc_auc_score(y_test, y_pred_proba),
                    }

                    # Perform cross-validation
                    cv_scores = cross_val_score(
                        model, X_train, y_train, cv=5, scoring="f1"
                    )
                    metrics["cv_f1_mean"] = cv_scores.mean()
                    metrics["cv_f1_std"] = cv_scores.std()

                    # Log metrics to MLflow
                    mlflow.log_metrics(metrics)

                    # Log model parameters
                    mlflow.log_params(model.get_params())

                    # Save model
                    mlflow.sklearn.log_model(model, model_name)

                    results[model_name] = metrics

                    # Update best model if current model has better F1 score
                    if metrics["f1"] > self.best_score:
                        self.best_score = metrics["f1"]
                        self.best_model = model
                        self.best_model_name = model_name

                        # Register the best model in MLflow Model Registry
                        try:
                            mlflow.sklearn.log_model(
                                model,
                                "best_model",
                                registered_model_name="intrusion_detector",
                                input_example=X_train[:1],  # Log first training example
                                signature=mlflow.models.infer_signature(
                                    X_train, y_train
                                ),
                            )
                            logger.info(
                                f"Registered best model ({model_name}) in MLflow Model Registry"
                            )
                        except Exception as e:
                            logger.error(
                                f"Failed to register model in MLflow Model Registry: {str(e)}"
                            )

                    logger.info(f"{model_name} metrics: {metrics}")

            except Exception as e:
                logger.error(f"Error training {model_name}: {str(e)}", exc_info=True)
                continue

        if not results:
            raise ValueError("No models were successfully trained")

        logger.info(f"Best model: {self.best_model_name} (F1: {self.best_score:.4f})")
        return results

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions using the best model.

        Args:
            X (np.ndarray): Features to predict

        Returns:
            np.ndarray: Predicted labels

        Raises:
            ValueError: If no model has been trained
        """
        if self.best_model is None:
            raise ValueError("No model has been trained yet")
        return self.best_model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Get prediction probabilities using the best model.

        Args:
            X (np.ndarray): Features to predict

        Returns:
            np.ndarray: Prediction probabilities

        Raises:
            ValueError: If no model has been trained
        """
        if self.best_model is None:
            raise ValueError("No model has been trained yet")
        return self.best_model.predict_proba(X)
