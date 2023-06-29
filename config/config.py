from common.constants import upload_folder


class DefaultConfig(object):
    DEBUG = True


class DevConfig:
    DEBUG = True
    MONGO_URI = "mongodb://localhost:27017/tractor_dealer?readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false"
    UPLOAD_FOLDER = upload_folder
    SECRET_KEY = "Imr@nRih@nReh@n202301"
