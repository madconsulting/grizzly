from typing import Any

from grizzly_main.deploy.spark.pyspark_examples.pyspark_example_dict import pyspark_example_dict
from grizzly_main.deploy.spark.utils.spark_context import get_spark_context


def run_pyspark_example(example_name: str, example_kwargs: dict[str, Any], run_mode: str) -> None:
    """
    Run pyspark example
    :param example_name: Pyspark example name
    :param example_kwargs: Pyspark example kwargs
    :param run_mode: Run mode
    :return: None
    """
    spark = get_spark_context(app_name=example_name, run_mode=run_mode)
    pyspark_example_dict[example_name](spark=spark, **example_kwargs)  # type: ignore
    spark.stop()


if __name__ == "__main__":
    # Inputs
    is_run_on_cluster = True
    example_name_ = "pyspark_example_1"
    # example_name_ = "pyspark_example_2"
    example_kwargs_: dict[str, Any] = {}

    # Example trigger
    if is_run_on_cluster:
        run_mode_ = "local_cluster"
    else:
        run_mode_ = "local_single_worker"
    run_pyspark_example(example_name=example_name_, example_kwargs=example_kwargs_, run_mode=run_mode_)
