# -*- coding: UTF-8 -*-

import time
import uuid
import base64
import urllib.parse
import hashlib
import requests
from gl import Global


def get_file_content(file_path):
    with open(file_path, "rb") as fp:
        return fp.read()


def post_request(url, params, data):
    return requests.post(url, params=params, data=data)


class BdOcr:
    def __init__(self):
        self.api_key = Global.config.get_value("bd_api_key")
        self.secret_key = Global.config.get_value("bd_secret_key")
        self.token = None
        self.api_list = {
            "general_basic": self.__general_basic,
            "general": self.__general,
            "accurate_basic": self.__accurate_basic,
            "accurate": self.__accurate,
            "web_image": self.__web_image,
        }
        self.api_url_list = {
            "token": Global.config.get_value("bd_access_token_url"),
            "general_basic": Global.config.get_value("bd_general_basic_url"),
            "general": Global.config.get_value("bd_general_url"),
            "accurate_basic": Global.config.get_value("bd_accurate_basic_url"),
            "accurate": Global.config.get_value("bd_accurate_url"),
            "web_image": Global.config.get_value("bd_web_image_url")
        }

    def __del__(self):
        print("BdOcr has been destroyed.")

    def get_token(self):
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key
        }
        response = requests.post(url=self.api_url_list["token"], data=params).json()

        if isinstance(response.get("error", -1), int):
            self.token = response["access_token"]
            return True

        return False

    def __general_basic(self, kwargs):
        image2base64 = base64.b64encode(get_file_content(kwargs["image"]))
        ocr_url = self.api_url_list["general_basic"]
        params = {
            "access_token": self.token
        }
        data = {
            "image": image2base64,
            "language_type": kwargs["lang"],
            "probability": "true"
        }

        return post_request(ocr_url, params, data).json()

    def __general(self, kwargs):
        image2base64 = base64.b64encode(get_file_content(kwargs["image"]))
        ocr_url = self.api_url_list["general"]
        params = {
            "access_token": self.token
        }
        data = {
            "image": image2base64,
            "language_type": kwargs["lang"],
            "probability": "true"
        }

        return post_request(ocr_url, params, data).json()

    def __accurate_basic(self, kwargs):
        image2base64 = base64.b64encode(get_file_content(kwargs["image"]))
        ocr_url = self.api_url_list["accurate_basic"]
        params = {
            "access_token": self.token
        }
        data = {
            "image": image2base64,
            "probability": "true"
        }

        return post_request(ocr_url, params, data).json()

    def __accurate(self, kwargs):
        image2base64 = base64.b64encode(get_file_content(kwargs["image"]))
        ocr_url = self.api_url_list["accurate"]
        params = {
            "access_token": self.token
        }
        data = {
            "image": image2base64,
            "probability": "true"
        }

        return post_request(ocr_url, params, data).json()

    def __web_image(self, kwargs):
        image2base64 = base64.b64encode(get_file_content(kwargs["image"]))
        ocr_url = self.api_url_list["web_image"]
        params = {
            "access_token": self.token
        }
        data = {
            "image": image2base64
        }

        return post_request(ocr_url, params, data).json()

    def get_ocr(self, api="general_basic", **kwargs):
        return self.api_list[api](kwargs)


class TxOcr:
    def __init__(self):
        self.app_id = Global.config.get_value("tx_app_id")
        self.app_key = Global.config.get_value("tx_app_key")
        self.general_ocr_url = Global.config.get_value("tx_general_ocr_url")

    def __del__(self):
        print("TxOcr has been destroyed.")

    @staticmethod
    def __generate_signature(_params, _app_key):
        _sorted_keys = sorted(_params.keys())
        _str = ""
        for _key in _sorted_keys:
            if _params[_key] == "":
                continue
            _str += urllib.parse.urlencode({_key: _params[_key]}) + "&"
        _str += "app_key=" + _app_key
        return hashlib.md5(_str.encode("utf-8")).hexdigest().upper()

    def get_ocr(self, image):
        data = dict({
            "app_id": self.app_id,
            "time_stamp": int(time.time()),
            "nonce_str": uuid.uuid4().hex,
            "image": base64.b64encode(get_file_content(image))
        })

        data["sign"] = self.__generate_signature(data, self.app_key)
        return post_request(self.general_ocr_url, None, data).json()
