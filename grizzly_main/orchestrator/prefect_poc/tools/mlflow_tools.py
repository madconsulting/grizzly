import json
import logging
import subprocess
from datetime import datetime
from typing import Any, Callable, Optional

import joblib
import mlflow
import numpy as np
import pandas as pd
from mlflow.tracking import MlflowClient

from grizzly_main.path_interations import get_base_dir


def configure_mlflow_tracking_uri(
    use_local_mlflow: bool = True,
    is_set_tracking_uri: bool = True,
    is_return_tracking_uri: bool = False,
) -> Optional[str]:
    """
    Configure MLflow Tracking URI.

    :param use_local_mlflow: Set to True for local MLflow recording, or False for remote Tracking Server.
    :param is_set_tracking_uri: True if setting the tracking URI in MLFlow, False if just retrieving it
    :param is_return_tracking_uri: True if returning the tracking URI, False otherwise
    :return: None or MLFlow tracking URI
    """
    if use_local_mlflow:
        base_dir = get_base_dir()
        mlflow_tracking_uri = f"sqlite:///{base_dir}/orchestrator/prefect_poc/mlflow_local/mlflow_tracking.db"
    else:
        raise NotImplementedError("Remote MLflow tracking server is not implemented yet")
    if is_set_tracking_uri:
        mlflow.set_tracking_uri(mlflow_tracking_uri)
    if is_return_tracking_uri:
        return mlflow_tracking_uri
    return None


def get_mlflow_artifact_location(
    use_local_mlflow: bool = True,
) -> str:
    """
    Get the artifact storage location for MLflow.

    :param use_local_mlflow: Set to True for local MLflow recording, or False for remote Tracking Server.
    :return: The path to the MLflow artifacts storage location.
    """
    if use_local_mlflow:
        base_dir = get_base_dir()
        artifact_location = f"{base_dir}/orchestrator/prefect_poc/mlflow_local/mlflow_artifacts"
    else:
        raise NotImplementedError("Remote MLflow tracking server is not implemented yet")
    return artifact_location


def configure_mlflow_experiment(
    mlflow_experiment_name: str,
    use_local_mlflow: bool = True,
) -> str:
    """
    Configure an MLflow experiment or retrieve it if it already exists.

    :param mlflow_experiment_name: Name of the MLflow experiment.
    :param use_local_mlflow: Set to True for local MLflow recording, or False for remote Tracking Server.
    :return: Experiment unique ID.
    """
    client = MlflowClient()
    experiment = client.get_experiment_by_name(name=mlflow_experiment_name)
    if experiment is None:
        artifact_location = get_mlflow_artifact_location(
            use_local_mlflow=use_local_mlflow,
        )
        experiment_id = mlflow.create_experiment(name=mlflow_experiment_name, artifact_location=artifact_location)
    else:
        experiment_id = experiment.experiment_id
    return experiment_id


def setup_mlflow_tracking_parameters(
    mlflow_experiment_name: str,
    use_local_mlflow: bool = True,
) -> tuple[str, str]:
    """
    Set up initial configurations for MLflow tracking.

    :param mlflow_experiment_name: Name of the MLflow experiment.
    :param use_local_mlflow: Set to True for local MLflow recording, or False for remote Tracking Server.
    :return: A tuple containing the experiment unique ID and the run name.
    """
    configure_mlflow_tracking_uri(
        use_local_mlflow=use_local_mlflow,
    )
    experiment_id = configure_mlflow_experiment(
        mlflow_experiment_name=mlflow_experiment_name,
        use_local_mlflow=use_local_mlflow,
    )
    run_name = f'{mlflow_experiment_name}_{datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")}'
    return experiment_id, run_name


def run_with_mlflow_tracking(
    function_to_run: Callable,
    function_kwargs: Optional[dict[str, Any]] = None,
    mlflow_tags: Optional[dict[str, Any]] = None,
    use_local_mlflow: bool = True,
) -> Any:
    """
    Run a function with MLflow tracking enabled.

    :param function_to_run: The function to execute with MLflow tracking.
    :param function_kwargs: Optional keyword arguments for the function.
    :param mlflow_tags: MLFlow tags
    :param use_local_mlflow: Set to True for local MLflow recording, or False for remote Tracking Server.
    :return: The result of the executed function.
    """
    if function_kwargs is None:
        function_kwargs = {}
    if mlflow_tags is None:
        mlflow_tags = {}
    mlflow_experiment_id, run_name = setup_mlflow_tracking_parameters(
        mlflow_experiment_name="adventure_works_pipeline",
        use_local_mlflow=use_local_mlflow,
    )
    logging.info("MLflow tracking parameters configured")
    with mlflow.start_run(experiment_id=mlflow_experiment_id, run_name=run_name, tags=mlflow_tags):
        logging.info("MLflow run started")
        result = function_to_run(**function_kwargs)
        logging.info("MLflow run finished")
    mlflow.end_run()
    return result


def create_or_update_model_in_mlflow(
    model_uri: str,
    model_name: str,
    model_tags: Optional[dict[str, str]] = None,
) -> None:
    """
    Create or update a model in MLFlow tracking, optionally adding model tags.

    If a model with the given name does not exist, a new model will be created with the specified version.
    If a model with the name already exists, a new model version will be created.

    :param model_uri: Model URI
    :param model_name: Model name in MLFlow tracking
    :param model_tags: Model tags to associate with the model version
    :return: None
    """
    tracked_model = mlflow.register_model(model_uri=model_uri, name=model_name)
    if model_tags is not None:
        mlflow_client = MlflowClient()
        for key, value in model_tags.items():
            mlflow_client.set_model_version_tag(
                name=model_name,
                version=tracked_model.version,
                key=key,
                value=value,
            )


def log_and_create_model_version_in_mlflow(
    model: Any,
    model_name: str,
    local_file_path: str,
    model_directory: str,
    model_tags: Optional[dict[str, str]] = None,
    include_poetry_files: bool = True,
    enable_mlflow_tracking: bool = True,
) -> None:
    """
    Save model locally and in MLFlow, and create a new model version in MLFlow.

    :param model: Model object
    :param model_name: Name of the model in MLFlow tracking
    :param local_file_path: Local file path where the model will be stored
    :param model_directory: The directory containing all files related to the trained model
    :param model_tags: Model tags to associate with the model version
    :param include_poetry_files: Include Poetry-related files in the trained model directory if True
    :param enable_mlflow_tracking: True if MLflow tracking is enabled, False otherwise.
    :return: None
    """
    base_dir = get_base_dir()
    save_joblib(
        object_to_store=model,
        file_path=f"{base_dir}/{local_file_path}",
        enable_mlflow_tracking=enable_mlflow_tracking,
        mlflow_artifact_path=model_directory,
    )
    if enable_mlflow_tracking:
        model_uri = f"runs:/{mlflow.active_run().info.run_id}/{model_directory}"
        if include_poetry_files:
            base_directory_root = str(base_dir).replace("grizzly_main", "")
            print(f"base_directory_root: {base_directory_root}")
            mlflow.log_artifact(
                f"{base_directory_root}pyproject.toml",
                artifact_path=f"{model_directory}/poetry_dependencies",
            )
            mlflow.log_artifact(
                f"{base_directory_root}poetry.lock",
                artifact_path=f"{model_directory}/poetry_dependencies",
            )
        create_or_update_model_in_mlflow(
            model_uri=model_uri,
            model_name=model_name,
            model_tags=model_tags,
        )
        logging.info("Model version created in MLFlow")


def save_plot(
    plot: Any,
    fig_path: str,
    enable_mlflow_tracking: bool = False,
    mlflow_artifact_path: Optional[str] = None,
) -> None:
    """
    Save a plot to disk and optionally to MLFlow

    :param plot: Plot object
    :param fig_path: Figure path
    :param enable_mlflow_tracking: True if MLflow tracking is enabled, False otherwise.
    :param mlflow_artifact_path: MLFlow artifact path
    :return: None
    """
    try:
        fig = plot.get_figure()
    except AttributeError:
        fig = plot.fig
    fig.savefig(fig_path)
    if enable_mlflow_tracking:
        mlflow.log_artifact(fig_path, artifact_path=mlflow_artifact_path)


def save_df(
    df: pd.DataFrame,
    file_path: str,
    enable_mlflow_tracking: bool = False,
    mlflow_artifact_path: Optional[str] = None,
) -> None:
    """
    Save a DataFrame to disk and optionally to MLFlow

    :param df: DataFrame
    :param file_path: File path
    :param enable_mlflow_tracking: True if MLflow tracking is enabled, False otherwise.
    :param mlflow_artifact_path: MLFlow artifact path
    :return: None
    """
    df.to_parquet(file_path)
    if enable_mlflow_tracking:
        mlflow.log_artifact(file_path, artifact_path=mlflow_artifact_path)


class CustomJSONizer(json.JSONEncoder):
    """
    If you have multiple bool_ keys or a nested structure, this will convert all bool_ fields including deeply
    nested values
    """

    def default(self, obj):  # pylint: disable=W0221
        return super().encode(bool(obj)) if isinstance(obj, np.bool_) else super().default(obj)


def save_dict(
    data_dict: dict[Any, Any],
    file_path: str,
    enable_mlflow_tracking: bool = False,
    mlflow_artifact_path: Optional[str] = None,
) -> None:
    """
    Save a dictionary to disk and optionally to MLFlow

    :param data_dict: Data dictionary
    :param file_path: File path
    :param enable_mlflow_tracking: True if MLflow tracking is enabled, False otherwise.
    :param mlflow_artifact_path: MLFlow artifact path
    :return:
    """
    with open(file_path, "w") as f:
        json.dump(data_dict, f, cls=CustomJSONizer)
    if enable_mlflow_tracking:
        mlflow.log_artifact(file_path, artifact_path=mlflow_artifact_path)


def save_joblib(
    object_to_store: Any,
    file_path: str,
    enable_mlflow_tracking: bool = False,
    mlflow_artifact_path: Optional[str] = None,
) -> None:
    """
    Serialize and save an object using joblib

    :param object_to_store: Object to be stored
    :param file_path: File path
    :param enable_mlflow_tracking: True if MLflow tracking is enabled, False otherwise.
    :param mlflow_artifact_path: MLFlow artifact path
    :return: None
    """
    with open(file_path, "wb") as f:
        joblib.dump(object_to_store, f)
    if enable_mlflow_tracking:
        mlflow.log_artifact(file_path, artifact_path=mlflow_artifact_path)


def start_mlflow_ui(
    use_local_mlflow: bool = True,
) -> None:
    """
    Start the MLflow UI locally or connect to a remote Tracking Server.

    :param use_local_mlflow: Set to True for local MLflow recording, or False for remote Tracking Server.
    :return: None
    """
    mlflow_tracking_uri = configure_mlflow_tracking_uri(
        use_local_mlflow=use_local_mlflow,
        is_set_tracking_uri=False,
        is_return_tracking_uri=True,
    )
    artifact_location = get_mlflow_artifact_location(
        use_local_mlflow=use_local_mlflow,
    )
    # Execute MLFlow UI from CLI command
    command = [
        "mlflow",
        "ui",
        f"--backend-store-uri={mlflow_tracking_uri}",
        f"--default-artifact-root={artifact_location}",
    ]
    subprocess.run(command, shell=False)  # pylint: disable= W1510


if __name__ in "__main__":
    start_mlflow_ui()
