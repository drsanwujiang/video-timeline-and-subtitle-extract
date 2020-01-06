# -*- coding: UTF-8 -*-

import time
import copy
from ocrapi import BdOcr, TxOcr, get_exp_account
from requests import RequestException
from gl import Global


class OCRUtils:
    def __init__(self):
        # 定义参数变量
        self.subtitle_list = None
        self.probability_bd = None
        self.subtitle_count = None
        self.binary_tmp = None
        self.output_dir = None
        self.video_name = None
        self.fps = None

        self.bd_retry_list = (1, 2, 282000, 216630)  # 需要重试的返回码列表
        self.bd_skip_list = (216200, 282810)  # 需要忽略的返回码列表
        self.tx_skip_list = (16405, 16415, 16430, 16431, 16439)  # 需要忽略的返回码列表
        self.bd_ocr_api = None  # 百度 OCR 参数
        self.bd_ocr_lang = None
        self.str_tx_app_id = None
        self.str_tx_app_key = None
        self.ocr = None  # OCR对象
        self.cancel_flag = False  # 线程中止标志

    def __get_params(self):
        self.subtitle_list = copy.deepcopy(Global.timeline)  # 深拷贝
        self.probability_bd = Global.config.get_value("probability_bd")
        self.subtitle_count = len(self.subtitle_list)
        self.binary_tmp = Global.config.get_value("binary_tmp")
        self.output_dir = Global.config.get_value("output_dir")
        self.video_name = Global.config.get_value("video_name")
        self.fps = Global.config.get_value("fps")
        self.bd_ocr_api = Global.config.get_value("bd_ocr_api")
        self.bd_ocr_lang = Global.config.get_value("bd_ocr_lang")

    def __get_subtitle_bd(self):
        self.__update_gui("初始化百度OCR...", 0)
        self.ocr = BdOcr()
        skip_images = []

        if not self.ocr.get_token():
            return -11, None

        current_subtitle = 0

        for subtitle in self.subtitle_list:
            retry_times = 0
            current_subtitle += 1
            image_name = str(subtitle[0]).zfill(6)

            try:
                result, status = self.__get_ocr_bd(image_name)

                while True:
                    if status == -1:  # QPS限制，重试
                        self.__update_gui("%s 触发QPS限制, 重试..." % image_name,
                                          int(current_subtitle * 100 / self.subtitle_count))
                        time.sleep(0.1)  # 线程暂停
                    elif status == -3:  # 需要重新请求的错误
                        self.__update_gui("%s 识别错误, 正在重试..." % image_name,
                                          int(current_subtitle * 100 / self.subtitle_count))
                        time.sleep(0.1)  # 线程暂停
                    elif status == -5:  # 预料之外的错误
                        retry_times += 1
                        self.__update_gui("返回预料之外的错误码! 正在第 %d 次重试……"
                                          % retry_times, int(current_subtitle * 100 / self.subtitle_count))
                        if retry_times == 10:
                            return -3, [image_name, result[0], result[1]]
                        time.sleep(0.5)  # 线程暂停
                    else:
                        break

                    result, status = self.__get_ocr_bd(image_name)

                if status == -2:  # 请求次数耗尽
                    return -12, None
                elif status == -4:  # 需要跳过的错误
                    self.__update_gui("%s 识别错误, 跳过..." % image_name,
                                      int(current_subtitle * 100 / self.subtitle_count))
                    subtitle[3] = "( 跳过, OCR识别错误 )"
                    skip_images.append(image_name)
                    continue
            except RequestException as e:
                return -1, [image_name, str(e)]

            words_list = [item["words"] for item in result if item["probability"]["average"] > self.probability_bd]
            words = " ".join(words_list)
            words = words if words.replace(' ', '') != "" else "( 未能识别出有效字幕 )"
            subtitle[3] = words

            self.__update_gui("%s 完成" % image_name, int(current_subtitle * 100 / self.subtitle_count))

            # 线程中止
            if self.cancel_flag:
                return -99, None

        # 写入文件
        output = open(self.output_dir + self.video_name + "_BD.srt", mode="w", encoding="utf-8")
        for i in range(len(self.subtitle_list) - 1):
            output.write("%d\n%s --> %s\n%s\n\n" % (i + 1,
                                                    self.__frame2time(self.subtitle_list[i][0], self.fps),
                                                    self.__frame2time(self.subtitle_list[i][1], self.fps),
                                                    self.subtitle_list[i][3]))
        output.close()
        return 0, skip_images

    def __get_subtitle_tx(self):
        self.__update_gui("初始化腾讯OCR...", 0)
        self.ocr = TxOcr(self.str_tx_app_id, self.str_tx_app_key)
        skip_images = []

        current_subtitle = 0

        for subtitle in self.subtitle_list:
            retry_times = 0
            current_subtitle += 1
            image_name = str(subtitle[0]).zfill(6)

            try:
                result, status = self.__get_ocr_tx(image_name)

                while True:
                    if status == -1:  # QPS限制，重试
                        self.__update_gui("%s 触发QPS限制, 重试..."
                                          % image_name, int(current_subtitle * 100 / self.subtitle_count))
                        time.sleep(0.1)  # 线程暂停
                    elif status == -5:
                        retry_times += 1
                        self.__update_gui("返回预料之外的错误码! 正在第 %d 次重试……"
                                          % retry_times, int(current_subtitle * 100 / self.subtitle_count))
                        if retry_times == 10:
                            return -3, [image_name, result[0], result[1]]
                        time.sleep(0.5)  # 线程暂停
                    else:
                        break

                    result, status = self.__get_ocr_tx(image_name)

                if status == -3:  # 接口鉴权失败
                    return -21, None
                elif status == -4:  # 需要跳过的错误
                    self.__update_gui("%s 识别错误, 跳过..."
                                      % image_name, int(current_subtitle * 100 / self.subtitle_count))
                    subtitle[3] = "( 跳过, OCR识别错误 )"
                    skip_images.append(image_name)
                    continue
            except RequestException as e:
                return -1, [image_name, str(e)]

            words_list = [item["itemstring"] for item in result]
            words = " ".join(words_list)
            words = words if words.replace(' ', '') != "" else "( 未能识别出有效字幕 )"
            subtitle[3] = words

            self.__update_gui("%s 完成" % image_name, int(current_subtitle * 100 / self.subtitle_count))

            # 线程中止
            if self.cancel_flag:
                return -99, None

        # 写入文件
        output = open(self.output_dir + self.video_name + "_TX.srt", mode="w")
        for i in range(len(self.subtitle_list) - 1):
            output.write("%d\n%s --> %s\n%s\n\n" % (i + 1,
                                                    self.__frame2time(self.subtitle_list[i][0], self.fps),
                                                    self.__frame2time(self.subtitle_list[i][1], self.fps),
                                                    self.subtitle_list[i][3]))
        output.close()
        return 0, skip_images

    def __get_ocr_bd(self, image_name):
        image_path = self.binary_tmp + image_name + ".jpg"
        response = self.ocr.get_ocr(api=self.bd_ocr_api, image=image_path, lang=self.bd_ocr_lang)
        code = response.get("error_code", -1)

        if code == -1:
            return response["words_result"], 0  # OK
        elif code == 18 or code == 4:
            return response["error_msg"], -1  # 达到OPS上限
        elif code == 17 or code == 19:
            return response["error_msg"], -2  # 请求次数耗尽
        elif code in self.bd_retry_list:
            return response["error_msg"], -3  # 需要重新请求的错误
        elif code in self.bd_skip_list:
            return response["error_msg"], -4  # 需要跳过的错误
        else:
            return [response["error_code"], response["error_msg"]], -5  # 预料之外的错误

    def __get_ocr_tx(self, image_name):
        image_path = self.binary_tmp + image_name + ".jpg"
        response = self.ocr.get_ocr(image_path)
        code = response["ret"]

        if code == 0:
            return response["data"]["item_list"], 0  # OK
        elif code == 9:
            return response["msg"], -1  # 达到OPS上限
        elif code == 16389:
            return response["msg"], -3  # 接口鉴权失败
        elif code in self.tx_skip_list:
            return response["msg"], -4  # 需要跳过的错误
        else:
            return [response["ret"], response["msg"]], -5  # 预料之外的错误

    def check_exp(self):
        if Global.config.get_value("experience") == 0:
            self.str_tx_app_id = Global.config.get_value("tx_app_id")
            self.str_tx_app_key = Global.config.get_value("tx_app_key")
            return True

        _status, self.str_tx_app_id, self.str_tx_app_key = get_exp_account()

        if not _status:
            return False
        return True

    @staticmethod
    def __update_gui(_message, _progress):
        Global.gui.update_current_st(_message)
        Global.gui.update_progress_st(_progress)

    @staticmethod
    def __frame2time(frame, fps):
        _s, _f = divmod(frame, fps)
        _f = int(_f * 1000 / fps)
        _m, _s = divmod(_s, 60)
        _h, _m = divmod(_m, 60)
        return "%02d:%02d:%02d,%03d" % (_h, _m, _s, _f)

    def run_recognize(self, ocr_engine):
        if not self.check_exp():
            return_msg = [
                "获取共享API失败!",
                "获取共享API失败! 请重试或使用自己的API",
                "获取共享API失败! 请重试或使用自己的API"
            ]
            return -1, return_msg

        self.cancel_flag = False
        self.__get_params()
        get_subtitle = self.__get_subtitle_bd  # 默认使用百度OCR

        if ocr_engine == 1:
            get_subtitle = self.__get_subtitle_tx

        result, message = get_subtitle()
        del self.ocr

        if result == 0 and len(message) == 0:
            return 0, None
        elif result == 0:
            return_msg = [
                "提取完成! 但是有 %d 张图片返回了需要跳过的错误, 编号为:\n\n%s\n\n"
                "请尝试在 binary_tmp 文件夹中找到列出的图片, 如果图片中包含字幕, 请将此情况告知作者, 谢谢!"
                % (len(message), ", ".join(message))
            ]
            return 1, return_msg
        elif result == -1:
            return_msg = [
                "%s 失败! 发生网络错误!" % message[0],
                "失败! 发生网络错误, 请检查网络连接并重试!",
                "错误信息:\n\n%s\n\n请根据错误信息检查网络连接并重试!" % message[1]
            ]
            return -1, return_msg
        elif result == -2:
            return_msg = [
                "%s 失败! 发生了预料之外的网络错误!" % message[0],
                "失败! 发生了预料之外的网络错误, 请检查网络连接并重试!",
                "失败! 发生了预料之外的网络错误, 但是理论上不应该发生这个错误, 请将详细信息告知作者!"
            ]
            return -1, return_msg
        elif result == -3:
            return_msg = [
                "%s 失败! OCR多次返回预料之外的错误码!" % message[0],
                "失败! OCR多次返回预料之外的错误码: %s" % message[1],
                "失败! OCR多次返回预料之外的错误码!\n\n错误码: %s\n错误信息: %s\n\n请过几分钟重试, 并将详细信息告知作者!"
                % (message[1], message[2])
            ]
            return -1, return_msg
        elif result == -11:
            return_msg = [
                "获取 Access Token 失败!",
                "获取 Access Token 失败!",
                "获取 Access Token 失败! 请检查百度 API Key 和 Secret Key 是否正确!"
            ]
            return -1, return_msg
        elif result == -12:
            return_msg = [
                "请求次数耗尽!",
                "调用的OCR接口请求次数耗尽!",
                "调用的OCR接口请求次数耗尽! 请保持百度云余额充足或切换其他的OCR接口!"
            ]
            return -1, return_msg
        elif result == -21:
            return_msg = [
                "接口鉴权失败!",
                "接口鉴权失败!",
                "接口鉴权失败! 请查阅说明文档, 检查腾讯OCR是否已接入通用OCR能力!"
            ]
            return -1, return_msg
        elif result == -99:
            return -99, None

    def cancel_recognize(self):
        self.cancel_flag = True
