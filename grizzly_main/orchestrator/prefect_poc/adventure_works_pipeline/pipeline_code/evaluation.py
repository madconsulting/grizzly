import logging
from typing import Any

from prefect import task

from grizzly_main.orchestrator.prefect_poc.tools.disk_interactions import read_dataset_from_disk
from grizzly_main.orchestrator.prefect_poc.tools.models.abstract_model import BaseModel


@task
def model_evaluation_pr_task(model: BaseModel, eval_metrics: dict[str, Any], enable_mlflow_tracking: bool) -> None:
    """
    Prefect task for model evaluation of the Adventure Works dataset

    :param model: Trained model
    :param eval_metrics: Evaluation metrics
    :param enable_mlflow_tracking: True if MLflow tracking is enabled, False otherwise.
    :return: None
    """
    logging.info("Starting model evaluation task in Prefect")
    X_test, y_test = read_dataset_from_disk(dataset_type="test")
    eval_metrics_res = model.evaluate(
        X_test=X_test,
        y_test=y_test,
        eval_metrics=eval_metrics,
        enable_mlflow_tracking=enable_mlflow_tracking,
    )
    logging.info(f"Evaluation metrics results: {eval_metrics_res}")
    logging.info("Model evaluation in prefect completed")
