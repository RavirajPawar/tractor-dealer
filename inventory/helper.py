import os
from logger import logger


def create_folder(chassis_number):
    try:
        if not os.path.exists(chassis_number):
            os.makedirs(os.path.join("data", chassis_number))
            logger.info(f"{chassis_number} has been created")
            return True
    except FileExistsError:
        logger.exception(f"{chassis_number} already exist")
        return False
    except Exception as e:
        logger.exception(f"create_folder got error", exc_info=True)
        return False


if __name__ == "__main__":
    print(create_folder("imran123"))
