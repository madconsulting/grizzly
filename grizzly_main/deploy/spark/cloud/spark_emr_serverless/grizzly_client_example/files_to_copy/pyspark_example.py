from typing import Any

from grizzly_main.deploy.spark.pyspark_examples.pyspark_example_dict import pyspark_example_dict
from grizzly_main.deploy.spark.utils.spark_context import get_spark_context


def pyspark_example(example_name: str, example_kwargs: dict[str, Any]) -> None:
    """
    Run a PySpark example available in the following folder: 'grizzly_main.deploy.spark.pyspark_examples'
    :param example_name: Pyspark example name
    :param example_kwargs: Pyspark example kwargs
    :return: None
    """
    spark = get_spark_context(app_name=example_name, run_mode="emr_serverless")
    pyspark_example_dict[example_name](spark=spark, **example_kwargs)  # type: ignore
    spark.stop()


if __name__ == "__main__":
    # Inputs

    # # - Pyspark example 1
    # example_name_ = "pyspark_example_1"
    # example_kwargs_ = {}

    # # - Pyspark example 2
    # example_name_ = "pyspark_example_2"
    # example_kwargs_ = {}

    # - Pyspark example 3
    # Note: By default we are limiting for a single csv file to limit computational costs of the example.
    example_name_ = "pyspark_example_3"
    example_kwargs_ = {
        "year": 2022,
        "is_specific_csv_file_only": True,
        # CSV file name from https://s3.console.aws.amazon.com/s3/buckets/noaa-gsod-pds
        "csv_file_name": "11213099999.csv",
    }

    # Run pyspark example
    pyspark_example(example_name=example_name_, example_kwargs=example_kwargs_)
