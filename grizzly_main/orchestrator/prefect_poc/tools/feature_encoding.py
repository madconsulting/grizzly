from typing import Any

import pandas as pd
from sklearn.preprocessing import LabelEncoder, OrdinalEncoder

from grizzly_main.orchestrator.prefect_poc.tools.mlflow_tools import save_joblib


class FeatureEncoding:
    """
    Feature encoding functionality
    """

    def __init__(
        self,
        is_categorical_features_encoder: bool = True,
        is_label_encoder: bool = True,
        enable_mlflow_tracking: bool = False,
    ):
        """
        Initialize FeatureEncoding class

        :param is_categorical_features_encoder: True if using a categorical features encoder
        :param is_label_encoder: True if using a label encoder
        :param enable_mlflow_tracking: True if MLflow tracking is enabled, False otherwise.
        """
        self.is_categorical_features_encoder = is_categorical_features_encoder
        self.is_label_encoder = is_label_encoder
        self.encoder_dict: dict[str, Any] = {}
        self.enable_mlflow_tracking = enable_mlflow_tracking

    def _categorical_features_encoder(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Categorical features encoder

        :param X: Feature DataFrame
        :return: Encoded feature DataFrame
        """
        enc = OrdinalEncoder()
        X_enc = enc.fit_transform(X)
        X = pd.DataFrame(X_enc)
        save_joblib(
            object_to_store=enc,
            file_path="categorical_features_encoder.joblib",
            enable_mlflow_tracking=self.enable_mlflow_tracking,
            mlflow_artifact_path="encoders",
        )
        self.encoder_dict.update({"ordinal_encoder": enc})
        return X

    def _label_encoder(self, y: pd.Series) -> pd.Series:
        """
        Label encoder

        :param y: Target Series
        :return: Encoded target Series
        """
        enc = LabelEncoder()
        y = pd.Series(enc.fit_transform(y))
        save_joblib(
            object_to_store=enc,
            file_path="label_encoder.joblib",
            enable_mlflow_tracking=self.enable_mlflow_tracking,
            mlflow_artifact_path="encoders",
        )
        self.encoder_dict.update({"label_encoder": enc})
        return y

    def run_process(
        self,
        X: pd.DataFrame,
        y: pd.Series,
    ) -> tuple[pd.DataFrame, pd.Series]:
        """
        Run main process of FeatureEncoding class, to execute all the encoders

        :param X: Feature DataFrame
        :param y: Target Series
        :return: Encoded feature DataFrame and encoded target Series
        """
        if self.is_categorical_features_encoder:
            X = self._categorical_features_encoder(X=X)
        if self.is_label_encoder:
            y = self._label_encoder(y=y)
        return X, y
