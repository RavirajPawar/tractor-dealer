import os
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
