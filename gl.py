# -*- coding: UTF-8 -*-


class Global:
    Types = (".mp4", ".avi", ".mkv", ".wmv", ".mov", ".flv")
    BD_API = {
        "通用文字识别": "general_basic",
        "通用文字识别（含位置信息版）": "general",
        "通用文字识别（高精度版）": "accurate_basic",
        "通用文字识别（高精度含位置版）": "accurate",
        "网络图片文字识别": "web_image"
    }
    BD_Lang = {
        "中英文混合": "CHN_ENG",
        "英文": "ENG",
        "葡萄牙语": "POR",
        "法语": "FRE",
        "德语": "GER",
        "意大利语": "ITA",
        "西班牙语": "SPA",
        "俄语": "RUS",
        "日语": "JAP",
        "韩语": "KOR",
    }

    config = None
    gui = None
    timeline = None
    jd_ocr = None
    bd_ocr = None
    opencv_utils = None
    ocr_utils = None
