import logging

import pandas as pd
from prefect import task

from grizzly_main.orchestrator.prefect_poc.tools.feature_encoding import FeatureEncoding


@task
def feature_post_processing_pr_task(
    X: pd.DataFrame, y: pd.Series, enable_mlflow_tracking: bool = False
) -> tuple[pd.DataFrame, pd.Series]:
    """
    Prefect task for post-processing of the Adventure Works dataset

    :param X: Feature DataFrame
    :param y: Target Series
    :param enable_mlflow_tracking: True if MLflow tracking is enabled, False otherwise.
    :return: Encoded feature DataFrame and encoded target Series
    """
    logging.info("Starting post-processing task in Prefect")
    feat_post = FeatureEncoding(enable_mlflow_tracking=enable_mlflow_tracking)
    X, y = feat_post.run_process(X=X, y=y)
    logging.info("Post-processing task completed in Prefect")
    return X, y


if __name__ in "__main__":
    from grizzly_main.orchestrator.prefect_poc.adventure_works_pipeline.pipeline_code.data_preprocessing import (
        DataPreprocessing,
    )
    from grizzly_main.orchestrator.prefect_poc.adventure_works_pipeline.pipeline_code.feature_engineering import (
        adventure_works_featuretools_engineering,
    )
    from grizzly_main.orchestrator.prefect_poc.tools.custom_logger import add_stdout_logger_as_root

    add_stdout_logger_as_root()

    df_dict = DataPreprocessing().run_process()
    X_, X_defs_, y_ = adventure_works_featuretools_engineering(df_dict=df_dict)

    feat_post_ = FeatureEncoding()
    # self = feat_post_  # For debugging purposes
    X_enc, y_enc = feat_post_.run_process(X=X_, y=y_)
