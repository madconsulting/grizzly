import boto3
from typing import Dict, Any


def stop_emr_app(spark_emr_serverless_config: Dict[str, Any]) -> None:
    """
    Stop EMR Serverless application. Note that stopping the app manually is not always required as
    the app automatically stops after x time of being idle, where x is defined in the Pulumi config.
    :param spark_emr_serverless_config: Spark EMR Serverless config
    :return: pyspark.tar.gz
    """
    emr_client = boto3.client("emr-serverless")
    _ = emr_client.stop_application(
        applicationId=spark_emr_serverless_config["emr_serverless"]["app_id"]
    )


if __name__ == "__main__":

    # Example of main config defined by a Mad Consulting client
    from grizzly.deploy.spark.cloud.spark_emr_serverless.main_config_example import (
        main_config,
    )
    from grizzly.deploy.spark.cloud.spark_emr_serverless.get_config_variables import (
        get_spark_emr_serverless_config,
    )

    spark_emr_serverless_config = get_spark_emr_serverless_config(**main_config)

    # Stop EMR Serverless application
    stop_emr_app(spark_emr_serverless_config=spark_emr_serverless_config)
