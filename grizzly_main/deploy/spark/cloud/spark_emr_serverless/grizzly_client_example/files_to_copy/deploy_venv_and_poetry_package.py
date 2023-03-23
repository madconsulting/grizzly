from grizzly_main.deploy.spark.cloud.spark_emr_serverless.build.deploy_venv_and_poetry_package import (
    deploy_venv_and_poetry_package,
)
from deploy_examples.spark_emr_serverless_example.main.main_config import main_config
from grizzly_main.path_interations import get_base_dir

base_dir_client_repo = get_base_dir(path_end=main_config["repository_name"],)

if __name__ in "__main__":
    deploy_venv_and_poetry_package(
        main_config=main_config, base_dir_client_repo=base_dir_client_repo
    )
