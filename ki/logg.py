import os
import sys
import logging


LOG_FORMAT = (
    "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:] %(message)s"
)


def configure(**kwargs):
    is_debug = kwargs.get("debug", os.environ.get("DEBUG", False))
    logging.basicConfig(
        level=(logging.DEBUG if is_debug else logging.INFO),
        stream=sys.stdout,
        format=LOG_FORMAT,
    )


def get(name):
    return logging.getLogger(name)
