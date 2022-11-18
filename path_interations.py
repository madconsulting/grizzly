import pathlib

from typing import Union


def get_base_dir(
    path_end: str = "grizzly",
    path_input: Union[str, pathlib.Path] = None,
) -> pathlib.Path:
    """
    Iterate until finding the end of the path. This is used to be able to run a script from multiple different
    directories, by retrieving the base dir.
    :param path_end: Path end
    :param path_input: Path input
    :return: The base path
    """
    if path_input is None:
        path_input = pathlib.Path(__file__).absolute()
    base_dir = pathlib.Path(
        pathlib.Path(path_input).resolve(strict=True).parent
    )
    is_found = False
    while not is_found:
        if base_dir.parts[-1] == path_end:
            is_found = True
        else:
            base_dir = pathlib.Path(base_dir.parent)
    return base_dir
