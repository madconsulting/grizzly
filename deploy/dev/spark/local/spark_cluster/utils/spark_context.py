import os

from pyspark.conf import SparkConf
from pyspark.sql import SparkSession
from subprocess import check_output

from local.spark_cluster.utils.spark_cluster_context_config import (
    spark_cluster_context_config,
)


def get_spark_context(
    app_name: str, is_run_on_cluster: bool = False, context_log_level: str = "WARN"
) -> SparkSession:
    """
    Get the spark context and setting the log level
    :param app_name: Spark app name
    :param is_run_on_cluster: True if running aplication on the spark cluster, False otherwise
    :param context_log_level: Context log level
    :return: Spark session
    """
    spark_config = SparkConf()
    config_var_list = [("spark.app.name", app_name)]
    if is_run_on_cluster:
        SPARK_DRIVER_HOST = (
            check_output(["hostname", "-i"]).decode(encoding="utf-8").strip()
        )
        # See: https://github.com/bitnami/bitnami-docker-spark/issues/18#issuecomment-701487655
        os.environ["SPARK_LOCAL_IP"] = SPARK_DRIVER_HOST
        config_var_list += [(k, v) for k, v in spark_cluster_context_config.items()] + [
            # spark.master = spark://<ip of master node>:<port of master node>
            (
                "spark.master",
                os.environ.get("SPARK_MASTER_URL", "spark://spark-master:7077"),
            ),
            # spark.driver.host = IP of the driver (e.g. the machine / docker container from where we are running the
            # pyspark code)
            ("spark.driver.host", SPARK_DRIVER_HOST),
        ]
    else:
        config_var_list += [("spark.master", "local")]
    spark_config.setAll(config_var_list)
    spark = SparkSession.builder.config(conf=spark_config).getOrCreate()
    spark.sparkContext.setLogLevel(context_log_level)
    return spark
