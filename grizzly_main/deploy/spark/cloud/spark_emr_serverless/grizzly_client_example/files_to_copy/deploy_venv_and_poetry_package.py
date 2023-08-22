from deploy_examples.spark_emr_serverless_example.main.get_base_dir import (
    get_client_base_dir,
)
from deploy_examples.spark_emr_serverless_example.main.main_config import main_config

from grizzly_main.deploy.spark.cloud.spark_emr_serverless.build.deploy_venv_and_poetry_package import (
    deploy_venv_and_poetry_package,
)

if __name__ in "__main__":
    deploy_venv_and_poetry_package(
        main_config=main_config, base_dir_client_repo=get_client_base_dir()
    )
