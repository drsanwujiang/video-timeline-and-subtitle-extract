# -*- coding: UTF-8 -*-

import hashlib
import time
import requests
from gl import Global


def get_file_content(file_path):
    with open(file_path, "rb") as fp:
        return fp.read()


def sign(secret_key):
    m = hashlib.md5()
    now_time = int(time.time() * 1000)
    before = secret_key + str(now_time)
    m.update(before.encode("utf8"))
    return now_time, m.hexdigest()


def post_request(url, params, img):
    params["timestamp"], params["sign"] = sign(params["secretkey"])
    params.pop("secretkey")
    return requests.post(url, params=params, data=img)


def jd_general_ocr(image_path):
    ocr_url = "https://aiapi.jd.com/jdai/ocr_universal"
    params = {
        "type": "json",
        "content": "json string",
        "appkey": Global.config.get_value("jd_app_key"),
        "secretkey": Global.config.get_value("jd_secret_key")
    }
    image = get_file_content(image_path)
    return post_request(ocr_url, params, image).json()
