import logging


class CustomLogger:
    """logger class which crates logging class object"""

    def __init__(self):
        self.custom_logger = logging.getLogger(__name__)
        self.custom_logger.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        log_formatter = logging.Formatter(
            "[%(asctime)s] - [%(levelname)s] - [%(filename)s:%(lineno)d] - %(message)s"
        )
        stream_handler.setFormatter(log_formatter)
        self.custom_logger.addHandler(stream_handler)


logger = CustomLogger().custom_logger

if __name__=="__main__":
    logger.debug("debug log")
    logger.info("info log")
    logger.warning("warn log")
    logger.error("error log")
    logger.exception("exception log")
