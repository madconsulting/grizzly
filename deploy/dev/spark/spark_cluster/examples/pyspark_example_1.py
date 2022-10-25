from pyspark.sql import SparkSession
import numpy as np

from spark_cluster.utils.spark_context import get_spark_context


def spark_example_1(is_run_on_cluster: bool = False) -> None:
    """
    Spark example nº 1 - Create and show DataFrame
    :param is_run_on_cluster: True if running aplication on the spark cluster, False otherwise
    :return: None
    """
    spark = get_spark_context(
        app_name="pyspark_example_1", is_run_on_cluster=is_run_on_cluster
    )
    data = [
        ("James", "", "Smith", "1991-04-01", "M", 3000),
        ("Michael", "Rose", "", "2000-05-19", "M", 4000),
        ("Robert", "", "Williams", "1978-09-05", "M", 4000),
        ("Maria", "Anne", "Jones", "1967-12-01", "F", 4000),
        ("Jen", "Mary", "Brown", "1980-02-17", "F", -1),
    ]
    columns = ["firstname", "middlename", "lastname", "dob", "gender", "salary"]
    df = spark.createDataFrame(data=data, schema=columns)
    df.show()
    spark.stop()


if __name__ == "__main__":
    spark_example_1(is_run_on_cluster=True)
