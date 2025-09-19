"""Fount SDK Documentation

This module provides the main Fount client for interacting with the Fount API.
"""

from typing import Dict, List, Optional
from fount.dataset import Dataset
from fount.jobs import InferenceJob, TrainingJob, TuningJob
from .transport import HTTPTransport
from .models import Config
from pandas.core.frame import DataFrame
import logging
import httpx
import os
import csv

logger = logging.getLogger("fount")


class Fount:
    api_key: str | None

    def __init__(
        self, transport: Optional[httpx.Client] = None, logs: str | None = None
    ):
        """Main client for interacting with the Fount API.

            The Fount client provides a high-level interface for machine learning operations
            including dataset management, model training, fine-tuning, and inference on the
            Fount platform.

            Attributes:
                config (Config): Configuration object containing API settings
                client (httpx.Client): HTTP client for making API requests
                job_name (Optional[str]): Name of the current job context
                logs (Optional[str]): Path or configuration for logging

            Examples:
                Basic initialization:

                >>> from fount import Fount
                >>> client = Fount(api_key="your-api-key")
                >>> jobs = client.list_all_jobs()

                With custom transport configuration:

                >>> import httpx
                >>> transport = httpx.Client(
                ...     timeout=30.0,
                ...     limits=httpx.Limits(max_keepalive_connections=5)
                ... )
                >>> client = Fount(
                ...     api_key="your-api-key",
                ...     transport=transport,
                ...     job_name="production-training"
                ... )

                Using context manager for automatic cleanup:

                >>> with Fount(api_key="your-api-key") as client:
                ...     result = client.train(config)

        Note:
            The client maintains a persistent HTTP connection pool for efficiency.
            Remember to close the client when done or use it as a context manager.

        See Also:
            - :func:`create_client`: Factory function for creating clients
            - :func:`from_env`: Create client from environment variables
            - :class:`Config`: Configuration class for client settings
        """
        self.config = Config()
        self.client = transport or HTTPTransport(
            base_url=self.config.fount_base_url,
            timeout=self.config.timeout,
            api_key=self.config.fount_api_key.get_secret_value(),
        )

    def upload_dataframe(
        self, dataframe: DataFrame, name: str | None = None
    ) -> Dataset:
        """Upload a pandas DataFrame to the Fount platform.

        Args:
            dataframe (DataFrame): The pandas DataFrame to upload. Must not be empty.
            name (str, optional): A descriptive name for the dataset. Defaults to None.

        Returns:
            Dataset: A Dataset object containing the ID of the uploaded dataset.

        Raises:
            ValueError: If the dataframe is empty.
            UploadError: If the upload fails due to network or server errors.

        Example:
            >>> df = pd.read_csv("sales_data.csv")
            >>> dataset = client.upload_dataframe(df, name="Q4_sales_2024")
            >>> print(f"Dataset ID: {dataset.id}")
        """
        if dataframe.empty:
            raise ValueError("Dataframe is empty. Cannot upload empty dataframe.")
        return Dataset.upload_dataframe(self.client, dataframe)

    def upload_csv(self, pathname: str, name: str | None) -> Dataset:
        """Upload a CSV file to the Fount platform.

        Args:
            pathname (str): Path to the CSV file to upload.
            name (str, optional): A descriptive name for the dataset.

        Returns:
            Dataset: A Dataset object containing the ID of the uploaded dataset.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            CSVParseError: If the CSV file cannot be parsed.
            UploadError: If the upload fails.

        Example:
            >>> dataset = client.upload_csv("data/sales_2024.csv", name="sales_data")
            >>> print(f"Uploaded dataset: {dataset.id}")
        """
        if not os.path.exists(pathname):
            raise FileNotFoundError("File does not exists")
        dataframe = csv.reader(open(pathname))
        return Dataset.upload_dataframe(self.client, dataframe)

    def upload_excel(self, pathname: str, sheet_name: str, name: str | None) -> Dataset:
        """Upload an Excel file to the Fount platform.

        Args:
            pathname (str): Path to the Excel file to upload.
            sheet_name (str): Name of the sheet to extract data from.
            name (str, optional): A descriptive name for the dataset.

        Returns:
            Dataset: A Dataset object containing the ID of the uploaded dataset.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            ValueError: If the specified sheet does not exist.
            UploadError: If the upload fails.

        Note:
            This method is not yet implemented.
        """
        ...

    def train(
        self,
        dataset: Dataset,
        categorical_cols: List[str],
        date_column: str,
        target: str,
        validation_data_required: bool,
        validation_split: float,
        **kwargs: Dict,
    ) -> TrainingJob:
        """Train a machine learning model on the Fount platform.

        Args:
            dataset (Dataset): The dataset to train on, obtained from upload methods.
            categorical_cols (List[str]): List of column names that contain categorical data.
            date_column (str): Name of the column containing date/time information.
            target (str): Name of the column to predict (target variable).
            validation_data_required (bool): Whether to split data for validation.
            validation_split (float): Proportion of data to use for validation (0.0 to 1.0).
            **kwargs: Additional training parameters such as:
                - epochs (int): Number of training epochs
                - batch_size (int): Batch size for training
                - learning_rate (float): Learning rate
                - early_stopping (bool): Enable early stopping
                - model_type (str): Type of model to train

        Returns:
            TrainingJob: A job object to track training progress and retrieve results.

        Raises:
            TrainingError: If training initialization fails.
            ValueError: If validation_split is not between 0 and 1.

        Example:
            >>> job = client.train(
            ...     dataset=my_dataset,
            ...     categorical_cols=["product_type", "region"],
            ...     date_column="order_date",
            ...     target="revenue",
            ...     validation_data_required=True,
            ...     validation_split=0.2,
            ...     epochs=100,
            ...     learning_rate=0.001
            ... )
            >>> status = job.status()
            >>> print(f"Training status: {status['state']}")
        """
        logger.info(f"Starting training for {dataset.id}")
        payload = {
            "dataset": dataset.id,
            "categorical_cols": categorical_cols,
            "date_col": date_column,
            "target_col": target,
            "validation_data_required": validation_data_required,
            "validation_split": validation_split,
            **kwargs,
        }
        return TrainingJob.run(self.client, "training", payload)

    def tune(
        self,
        categorical_cols: List[str],
        date_column: str,
        target: str,
        validation_data_required: bool,
        validation_split: float,
        **kwargs: Dict,
    ) -> TuningJob:
        """Fine-tune a model with hyperparameter optimization.

        Args:
            categorical_cols (List[str]): List of column names that contain categorical data.
            date_column (str): Name of the column containing date/time information.
            target (str): Name of the column to predict (target variable).
            validation_data_required (bool): Whether to split data for validation.
            validation_split (float): Proportion of data to use for validation (0.0 to 1.0).
            **kwargs: Additional tuning parameters such as:
                - param_grid (dict): Hyperparameter search space
                - n_trials (int): Number of tuning trials
                - optimization_metric (str): Metric to optimize
                - search_strategy (str): Search strategy (grid, random, bayesian)
                - base_model (str): Base model to tune

        Returns:
            TuningJob: A job object to track tuning progress and retrieve best parameters.

        Raises:
            TuningError: If tuning initialization fails.
            ValueError: If required parameters are invalid.

        Example:
            >>> job = client.tune(
            ...     categorical_cols=["category", "brand"],
            ...     date_column="timestamp",
            ...     target="sales",
            ...     validation_data_required=True,
            ...     validation_split=0.2,
            ...     param_grid={
            ...         "learning_rate": [0.001, 0.01, 0.1],
            ...         "batch_size": [32, 64, 128],
            ...         "dropout": [0.1, 0.2, 0.3]
            ...     },
            ...     n_trials=50
            ... )
            >>> best_params = job.metrics()["best_parameters"]
        """
        payload = {
            "categorical_cols": [categorical_cols],
            "date_col": date_column,
            "target_col": target,
            "validation_data_required": validation_data_required,
            "validation_split": validation_split,
            **kwargs,
        }
        return TuningJob.run(self.client, "tuning", payload)

    def inference(
        self, model_name: str, batch_size: int, **kwargs: Dict
    ) -> InferenceJob:
        """Run inference using a trained model.

        Args:
            model_name (str): Name or ID of the trained model to use for predictions.
            batch_size (int): Number of samples to process in each batch.
            **kwargs: Additional inference parameters such as:
                - input_dataset (str): ID of the dataset to run inference on
                - output_format (str): Format for predictions (csv, json, parquet)
                - include_probabilities (bool): Include prediction probabilities
                - threshold (float): Prediction threshold for classification
                - gpu_acceleration (bool): Use GPU for inference

        Returns:
            InferenceJob: A job object to track inference progress and retrieve predictions.

        Raises:
            InferenceError: If inference initialization fails.
            ValueError: If model_name is not found or batch_size is invalid.

        Example:
            >>> # Run batch inference on new data
            >>> inference_job = client.inference(
            ...     model_name="sales_forecast_v2",
            ...     batch_size=1000,
            ...     input_dataset=test_dataset.id,
            ...     include_probabilities=True
            ... )
            ...
            >>> # Wait for completion and get results
            >>> while inference_job.status()["state"] != "completed":
            ...     time.sleep(10)
            >>> predictions = inference_job.metrics()["predictions"]
        """
        payload = {"model_name": model_name, "batch_size": batch_size, **kwargs}
        return InferenceJob.run(self.client, "inference", payload)

    def close(self) -> None:
        """Close the HTTP client and release resources.

        This method should be called when you're done using the client to ensure
        proper cleanup of network connections and resources. Alternatively, use
        the client as a context manager for automatic cleanup.

        Example:
            >>> client = Fount()
            >>> # ... use client ...
            >>> client.close()

            Or use context manager:
            >>> with Fount() as client:
            ...     # ... use client ...
            ...     pass  # Automatically closed
        """
        self.client.close()
