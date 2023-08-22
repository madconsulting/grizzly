from typing import Any, Dict

from grizzly_main.deploy.spark.pyspark_examples.pyspark_example_dict import (
    pyspark_example_dict,
)
from grizzly_main.deploy.spark.utils.spark_context import get_spark_context


def run_pyspark_example(
    example_name: str, example_kwargs: Dict[str, Any], run_mode: str
) -> None:
    """
    Run pyspark example
    :param example_name: Pyspark example name
    :param example_kwargs: Pyspark example kwargs
    :param run_mode: Run mode
    :return: None
    """
    spark = get_spark_context(app_name=example_name, run_mode=run_mode)
    pyspark_example_dict[example_name](spark=spark, **example_kwargs)
    spark.stop()


if __name__ == "__main__":
    # Inputs
    is_run_on_cluster = True
    example_name = "pyspark_example_1"
    # example_name = "pyspark_example_2"
    example_kwargs = {}

    # Example trigger
    if is_run_on_cluster:
        run_mode = "local_cluster"
    else:
        run_mode = "local_single_worker"
    run_pyspark_example(
        example_name=example_name, example_kwargs=example_kwargs, run_mode=run_mode
    )
