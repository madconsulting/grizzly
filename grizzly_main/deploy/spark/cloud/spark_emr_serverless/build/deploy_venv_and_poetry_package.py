import os
import inspect
import shutil
import subprocess
from typing import Dict, Any

from grizzly_main.path_interations import cd, get_base_dir
import grizzly_main.deploy.spark.cloud.spark_emr_serverless.build
from grizzly_main.iac_pulumi.pulumi_rest_api_functions import get_pulumi_stack_state
from grizzly_main.deploy.spark.cloud.spark_emr_serverless.get_config_variables import get_s3_bucket_id_from_pulumi

base_dir = get_base_dir()


def copy_poetry_raw_files(poetry_dir: str):
    poetry_dir = os.path.abspath(poetry_dir)
    for file in ["pyproject.toml", "poetry.lock"]:
        shutil.copyfile(
            src=f"{poetry_dir}/{file}",
            dst=f"{base_dir}/deploy/spark/cloud/spark_emr_serverless/build/temp_artifacts/poetry_raw_files/{file}"
        )


def delete_copies_of_poetry_raw_files():
    for file in ["pyproject.toml", "poetry.lock"]:
        os.remove(f"{base_dir}/deploy/spark/cloud/spark_emr_serverless/build/temp_artifacts/poetry_raw_files/{file}")


def deploy_venv_and_poetry_package(main_config: Dict[str, Any]):
    python_version = main_config["python_version"]
    os.environ["PYTHON_VERSION"] = python_version
    os.environ["PYTHON_VERSION_SHORT"] = python_version[:python_version.rfind('.')]
    os.environ["POETRY_VERSION"] = main_config["poetry_version"]
    os.environ["GRIZZLY_BASE_DIR"] = str(base_dir)
    pulumi_organization = main_config["pulumi_organization"]
    pulumi_project = main_config["pulumi_project"]
    pulumi_stack = main_config["pulumi_stack"]
    stack_state_dict = get_pulumi_stack_state(
        pulumi_organization=pulumi_organization,
        pulumi_project=pulumi_project,
        pulumi_stack=pulumi_stack,
    )
    os.environ["S3_BUCKET"] = get_s3_bucket_id_from_pulumi(
        stack_state_dict=stack_state_dict,
        project_stack_name=f"{pulumi_organization}/{pulumi_project}/{pulumi_stack}"
    )
    build_dir = os.path.dirname(
                inspect.getfile(grizzly_main.deploy.spark.cloud.spark_emr_serverless.build)
    )
    build_file_path = os.path.abspath(f"{build_dir}/build.sh")
    copy_poetry_raw_files(poetry_dir=main_config["poetry_dir"])
    subprocess.call(['sh', build_file_path])
    delete_copies_of_poetry_raw_files()
