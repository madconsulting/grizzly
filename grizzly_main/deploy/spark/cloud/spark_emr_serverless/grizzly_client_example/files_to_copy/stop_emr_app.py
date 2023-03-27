from grizzly_main.deploy.spark.cloud.spark_emr_serverless.stop_emr_app import (
    stop_emr_app,
)
from grizzly_main.deploy.spark.cloud.spark_emr_serverless.get_config_variables import (
    get_spark_emr_serverless_config,
)

from deploy_examples.spark_emr_serverless_example.main.main_config import main_config
from deploy_examples.spark_emr_serverless_example.main.get_base_dir import (
    get_client_base_dir,
)

base_dir_client_repo = get_client_base_dir()
spark_emr_serverless_config = get_spark_emr_serverless_config(
    base_dir_client_repo=base_dir_client_repo, **main_config
)

if __name__ in "__main__":
    # Stop EMR Serverless application
    stop_emr_app(spark_emr_serverless_config=spark_emr_serverless_config)
