import os
import time
from flask import request
from functools import wraps
from common.constants import upload_folder
from logger import logger


def setup_app():
    logger.info("stared checking setup")
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        logger.info(f"{upload_folder} created successfully.")
    else:
        logger.info(f"{upload_folder} already exists.")
    logger.info("finished checking setup")


def calculate_time(inner_function):
    @wraps(inner_function)
    def wrapper_function(*args, **kwargs):
        logger.info(
            f"HTTP METHOD:{request.method} URL:{request.base_url}".center(100, "*")
        )
        start_time = time.time()
        rtn = inner_function(*args, **kwargs)
        end_time = time.time()
        logger.info(
            f"VIWE: {inner_function.__name__} took {end_time-start_time}s".center(
                100, "*"
            )
        )
        return rtn

    return wrapper_function
