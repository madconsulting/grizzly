import os
import pathlib
from typing import Optional, Union


def get_base_dir(
    path_end: str = "grizzly_main",
    path_input: Optional[Union[str, pathlib.Path]] = None,
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
    base_dir = pathlib.Path(pathlib.Path(path_input).resolve(strict=True))
    if path_end not in str(base_dir):
        raise ValueError(f"path_end={path_end} not present in the input path.")
    is_found = False
    while not is_found:
        if base_dir.parts[-1] == path_end:
            is_found = True
        else:
            base_dir = pathlib.Path(base_dir.parent)
    return base_dir


class cd:
    """Context manager for changing the current working directory"""

    def __init__(self, new_path):
        """
        The function initializes a new instance of a class with a given path.

        :param new_path: The `new_path` parameter is a string that represents a file path. It is used to initialize an
        instance of the class. The `os.path.expanduser()` function is used to expand the user's home directory in the
        file path, if it contains a tilde (~) character
        """
        self.new_path = os.path.expanduser(new_path)
        self.saved_path = None

    def __enter__(self):
        """
        The `__enter__` function changes the current working directory to a new path.
        """
        self.saved_path = os.getcwd()
        os.chdir(self.new_path)

    def __exit__(self, etype, value, traceback):
        """
        The function restores the current working directory to its original path when exiting a context manager.

        :param etype: The `etype` parameter in the `__exit__` method represents the type of exception that was raised,
        if any. It is a reference to the exception class itself
        :param value: The `value` parameter in the `__exit__` method is used to capture the exception value, if any,
        that was raised in the `with` block. It represents the actual exception object that was raised. If no
        exception was raised, the `value` parameter will be `None`
        :param traceback: The traceback parameter is a traceback object that contains information about the current call
        stack. It provides details about the sequence of function calls that led to the current point of execution
        """
        os.chdir(self.saved_path)
