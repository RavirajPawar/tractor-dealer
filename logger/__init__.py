import logging


class CustomLogger:
    """logger class which crates logging class object"""

    def __init__(self):
        self.custom_logger = logging.getLogger()
        stream_handler = logging.StreamHandler()
        log_formatter = logging.Formatter(
            "[%(asctime)s] - [%(levelname)s] - [%(filename)s:%(lineno)d] - %(message)s"
        )
        stream_handler.setFormatter(log_formatter)
        self.custom_logger.addHandler(stream_handler)


logger = CustomLogger().custom_logger
