import logging
import os
import sys
import warnings
from typing import Optional


def _get_default_log_formatter() -> logging.Formatter:
    """
    Get default logging formatter

    :return: Logging formatter
    """
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    log_dt_format = "%m/%d/%Y %H:%M:%S %z"
    return logging.Formatter(fmt=log_format, datefmt=log_dt_format)


def add_extra_logger_to_prefect(logger_name: str) -> None:
    """
    Add extra logger to Prefect

    :param logger_name: Logger name to add
    :return: None
    """
    current_prefect_loggers = os.environ.get("PREFECT_LOGGING_EXTRA_LOGGERS")
    if not current_prefect_loggers:
        os.environ["PREFECT_LOGGING_EXTRA_LOGGERS"] = logger_name
        logging.info(f"Added logger: {logger_name} to Prefect")
    elif logger_name not in os.environ["PREFECT_LOGGING_EXTRA_LOGGERS"].split(","):
        os.environ["PREFECT_LOGGING_EXTRA_LOGGERS"] = f"{current_prefect_loggers},{logger_name}"
        logging.info(f"Added logger: {logger_name} to Prefect")


def remove_duplicate_handlers_by_name(logger) -> None:
    """
    Remove duplicate handlers by name

    :param logger: Logger
    :return: None
    """
    handler_names = set()  # A set to keep track of unique handler names
    handlers_to_remove = []  # A list to collect duplicate handlers

    for handler in logger.handlers:
        if handler.name in handler_names:
            handlers_to_remove.append(handler)
        else:
            handler_names.add(handler.name)

    # Remove the duplicate handlers
    for handler in handlers_to_remove:
        logger.removeHandler(handler)


def add_stdout_logger_as_root(
    log_level: str = "INFO",
    logger_name: str = "stdout_logger",
    log_formatter: Optional[logging.Formatter] = None,
    is_enable_in_prefect: bool = False,
    is_remove_all_previous_handlers: bool = False,
    is_remove_duplicate_handler_names: bool = True,
) -> None:
    """
    Add STDOUT logger

    :param log_level: Log level
    :param logger_name: Logger name
    :param log_formatter: Log formatter
    :param is_enable_in_prefect: True if enabling logger in Prefect, False otherwise
    :param is_remove_all_previous_handlers: True if removing all previous handlers for the logger with logger_name
    :param is_remove_duplicate_handler_names: True if removing duplicate handler names
    :return: None
    """
    stdout_logger = logging.getLogger(logger_name)
    if is_remove_all_previous_handlers:
        for handler in stdout_logger.handlers:
            stdout_logger.removeHandler(handler)
    stdout_logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    if not log_formatter:
        log_formatter = _get_default_log_formatter()
    handler.setFormatter(log_formatter)
    stdout_logger.addHandler(handler)
    if is_enable_in_prefect:
        add_extra_logger_to_prefect(logger_name=logger_name)
    else:
        # A disabled root logger handler appears also in logging.root when importing the prefect library. So we will
        # disable warnings related to that disabled logger handler
        warning_pattern = r"Logger 'stdout_logger' attempted to send logs to the API without a flow run id."
        warnings.filterwarnings("ignore", category=UserWarning, message=warning_pattern)
    if is_remove_duplicate_handler_names:
        remove_duplicate_handlers_by_name(stdout_logger)
    # Define the stdout logger as the root logger
    logging.root = stdout_logger  # type: ignore


def redirect_logger_to_root_logger(
    logger_name: str,
    is_enable_in_prefect: bool = False,
) -> None:
    """
    Redirect logger to root logger

    :param logger_name: Logger name
    :param is_enable_in_prefect: True if enabling logger in Prefect, False otherwise
    :return:
    """
    root_logger = logging.getLogger()
    optuna_logger = logging.getLogger(logger_name)
    optuna_logger.handlers = root_logger.handlers
    optuna_logger.setLevel(root_logger.level)  # noqa: W0105
    if is_enable_in_prefect:
        add_extra_logger_to_prefect(logger_name=logger_name)


if __name__ in "__main__":
    # Example on how to use custom logger in Prefect

    from prefect import flow, task

    def function_example() -> None:
        """
        Function example

        :return: None
        """
        logging.info("This is a INFO logging statement from a function called by Prefect")
        logging.warning("This is a WARNING logging statement from a function called by Prefect")

    @task
    def task_example() -> None:
        """
        Task example

        :return: None
        """
        logging.info("This is a INFO logging statement from a Prefect task")
        logging.warning("This is a WARNING logging statement from a  Prefect task")
        function_example()

    @flow(log_prints=True)
    def example_logger() -> None:
        """
        Example logger

        :return: None
        """
        add_stdout_logger_as_root(is_enable_in_prefect=True)
        logging.info("This is a INFO logging statement from a Prefect flow")
        logging.warning("This is a WARNING logging statement from a  Prefect flow")
        task_example()

    example_logger()
