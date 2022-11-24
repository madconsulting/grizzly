import os
import sys
import pprint
import tomlkit
from zipfile import ZipFile
from typing import Tuple, Optional
from path_interations import get_base_dir

base_dir = get_base_dir()


def _get_current_poetry_package_name_and_version() -> Tuple[str, str]:
    """
    Get current Poetry package name and version from pyproject.toml file
    :return: Current poetry package name and version
    """
    with open(f"{base_dir}/pyproject.toml") as pyproject:
        file_contents = pyproject.read()
    package_name = tomlkit.parse(file_contents)["tool"]["poetry"]["name"]
    package_version = tomlkit.parse(file_contents)["tool"]["poetry"]["version"]
    return package_name, package_version


def get_poetry_wheel_file(
        poetry_distributions_folder: str = "deploy/dev/spark/cloud/poc_spark_emr_serverless/build/artifacts/package_wheel_files",
        is_return_file_name: bool = False,
) -> Optional[str]:
    """
    Get the poetry wheel file for the current Poetry package name and version
    :param poetry_distributions_folder: Folder where we store the wheel files of Poetry
    :param is_return_file_name: True if returning the wheel file name, False otherwise
    :return: Wheel file name or None
    """
    package_name, package_version = _get_current_poetry_package_name_and_version()
    built_files = os.listdir(path=f"{base_dir}/{poetry_distributions_folder}")
    current_package_wheel_file = [
        file_name
        for file_name in built_files
        if file_name.startswith(f"{package_name}-{package_version}-py3") and file_name.endswith(".whl")
    ]
    if len(current_package_wheel_file) == 0:
        raise ValueError(
            f"No wheel file has been found for current package {package_name} and "
            f"version {package_version}"
        )
    elif len(current_package_wheel_file) == 1:
        wheel_file_name = current_package_wheel_file[0]
        print(f"{poetry_distributions_folder}/{wheel_file_name}")
        if is_return_file_name:
            return wheel_file_name
    else:
        raise ValueError(
            f"Multiple wheel files has been found for current package {package_name} and "
            f"version {package_version}: {current_package_wheel_file}. We should only have that "
            f"-> revise that!"
        )


def list_files_inside_wheel(wheel_file_path: str):
    """
    List files inside wheel
    :param wheel_file_path: Wheel file path
    :return:
    """
    names = ZipFile(wheel_file_path).namelist()
    pprint.pprint(names)


if __name__ == "__main__":
    args = sys.argv
    # args[0] = current file
    # args[1] = function name
    # args[2:] = function args : (*unpacked)
    globals()[args[1]](*args[2:])

    # To debug wheel file: list_files_inside_wheel(wheel_file_path="dist/spark-0.1.0-py3-none-any.whl")
