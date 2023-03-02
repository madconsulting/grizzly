import os
import sys
import pprint
import tomlkit
from zipfile import ZipFile
from typing import Tuple, Optional
from grizzly_main.path_interations import get_base_dir

base_dir = get_base_dir()


# ----------- Poetry functions -----------
def _get_current_poetry_package_name_and_version(poetry_dir: str) -> Tuple[str, str]:
    """
    Get current Poetry package name and version from pyproject.toml file
    :param poetry_dir: Poetry directory
    :return: Current poetry package name and version
    """
    if poetry_dir != "":
        poetry_dir += "/"
    with open(os.path.abspath(f"{poetry_dir}pyproject.toml")) as pyproject:
        file_contents = pyproject.read()
    package_name = tomlkit.parse(file_contents)["tool"]["poetry"]["name"]
    package_version = tomlkit.parse(file_contents)["tool"]["poetry"]["version"]
    return package_name, package_version


def _get_poetry_package_name_and_version(
    poetry_dir: str = "", package_version: str = None
) -> Tuple[str, str]:
    """
    Get Poetry package name and version from pyproject.toml file (or overwritten by input)
    :param poetry_dir: Poetry directory
    :param package_version: Poetry package version. By default (None) using the current package version in
                            the pyproject.toml file
    :return: Poetry package name and version
    """
    (
        package_name,
        current_package_version,
    ) = _get_current_poetry_package_name_and_version(poetry_dir=poetry_dir)
    if package_version is None:
        package_version = current_package_version
    return package_name, package_version


# ----------- Wheel file functions -----------
def get_poetry_wheel_file(
    poetry_dir: str = "",
    file_folder: str = "deploy/spark/cloud/spark_emr_serverless/build/temp_artifacts/package_wheel_files",
    package_version: str = None,
) -> Optional[str]:
    """
    Get wheel file name
    :param poetry_dir: Poetry directory
    :param file_folder: Wheel file folder
    :param package_version: Poetry package version. By default (None) using the current package version in
                            the pyproject.toml file
    :return: Wheel file name
    """
    package_name, package_version = _get_poetry_package_name_and_version(
        poetry_dir=poetry_dir, package_version=package_version
    )
    wheel_file_name = f"{package_name}-{package_version}.whl"
    print(f"{file_folder}/{wheel_file_name}")
    return wheel_file_name


def rename_poetry_wheel_file(
    poetry_dir: str = "",
    file_folder: str = "deploy/spark/cloud/spark_emr_serverless/build/temp_artifacts/package_wheel_files",
) -> None:
    """
    Get the poetry wheel file for the current Poetry package name and version
    :param poetry_dir: Poetry directory
    :param file_folder: Folder where we store the wheel files of Poetry
    :return: None
    """
    package_name, package_version = _get_poetry_package_name_and_version(
        poetry_dir=poetry_dir, package_version=None
    )
    built_files = os.listdir(path=f"{base_dir}/{file_folder}")
    current_package_wheel_file = [
        file_name
        for file_name in built_files
        if file_name.replace("_", "-").startswith(f"{package_name.replace('_', '-')}-{package_version}-py3")
        and file_name.endswith(".whl")
    ]
    if len(current_package_wheel_file) == 0:
        raise ValueError(
            f"No wheel file has been found for current package {package_name} and "
            f"version {package_version}"
        )
    elif len(current_package_wheel_file) == 1:
        wheel_file_name = current_package_wheel_file[0]
        new_wheel_file_name = get_poetry_wheel_file(
            poetry_dir=poetry_dir, file_folder=file_folder, package_version=None
        )
        os.rename(
            f"{base_dir}/{file_folder}/{wheel_file_name}",
            f"{base_dir}/{file_folder}/{new_wheel_file_name}",
        )
    else:
        raise ValueError(
            f"Multiple wheel files has been found for current package {package_name} and "
            f"version {package_version}: {current_package_wheel_file}. We should only have that "
            f"-> revise that!"
        )


def list_files_inside_wheel(wheel_file_path: str) -> None:
    """
    List files inside wheel
    :param wheel_file_path: Wheel file path
    :return: None
    """
    names = ZipFile(wheel_file_path).namelist()
    pprint.pprint(names)


# ----------- Venv file functions -----------
def get_venv_file(
    poetry_dir: str = "",
    file_folder: str = "deploy/spark/cloud/spark_emr_serverless/build/temp_artifacts/venvs",
    package_version: str = None,
) -> str:
    """
    Get venv file name
    :param poetry_dir: Poetry directory
    :param file_folder: Venv file folder
    :param package_version: Poetry package version. By default (None) using the current package version in
                            the pyproject.toml file
    :return: Venv file name
    """
    package_name, package_version = _get_poetry_package_name_and_version(
        poetry_dir=poetry_dir, package_version=package_version
    )
    venv_file_name = f"{package_name}-{package_version}.tar.gz"
    print(f"{file_folder}/{venv_file_name}")
    return venv_file_name


def add_package_version_to_venv(
    poetry_dir: str = "",
    file_folder: str = "deploy/spark/cloud/spark_emr_serverless/build/temp_artifacts/venvs",
    file_name: str = "pyspark.tar.gz",
) -> None:
    """
    Add current Poetry package version to venv file
    :param poetry_dir: Poetry directory
    :param file_folder: Venv file folder
    :param file_name: Venv original file name
    :return: None
    """
    new_venv_file_name = get_venv_file(poetry_dir=poetry_dir, file_folder=file_folder, package_version=None)
    os.rename(
        f"{base_dir}/{file_folder}/{file_name}",
        f"{base_dir}/{file_folder}/{new_venv_file_name}",
    )


if __name__ == "__main__":
    args = sys.argv
    # args[0] = current file
    # args[1] = function name
    # args[2:] = function args : (*unpacked)
    globals()[args[1]](*args[2:])

    # To debug wheel file: list_files_inside_wheel(wheel_file_path="dist/spark-0.1.0-py3-none-any.whl")
