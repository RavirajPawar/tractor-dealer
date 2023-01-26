import os
from logger import logger


def create_folder(chassis_number):
    try:
        logger.info(f"creating_folder {chassis_number}")
        if not os.path.exists(chassis_number):
            os.makedirs(os.path.join("data", chassis_number, "before"))
            os.makedirs(os.path.join("data", chassis_number, "after"))
            logger.info(f"{chassis_number} has been created")
            return True
    except FileExistsError:
        logger.exception(f"{chassis_number} already exist")
        return False
    except Exception as e:
        logger.exception(f"create_folder got error", exc_info=True)
        return False


def lowercase_data(given_dict):
    return {str(key).lower(): str(value).lower() for key, value in given_dict.items()}


if __name__ == "__main__":
    print(create_folder("1234GH45"))
    print(lowercase_data({"HI": "hELLo"}))
