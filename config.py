# -*- coding: UTF-8 -*-

import sys
import configparser


class Config:
    def __init__(self):
        self.Maps = {}
        self.set_default()

    def set_default(self):
        config = configparser.ConfigParser()
        config.read("config.ini", encoding="utf-8")
        config_app_info = config["app_info"]
        config_params = config["params"]
        config_paths = config["paths"]

        self.Maps["jd_app_key"] = config_app_info["jd_app_key"]
        self.Maps["jd_secret_key"] = config_app_info["jd_secret_key"]

        self.Maps["jpg_quality"] = int(config_params["jpg_quality"])
        self.Maps["probability"] = float(config_params["probability"])
        self.Maps["binary_threshold"] = int(config_params["binary_threshold"])

        self.Maps["current_dir"] = sys.path[0]
        self.Maps["video_dir"] = self.Maps["current_dir"] + config_paths["video_dir"]
        self.Maps["binary_tmp"] = self.Maps["current_dir"] + config_paths["binary_tmp"]
        self.Maps["output_dir"] = self.Maps["current_dir"] + config_paths["output_dir"]

    def set_video_dir(self, _dir):
        self.Maps["video_dir"] = _dir + "/"  # 指定视频源文件目录

    def set_video_name(self, _name):
        self.Maps["video_name"] = _name[:_name.rfind(".")]
        self.Maps["video_suffix"] = _name[_name.rfind("."):]
        self.Maps["video_path"] = self.Maps["video_dir"] + _name

    def set_video_info(self, _w, _h, _fc, _fps):
        self.Maps["video_width"] = _w
        self.Maps["video_height"] = _h
        self.Maps["frame_count"] = _fc
        self.Maps["fps"] = _fps

    def set_params(self, _yf, _yt, _bth):
        self.Maps["y_from"] = _yf
        self.Maps["y_to"] = _yt
        self.Maps["binary_threshold"] = _bth

    def get_value(self, key):
        return self.Maps[key]
