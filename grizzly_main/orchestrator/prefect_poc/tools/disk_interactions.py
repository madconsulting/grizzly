"""
Prefect's Flow parameters can't exceed 512kb in size. Thus, we are using disk as buffer with the following
read / write operations
"""

from typing import Any

import joblib
import pandas as pd

from grizzly_main.path_interations import get_base_dir

base_dir = get_base_dir()


def write_dataset_to_disk(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
) -> None:
    """
    Write train and test datasets to disk

    :param X_train: Train features DataFrame
    :param X_test: Test features DataFrame
    :param y_train: Train labels DataFrame
    :param y_test: Test labels DataFrame
    :return:
    """

    X_train.to_parquet(f"{base_dir}/X_train.parquet")
    pd.DataFrame(y_train).to_parquet(f"{base_dir}/y_train.parquet")
    X_test.to_parquet(f"{base_dir}/X_test.parquet")
    pd.DataFrame(y_test).to_parquet(f"{base_dir}/y_test.parquet")


def read_dataset_from_disk(dataset_type: str) -> tuple[pd.DataFrame, pd.Series]:
    """
    Read train or test dataset from disk

    :param dataset_type: Dataset type ('train' or 'test')
    :return: Features and labels Dataframes
    """
    allowed_types = ["train", "test"]
    if dataset_type not in allowed_types:
        raise ValueError(f"dataset_type must be equal to one of the following values: {allowed_types}")
    X = pd.read_parquet(f"{base_dir}/X_{dataset_type}.parquet")
    y = pd.read_parquet(f"{base_dir}/y_{dataset_type}.parquet").squeeze()
    return X, y


def write_joblib_to_disk(data_object: Any, file_path: str) -> None:
    """
    Write joblib object to disk

    :param data_object: Object
    :param file_path: File path
    :return:
    """
    with open(f"{base_dir}/{file_path}", "wb") as f:
        joblib.dump(data_object, f)


def read_joblib_from_disk(file_path: str) -> Any:
    """
    Read joblib object from disk

    :param file_path: File path
    :return: Any
    """
    return joblib.load(f"{base_dir}/{file_path}")
