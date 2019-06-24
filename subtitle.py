# -*- coding: UTF-8 -*-

import re
import time
import ocrapi
from config import Config


def get_subtitle(gui):
    subtitle_list = Config.Timeline
    probability = float(Config.get_value("probability"))

    for subtitle in subtitle_list:
        image_name = str(subtitle[0]).zfill(6)
        ocr_result, status = get_ocr(image_name)

        while status == -1:  # QPS限制，重试
            gui.str_current_st.set("%s 触发QPS限制, 重试....." % image_name)  # 更新GUI
            time.sleep(0.1)  # 线程暂停避免触发QPS限制
            ocr_result, status = get_ocr(image_name)

        if status == -2:  # 无内容被识别
            subtitle[2] = "跳过 (无内容被识别)"
            gui.str_current_st.set("%s 跳过 (无内容被识别)" % image_name)  # 更新GUI
            time.sleep(0.1)  # 线程暂停避免触发QPS限制
            continue
        elif status == -3:  # 其他错误
            subtitle[2] = "跳过 (其他错误)"
            gui.str_current_st.set("%s 跳过 (其他错误)" % image_name)  # 更新GUI
            time.sleep(0.1)  # 线程暂停避免触发QPS限制
            continue
        elif status != 0:
            gui.str_current_st.set("%s 失败! 错误码: %s" % (image_name, status))  # 更新GUI
            gui.error_message.set("%s 失败! 错误码: %s. 请查阅OCR说明文档或向作者反馈" % (image_name, status))  # 更新GUI
            return False

        words = ""
        for word in ocr_result:
            if float(word["probility"]) < probability:
                continue

            words += word["text"]

        subtitle[2] = words
        gui.str_current_st.set("%s 完成" % image_name)  # 更新GUI
        time.sleep(0.1)  # 线程暂停避免触发QPS限制

    output = open(Config.get_value("output_dir") + Config.get_value("video_name") + ".txt", mode="w")  # 写入文件
    output.write("----------时:分:秒:帧----------\n\n")

    for i in range(len(subtitle_list) - 1):
        output.write("%d\n%s --> %s\n%s\n\n" % (i + 1, frame2time(subtitle_list[i][0]),
                                                frame2time(subtitle_list[i][1]),
                                                subtitle_list[i][2]))

    output.close()
    return True


def get_file_content(file_path):
    with open(file_path, "rb") as fp:
        return fp.read()


def is_image(f):
    return re.match(r".+jpg", f)


def get_ocr(image_name):
    image = get_file_content(Config.get_value("image_dir") + image_name + ".jpg")
    res = ocrapi.jd_general_ocr(image)
    code = int(res["code"])
    if code != 10000:
        if code in [10043, 10044]:  # 达到OPS上限
            return res["msg"], -1
        return res["msg"], res["code"]  # 系统级错误
    else:
        code = int(res["result"]["code"])

        if code == 0:
            return res["result"]["resultData"], 0  # OK
        elif code == 13004:
            return res["result"]["message"], -2  # 无内容被识别
        elif code == 13005:
            return res["result"]["message"], -3  # 其他错误
        else:
            return res["result"]["message"], res["result"]["code"]  # 业务级错误


def frame2time(frame, fps=24):
    _s, _f = divmod(frame, fps)
    _m, _s = divmod(_s, 60)
    _h, _m = divmod(_m, 60)
    return "%02d:%02d:%02d:" % (_h, _m, _s)

