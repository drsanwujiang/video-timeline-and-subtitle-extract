# -*- coding: UTF-8 -*-

import cv2
import copy
import threading
from skimage.measure import compare_ssim
from gl import Global


class OpenCVUtils:
    def __init__(self):
        # 定义参数变量
        self.video_path = None
        self.tmp_dir = None
        self.jpg_quality = None
        self.y_from = None
        self.y_to = None
        self.frame_count = None
        self.binary_threshold = None
        self.ssim_threshold = None

        self.subtitle_list = []
        self.current_analyse = 0
        self.current_ssim = 0
        self.timer = None
        self.ssim_flag = False  # 阶段标志
        self.running_flag = False  # 运行标志
        self.cancel_flag = False  # 线程中止标志

    def __get_params(self):
        self.video_path = Global.config.get_value("video_path")
        self.tmp_dir = Global.config.get_value("binary_tmp")
        self.jpg_quality = Global.config.get_value("jpg_quality")
        self.y_from = Global.config.get_value("y_from")
        self.y_to = Global.config.get_value("y_to")
        self.frame_count = Global.config.get_value("frame_count")
        self.binary_threshold = Global.config.get_value("binary_threshold")
        self.ssim_threshold = Global.config.get_value("ssim_threshold")

    def __preliminary_analyse(self):
        cv = cv2.VideoCapture(self.video_path)  # 读入视频文件
        self.current_analyse = 0
        similarity = [0, 0, 0]
        current_subtitle = [-1, -1, None, None]
        self.subtitle_list = []

        if cv.isOpened():  # 判断是否正常打开
            _r, frame = cv.read()
            cropped = frame[self.y_from:self.y_to, :]  # 截取指定区域
            gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)  # 灰度化
            _, binary = cv2.threshold(gray, self.binary_threshold, 255, cv2.THRESH_BINARY_INV)  # 反转二值化
            previous_binary = binary
        else:
            cv.release()
            return -1

        while _r:   # 循环读取视频帧
            cropped = frame[self.y_from:self.y_to, :]  # 截取指定区域
            gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)  # 灰度化
            _, binary = cv2.threshold(gray, self.binary_threshold, 255, cv2.THRESH_BINARY_INV)  # 反转二值化

            similarity = [similarity[1], similarity[2], self.__similar_to_previous(previous_binary, binary)]

            # 如果大于第1帧，且前一帧非空白图片
            if self.current_analyse > 1 and self.__calculate_white(previous_binary) < 0.99:
                # 如果综合判断为是不同帧
                if similarity[1] > 10 * similarity[0] and similarity[1] > 10 * similarity[2]:
                    # 如果不是第一次添加时间轴
                    if current_subtitle[0] != -1:
                        self.subtitle_list.append(copy.deepcopy(current_subtitle))  # 添加时间轴

                    current_subtitle[0] = self.current_analyse - 1  # 将当前时间轴起点设为前一帧
                    current_subtitle[2] = previous_binary  # 前一帧
                else:
                    current_subtitle[1] = self.current_analyse - 1  # 将当前时间轴终点设为前一帧

            cv2.waitKey(1)
            previous_binary = binary
            _r, frame = cv.read()  # 下一帧
            self.current_analyse += 1

            # 线程中止
            if self.cancel_flag:
                cv.release()
                return -99

        self.subtitle_list.append(copy.deepcopy(current_subtitle))  # 添加时间轴
        cv.release()
        return 0

    @staticmethod
    def __calculate_white(_binary):
        """
        :param _binary: Mat矩阵
        :return: 白色像素点占比
        """
        height, width = _binary.shape
        return cv2.countNonZero(_binary) / (height * width)

    @staticmethod
    def __similar_to_previous(_previous, _current):
        """
        :param _previous: 前一帧
        :param _current: 当前帧
        :return: 不同像素点数量
        """
        _image = cv2.absdiff(_previous, _current)
        return cv2.countNonZero(_image) + 1

    def __ssim_contrast(self):
        self.current_ssim = 0

        while True:
            _ssim = compare_ssim(self.subtitle_list[self.current_ssim][2], self.subtitle_list[self.current_ssim + 1][2])

            if _ssim > self.ssim_threshold and \
                    self.subtitle_list[self.current_ssim + 1][0] - self.subtitle_list[self.current_ssim][1] <= 5:
                self.subtitle_list[self.current_ssim][1] = self.subtitle_list[self.current_ssim + 1][1]
                del (self.subtitle_list[self.current_ssim + 1])
            else:
                self.current_ssim += 1

            if self.current_ssim == len(self.subtitle_list) - 1:
                return 0
            elif self.cancel_flag:
                return -99

    def __frame2file(self):
        for subtitle in self.subtitle_list:
            cv2.imencode(".jpg", subtitle[2], [int(cv2.IMWRITE_JPEG_QUALITY), self.jpg_quality])[1]. \
                tofile(self.tmp_dir + str(subtitle[0]).zfill(6) + ".jpg")

    def __update_gui_analysis(self):
        Global.gui.update_current_tl("初步分析时间轴: %d of %d" % (self.current_analyse, self.frame_count))
        Global.gui.update_progress_tl(int((self.current_analyse + 1) * 90 / self.frame_count))

    def __update_gui_ssim(self):
        Global.gui.update_current_tl("SSIM对比去重: %d" % self.subtitle_list[self.current_ssim][0])  # 更新GUI
        Global.gui.update_progress_tl(int((self.current_ssim + 1) * 10 / len(self.subtitle_list)) + 90)

    def __update_gui_interval(self):
        if self.running_flag:
            if not self.ssim_flag:
                self.__update_gui_analysis()
            else:
                self.__update_gui_ssim()

            self.timer = threading.Timer(1, self.__update_gui_interval)
            self.timer.start()

    def run_extract(self):
        self.running_flag = True
        self.ssim_flag = False
        self.cancel_flag = False
        self.timer = threading.Timer(1, self.__update_gui_interval)
        self.timer.start()
        self.__get_params()

        _preliminary_analyse_result = self.__preliminary_analyse()

        if _preliminary_analyse_result == -1:
            # 视频打开失败
            self.running_flag = False
            return -1
        elif _preliminary_analyse_result == -99:
            # 线程中止
            self.running_flag = False
            return -99
        '''
        if len(self.subtitle_list) < 2:
            Global.gui.update_current_tl("提取出的时间轴少于2条, 无法进行SSIM对比!")  # 更新GUI
        else:
            self.ssim_flag = True

            if self.__ssim_contrast() == -99:
                # 线程中止
                return -99
        '''
        Global.gui.update_progress_tl(100)
        self.running_flag = False
        Global.gui.update_current_tl("正在输出文件...")
        self.__frame2file()
        Global.timeline = self.subtitle_list
        Global.gui.update_current_tl("时间轴提取完成!")
        return 0

    def cancel_extract(self):
        self.cancel_flag = True


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


def get_frame(_index, _y_from, _y_to, _bth, _width):
    """
    :param _index: 帧索引
    :param _y_from: 区域上限
    :param _y_to: 区域下限
    :param _bth: 二值化阈值
    :param _width: 等比缩放后的宽度
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
        _dim = (_width, int(_binary.shape[0] * _width / _binary.shape[1]))  # 等比缩放
        _resize = cv2.resize(_binary, _dim, interpolation=cv2.INTER_AREA)
        return cv2.cvtColor(_resize, cv2.COLOR_BGR2RGB)  # BGR 转 RGB
    except cv2.error:
        return -1
