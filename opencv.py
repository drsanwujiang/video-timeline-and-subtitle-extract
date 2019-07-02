# -*- coding: UTF-8 -*-

import cv2
import copy
import os
from skimage.measure import compare_ssim
from gl import Global


def get_timeline():
    video_path = Global.config.get_value("video_path")
    tmp_dir = Global.config.get_value("binary_tmp")
    jpg_quality = Global.config.get_value("jpg_quality")
    y_from = Global.config.get_value("y_from")
    y_to = Global.config.get_value("y_to")
    frame_count = Global.config.get_value("frame_count")
    binary_threshold = Global.config.get_value("binary_threshold")

    cv = cv2.VideoCapture(video_path)  # 读入视频文件
    current_frame = 0
    similarity = [0, 0, 0]
    current_subtitle = [-1, -1, None, None]
    subtitle_list = []

    if cv.isOpened():  # 判断是否正常打开
        _r, frame = cv.read()
        cropped = frame[y_from:y_to, :]  # 截取指定区域
        gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)  # 灰度化
        _, binary = cv2.threshold(gray, binary_threshold, 255, cv2.THRESH_BINARY_INV)  # 反转二值化
        previous_binary = binary
    else:
        cv.release()
        Global.gui.update_errmsg_tl("视频打开失败！")
        Global.gui.b_begin_tl.configure(state="normal")
        return False

    while _r:   # 循环读取视频帧
        cropped = frame[y_from:y_to, :]  # 截取指定区域
        gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)  # 灰度化
        _, binary = cv2.threshold(gray, binary_threshold, 255, cv2.THRESH_BINARY_INV)  # 反转二值化

        similarity[0] = similarity[1]
        similarity[1] = similarity[2]
        similarity[2] = similar_to_previous(previous_binary, binary)

        # 如果大于第1帧，且前一帧非空白图片
        if current_frame > 1 and calculate_white(previous_binary) < 0.99:
            # 如果综合判断为是不同帧
            if similarity[1] > 10 * similarity[0] and similarity[1] > 10 * similarity[2]:
                # 如果不是第一次添加时间轴
                if current_subtitle[0] != -1:
                    subtitle_list.append(copy.deepcopy(current_subtitle))  # 添加时间轴

                current_subtitle[0] = current_frame - 1  # 将当前时间轴起点设为前一帧
                current_subtitle[2] = previous_binary  # 前一帧
                cv2.imencode(".jpg", previous_binary, [int(cv2.IMWRITE_JPEG_QUALITY), jpg_quality])[1]. \
                    tofile(tmp_dir + str(current_frame - 1).zfill(6) + ".jpg")
            else:
                current_subtitle[1] = current_frame - 1  # 将当前时间轴终点设为前一帧

        Global.gui.update_current_tl("初步分析时间轴: %d of %d" % (current_frame, frame_count))  # 更新GUI
        Global.gui.update_process_tl("%d %%" % int((current_frame + 1) * 90 / frame_count))

        cv2.waitKey(1)
        previous_binary = binary
        _r, frame = cv.read()  # 下一帧
        current_frame += 1

    subtitle_list.append(copy.deepcopy(current_subtitle))  # 添加时间轴
    cv.release()

    _current = 0
    while True:
        _ssim = compare_ssim(subtitle_list[_current][2], subtitle_list[_current + 1][2])
        if _ssim > 0.9 and subtitle_list[_current + 1][0] - subtitle_list[_current][1] <= 5:
            subtitle_list[_current][1] = subtitle_list[_current + 1][1]
            os.remove(tmp_dir + str(subtitle_list[_current + 1][0]).zfill(6) + ".jpg")
            del(subtitle_list[_current + 1])
        else:
            _current += 1

        Global.gui.update_current_tl("SSIM对比去重: %d" % subtitle_list[_current][0])  # 更新GUI
        Global.gui.update_process_tl("%d %%" % (int((_current + 1) * 10 / len(subtitle_list)) + 90))

        if _current == len(subtitle_list) - 1:
            break

    Global.timeline = subtitle_list
    Global.gui.update_current_tl("时间轴提取完成!")  # 更新GUI
    Global.gui.b_begin_tl.configure(state="normal")
    return True


def calculate_white(_binary):
    """
    :param _binary: Mat矩阵
    :return: 白色像素点占比
    """
    height, width = _binary.shape
    return cv2.countNonZero(_binary) / (height * width)


def similar_to_previous(_previous, _current):
    """
    :param _previous: 前一帧
    :param _current: 当前帧
    :return: 不同像素点数量
    """
    _image = cv2.absdiff(_previous, _current)
    return cv2.countNonZero(_image) + 1


def test_file():
    """
    :return: 是否正常打开
    """
    _path = Global.config.get_value("video_path")
    _cv = cv2.VideoCapture(_path)  # 读入视频文件
    if _cv.isOpened():  # 判断是否正常打开
        _cv.release()
        return True
    else:
        _cv.release()
        return False


def get_video_info():
    """
    :return _w, _h, _fc, _fps: 宽, 高, 总帧数, 帧率(向上取整)
    """
    _p = Global.config.get_value("video_path")
    _cv = cv2.VideoCapture(_p)
    _w = int(_cv.get(cv2.CAP_PROP_FRAME_WIDTH))
    _h = int(_cv.get(cv2.CAP_PROP_FRAME_HEIGHT))
    _fc = int(_cv.get(cv2.CAP_PROP_FRAME_COUNT))
    _fps = float(_cv.get(cv2.CAP_PROP_FPS))
    _cv.release()
    return _w, _h, _fc, _fps


def get_frame(_index, _y_from, _y_to, _bth):
    """
    :param _index: 帧索引
    :param _y_from: 区域上限
    :param _y_to: 区域下限
    :param _bth: 二值化阈值
    :return: RGB 通道图像
    """
    try:
        _path = Global.config.get_value("video_path")
        _cv = cv2.VideoCapture(_path)
        _cv.set(cv2.CAP_PROP_POS_FRAMES, _index)  # 设置要获取的帧号
        _r, _frame = _cv.read()
        _cv.release()
        cropped = _frame[_y_from:_y_to, :]  # 截取指定区域
        gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)  # 灰度化
        _, _binary = cv2.threshold(gray, _bth, 255, cv2.THRESH_BINARY_INV)  # 反转二值化
        _dim = (400, int(_binary.shape[0] * 400.0 / _binary.shape[1]))  # 缩放为 400 宽
        _resize = cv2.resize(_binary, _dim, interpolation=cv2.INTER_AREA)
        return cv2.cvtColor(_resize, cv2.COLOR_BGR2RGB)  # BGR 转 RGB
    except cv2.error:
        return -1
