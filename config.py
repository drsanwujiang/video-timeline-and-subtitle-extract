# -*- coding: UTF-8 -*-

import sys
import json
import copy


class Config:
    def __init__(self):
        self.__config = None
        self.__temp_config = None
        self.__set_default()

    def __set_default(self):
        with open("config.json", 'r') as _f:
            self.__config = json.loads(_f.read())
        self.__temp_config = copy.deepcopy(self.__config)

        self.__temp_config["current_dir"] = sys.path[0]
        self.__temp_config["video_dir"] = self.__temp_config["current_dir"] + self.__config["video_dir"]
        self.__temp_config["binary_tmp"] = self.__temp_config["current_dir"] + self.__config["binary_tmp"]
        self.__temp_config["output_dir"] = self.__temp_config["current_dir"] + self.__config["output_dir"]

    def set_video_dir(self, _dir):
        self.__temp_config["video_dir"] = _dir + "/"  # 指定视频源文件目录

    def set_video_name(self, _name):
        self.__temp_config["video_name"] = _name[:_name.rfind(".")]
        self.__temp_config["video_suffix"] = _name[_name.rfind("."):]
        self.__temp_config["video_path"] = self.__temp_config["video_dir"] + _name

    def set_video_info(self, _w, _h, _fc, _fps):
        self.__temp_config["video_width"] = _w
        self.__temp_config["video_height"] = _h
        self.__temp_config["frame_count"] = _fc
        self.__temp_config["fps"] = _fps

    def set_params(self, _yf, _yt, _bth):
        self.__temp_config["y_from"] = _yf
        self.__temp_config["y_to"] = _yt
        self.__temp_config["binary_threshold"] = _bth

    def set_api_info(self, _bak, _bsk, _boa, _bol, _tai, _tak, _exp):
        self.__config["bd_api_key"] = self.__temp_config["bd_api_key"] = _bak
        self.__config["bd_secret_key"] = self.__temp_config["bd_secret_key"] = _bsk
        self.__config["bd_ocr_api"] = self.__temp_config["bd_ocr_api"] = _boa
        self.__config["bd_ocr_lang"] = self.__temp_config["bd_ocr_lang"] = _bol
        self.__config["tx_app_id"] = self.__temp_config["tx_app_id"] = _tai
        self.__config["tx_app_key"] = self.__temp_config["tx_app_key"] = _tak
        self.__config["experience"] = self.__temp_config["experience"] = _exp

    def save_json(self):
        with open("config.json", 'w') as _f:
            json.dump(self.__config, _f, indent="\t")

    def get_value(self, key):
        return self.__temp_config[key]
