import os
from logger import logger
from common.constants import upload_folder, before_sell, after_sell


def create_folder(chassis_number):
    """
    * creates folder name chassis_number with `before` and `after` subfolder.
    * `before` is used for storing files before sell
    * `after` is used for storing after sell files.

    Args:
        chassis_number (str): tractor chassis number `primary key`

    Returns:
        bool: True means successfully created folders.
    """
    try:
        logger.info(f"creating_folder {upload_folder}\\{chassis_number}")
        os.makedirs(os.path.join(upload_folder, chassis_number, before_sell))
        os.makedirs(os.path.join(upload_folder, chassis_number, after_sell))
        logger.info(f"{upload_folder}\\{chassis_number} has been created")
        return True
    except FileExistsError:
        logger.exception(f"{chassis_number} already exist")
        return False
    except Exception as e:
        logger.exception(f"create_folder got error", exc_info=True)
        return False


def lowercase_data(given_dict):
    """
    user input collected from HTML form is converted to lower case for data `consistency`.

    Args:
        given_dict (dict): `flask request.form` object or `dict`

    Returns:
        dict: whose keys and values are converted `lowercase`
    """
    return {str(key).lower(): str(value).lower() for key, value in given_dict.items()}


if __name__ == "__main__":
    print(create_folder("1234GH45"))
    print(lowercase_data({"HI": "hELLo"}))
