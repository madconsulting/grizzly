from grizzly_main.deploy.spark.cloud.spark_emr_serverless.stop_emr_app import (
    stop_emr_app,
)
from deploy_examples.spark_emr_serverless_example.main_config import main_config
from grizzly_main.deploy.spark.cloud.spark_emr_serverless.get_config_variables import (
    get_spark_emr_serverless_config,
)
from grizzly_main.path_interations import get_base_dir

base_dir_client_repo = get_base_dir(path_end=main_config["repository_name"],)
spark_emr_serverless_config = get_spark_emr_serverless_config(
    base_dir_client_repo=base_dir_client_repo, **main_config
)

if __name__ in "__main__":
    # Stop EMR Serverless application
    stop_emr_app(spark_emr_serverless_config=spark_emr_serverless_config)
