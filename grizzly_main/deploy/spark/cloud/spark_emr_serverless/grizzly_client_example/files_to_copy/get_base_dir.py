import pathlib

from deploy_examples.spark_emr_serverless_example.main.main_config import main_config

from grizzly_main.path_interations import get_base_dir


def get_client_base_dir():
    """
    Get client base directory
    :return:
    """
    try:
        # File path
        path_input = pathlib.Path(__file__).absolute()
    except NameError:
        # Current working directory path
        path_input = pathlib.Path().absolute()
    return get_base_dir(path_end=main_config["repository_name"], path_input=path_input)
