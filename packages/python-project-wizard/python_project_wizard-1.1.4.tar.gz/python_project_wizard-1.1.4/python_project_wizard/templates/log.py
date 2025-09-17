import logging
import logging.config
import os


def enable_logging() -> None:
    log_filename = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "..", "logging.conf"
    )
    with open(log_filename) as file:
        logging.config.fileConfig(file)
