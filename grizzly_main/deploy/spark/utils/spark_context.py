import os

from pyspark.conf import SparkConf
from pyspark.sql import SparkSession
from subprocess import check_output

from grizzly_main.deploy.spark.utils.spark_local_cluster_context_config import (
    spark_local_cluster_context_config,
)


def get_spark_context(
    app_name: str,
    run_mode: str = "local_single_worker",
    context_log_level: str = "WARN",
) -> SparkSession:
    """
    Get the spark context and setting the log level
    :param app_name: Spark app name
    :param run_mode: Run mode
    :param context_log_level: Context log level
    :return: Spark session
    """
    spark_config = SparkConf()
    config_var_list = [("spark.app.name", app_name)]
    if run_mode == "local_single_worker":
        config_var_list += [("spark.master", "local")]
    elif run_mode == "local_cluster":
        SPARK_DRIVER_HOST = (
            check_output(["hostname", "-i"]).decode(encoding="utf-8").strip()
        )
        # See: https://github.com/bitnami/bitnami-docker-spark/issues/18#issuecomment-701487655
        os.environ["SPARK_LOCAL_IP"] = SPARK_DRIVER_HOST
        config_var_list += [
            (k, v) for k, v in spark_local_cluster_context_config.items()
        ] + [
            # spark.master = spark://<ip of master node>:<port of master node>
            (
                "spark.master",
                os.environ.get("SPARK_MASTER_URL", "spark://spark-master:7077"),
            ),
            # spark.driver.host = IP of the driver (e.g. the machine / docker container from where we are running the
            # pyspark code)
            ("spark.driver.host", SPARK_DRIVER_HOST),
        ]
    elif run_mode == "emr_serverless":
        # Note - The config is sent when triggering the EMR Serverless job, not when creating the spark context
        pass
    else:
        raise NotImplementedError(f"Run mode {run_mode} not implemented")
    spark_config.setAll(config_var_list)
    spark = SparkSession.builder.config(conf=spark_config).getOrCreate()
    spark.sparkContext.setLogLevel(context_log_level)
    return spark
