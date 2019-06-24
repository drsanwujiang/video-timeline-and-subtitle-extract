# -*- coding: UTF-8 -*-

import os
import cv2
import copy
from config import Config


def get_timeline(gui):
    video_path = Config.get_value("video_path")
    image_dir = Config.get_value("image_dir")
    jpg_quality = int(Config.get_value("jpg_quality"))
    y_from = Config.get_value("y_from")
    y_to = Config.get_value("y_to")
    frame_count = Config.get_value("frame_count")
    binary_threshold = Config.get_value("binary_threshold")
    similarity_limit = float(Config.get_value("similarity"))

    if not(os.path.exists(image_dir)):
        os.makedirs(image_dir)

    if not(os.path.exists(Config.get_value("output_dir"))):
        os.makedirs(Config.get_value("output_dir"))

    cv = cv2.VideoCapture(video_path)  # 读入视频文件
    current_frame = 0
    current_subtitle = [-1, -1, ""]
    subtitle_list = []

    if cv.isOpened():  # 判断是否正常打开
        _r, frame = cv.read()
        cropped = frame[y_from:y_to, :]  # 截取指定区域
        gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)  # 灰度化
        _, binary = cv2.threshold(gray, binary_threshold, 255, cv2.THRESH_BINARY_INV)  # 反转二值化
        previous_binary = binary
    else:
        cv.release()
        gui.error_message.set("视频打开失败！")
        gui.b_begin.configure(state="normal")  # 启用按钮
        return False

    while _r:   # 循环读取视频帧
        cropped = frame[y_from:y_to, :]  # 截取指定区域
        gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)  # 灰度化
        _, binary = cv2.threshold(gray, binary_threshold, 255, cv2.THRESH_BINARY_INV)  # 反转二值化
        similarity = img_similarity(previous_binary, binary)  # 比较相似度

        if similarity != -1 and current_subtitle[0] == -1:  # 当前字幕无起点
            current_subtitle[0] = current_frame - 1  # 起点设为前一帧
            current_subtitle[1] = current_frame  # 终点设为本帧
            cv2.imencode(".jpg", previous_binary, [int(cv2.IMWRITE_JPEG_QUALITY), jpg_quality])[1].\
                tofile(image_dir + str(current_frame - 1).zfill(6) + ".jpg")
        elif similarity != -1 and similarity > similarity_limit:  # 字幕相同但有起点
            current_subtitle[1] = current_frame  # 终点设为本帧
        elif similarity != -1:  # 字幕不同
            subtitle_list.append(copy.copy(current_subtitle))  # 增加字幕——当前对象的拷贝
            current_subtitle[0] = current_frame  # 起点设为本帧
            cv2.imencode(".jpg", binary, [int(cv2.IMWRITE_JPEG_QUALITY), jpg_quality])[1]. \
                tofile(image_dir + str(current_frame).zfill(6) + ".jpg")
        elif current_subtitle[0] != -1:  # 识别失败且有起点
            subtitle_list.append(copy.copy(current_subtitle))  # 增加字幕——当前对象的拷贝
            current_subtitle[0] = -1  # 将当前字幕起点设为-1

        gui.str_current_tl.set("%d of %d" % (current_frame + 1, frame_count))  # 更新GUI

        cv2.waitKey(1)
        previous_binary = binary
        _r, frame = cv.read()  # 下一帧
        current_frame += 1

    cv.release()
    Config.Timeline = subtitle_list
    return True


def img_similarity(img1, img2):
    """
    :param img1: 图片1
    :param img2: 图片2
    :return: 图片相似度
    """
    try:
        # 初始化ORB检测器
        orb = cv2.ORB_create()
        kp1, des1 = orb.detectAndCompute(img1, None)
        kp2, des2 = orb.detectAndCompute(img2, None)

        # 提取并计算特征点
        bf = cv2.BFMatcher(cv2.NORM_HAMMING)

        # knn筛选结果
        matches = bf.knnMatch(des1, trainDescriptors=des2, k=2)

        # 查看最大匹配点数目
        good = [m for (m, n) in matches if m.distance < 0.75 * n.distance]
        similary = len(good) / len(matches)
        return similary

    except:
        return -1


def test_file():
    _path = Config.get_value("video_path")
    _cv = cv2.VideoCapture(_path)  # 读入视频文件
    if _cv.isOpened():  # 判断是否正常打开
        _cv.release()
        return True
    else:
        _cv.release()
        return False


def get_video_info():
    _p = Config.get_value("video_path")
    _cv = cv2.VideoCapture(_p)
    _w = int(_cv.get(cv2.CAP_PROP_FRAME_WIDTH))
    _h = int(_cv.get(cv2.CAP_PROP_FRAME_HEIGHT))
    _fc = int(_cv.get(cv2.CAP_PROP_FRAME_COUNT))
    _cv.release()
    return _w, _h, _fc


def get_frame(_index, _y_from, _y_to, _bth):
    _path = Config.get_value("video_path")
    _cv = cv2.VideoCapture(_path)
    _cv.set(cv2.CAP_PROP_POS_FRAMES, _index)  # 设置要获取的帧号
    _r, _frame = _cv.read()
    _cv.release()
    cropped = _frame[_y_from:_y_to, :]  # 截取指定区域
    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)  # 灰度化
    _, _binary = cv2.threshold(gray, _bth, 255, cv2.THRESH_BINARY_INV)  # 反转二值化
    dim = (400, int(_binary.shape[0] * 400.0 / _binary.shape[1]))
    resized = cv2.resize(_binary, dim, interpolation=cv2.INTER_AREA)
    return cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
