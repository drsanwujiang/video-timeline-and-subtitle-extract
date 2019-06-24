# -*- coding: UTF-8 -*-

import hashlib
import time

import requests

from config import Config


# sign
def sign(secretkey):
    m = hashlib.md5()
    now_time = int(time.time() * 1000)
    before = secretkey + str(now_time)
    m.update(before.encode('utf8'))
    return now_time, m.hexdigest()


def post_request(url, params, img):
    params['timestamp'], params['sign'] = sign(params['secretkey'])
    params.pop('secretkey')
    return requests.post(url, params=params, data=img)


def jd_general_ocr(image):
    ocr_url = "https://aiapi.jd.com/jdai/ocr_universal"
    params = {
        'type': 'json',
        'content': 'json string',
        'appkey': Config.get_value('APP_KEY'),
        'secretkey': Config.get_value('SECRET_KEY')
    }
    return post_request(ocr_url, params, image).json()
