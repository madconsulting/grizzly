from typing import Any, Dict

import boto3


def stop_emr_app(spark_emr_serverless_config: Dict[str, Any]) -> None:
    """
    Stop EMR Serverless application. Note that stopping the app manually is not always required as
    the app automatically stops after x time of being idle, where x is defined in the Pulumi config.
    :param spark_emr_serverless_config: Spark EMR Serverless config
    :return: pyspark.tar.gz
    """
    emr_client = boto3.client("emr-serverless")
    _ = emr_client.stop_application(applicationId=spark_emr_serverless_config["emr_serverless"]["app_id"])
    print("EMR Serverless application stopped.")
