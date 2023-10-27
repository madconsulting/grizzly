from abc import ABC, abstractmethod
from typing import Any, Optional

import pandas as pd

from grizzly_main.orchestrator.prefect_poc.tools.metrics import metric_func_dict, plot_confusion_matrix
from grizzly_main.orchestrator.prefect_poc.tools.mlflow_tools import save_dict


class BaseModel(ABC):
    """
    An abstract base class for machine learning models.
    """

    def __init__(self, params: Optional[dict[str, Any]] = None, verbose: int = -1):
        """
        Initialize the BaseModel instance.

        :param params: Model-specific parameters. Default is an empty dictionary.
        :param verbose: Verbose level
        """
        self.params = params if params else {}
        self.verbose = verbose
        # Arguments to be defined in child model classes
        self.model: Optional[Any] = None
        self.metric_list: Optional[list[str]] = None
        self.model_type: Optional[str] = None

    @abstractmethod
    def train(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        """
        Train the machine learning model.

        :param X_train: Training feature DataFrame.
        :param y_train: Training target Series.
        :return: None
        """

    @abstractmethod
    def predict(self, X: pd.DataFrame) -> pd.Series:
        """
        Make predictions using the trained model.

        :param X: Feature DataFrame for predictions.
        :return: Predicted values as a Series or a DataFrame.
        """

    @abstractmethod
    def evaluate(
        self,
        X_test: pd.DataFrame,
        y_test: pd.Series,
        eval_metrics: dict[str, Any],
        enable_mlflow_tracking: bool = False,
    ) -> dict[str, Any]:
        """
        Evaluate the model on a test set using the specified metrics.

        :param X_test: Test feature DataFrame.
        :param y_test: Test target Series.
        :param eval_metrics: Evaluation metric dictionary. Keys are metric names
                            (e.g., 'accuracy', 'mae', etc.), values are a dict of metric function kwargs
        :param enable_mlflow_tracking: True if saving evaluation metrics to MLflow is enabled, False otherwise.
        :return: Dictionary with evaluation scores for each metric
        """
        if self.model:
            metric_res = {}
            y_pred = self.predict(X=X_test)
            for eval_metric in eval_metrics.keys():
                if eval_metric in metric_func_dict.keys():
                    metric_val = metric_func_dict[eval_metric](y_test, y_pred, **eval_metrics[eval_metric])
                    if eval_metric == "confusion_matrix":
                        plot_confusion_matrix(
                            cm_result=metric_val,
                            enable_mlflow_tracking=enable_mlflow_tracking,
                            mlflow_artifact_path="evaluation_results",
                        )
                        metric_val = metric_val.tolist()  # To make it JSON serializable
                    metric_res.update({f"eval_{eval_metric}": metric_val})
                else:
                    raise NotImplementedError(f"Metric {eval_metric} not implemented yet")
            if enable_mlflow_tracking:
                save_dict(
                    data_dict=metric_res,
                    file_path="evaluation_metrics.json",
                    enable_mlflow_tracking=enable_mlflow_tracking,
                    mlflow_artifact_path="evaluation_results",
                )
            return metric_res
        raise ValueError("Model has not been trained yet.")

    @abstractmethod
    def train_with_cv(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        nfold: int,
        is_return_mean_of_metrics: bool = True,
    ) -> Any:
        """
        Train the model with cross-validation.

        :param X: Feature DataFrame for cross-validation.
        :param y: Target Series for cross-validation.
        :param nfold: Number of cross-validation folds.
        :param is_return_mean_of_metrics: If this flag is True we return only the mean of each metric at the end of
                                  training, otherwise we return the history of metric mean and standard
                                  deviation for every boosting round
        :return: Cross validation results
        """
