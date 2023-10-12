import asyncio
import logging
from typing import Any, Optional

import numpy as np
import pandas as pd
from prefect import flow, get_client, task
from prefect.blocks.system import Secret
from prefect.exceptions import ObjectNotFound
from sklearn.model_selection import train_test_split

from grizzly_main.orchestrator.prefect_poc.tools.custom_logger import add_stdout_logger_as_root
from grizzly_main.orchestrator.prefect_poc.tools.disk_interactions import (
    read_dataset_from_disk,
    read_joblib_from_disk,
    write_dataset_to_disk,
    write_joblib_to_disk,
)
from grizzly_main.orchestrator.prefect_poc.tools.mlflow_tools import save_df
from grizzly_main.orchestrator.prefect_poc.tools.models.abstract_model import BaseModel
from grizzly_main.orchestrator.prefect_poc.tools.models.lightgbm_model import LightGBMModel
from grizzly_main.orchestrator.prefect_poc.tools.optuna_optimizer import OptunaOptimizer
from grizzly_main.orchestrator.prefect_poc.tools.prefect_tools import generate_flow_run_name

concurrency_limit_tag: str = "aw_local_concurrency_limit"

# Set the random seed for Scikit-Learn
random_seed = 42
np.random.seed(random_seed)


@task
def split_dataset_pr_task(X: pd.DataFrame, y: pd.Series, enable_mlflow_tracking: bool) -> None:
    """
    Prefect task to split the dataset, which is written to disk

    :param X: Feature dataset
    :param y: Target dataset
    :return: None
    """
    logging.info("Starting split dataset in train - test task in Prefect")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    dataset_dict = {
        "X_train": X_train,
        "X_test": X_test,
        "y_train": pd.DataFrame(y_train),
        "y_test": pd.DataFrame(y_test),
    }
    for dataset_name, dataset_val in dataset_dict.items():
        save_df(
            df=dataset_val,
            file_path=f"{dataset_name}.parquet",
            enable_mlflow_tracking=enable_mlflow_tracking,
            mlflow_artifact_path="train_test_dataset",
        )
    write_dataset_to_disk(X_train=X_train, X_test=X_test, y_train=y_train, y_test=y_test)
    logging.info("Split dataset in train - test task completed in Prefect")


@task(tags=[concurrency_limit_tag])
def _run_single_optuna_trial_pr_task(optimizer: OptunaOptimizer) -> None:
    """
    Prefect task to run a single Optuna trial. This task has the concurrency limited limited by the
    tag: concurrency_limit_tag

    :param optimizer: Optuna optimizer
    :return: None
    """
    optimizer.optimize(n_trials=1)


async def _update_concurrency_limit(
    concurrency_limit: int,
) -> None:
    """
    Update the concurrency limit and set it as a tag: concurrency_limit_tag
    Note: This function is async, as the Prefect client can only be retrieved in an async fashion

    :param concurrency_limit: Concurrency limit value
    :return: None
    """
    async with get_client() as client:
        is_add_limit = True
        try:
            limit = await client.read_concurrency_limit_by_tag(tag=concurrency_limit_tag)
            current_concurrency_limit = limit.concurrency_limit
            logging.info(f"Current concurrency limit = {current_concurrency_limit}")
            if current_concurrency_limit != concurrency_limit:
                await client.delete_concurrency_limit_by_tag(tag=concurrency_limit_tag)
                logging.info("Current concurrency limit deleted")
            else:
                logging.info("No need to update the concurrency limit")
                is_add_limit = False
        except ObjectNotFound:
            logging.info(f"Concurrency limit = {concurrency_limit} does not exist yet")
        except Exception as e:
            raise ValueError(f"Error not expected: {e}") from e
        if is_add_limit:
            await client.create_concurrency_limit(tag=concurrency_limit_tag, concurrency_limit=concurrency_limit)
            logging.info(f"Concurrency limit = {concurrency_limit} created")


@flow(flow_run_name=generate_flow_run_name)
def run_optuna_trials_concurrently_pr_flow(
    n_trials: int,
    concurrency_limit: int,
) -> OptunaOptimizer:
    """
    Prefect flow to run Optuna trials concurrently

    :param n_trials: Number of trials for the hyperparameter tuning study
    :param concurrency_limit: Concurrency limit
    :return: Optuna optimizer
    """
    add_stdout_logger_as_root(is_enable_in_prefect=True)
    optimizer = read_joblib_from_disk(file_path="optimizer.pkl")
    asyncio.run(_update_concurrency_limit(concurrency_limit=concurrency_limit))
    for _ in range(0, n_trials):
        _run_single_optuna_trial_pr_task.submit(optimizer)
    logging.info("Optuna trials ran concurrently")
    return optimizer


@task
def _run_optuna_trials_in_series(
    optimizer: OptunaOptimizer,
    n_trials: int,
) -> OptunaOptimizer:
    """
    Prefect flow to run Optuna trials in series

    :param optimizer: Optuna optimizer
    :param n_trials: Number of trials for the hyperparameter tuning study
    :return: Optuna optimizer
    """
    optimizer.optimize(n_trials=n_trials)
    return optimizer


def _get_optuna_storage() -> str:
    """
    Get optuna storage, retrieving the secrets for the local MySQL DB from Prefect

    :return: Optuna storage
    """
    mysql_dbname = Secret.load("mysql-local-dbname")
    mysql_username = Secret.load("mysql-local-username")
    mysql_password = Secret.load("mysql-local-password")
    return f"mysql://{mysql_username.get()}:{mysql_password.get()}@localhost/{mysql_dbname.get()}"


@flow(flow_run_name=generate_flow_run_name)
def hyperparameter_tuning_optuna_pr_flow(
    model_type: str,
    param_dict: dict[str, Any],
    n_trials: int,
    is_run_trials_concurrently: bool,
    concurrency_limit: Optional[int],
    enable_mlflow_tracking: bool,
) -> OptunaOptimizer:
    """
    Prefect flow for hyperparameter tuning in Optuna of the Adventure Works dataset

    :param model_type: Model type
    :param param_dict: Parameter dictionaru
    :param n_trials: Number of trials for the hyperparameter tuning study
    :param is_run_trials_concurrently: True if running trials concurrently, False if running them in series
    :param concurrency_limit: Concurrency limit
    :param enable_mlflow_tracking: True if MLflow tracking is enabled, False otherwise.
    :return: Optuna optimizer
    """
    logging.info("Starting hyperparameter tuning task in Prefect")
    add_stdout_logger_as_root(is_enable_in_prefect=True)
    available_model_types = {
        "lightgbm": LightGBMModel,
    }
    if model_type not in available_model_types:
        raise NotImplementedError(f"Model type {model_type} not implemented yet")
    X_train, y_train = read_dataset_from_disk(dataset_type="train")
    optimizer = OptunaOptimizer(
        X=X_train,
        y=y_train,
        model=LightGBMModel,
        direction="minimize",
        param_dict=param_dict,
        is_run_in_prefect=True,
        storage=_get_optuna_storage(),
    )
    if is_run_trials_concurrently:
        if concurrency_limit is None:
            raise ValueError("concurrency_limit needs to be defined if is_run_trials_concurrently is True")
        # Can't pass optimizer to subflow to run concurrently, for being above 512kb size
        write_joblib_to_disk(data_object=optimizer, file_path="optimizer.pkl")
        optimizer = run_optuna_trials_concurrently_pr_flow(
            n_trials=n_trials, concurrency_limit=concurrency_limit
        )  # type: ignore
    else:
        optimizer = _run_optuna_trials_in_series(optimizer=optimizer, n_trials=n_trials)  # type: ignore
    optimizer.generate_optuna_plots(
        enable_mlflow_tracking=enable_mlflow_tracking,
        mlflow_artifact_path="hyperparameter_tuning_results",
        figure_name_prefix="adventure_works",
    )
    logging.info("Hyperparameter tuning task completed in Prefect")
    return optimizer


@task
def training_with_best_hyperparam_pr_flow(
    model_type: str,
    optimizer: OptunaOptimizer,
    enable_mlflow_tracking: bool,
) -> BaseModel:
    """
    Train model with the best hyperparameters from the Optuna study

    :param model_type: Model type
    :param optimizer: Optuna optimizer
    :param enable_mlflow_tracking: True if MLflow tracking is enabled, False otherwise.
    :return: Trained model (BaseModel class)
    """
    logging.info("Starting training with best parameter task in Prefect")
    best_model = optimizer.train_best_model(
        is_store_model=True,
        enable_mlflow_tracking=enable_mlflow_tracking,
        model_tags={"model_type": model_type},
    )
    logging.info("Training with best parameter task completed in Prefect")
    return best_model
