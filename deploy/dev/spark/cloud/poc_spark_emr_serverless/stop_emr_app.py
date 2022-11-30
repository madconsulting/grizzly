import boto3

from deploy.dev.spark.cloud.poc_spark_emr_serverless.config import (
    poc_spark_emr_serverless_config as poc_config,
)


def stop_emr_app() -> None:
    """
    Stop EMR Serverless application. Note that stopping the app manually is not always required as
    the app automatically stops after x time of being idle, where x is defined in the Pulumi config.
    :return: pyspark.tar.gz
    """
    emr_client = boto3.client("emr-serverless")
    _ = emr_client.stop_application(
        applicationId=poc_config["emr_serverless"]["app_id"]
    )


if __name__ == "__main__":

    # Stop EMR Serverless application
    stop_emr_app()
