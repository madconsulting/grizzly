import numpy as np
from pyspark.mllib.stat import Statistics
from pyspark.sql import SparkSession


def pyspark_example_2(spark: SparkSession) -> None:
    """
    Pyspark example nº 2 - Correlation matrix
    Based on: https://github.com/apache/spark/blob/master/examples/src/main/python/mllib/correlations_example.py
    :param spark: Spark session
    :return: None
    """
    seriesX = spark.sparkContext.parallelize([1.0, 2.0, 3.0, 3.0, 5.0])
    # seriesY must have the same number of partitions and cardinality as seriesX
    seriesY = spark.sparkContext.parallelize([11.0, 22.0, 33.0, 33.0, 555.0])
    # Compute the correlation using Pearson's method.
    print("Correlation is: " + str(Statistics.corr(seriesX, seriesY, method="pearson")))
    data = spark.sparkContext.parallelize(
        [
            np.array([1.0, 10.0, 100.0]),
            np.array([2.0, 20.0, 200.0]),
            np.array([5.0, 33.0, 366.0]),
        ]
    )  # an RDD of Vectors
    # Calculate the correlation matrix using Pearson's method.
    print(Statistics.corr(data, method="pearson"))
