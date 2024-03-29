from deploy_examples.spark_emr_serverless_example.main.get_base_dir import get_client_base_dir
from deploy_examples.spark_emr_serverless_example.main.main_config import main_config

from grizzly_main.deploy.spark.cloud.spark_emr_serverless.get_config_variables import get_spark_emr_serverless_config
from grizzly_main.deploy.spark.cloud.spark_emr_serverless.trigger_emr_job import trigger_emr_job

base_dir_client_repo = get_client_base_dir()
spark_emr_serverless_config = get_spark_emr_serverless_config(base_dir_client_repo=base_dir_client_repo, **main_config)


if __name__ in "__main__":
    # Additional Inputs --------------------------------------------------------------------------------------------
    is_update_script_s3 = True
    exec_timeout_min = 20
    # Note: Multiple examples available in the pyspark_example.py script - modify its __main__ to select one example
    # from all the available ones in "grizzly_main/deploy/spark/pyspark_examples" examples available
    script_path = "deploy_examples/spark_emr_serverless_example/main/pyspark_example.py"
    # --------------------------------------------------------------------------------------------------------------

    # Trigger EMR Serverless job
    job_run_id = trigger_emr_job(
        spark_emr_serverless_config=spark_emr_serverless_config,
        script_file_path=script_path,
        is_update_script_s3=is_update_script_s3,
        base_dir_client_repo=base_dir_client_repo,
        execution_timeout_min=exec_timeout_min,
    )
