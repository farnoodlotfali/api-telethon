from bingx.api import BingxAPI
from dotenv import dotenv_values

# ****************************************************************************************************************************

config = dotenv_values(".env")


API_KEY = config["API_KEY"]
SECRET_KEY = config["SECRET_KEY"]
# bingx = BingxAPI(API_KEY, SECRET_KEY, timestamp="local")


class BingXApiClass:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = BingxAPI(API_KEY, SECRET_KEY, timestamp="local")
        return cls._instance
