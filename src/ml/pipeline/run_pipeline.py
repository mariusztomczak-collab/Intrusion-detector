import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from pathlib import Path
import joblib
import mlflow
import mlflow.sklearn
from preprocessing.preprocessor import DataPreprocessor
from training.trainer import ModelTrainer
from evaluation.evaluator import ModelEvaluator
import logging
import os
from typing import Dict, Any, Optional, Tuple
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set MLflow tracking URI
mlflow.set_tracking_uri("http://localhost:5000")

def load_data(data_path: str) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Load and prepare the dataset using only the selected features.
    Convert target variable to binary (0 for normal, 1 for any attack).
    
    Args:
        data_path (str): Path to the dataset
        
    Returns:
        tuple: Features (X) and target variable (y)
        
    Raises:
        FileNotFoundError: If data file doesn't exist
        ValueError: If data file is empty or invalid
    """
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data file not found: {data_path}")
        
    logger.info(f"Loading data from {data_path}")
    try:
        # Define KDD column names
        columns = [
            'duration','protocol_type','service','flag','src_bytes','dst_bytes','land','wrong_fragment',
            'urgent','hot','num_failed_logins','logged_in','num_compromised','root_shell','su_attempted',
            'num_root','num_file_creations','num_shells','num_access_files','num_outbound_cmds','is_host_login',
            'is_guest_login','count','srv_count','serror_rate','srv_serror_rate','rerror_rate',
            'srv_rerror_rate','same_srv_rate','diff_srv_rate','srv_diff_host_rate','dst_host_count',
            'dst_host_srv_count','dst_host_same_srv_rate','dst_host_diff_srv_rate',
            'dst_host_same_src_port_rate','dst_host_srv_diff_host_rate','dst_host_serror_rate',
            'dst_host_srv_serror_rate','dst_host_rerror_rate','dst_host_srv_rerror_rate','kind_of_activity','level'
        ]
        
        # Load data without header and assign column names
        df = pd.read_csv(data_path, header=None, names=columns)
        if df.empty:
            raise ValueError("Data file is empty")
            
        # Define selected features (matching DataPreprocessor)
        selected_features = [
            'logged_in', 'count', 'serror_rate', 'srv_serror_rate', 'same_srv_rate',
            'dst_host_srv_count', 'dst_host_same_srv_rate', 'dst_host_serror_rate',
            'dst_host_srv_serror_rate', 'flag'
        ]
        
        # Select only the required features
        X = df[selected_features]
        
        # Convert target to binary (0 for normal, 1 for any attack)
        y = (df['kind_of_activity'] != 'normal').astype(int)
        
        logger.info(f"Loaded data with {len(X)} samples and {len(X.columns)} selected features")
        logger.info(f"Target distribution: {y.value_counts().to_dict()}")
        return X, y
        
    except Exception as e:
        raise ValueError(f"Error loading data: {str(e)}")

def run_pipeline(
    train_data_path: str,
    test_data_path: str,
    n_features_to_select: int = 10,
    random_state: int = 42
) -> Dict[str, Dict[str, float]]:
    """
    Run the complete machine learning pipeline.
    
    Args:
        train_data_path (str): Path to the training dataset
        test_data_path (str): Path to the test dataset
        n_features_to_select (int): Number of features to select
        random_state (int): Random state for reproducibility
        
    Returns:
        dict: Dictionary containing evaluation metrics for all models
        
    Raises:
        ValueError: If pipeline execution fails
    """
    try:
        # Create artifacts directory if it doesn't exist
        artifacts_dir = Path("artifacts")
        artifacts_dir.mkdir(exist_ok=True)
        
        # Load training data
        X_train, y_train = load_data(train_data_path)
        
        # Load test data
        X_test, y_test = load_data(test_data_path)
        
        logger.info(f"Loaded training data: {len(X_train)} samples")
        logger.info(f"Loaded test data: {len(X_test)} samples")
        
        # Initialize preprocessor
        preprocessor = DataPreprocessor()
        
        # Fit and transform training data
        logger.info("Preprocessing training data...")
        X_train_processed = preprocessor.fit_transform(X_train, y_train)
        
        # Save only the fitted ColumnTransformer with a custom name
        preprocessor_path = artifacts_dir / "preprocessor.joblib"
        joblib.dump(preprocessor.preprocessor, preprocessor_path, protocol=4)
        logger.info(f"Saved fitted ColumnTransformer to {preprocessor_path}")
        
        # Transform test data
        logger.info("Preprocessing test data...")
        X_test_processed = preprocessor.transform(X_test)
        
        # Get selected feature names
        selected_features = preprocessor.get_feature_names()
        logger.info(f"Selected {len(selected_features)} features: {selected_features}")
        
        # Initialize and run model trainer
        trainer = ModelTrainer(random_state=random_state)
        
        # Train and evaluate models
        logger.info("Training and evaluating models...")
        results = trainer.train_and_evaluate(
            X_train_processed,
            X_test_processed,
            y_train,
            y_test,
            experiment_name="Intrusion Detection"
        )
        
        return results
        
    except Exception as e:
        logger.error(f"Error running pipeline: {str(e)}", exc_info=True)
        raise

def main():
    """Main function to run the pipeline with command line arguments."""
    parser = argparse.ArgumentParser(description='Run intrusion detection pipeline')
    parser.add_argument('--train_data_path', type=str, required=True,
                      help='Path to the training dataset')
    parser.add_argument('--test_data_path', type=str, required=True,
                      help='Path to the test dataset')
    parser.add_argument('--n_features', type=int, default=10,
                      help='Number of features to select')
    parser.add_argument('--random_state', type=int, default=42,
                      help='Random state for reproducibility')
    
    args = parser.parse_args()
    
    try:
        results = run_pipeline(
            train_data_path=args.train_data_path,
            test_data_path=args.test_data_path,
            n_features_to_select=args.n_features,
            random_state=args.random_state
        )
        
        # Print final results
        logger.info("\nFinal Results:")
        for model_name, metrics in results.items():
            logger.info(f"\n{model_name.upper()} METRICS:")
            for metric_name, value in metrics.items():
                logger.info(f"{metric_name}: {value:.4f}")
                
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main() 