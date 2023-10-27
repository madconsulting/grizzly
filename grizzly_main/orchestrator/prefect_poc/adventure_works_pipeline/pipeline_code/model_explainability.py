import logging

import fasttreeshap
import matplotlib.pyplot as plt
import shap
from prefect import task

from grizzly_main.orchestrator.prefect_poc.tools.disk_interactions import read_dataset_from_disk
from grizzly_main.orchestrator.prefect_poc.tools.mlflow_tools import save_plot
from grizzly_main.orchestrator.prefect_poc.tools.models.abstract_model import BaseModel


@task
def shap_explainer_pr_task(
    best_model: BaseModel,
    enable_mlflow_tracking: bool = False,
    is_use_fastrree_shap: bool = False,
) -> None:
    """
    Prefect task to explain the model with SHAP for the Adventure Works dataset

    :param best_model: Best model trained
    :param enable_mlflow_tracking: True if MLflow tracking is enabled, False otherwise.
    :param is_use_fastrree_shap: True if using fast SHAP explainer implementation from fasttreeshap library,
                                 False if using regular SHAP library
    :return: None
    """
    logging.info("Starting shap explainer task in Prefect")
    X_test, _ = read_dataset_from_disk(dataset_type="test")
    if is_use_fastrree_shap:
        explainer = fasttreeshap.TreeExplainer(best_model.model, algorithm="auto", n_jobs=-1)
        shap_values = explainer(X_test).values
    else:
        explainer = shap.TreeExplainer(best_model.model)
        shap_values = explainer(X_test).values
        # Contribution towards predicting churn = 1 (Note that the contribution towards predicting 0 is exactly the
        # opposite value, as this is a binary classification problem)
        shap_values = shap_values[:, :, 1]
    shap.summary_plot(shap_values, X_test, show=False)
    plt.tight_layout()
    fig = plt.gcf()
    save_plot(
        plot=fig,
        fig_path="adventure_works_shap_summary_plot.png",
        enable_mlflow_tracking=enable_mlflow_tracking,
        mlflow_artifact_path="model_explainability",
    )
    plt.close()
    logging.info("Shap explainer task completed in Prefect")
