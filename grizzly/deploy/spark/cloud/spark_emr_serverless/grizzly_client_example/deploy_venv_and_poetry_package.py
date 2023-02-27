from grizzly.deploy.spark.cloud.spark_emr_serverless.build.deploy_venv_and_poetry_package import (
    deploy_venv_and_poetry_package,
)
from grizzly.deploy.spark.cloud.spark_emr_serverless.grizzly_client_example.main_config import (
    main_config,
)

deploy_venv_and_poetry_package(main_config=main_config)
