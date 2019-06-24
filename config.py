# -*- coding: UTF-8 -*-

import sys
import configparser


class Config:
    Maps = {}
    Types = [".mp4", ".avi", ".mkv", ".wmv", ".mov", ".flv"]
    Timeline = None

    @staticmethod
    def set_default():
        config = configparser.ConfigParser()
        config.read("config.ini", encoding="utf-8")
        config_app_info = config["app_info"]
        config_params = config["params"]
        config_paths = config["paths"]

        Config.Maps["APP_KEY"] = config_app_info["APP_KEY"]
        Config.Maps["SECRET_KEY"] = config_app_info["SECRET_KEY"]
        Config.Maps["jpg_quality"] = config_params["jpg_quality"]
        Config.Maps["probability"] = config_params["probability"]
        Config.Maps["similarity"] = config_params["similarity"]
        Config.Maps["y_from"] = config_params["y_from"]
        Config.Maps["y_to"] = config_params["y_to"]
        Config.Maps["binary_threshold"] = config_params["binary_threshold"]
        Config.Maps["current_dir"] = sys.path[0]
        Config.Maps["video_dir"] = Config.Maps["current_dir"] + config_paths["video_dir"]
        Config.Maps["binary_tmp"] = Config.Maps["current_dir"] + config_paths["binary_tmp"]
        Config.Maps["output_dir"] = Config.Maps["current_dir"] + config_paths["output_dir"]

    @staticmethod
    def set_video_dir(_dir):
        Config.Maps["video_dir"] = _dir + "/"  # 指定视频源文件目录

    @staticmethod
    def set_video_name(_name):
        Config.Maps["video_name"] = _name[:_name.rfind(".")]
        Config.Maps["video_suffix"] = _name[_name.rfind("."):]
        Config.Maps["video_path"] = Config.Maps["video_dir"] + _name
        Config.Maps["image_dir"] = "%s%s/" % (Config.Maps["binary_tmp"], Config.Maps["video_name"])

    @staticmethod
    def set_video_info(_w, _h, _fc):
        Config.Maps["video_width"] = _w
        Config.Maps["video_height"] = _h
        Config.Maps["frame_count"] = _fc

    @staticmethod
    def set_params(_yf, _yt, _bth):
        Config.Maps["y_from"] = _yf
        Config.Maps["y_to"] = _yt
        Config.Maps["binary_threshold"] = _bth

    @staticmethod
    def get_value(key):
        return Config.Maps[key]

