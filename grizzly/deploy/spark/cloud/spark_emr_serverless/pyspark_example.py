import sys
import pulumi
from typing import Dict, Any

from grizzly.deploy.spark.utils.spark_context import get_spark_context
from grizzly.deploy.spark.pyspark_examples.pyspark_example_dict import (
    pyspark_example_dict,
)


def check_python_version() -> None:
    """
    STDOUT to check that the python version corresponds to the one installed in the custom venv used for the job
    :return: None
    """
    print(sys.executable)
    print(sys.version)


def check_imported_package() -> None:
    """
    STDOUT to check that an imported package from Poetry (e.g. Pulumi) is in the spark venv
    :return: None
    """
    pulumi.info(
        msg="Verification that a package from Poetry (e.g. Pulumi) is in the spark venv"
    )


def pyspark_example(example_name: str, example_kwargs: Dict[str, Any]) -> None:
    """
    Spark example nº 1 - Create and show DataFrame
    :param example_name: Pyspark example name
    :param example_kwargs: Pyspark example kwargs
    :return: None
    """
    check_python_version()
    check_imported_package()
    spark = get_spark_context(app_name=example_name, run_mode="emr_serverless")
    pyspark_example_dict[example_name](spark=spark, **example_kwargs)
    spark.stop()


if __name__ == "__main__":

    # Inputs

    # # - Pyspark example 1
    # example_name = "pyspark_example_1"
    # example_kwargs = {}

    # - Pyspark example 3
    # Note: By default we are limiting for a single csv file to limit computational costs of the example.
    example_name = "pyspark_example_3"
    example_kwargs = {
        "year": 2022,
        "is_specific_csv_file_only": True,
        # CSV file name from https://s3.console.aws.amazon.com/s3/buckets/noaa-gsod-pds
        "csv_file_name": "11213099999.csv",
    }

    # Run pyspark example
    pyspark_example(example_name=example_name, example_kwargs=example_kwargs)
