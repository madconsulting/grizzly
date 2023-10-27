import logging
from typing import Any, Optional, Union

import lightgbm as lgbm
import pandas as pd

from grizzly_main.orchestrator.prefect_poc.tools.models.abstract_model import BaseModel


class LightGBMModel(BaseModel):
    """
    A class that encapsulates LightGBM model functionality
    """

    def __init__(
        self,
        params: Optional[dict[str, Any]] = None,
        verbose: int = -1,
        random_seed: int = 42,
    ):
        """
        Initialize the LightGBMModel instance

        :param params: LightGBM parameters. Default is an empty dictionary
        :param verbose: Verbose level
        :param random_seed: Random seed
        """
        super().__init__(params=params, verbose=verbose)
        if "verbose" in self.params.keys():
            raise ValueError("verbosity should be defined using the verbose argument of LightGBMModel, not in params")
        self.params["verbose"] = verbose
        self.params["random_state"] = random_seed
        self.model: Optional[lgbm.Booster] = None
        self.metric_list = self._verify_metric_param()
        self.problem_type = self._get_problem_type()

    def _verify_metric_param(self) -> list[str]:
        """
        Verify metric parameter, ensuring that we only have a single metric alias defined

        :return: List of metrics defined in parameters
        """
        # https://lightgbm.readthedocs.io/en/latest/Parameters.html#metric
        metric_aliases = ["metric", "metrics", "metric_types"]
        is_metric_defined = False
        metric_val = ""
        for metric in metric_aliases:
            if metric in self.params:
                if is_metric_defined:
                    raise ValueError("The metric field has been defined using multiple aliases")
                is_metric_defined = True
                metric_val = self.params[metric]
        if not is_metric_defined:
            raise ValueError(
                f"Please define the metric argument in LightGBMModel, using any of its aliases: {metric_aliases}"
            )
        return metric_val.split(",")

    def _get_problem_type(self) -> str:
        """
        Get the problem type ('classification', 'multi-classification' or 'regression') from the objective field
        in params

        :return: Problem type
        """
        objective = self.params["objective"]
        # See https://lightgbm.readthedocs.io/en/latest/Parameters.html#objective
        if objective in ["binary"]:
            problem_type = "classification"
        elif objective in ["multiclass", "multiclassova", "num_class"]:
            problem_type = "multi-classification"
        elif objective in [
            "regression",
            "regression",
            "huber",
            "fair",
            "poisson",
            "quantile",
            "mape",
            "gamma",
            "tweedie",
        ]:
            problem_type = "regression"
        else:
            raise NotImplementedError(f"Problem type not specified yet for objective: {objective}")
        return problem_type

    @staticmethod
    def _get_dataset(X: pd.DataFrame, y: pd.Series) -> lgbm.Dataset:
        """
        Get LightGBM dataset from feature DataFrame and target Series.

        :param X: Feature DataFrame
        :param y: Target Series
        :return: LightGBM dataset
        """
        return lgbm.Dataset(data=X, label=y)

    def train(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        """
        Train the LightGBM model

        :param X_train: Training feature DataFrame
        :param y_train: Training target Series
        :return: None
        """
        train_set = self._get_dataset(X=X_train, y=y_train)
        self.model = lgbm.train(params=self.params, train_set=train_set, valid_sets=[train_set])
        logging.info("LightGBM model trained")

    def predict(self, X: pd.DataFrame) -> pd.Series:
        """
        Make predictions using the trained LightGBM model

        :param X: Feature DataFrame for predictions
        :return: Predicted values as a Series.
        """
        if self.model:
            pred = self.model.predict(X)
            if pred.shape[1] > 1:  # type: ignore
                pred = pd.DataFrame(pred, index=X.index)
                if self.problem_type == "multi-classification":
                    return pred.idxmax(axis=1)
                raise ValueError(f"Multiple prediction columns not expected for problem type: {self.problem_type}")
            else:
                pred = pd.Series(pred, index=X.index)
                if self.problem_type == "classification":
                    pred = pred.astype(int)
                return pred
        raise ValueError("Model has not been trained yet.")

    def train_with_cv(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        nfold: int = 5,
        is_return_mean_of_metrics: bool = True,
    ) -> Union[dict[str, list[Union[int, float]]], dict[str, Union[int, float]]]:
        """
        Train the LightGBM model with cross-validation

        :param X: Feature DataFrame for cross-validation
        :param y: Target Series for cross-validation
        :param nfold : Number of cross-validation folds. Default is 5
        :param is_return_mean_of_metrics: If this flag is True we return only the mean of each metric at the end of
                                          training, otherwise we return the history of metric mean and standard
                                          deviation for every boosting round
        :return: Cross-validation results
        """
        train_set = self._get_dataset(X=X, y=y)
        cv_results = lgbm.cv(
            params=self.params,
            train_set=train_set,
            nfold=nfold,
        )
        logging.info("LightGBM model trained with cross-validation")
        if is_return_mean_of_metrics:
            metrics_res = {}
            for metric in self.metric_list:  # type: ignore
                metric_mean_field = f"valid {metric}-mean"
                metrics_res.update({metric: cv_results[metric_mean_field][-1]})  # type: ignore
            return metrics_res
        else:
            return cv_results  # type: ignore

    def evaluate(
        self,
        X_test: pd.DataFrame,
        y_test: pd.Series,
        eval_metrics: dict[str, Any],
        enable_mlflow_tracking: bool = False,
    ) -> dict[str, Any]:
        """
        Evaluate the model on a test set using the specified metrics

        :param X_test: Test feature DataFrame
        :param y_test: Test target Series
        :param eval_metrics: Evaluation metric dictionary. Keys are metric names
                            (e.g., 'accuracy', 'mae', etc.), values are a dict of metric function kwargs
        :param enable_mlflow_tracking: True if saving evaluation metrics to MLflow is enabled, False otherwise
        :return: Dictionary with evaluation scores for each metric
        """
        return super().evaluate(
            X_test=X_test,
            y_test=y_test,
            eval_metrics=eval_metrics,
            enable_mlflow_tracking=enable_mlflow_tracking,
        )


if __name__ in "__main__":
    from sklearn.datasets import load_iris
    from sklearn.model_selection import train_test_split

    # Load the Iris dataset
    data = load_iris()
    X_ = pd.DataFrame(data.data, columns=data.feature_names)
    y_ = pd.Series(data.target, name="target")

    # Split the dataset into training and testing sets
    X_train_, X_test_, y_train_, y_test_ = train_test_split(X_, y_, test_size=0.2, random_state=42)

    # Initialize the LightGBMModel instance for classification
    # See parameters in https://lightgbm.readthedocs.io/en/latest/Parameters.html#
    model = LightGBMModel(
        params={
            "objective": "multiclass",  # Multi-class classification
            "num_class": 3,  # Number of classes in the target variable
            "metric": "multi_logloss",  # Log loss as the evaluation metric
            "n_jobs": -1,  # Use all available cores for parallelism
        },
        verbose=-1,
    )

    # Train the model
    model.train(X_train=X_train_, y_train=y_train_)

    # Train the model with cross-validation
    metrics_res_ = model.train_with_cv(X=X_, y=y_, nfold=3, is_return_mean_of_metrics=True)
    print("Metric val results from training with CV:")
    print(metrics_res_)

    # Make predictions on the test set
    pred_df = model.predict(X=X_test_)
    print("Predictions (Probabilities for each class):")
    print(pred_df)

    # Evaluate model
    metrics_res_ = model.evaluate(
        X_test=X_test_,
        y_test=y_test_,
        eval_metrics={
            "accuracy": {},
            "f1_score": {"average": "weighted"},
            "confusion_matrix": {},
        },
    )
    print(f"Evaluation metrics results: {metrics_res_}")
