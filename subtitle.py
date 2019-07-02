# -*- coding: UTF-8 -*-

import time
import copy
import jd_ocrapi
from gl import Global


def get_subtitle_jd():
    subtitle_list = copy.deepcopy(Global.timeline)  # 深拷贝
    probability = Global.config.get_value("probability")
    subtitle_count = len(subtitle_list)
    fps = Global.config.get_value("fps")
    current_subtitle = 0

    for subtitle in subtitle_list:
        current_subtitle += 1
        image_name = str(subtitle[0]).zfill(6)

        try:
            ocr_result, status = get_ocr_jd(image_name)
        except (BaseException, Exception, IOError, OSError) as e:
            Global.gui.update_current_st("%s 失败! 发生网络错误!" % image_name)  # 更新GUI
            Global.gui.update_errmsg_st("失败! 发生网络错误，错误信息已弹出，请检查网络连接并重试!")
            Global.gui.b_begin_st.configure(state="normal")
            Global.gui.show_dialog("错误", str(e), "error")
            return False
        except:
            Global.gui.update_current_st("%s 失败! 发生网络错误!" % image_name)  # 更新GUI
            Global.gui.update_errmsg_st("失败! 发生预料之外的网络错误，请检查网络连接并重试!")
            Global.gui.b_begin_st.configure(state="normal")
            return False

        while status == -1:  # QPS限制，重试
            Global.gui.update_current_st("%s 触发QPS限制, 重试....." % image_name)  # 更新GUI
            Global.gui.update_process_st("%d %%" % int(current_subtitle * 100 / subtitle_count))
            time.sleep(0.1)  # 线程暂停避免触发QPS限制
            ocr_result, status = get_ocr_jd(image_name)

        if status == -2:  # 无内容被识别
            subtitle[3] = "跳过 (无内容被识别)"
            Global.gui.update_current_st("%s 跳过 (无内容被识别)" % image_name)  # 更新GUI
            Global.gui.update_process_st("%d %%" % int(current_subtitle * 100 / subtitle_count))
            time.sleep(0.1)  # 线程暂停避免触发QPS限制
            continue
        elif status == -3:  # 其他错误
            subtitle[3] = "跳过 (其他错误)"
            Global.gui.update_current_st("%s 跳过 (其他错误)" % image_name)  # 更新GUI
            Global.gui.update_process_st("%d %%" % int(current_subtitle * 100 / subtitle_count))
            time.sleep(0.1)  # 线程暂停避免触发QPS限制
            continue
        elif status != 0:
            Global.gui.update_current_st("%s 失败! 错误码: %s" % (image_name, status))  # 更新GUI
            Global.gui.update_errmsg_st("失败! 错误码: %s. 请查阅OCR说明文档或向作者反馈" % status)
            Global.gui.b_begin_st.configure(state="normal")
            return False

        words = ""
        for word in ocr_result:
            if float(word["probility"]) < probability:
                continue
            words += word["text"]

        if words == "":
            subtitle[3] = "跳过 (无内容被识别)"
        else:
            subtitle[3] = words

        Global.gui.update_current_st("%s 完成" % image_name)  # 更新GUI
        Global.gui.update_process_st("%d %%" % int(current_subtitle * 100 / subtitle_count))

        time.sleep(0.1)  # 线程暂停避免触发QPS限制

    # 写入文件
    output = open(Global.config.get_value("output_dir") + Global.config.get_value("video_name") + "_JD.txt", mode="w")
    for i in range(len(subtitle_list) - 1):
        output.write("%d\n%s --> %s\n%s\n\n" % (i + 1, frame2time(subtitle_list[i][0], fps),
                                                frame2time(subtitle_list[i][1], fps),
                                                subtitle_list[i][3]))
    output.close()

    Global.gui.b_begin_st.configure(state="normal")
    Global.gui.show_dialog("完成", "提取完成!", "info")
    return True


def get_subtitle_bd():
    pass


# 调用京东OCR
def get_ocr_jd(image_name):
    image_path = Global.config.get_value("binary_tmp") + image_name + ".jpg"
    res = jd_ocrapi.jd_general_ocr(image_path)
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


# 调用百度OCR
def get_ocr_bd(image):
    pass


def frame2time(frame, fps):
    _s, _f = divmod(frame, fps)
    _f = int(_f * 1000 / fps)
    _m, _s = divmod(_s, 60)
    _h, _m = divmod(_m, 60)
    return "%02d:%02d:%02d,%03d" % (_h, _m, _s, _f)
