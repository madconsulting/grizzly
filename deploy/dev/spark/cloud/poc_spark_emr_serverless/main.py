import boto3

from path_interations import get_base_dir
from deploy.dev.spark.cloud.poc_spark_emr_serverless.config import poc_spark_emr_serverless_config as poc_config


def upload_file_to_s3(code_file_path: str):
    base_dir = get_base_dir()
    s3_client = boto3.client("s3")
    s3_client.upload_file(
        Filename=f"{base_dir}/deploy/dev/spark/cloud/poc_spark_emr_serverless/{code_file_path}",
        Bucket=poc_config["s3_bucket"],
        Key=code_file_path,
    )


def trigger_emr_job(code_file_path: str, execution_timeout_min: int = 30):
    emr_app_id = poc_config["emr_serverless"]["app_id"]
    emr_client = boto3.client('emr-serverless')
    emr_app_details = emr_client.get_application(applicationId=emr_app_id)["application"]
    print(f"{poc_config['emr_serverless']['app_name']} - details:")
    print(emr_app_details)
    _ = emr_client.start_application(
        applicationId=emr_app_id
    )
    spark_submit_parameters = " ".join([f"--conf {k}={v}" for k, v in poc_config["spark_submit_parameters"].items()])
    start_job_run_resp = emr_client.start_job_run(
        applicationId=emr_app_id,
        executionRoleArn=poc_config["emr_serverless"]["job_role_arn"],
        jobDriver={
            'sparkSubmit': {
                'entryPoint': f"s3://{poc_config['s3_bucket']}/{code_file_path}",
                'sparkSubmitParameters': spark_submit_parameters
            },
        },
        configurationOverrides={
            'monitoringConfiguration': {
                's3MonitoringConfiguration': {
                    'logUri': f"s3://{poc_config['s3_bucket']}/logs/",
                },
            }
        },
        executionTimeoutMinutes=execution_timeout_min,
        # name='' # TODO - after looking default name, use name format with datetime in it if necessary
    )
    _ = emr_client.stop_application(
        applicationId=emr_app_id
    )


def analyse_job_run():
    # TODO
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/emr-serverless.html#EMRServerless.Client.get_dashboard_for_job_run
    pass


if __name__ == "__main__":

    # Inputs
    is_update_code = False
    # code_file_path = "code_examples/extreme_weather.py"
    code_file_path = "code_examples/simple_example.py"

    # Trigger example
    if is_update_code:
        upload_file_to_s3(code_file_path=code_file_path)
    trigger_emr_job(code_file_path=code_file_path)

    # TODO - find ways to run from jupyter notebook as well.

