import logging
import warnings
from typing import Any, Optional
from uuid import uuid4

import featuretools as ft
import pandas as pd

from grizzly_main.orchestrator.prefect_poc.adventure_works_pipeline.configs.dataset_info import (
    dataset_fields as default_dataset_fields,
)
from grizzly_main.orchestrator.prefect_poc.adventure_works_pipeline.configs.dataset_info import (
    dataset_relationships as default_dataset_relationships,
)
from grizzly_main.orchestrator.prefect_poc.tools.mlflow_tools import save_dict

# Filter out the FutureWarning related to is_categorical_dtype
warnings.filterwarnings("ignore", category=FutureWarning, module="woodwork")


class FeatureToolsEngineering:
    """
    Feature engineering using featuretools library
    """

    def __init__(
        self,
        df_dict: dict[str, pd.DataFrame],
        dataset_fields: Optional[dict[str, dict[str, Any]]] = None,
        dataset_relationships: Optional[list[dict[str, str]]] = None,
        entity_set_id: Optional[str] = None,
        enable_mlflow_tracking: bool = False,
    ):
        """
        Initialize FeatureToolsEngineering class

        :param df_dict: Dictionary of data group DataFrame's
        :param dataset_fields: Dataset fields
        :param dataset_relationships: Dataset relationships
        :param entity_set_id: Entity set id
        :param enable_mlflow_tracking: True if MLflow tracking is enabled, False otherwise.
        """
        if entity_set_id is None:
            entity_set_id = str(uuid4())
        self.entity_set_id = entity_set_id
        logging.info(f"Entity set id: {self.entity_set_id}")
        if dataset_fields is None:
            dataset_fields = default_dataset_fields
        self.dataset_fields = dataset_fields
        if dataset_relationships is None:
            dataset_relationships = default_dataset_relationships
        self.dataset_relationships = dataset_relationships
        self.df_dict = df_dict
        self.enable_mlflow_tracking = enable_mlflow_tracking

    def _create_featuretools_entity_set(self) -> ft.EntitySet:
        """
        Create featuretools entity set

        :return: featuretools entity set
        """
        return ft.EntitySet(id=self.entity_set_id)

    def _add_featuretools_dataframes(self, es: ft.EntitySet) -> ft.EntitySet:
        """
        Add DataFrame for each data group to the featuretools entity set

        :param es: featuretools entity set
        :return: Modified featuretools entity set
        """
        for data_group, df in self.df_dict.items():
            logging.info(f"Adding DF for {data_group} to featuretools entity")
            short_prefix = f"{self.dataset_fields[data_group]['short_prefix']}"  # type: ignore
            index = self.dataset_fields[data_group]["index"]  # type: ignore
            if isinstance(index, str):
                index = f"{short_prefix}_{index}"
            elif isinstance(index, list):
                # Create a combined index if multiple fields are provided for the index
                index = [f"{short_prefix}_{i}" for i in index]
                index_fields = index
                index = ("_").join(index)
                df[index] = df[index_fields].astype(str).apply("_".join, axis=1)
            time_index = self.dataset_fields[data_group]["time_index"]  # type: ignore
            if time_index is not None:
                time_index = f"{short_prefix}_{time_index}"
            es = es.add_dataframe(
                dataframe_name=data_group,
                dataframe=df.copy(),
                index=index,
                time_index=time_index,
                logical_types={
                    f"{short_prefix}_{k}": v
                    for k, v in self.dataset_fields[data_group]["logical_types"].items()  # type: ignore
                },
            )
        return es

    def _add_featuretools_relationships(self, es: ft.EntitySet) -> ft.EntitySet:
        """
        Add relationships between DataFrames to the featuretools entity set

        :param es: featuretools entity set
        :return: Modified featuretools entity set
        """
        for dataset_relationships in self.dataset_relationships:
            for dataset_type in ["parent", "child"]:
                data_group = dataset_relationships[f"{dataset_type}_dataframe_name"]
                prefix = self.dataset_fields[data_group]["short_prefix"]  # type: ignore
                column_name = f"{dataset_type}_column_name"
                dataset_relationships[column_name] = f"{prefix}_{dataset_relationships[column_name]}"
            es = es.add_relationship(**dataset_relationships)
        logging.info("featuretools Relationships added")
        return es

    @staticmethod
    def _deep_feature_synthesis(
        es: ft.EntitySet,
        target_dataframe_name: str,
        target_col_name: str,
        additional_features_to_remove: list[str],
        dfs_kwargs: Optional[dict[str, Any]] = None,
    ) -> tuple[pd.DataFrame, list[ft.FeatureBase]]:
        """
        Run Deep Feature Synthesis algorithm

        :param es: featuretools entity set
        :param target_dataframe_name: Target DataFrame name
        :param target_col_name: Target column name
        :param additional_features_to_remove: Additional features to remove
        :param dfs_kwargs: Deep Feature Synthesis additional arguments for featuretools ft.dfs function
        :return: Features DataFrame and list of feature definitions
        """
        if dfs_kwargs is None:
            dfs_kwargs = {}
        X, X_defs = ft.dfs(entityset=es, target_dataframe_name=target_dataframe_name, **dfs_kwargs)
        # Remove features that contain the target column name
        target_based_features = [x for x in X.columns.to_list() if target_col_name in x]
        features_to_remove = additional_features_to_remove + target_based_features
        X.drop(columns=features_to_remove, inplace=True)
        X_defs = [defn for defn in X_defs if defn.get_name() not in features_to_remove]
        return X, X_defs

    def _generate_and_store_feature_descriptions(self, X_defs: list[ft.FeatureBase]) -> None:
        """
        Generate and store feature descriptions

        :param X_defs: List of feature definitions
        :return: None
        """
        feature_dict = {}
        for i, feature in enumerate(X_defs):
            feature_dict[i] = {
                "name": feature.get_name(),
                "description": ft.describe_feature(feature),
            }
        save_dict(
            data_dict=feature_dict,
            file_path="featuretools_features_definition.json",
            enable_mlflow_tracking=self.enable_mlflow_tracking,
            mlflow_artifact_path="feature_engineering",
        )

    def run_process(
        self,
        target_dataframe_name: str,
        target_col_name: str,
        additional_features_to_remove: list[str],
        dfs_kwargs: Optional[dict[str, Any]] = None,
    ) -> tuple[pd.DataFrame, list[ft.FeatureBase], pd.Series]:
        """
        Run feature engineering main process of the FeatureToolsEngineering class

        :param target_dataframe_name: Target DataFrame name
        :param target_col_name: Target column name
        :param additional_features_to_remove: Additional features to remove
        :param dfs_kwargs: Deep Feature Synthesis additional arguments for featuretools ft.dfs function
        :return: Features DataFrame, list of feature definitions and target Series
        """
        es = self._create_featuretools_entity_set()
        es = self._add_featuretools_dataframes(es=es)
        es = self._add_featuretools_relationships(es=es)
        X, X_defs = self._deep_feature_synthesis(
            es=es,
            target_dataframe_name=target_dataframe_name,
            target_col_name=target_col_name,
            additional_features_to_remove=additional_features_to_remove,
            dfs_kwargs=dfs_kwargs,
        )
        self._generate_and_store_feature_descriptions(X_defs=X_defs)
        return X, X_defs, self.df_dict[target_dataframe_name][target_col_name]
