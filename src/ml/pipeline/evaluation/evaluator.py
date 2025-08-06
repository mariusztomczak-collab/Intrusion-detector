import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)
import mlflow
from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class ModelEvaluator:
    """Class for evaluating model performance."""
    
    def __init__(self, model_name: str):
        """
        Initialize the ModelEvaluator.
        
        Args:
            model_name (str): Name of the model being evaluated
        """
        self.model_name = model_name
        self.metrics = {}
    
    def evaluate(self, y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray) -> Dict[str, float]:
        """
        Evaluate model performance using various metrics.
        
        Args:
            y_true (np.ndarray): True labels
            y_pred (np.ndarray): Predicted labels
            y_prob (np.ndarray): Predicted probabilities
            
        Returns:
            Dict[str, float]: Dictionary of evaluation metrics
        """
        try:
            # Calculate metrics
            self.metrics = {
                'accuracy': accuracy_score(y_true, y_pred),
                'precision': precision_score(y_true, y_pred),
                'recall': recall_score(y_true, y_pred),
                'f1': f1_score(y_true, y_pred),
                'roc_auc': roc_auc_score(y_true, y_prob)
            }
            
            # Log metrics to MLflow
            for metric_name, metric_value in self.metrics.items():
                mlflow.log_metric(f"{self.model_name}_{metric_name}", metric_value)
            
            # Log confusion matrix
            cm = confusion_matrix(y_true, y_pred)
            mlflow.log_metric(f"{self.model_name}_tn", cm[0, 0])
            mlflow.log_metric(f"{self.model_name}_fp", cm[0, 1])
            mlflow.log_metric(f"{self.model_name}_fn", cm[1, 0])
            mlflow.log_metric(f"{self.model_name}_tp", cm[1, 1])
            
            # Log classification report
            report = classification_report(y_true, y_pred, output_dict=True)
            for label, metrics in report.items():
                if isinstance(metrics, dict):
                    for metric_name, metric_value in metrics.items():
                        mlflow.log_metric(f"{self.model_name}_{label}_{metric_name}", metric_value)
            
            logger.info(f"Model {self.model_name} evaluation completed successfully")
            return self.metrics
            
        except Exception as e:
            logger.error(f"Error during model evaluation: {str(e)}")
            raise
    
    def get_metrics(self) -> Dict[str, float]:
        """
        Get the calculated metrics.
        
        Returns:
            Dict[str, float]: Dictionary of evaluation metrics
        """
        return self.metrics 