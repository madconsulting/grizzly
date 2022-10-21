""""
Example to compute correlation matrix.
From: https://github.com/apache/spark/blob/master/examples/src/main/python/mllib/correlations_example.py
"""
import numpy as np
from pyspark.mllib.stat import Statistics
from spark_cluster.utils.spark_context import get_spark_context


def spark_example_2(is_run_on_cluster: bool = False) -> None:
    """
    Spark example nº 2 - Correlation matrix
    Based on: https://github.com/apache/spark/blob/master/examples/src/main/python/mllib/correlations_example.py

    :param is_run_on_cluster: True if running aplication on the spark cluster, False otherwise
    :return: None
    """
    spark = get_spark_context(app_name="pyspark_example_2", is_run_on_cluster=is_run_on_cluster)  # SparkContext
    seriesX = spark.sparkContext.parallelize([1.0, 2.0, 3.0, 3.0, 5.0])
    # seriesY must have the same number of partitions and cardinality as seriesX
    seriesY = spark.sparkContext.parallelize([11.0, 22.0, 33.0, 33.0, 555.0])
    # Compute the correlation using Pearson's method.
    print("Correlation is: " + str(Statistics.corr(seriesX, seriesY, method="pearson")))
    data = spark.sparkContext.parallelize(
        [np.array([1.0, 10.0, 100.0]), np.array([2.0, 20.0, 200.0]), np.array([5.0, 33.0, 366.0])]
    )  # an RDD of Vectors
    # Calculate the correlation matrix using Pearson's method.
    print(Statistics.corr(data, method="pearson"))
    spark.stop()


if __name__ == "__main__":
    spark_correlation_example(is_run_on_cluster=True)
