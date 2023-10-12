import logging
from typing import Any, Optional

import featuretools as ft
import pandas as pd
from prefect import task

from grizzly_main.orchestrator.prefect_poc.tools.featuretools_feat_engineering import FeatureToolsEngineering


def adventure_works_featuretools_engineering(
    df_dict: dict[str, pd.DataFrame],
    dfs_kwargs: Optional[dict[str, Any]] = None,
    enable_mlflow_tracking: bool = False,
) -> tuple[pd.DataFrame, list[ft.FeatureBase], pd.Series]:
    """
    Adventure Works Feature Engineering using featuretools

    :param df_dict: Dictionary of data group DataFrame's
    :param dfs_kwargs: Deep Feature Synthesis additional arguments for featuretools ft.dfs function
    :param enable_mlflow_tracking: True if MLflow tracking is enabled, False otherwise.
    :return: Feature DataFrame, list of feature definitions and target Series
    """
    return FeatureToolsEngineering(
        df_dict=df_dict,
        entity_set_id="adventure_works",
        enable_mlflow_tracking=enable_mlflow_tracking,
    ).run_process(
        target_dataframe_name="target",
        target_col_name="tar_churn",
        # Remove Sales Order ID and Customer ID for this dataset, as the churn is skewed towards
        # higher sales order ids and customer ids. So removing these features for a more realistic churn
        # prediction problem.
        additional_features_to_remove=["tar_SalesOrderID", "sales_order.so_CustomerID"],
        dfs_kwargs=dfs_kwargs,
    )


@task
def feature_engineering_pr_task(
    df_dict: dict[str, pd.DataFrame],
    dfs_kwargs: Optional[dict[str, Any]] = None,
    enable_mlflow_tracking: bool = False,
) -> tuple[pd.DataFrame, pd.Series]:
    """
    Prefect task for feature engineering of the Adventure Works dataset

    :param df_dict: Dictionary of data group DataFrame's
    :param dfs_kwargs: Deep Feature Synthesis additional arguments for featuretools ft.dfs function
    :param enable_mlflow_tracking: True if MLflow tracking is enabled, False otherwise.
    :return: Feature DataFrame and target Series
    """
    logging.info("Starting feature engineering task in Prefect")
    X, _, y = adventure_works_featuretools_engineering(
        df_dict=df_dict,
        dfs_kwargs=dfs_kwargs,
        enable_mlflow_tracking=enable_mlflow_tracking,
    )
    logging.info("Feature engineering task completed in Prefect")
    return X, y


if __name__ in "__main__":
    from grizzly_main.orchestrator.prefect_poc.adventure_works_pipeline.pipeline_code.data_preprocessing import (
        DataPreprocessing,
    )
    from grizzly_main.orchestrator.prefect_poc.tools.custom_logger import add_stdout_logger_as_root

    add_stdout_logger_as_root()

    df_dict_ = DataPreprocessing().run_process()

    X_, X_defs_, y_ = adventure_works_featuretools_engineering(df_dict=df_dict_)

    # Store locally for debugging purposes
    X_.to_parquet("X.parquet")
    import joblib

    with open("../X_defs.pkl", "wb") as f:
        joblib.dump(X_defs_, f)
    pd.DataFrame(y_).to_parquet("../y.parquet")
