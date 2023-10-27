# isort: skip_file
# Note: Skipping isort to ensure that lengthy imports are not reformatted
from typing import Any
from prefect import flow

from grizzly_main.orchestrator.prefect_poc.adventure_works_pipeline.pipeline_code.data_preprocessing import (
    data_preprocessing_pr_task,
)
from grizzly_main.orchestrator.prefect_poc.adventure_works_pipeline.pipeline_code.evaluation import (
    model_evaluation_pr_task,
)
from grizzly_main.orchestrator.prefect_poc.adventure_works_pipeline.pipeline_code.feature_engineering import (
    feature_engineering_pr_task,
)
from grizzly_main.orchestrator.prefect_poc.adventure_works_pipeline.pipeline_code.feature_post_processing import (
    feature_post_processing_pr_task,
)
from grizzly_main.orchestrator.prefect_poc.adventure_works_pipeline.pipeline_code.model_explainability import (
    shap_explainer_pr_task,
)

# fmt: off
from grizzly_main.orchestrator.prefect_poc.adventure_works_pipeline.pipeline_code.training_and_hyperparameter_tuning \
    import hyperparameter_tuning_optuna_pr_flow, split_dataset_pr_task, training_with_best_hyperparam_pr_flow
# fmt: on
from grizzly_main.orchestrator.prefect_poc.tools.custom_logger import add_stdout_logger_as_root
from grizzly_main.orchestrator.prefect_poc.tools.mlflow_tools import run_with_mlflow_tracking, save_dict
from grizzly_main.orchestrator.prefect_poc.tools.prefect_tools import generate_flow_run_name


def _store_main_config(main_config: dict[str, Any], enable_mlflow_tracking: bool = False) -> None:
    """
    Store main configuration in MLFlow

    :param main_config: Main configuration dictionary
    :param enable_mlflow_tracking: True if MLflow tracking is enabled, False otherwise.
    :return: None
    """
    if enable_mlflow_tracking:
        save_dict(
            data_dict=main_config,
            file_path="main_config.json",
            enable_mlflow_tracking=enable_mlflow_tracking,
            mlflow_artifact_path="input",
        )


@flow(flow_run_name=generate_flow_run_name)
def adventure_works_orchestrator_pr_flow(main_config: dict[str, Any], enable_mlflow_tracking: bool = False) -> None:
    """
    Prefect flow for the orchestration of the Adventure works pipeline

    :param main_config: Main configuration dictionary
    :param enable_mlflow_tracking: True if MLflow tracking is enabled, False otherwise.
    :return: None
    """
    add_stdout_logger_as_root(is_enable_in_prefect=True)
    _store_main_config(main_config=main_config, enable_mlflow_tracking=enable_mlflow_tracking)
    df_dict = data_preprocessing_pr_task()
    X, y = feature_engineering_pr_task(  # type: ignore
        df_dict=df_dict,
        dfs_kwargs=main_config["dfs_kwargs"],
        enable_mlflow_tracking=enable_mlflow_tracking,
    )
    X, y = feature_post_processing_pr_task(X=X, y=y, enable_mlflow_tracking=enable_mlflow_tracking)  # type: ignore
    split_dataset_pr_task(X=X, y=y, enable_mlflow_tracking=enable_mlflow_tracking)
    model_type = main_config["model_type"]
    optimizer = hyperparameter_tuning_optuna_pr_flow(
        model_type=model_type,
        param_dict=main_config["hyperparameter_tuning"]["param_dict"],
        n_trials=main_config["hyperparameter_tuning"]["n_trials"],
        is_run_trials_concurrently=main_config["hyperparameter_tuning"]["is_run_trials_concurrently"],
        concurrency_limit=main_config["hyperparameter_tuning"]["concurrency_limit"],
        enable_mlflow_tracking=enable_mlflow_tracking,
    )
    best_model = training_with_best_hyperparam_pr_flow(  # type: ignore
        model_type=model_type,
        optimizer=optimizer,
        enable_mlflow_tracking=enable_mlflow_tracking,
    )
    shap_explainer_pr_task(
        best_model=best_model,
        enable_mlflow_tracking=enable_mlflow_tracking,
        is_use_fastrree_shap=main_config["is_use_fastrree_shap"],
    )
    model_evaluation_pr_task(
        model=best_model,
        eval_metrics=main_config["eval_metrics"],
        enable_mlflow_tracking=enable_mlflow_tracking,
    )


def adventure_works_orchestrator_prefect_pipeline_in_mlflow(main_config: dict[str, Any]):
    """
    Run Prefect flow for the orchestration of the Adventure works pipeline in MLFlow
    :param main_config: Main configuration dictionary
    :return: None
    """
    return run_with_mlflow_tracking(
        function_to_run=adventure_works_orchestrator_pr_flow,
        function_kwargs={"enable_mlflow_tracking": True, "main_config": main_config},
    )


if __name__ == "__main__":
    from grizzly_main.orchestrator.prefect_poc.adventure_works_pipeline.configs.main_config import (
        main_config as main_config_,
    )

    if main_config_["enable_mlflow_tracking"]:
        adventure_works_orchestrator_prefect_pipeline_in_mlflow(main_config=main_config_)
    else:
        adventure_works_orchestrator_pr_flow(main_config=main_config_)
