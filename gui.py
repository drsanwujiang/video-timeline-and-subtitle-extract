# -*- coding: UTF-8 -*-

import sys
import os
import shutil
from threading import Thread
from tkinter import ttk, filedialog, StringVar, IntVar, messagebox, Toplevel
from PIL import Image, ImageTk
from cv import test_file, get_video_info, get_frame
from gl import Global


class MainWindow:
    def __init__(self, master):
        self.master = master
        center_window(self.master, 500, 450)
        self.master.title("视频时间轴及字幕提取")
        self.master.iconbitmap("favico.ico")
        self.current_dir = Global.config.get_value("current_dir")

        # 定义控件
        self.tab_control = None  # Notebook
        self.list_file_list = None  # 文件列表
        self.b_load = None  # 读取按钮
        self.lb_preview = None  # 二值化结果预览图片
        self.scale_y_from = None  # 字幕区域上限滑块
        self.scale_y_to = None  # 字幕区域下限滑块
        self.scale_frame = None  # 当前预览帧滑块
        self.b_begin_tl = None  # 时间轴-开始提取按钮
        self.b_cancel_tl = None  # 时间轴-取消按钮
        self.b_begin_st = None  # 字幕-开始提取按钮
        self.b_cancel_st = None  # 字幕-取消按钮

        # 定义绑定变量
        self.str_file_path = StringVar(value="")  # FilePath
        self.str_file_name = StringVar(value="")  # FileName
        self.str_file_resolution = StringVar(value="")  # 分辨率
        self.int_current_frame = IntVar(value=0)  # 当前帧
        self.int_y_from = IntVar(value=0)  # 字幕区域上限
        self.int_y_to = IntVar(value=0)  # 字幕区域下限
        self.int_binary_threshold = IntVar(value=250)  # 二值化阈值
        self.str_current_tl = StringVar(value="")  # 时间轴-当前帧
        self.int_progress_tl = IntVar(value=0)  # 时间轴-进度
        self.str_errmsg_tl = StringVar(value="")  # 时间轴-错误信息
        self.int_ocr_engine = IntVar(value=0)  # OCR引擎
        self.str_current_st = StringVar(value="")  # 字幕-当前帧
        self.int_progress_st = IntVar(value=0)  # 字幕-进度
        self.str_errmsg_st = StringVar(value="")  # 字幕-错误信息

        # 定义变量
        self.image_preview = None  # 将预览图像定义为全局变量防止被回收

        self.__init_widgets()  # 初始化控件
        self.__load_file_list()  # 加载文件列表
        self.__first_time_check()  # 第一次使用判断

    def __init_widgets(self):
        self.tab_control = ttk.Notebook(self.master)
        self.tab_control.pack(fill="both", expand=True)

        self.__init_start()  # 加载开始标签页
        self.__init_params()  # 加载参数标签页
        self.__init_extract()  # 加载提取标签页

    # 开始标签页
    def __init_start(self):
        tab_start = ttk.Frame(self.tab_control)
        self.tab_control.add(tab_start, text="开始")

        # 版本号
        ttk.Label(tab_start, text="当前版本: {}".format(Global.config.get_value("version"))).pack(pady=10)

        # OCR选项
        lf_ocr = ttk.LabelFrame(tab_start, text=" OCR选项 ")
        lf_ocr.pack(fill="x", padx=10, pady=5)
        lf_ocr.grid_columnconfigure(0, weight=1)
        ttk.Label(lf_ocr, text="设置OCR相关参数").grid(row=0, column=0, padx=10, sticky="ew")
        ttk.Button(lf_ocr, text="OCR选项", command=self.show_ocr_settings).grid(row=0, column=1, padx=10, pady=10)

        # 选择目录
        lf_file_path = ttk.LabelFrame(tab_start, text=" 视频目录 ")
        lf_file_path.pack(fill="x", padx=10, pady=5)
        lf_file_path.grid_columnconfigure(0, weight=1)
        ttk.Entry(lf_file_path, textvariable=self.str_file_path).grid(row=0, column=0, padx=10, sticky="ew")
        ttk.Button(lf_file_path, text="选择目录...", command=self.__open_dir).grid(row=0, column=1, padx=10, pady=10)

        # 文件列表
        lf_file_list = ttk.LabelFrame(tab_start, text=" 文件列表 ")
        lf_file_list.pack(fill="both", expand=True, padx=10, pady=10)
        self.list_file_list = ttk.Combobox(lf_file_list, textvariable=self.str_file_name, state="readonly")
        self.list_file_list.pack(fill="x", padx=10, pady=10, side="top")

        # 读取文件
        fr_load = ttk.Frame(tab_start)
        fr_load.pack(fill="x", padx=10, pady=10)
        self.b_load = ttk.Button(fr_load, text="下一步", command=self.__async_load_video)
        self.b_load.pack()

    # 参数标签页
    def __init_params(self):
        tab_params = ttk.Frame(self.tab_control)
        self.tab_control.add(tab_params, text="参数", state="disabled")

        # 文件信息
        lf_file_info = ttk.LabelFrame(tab_params, text=" 文件信息 ")
        lf_file_info.pack(fill="x", padx=10, pady=5)
        lf_file_info.grid_columnconfigure(1, weight=1)
        ttk.Label(lf_file_info, text="文件名: ").grid(row=0, column=0, padx=10, pady=5)
        ttk.Label(lf_file_info, textvariable=self.str_file_name).grid(row=0, column=1, padx=10)
        ttk.Label(lf_file_info, text="分辨率: ").grid(row=1, column=0, padx=10, pady=5)
        ttk.Label(lf_file_info, textvariable=self.str_file_resolution).grid(row=1, column=1, padx=10)

        # 参数调整
        lf_params_adjust = ttk.LabelFrame(tab_params, text=" 参数调整 ")
        lf_params_adjust.pack(fill="x", padx=10, pady=5)
        lf_params_adjust.grid_columnconfigure(2, weight=1)
        ttk.Label(lf_params_adjust).grid(row=0, column=0, padx=5)
        ttk.Label(lf_params_adjust).grid(row=0, column=3, padx=5)
        ttk.Label(lf_params_adjust, text="字幕区域起点: ").grid(row=0, column=1, sticky="e")
        self.scale_y_from = ttk.LabeledScale(lf_params_adjust, from_=0, to=0, variable=self.int_y_from)
        self.scale_y_from.grid(row=0, column=2, pady=5, sticky="ew")
        self.scale_y_from.scale.bind("<ButtonRelease-1>", self.__async_load_preview)
        ttk.Label(lf_params_adjust, text="字幕区域终点: ").grid(row=1, column=1, sticky="e")
        self.scale_y_to = ttk.LabeledScale(lf_params_adjust, from_=0, to=0, variable=self.int_y_to)
        self.scale_y_to.grid(row=1, column=2, pady=5, sticky="ew")
        self.scale_y_to.scale.bind("<ButtonRelease-1>", self.__async_load_preview)
        ttk.Label(lf_params_adjust, text="二值化阈值: ").grid(row=2, column=1, sticky="e")
        scale_bth = ttk.LabeledScale(lf_params_adjust, from_=150, to=255, variable=self.int_binary_threshold)
        scale_bth.grid(row=2, column=2, pady=5, sticky="ew")
        scale_bth.scale.bind("<ButtonRelease-1>", self.__async_load_preview)

        # 字幕区域及效果预览
        lf_preview = ttk.LabelFrame(tab_params, text=" 字幕区域及效果预览(拖动滑块选择帧) ")
        lf_preview.pack(fill="both", expand=True, padx=10, pady=5)
        self.lb_preview = ttk.Label(lf_preview, image=None, anchor="center")
        self.lb_preview.pack(fill="both", expand=True)
        self.scale_frame = ttk.LabeledScale(lf_preview, from_=0, to=0, variable=self.int_current_frame)
        self.scale_frame.pack(fill="x", padx=10, side="bottom")
        self.scale_frame.scale.bind("<ButtonRelease-1>", self.__async_load_preview)

        # 下一步
        fr_next = ttk.Frame(tab_params)
        fr_next.pack(fill="x", padx=10, pady=10)
        ttk.Button(fr_next, text="下一步", command=lambda: self.tab_control.select(2)).pack()

    # 提取标签页
    def __init_extract(self):
        tab_extract = ttk.Frame(self.tab_control)
        self.tab_control.add(tab_extract, text="提取", state="disabled")

        # 时间轴提取
        lf_timeline = ttk.LabelFrame(tab_extract, text=" 时间轴提取 ")
        lf_timeline.pack(fill="both", expand=True, padx=10, pady=10)

        fr_current_tl = ttk.Frame(lf_timeline)
        fr_current_tl.pack(fill="both", expand=True, padx=10)
        ttk.Label(fr_current_tl, text="当前: ").pack(side="left")
        ttk.Label(fr_current_tl, textvariable=self.str_current_tl).pack(fill="x", expand=True, side="left")

        fr_progress_tl = ttk.Frame(lf_timeline)
        fr_progress_tl.pack(fill="both", expand=True, padx=10)
        ttk.Label(fr_progress_tl, text="进度: ").pack(side="left")
        ttk.Progressbar(fr_progress_tl, orient="horizontal", mode="determinate", variable=self.int_progress_tl) \
            .pack(fill="x", expand=True, side="right")

        fr_start_tl = ttk.Frame(lf_timeline)
        fr_start_tl.pack(fill="both", expand=True, padx=10)
        self.b_begin_tl = ttk.Button(fr_start_tl, text="开始提取", command=self.__async_start_extract)
        self.b_begin_tl.pack(side="left")
        self.b_cancel_tl = ttk.Button(fr_start_tl, text="取消", command=self.__cancel_extract, state="disabled")
        self.b_cancel_tl.pack(side="left")
        ttk.Label(fr_start_tl, textvariable=self.str_errmsg_tl, foreground="red").pack(fill="x", side="left")

        # 字幕识别
        lf_subtitle = ttk.LabelFrame(tab_extract, text=" 字幕识别 ")
        lf_subtitle.pack(fill="both", expand=True, padx=10, pady=10)

        fr_engine_st = ttk.Frame(lf_subtitle)
        fr_engine_st.pack(fill="both", expand=True, padx=10)
        ttk.Radiobutton(fr_engine_st, text="百度OCR", variable=self.int_ocr_engine, value=0) \
            .pack(fill="x", expand=True, side="left")
        ttk.Radiobutton(fr_engine_st, text="腾讯OCR", variable=self.int_ocr_engine, value=1, state="disabled") \
            .pack(fill="x", expand=True, side="left")

        fr_current_st = ttk.Frame(lf_subtitle)
        fr_current_st.pack(fill="both", expand=True, padx=10)
        ttk.Label(fr_current_st, text="当前: ").pack(side="left")
        ttk.Label(fr_current_st, textvariable=self.str_current_st).pack(fill="x", expand=True, side="left")

        fr_progress_st = ttk.Frame(lf_subtitle)
        fr_progress_st.pack(fill="both", expand=True, padx=10)
        ttk.Label(fr_progress_st, text="进度: ").pack(side="left")
        ttk.Progressbar(fr_progress_st, orient="horizontal", mode="determinate", variable=self.int_progress_st) \
            .pack(fill="x", expand=True, side="right")

        fr_start_st = ttk.Frame(lf_subtitle)
        fr_start_st.pack(fill="both", expand=True, padx=10)
        self.b_begin_st = ttk.Button(fr_start_st, text="开始识别", command=self.__async_start_recognize, state="disabled")
        self.b_begin_st.pack(side="left")
        self.b_cancel_st = ttk.Button(fr_start_st, text="取消", command=self.__cancel_recognize, state="disabled")
        self.b_cancel_st.pack(side="left")
        ttk.Label(fr_start_st, textvariable=self.str_errmsg_st, foreground="red").pack(fill="x", side="left")

    def __load_file_list(self):
        self.str_file_path.set(Global.config.get_value("video_dir"))

        try:
            video_list = os.listdir(Global.config.get_value("video_dir"))
            self.list_file_list["value"] = video_list

            if len(video_list) != 0:
                self.list_file_list.current(0)
        except OSError:  # 当默认视频目录不存在
            self.list_file_list.delete(0, "end")

    def __first_time_check(self):
        if (Global.config.get_value("bd_api_key") == "" or Global.config.get_value("bd_secret_key") == "") and \
                (Global.config.get_value("tx_app_id") == "" or Global.config.get_value("tx_app_key") == "") and \
                Global.config.get_value("experience") == 0:
            self.show_message_window("欢迎", "欢迎使用\n视频字幕及时间轴提取\n\n使用前请先填写OCR API信息, 否则后续字幕识别功能将无法使用\n\n" +
                                     "更多帮助请访问Github", 400, 200, True, True, True)
            # self.show_ocr_settings()

    def show_ocr_settings(self):
        window = Toplevel(self.master)  # 子窗口
        window.grab_set()  # 模态
        OCRSettings(window)  # 初始化gui

    def __open_dir(self):
        # 调用askdirectory方法打开目录
        _file_path = filedialog.askdirectory(title="选择目录", initialdir=self.current_dir)
        if _file_path != "":
            Global.config.set_video_dir(_file_path)
            self.__load_file_list()

    # 异步读取视频文件
    def __async_load_video(self):
        if not Global.config.get_value("bd_api_key") or not Global.config.get_value("bd_secret_key"):
            self.show_message_box("警告", "OCR API相关参数未设置，字幕识别功能将无法使用", "warning")
            self.b_load.configure(state="normal", text="下一步")

        def load_video():
            self.b_load.configure(state="disabled", text="读取中...")
            Global.config.set_video_name(self.str_file_name.get())

            if not test_file():
                self.show_message_box("错误", "文件打开失败，请检查格式或编码", "error")
                self.b_load.configure(state="normal", text="下一步")
                return
            elif Global.config.get_value("video_suffix") not in Global.Types:
                self.show_message_box("警告", "文件格式并非常见视频格式，可能导致程序不稳定", "warning")

            load_settings()
            self.tab_control.tab(1, state="normal")  # 启用标签页
            self.tab_control.tab(2, state="normal")
            self.tab_control.select(1)  # 进入参数标签页
            self.b_load.configure(state="normal", text="下一步")

        def load_settings():
            # 加载指定文件的信息以及默认参数
            _w, _h, _fc, _fps = get_video_info()
            Global.config.set_video_info(_w, _h, _fc, _fps)  # 保存当前视频信息
            self.str_file_name.set(Global.config.get_value("video_name") + Global.config.get_value("video_suffix"))
            self.str_file_resolution.set("%s x %s" % (_w, _h))
            self.scale_frame.scale.configure(to=(_fc - 1))
            self.scale_y_from.scale.configure(to=_h)
            self.scale_y_to.scale.configure(to=_h)
            self.int_current_frame.set(int(_fc / 2))
            self.int_y_from.set(int(_h * 0.83))
            self.int_y_to.set(_h)
            self.int_binary_threshold.set(Global.config.get_value("binary_threshold"))
            self.int_current_frame.set(int(_fc / 2))

            self.int_ocr_engine.set(0)  # 加载OCR相关参数
            self.__async_load_preview()

        # 开启子线程
        task_load_video = ChildThreading(load_video)
        task_load_video.setDaemon(True)
        task_load_video.start()

    # 异步加载预览图
    def __async_load_preview(self, _e=None):
        def load_preview():
            self.int_y_from.set(self.int_y_from.get())
            self.int_y_to.set(self.int_y_to.get())
            self.int_binary_threshold.set(self.int_binary_threshold.get())
            self.int_current_frame.set(self.int_current_frame.get())

            Global.config.set_params(self.int_y_from.get(), self.int_y_to.get(),
                                     self.int_binary_threshold.get())  # 保存更改后的参数
            _img = get_frame(self.int_current_frame.get(), self.int_y_from.get(), self.int_y_to.get(),
                             self.int_binary_threshold.get(), self.lb_preview.winfo_width())  # 加载图片预览

            if isinstance(_img, int):
                _w, _h, _, _ = get_video_info()
                self.int_y_from.set(int(_h * 0.83))
                self.int_y_to.set(_h)
                self.show_message_box("警告", "字幕区域设置错误!", "warning")
                load_preview()
                return False

            self.image_preview = ImageTk.PhotoImage(Image.fromarray(_img))
            self.lb_preview.configure(image=self.image_preview)
            return True

        # 开启子线程
        task_load_preview = ChildThreading(load_preview)
        task_load_preview.setDaemon(True)
        task_load_preview.start()

    # 异步开始时间轴提取
    def __async_start_extract(self, _e=None):
        def start_extract():
            self.update_current_tl("")
            self.update_progress_tl(0)
            self.update_errmsg_tl("")
            self.b_begin_tl.configure(state="disabled")
            self.b_cancel_tl.configure(state="disabled")
            self.b_begin_st.configure(state="disabled")
            self.b_cancel_st.configure(state="disabled")

            # 检查目录是否存在
            if os.path.exists(Global.config.get_value("binary_tmp")):
                try:
                    shutil.rmtree(Global.config.get_value("binary_tmp"))
                except OSError:
                    self.b_begin_tl.configure(state="normal")  # 启用按钮
                    self.update_errmsg_tl("无法删除临时图片目录!")
                    self.show_message_box("错误", "无法删除临时图片目录! 请关闭占用文件夹的程序并重试,"
                                                "或手动删除 binary_tmp 目录后重试!", "error")
                    return

            os.makedirs(Global.config.get_value("binary_tmp"))

            if not (os.path.exists(Global.config.get_value("output_dir"))):
                os.makedirs(Global.config.get_value("output_dir"))

            self.b_cancel_tl.configure(state="normal")  # 启用取消按钮
            _result = Global.opencv_utils.run_extract()

            self.b_begin_tl.configure(state="normal")
            self.b_cancel_tl.configure(state="disabled")

            if _result == 0:
                # 正常结束
                self.b_begin_st.configure(state="normal")
                self.b_cancel_st.configure(state="disabled")
                self.__async_start_recognize()
            elif _result == -1:
                # 视频打开失败
                self.update_current_tl("")
                self.update_progress_tl(0)
                self.update_errmsg_tl("视频打开失败!")
            elif _result == -99:
                # 线程中止
                self.update_current_tl("")
                self.update_progress_tl(0)
                self.update_errmsg_tl("已取消!")

        # 开启子线程
        task_start_extract = ChildThreading(start_extract)
        task_start_extract.setDaemon(True)
        task_start_extract.start()

    def __cancel_extract(self):
        self.b_cancel_tl.configure(state="disabled")
        Global.opencv_utils.cancel_extract()

    # 异步开始字幕识别
    def __async_start_recognize(self, _e=None):
        """
        def check_exp():
            if Global.config.get_value("experience") == 1 and self.int_ocr_engine.get() == 0:
                self.int_ocr_engine.set(1)
                window = self.show_message_window("提示", "共享API模式无法使用百度OCR, 已自动切换至腾讯OCR", 400, 150,
                                                  transient=True)
                self.master.after(3000, window.destroy)

        def check_empty_api_info():
            if Global.config.get_value("experience") == 0:
                if self.int_ocr_engine.get() == 0 and (Global.config.get_value("bd_api_key") == "" or Global.config.get_value("bd_secret_key") == ""):
                    self.int_ocr_engine.set(1)
                    window = self.show_message_window("提示", "检测到百度OCR API信息为空, 已自动切换至腾讯OCR", 400, 150,
                                                      transient=True)
                    self.master.after(3000, window.destroy)
                elif self.int_ocr_engine.get() == 1 and (Global.config.get_value("tx_app_id") == "" or Global.config.get_value("tx_app_key") == ""):
                    self.int_ocr_engine.set(0)
                    window = self.show_message_window("提示", "检测到腾讯OCR API信息为空, 已自动切换至百度OCR", 400, 150,
                                                      transient=True)
                    self.master.after(3000, window.destroy)
        """

        if not Global.config.get_value("bd_api_key") or not Global.config.get_value("bd_secret_key"):
            self.show_message_box("警告", "OCR API相关参数未设置，无法进行字幕识别", "warning")
            return

        def start_recognize():
            self.update_current_st("")
            self.update_progress_st(0)
            self.update_errmsg_st("")
            self.b_begin_tl.configure(state="disabled")
            self.b_cancel_tl.configure(state="disabled")
            self.b_begin_st.configure(state="disabled")
            self.b_cancel_st.configure(state="normal")
            # check_exp()
            # check_empty_api_info()
            _result, _message = Global.ocr_utils.run_recognize(self.int_ocr_engine.get())

            if _result == 0:
                self.show_message_window("完成", "提取完成!", 200, 100)
            elif _result == 1:
                # 弹出警告消息框
                self.show_message_box("警告", _message[0], "warning")
            elif _result == -1:
                # 显示错误并弹出消息框
                self.update_current_st(_message[0])
                self.update_errmsg_st(_message[1])
                self.show_message_box("错误", _message[2], "error")
            elif _result == -99:
                # 线程中止
                self.update_current_st("")
                self.update_progress_st(0)
                self.update_errmsg_st("已取消!")

            self.b_begin_tl.configure(state="normal")
            self.b_begin_st.configure(state="normal")
            self.b_cancel_st.configure(state="disabled")

        # 开启子线程
        task_start_recognize = ChildThreading(start_recognize)
        task_start_recognize.setDaemon(True)
        task_start_recognize.start()

    def __cancel_recognize(self):
        self.b_cancel_st.configure(state="disabled")
        Global.ocr_utils.cancel_recognize()

    def update_current_tl(self, _msg):
        self.str_current_tl.set(_msg)

    def update_progress_tl(self, _progress):
        self.int_progress_tl.set(_progress)

    def update_errmsg_tl(self, _errmsg):
        self.str_errmsg_tl.set(_errmsg)

    def update_current_st(self, _msg):
        self.str_current_st.set(_msg)

    def update_progress_st(self, _progress):
        self.int_progress_st.set(_progress)

    def update_errmsg_st(self, _errmsg):
        self.str_errmsg_st.set(_errmsg)

    @staticmethod
    def show_message_box(title, text, icon="info", type_="ok"):
        messagebox.showinfo(title, text, icon=icon, type=type_)

    def show_message_window(self, title, msg, width=400, height=200, modal=False, transient=False, wait=False):
        window = Toplevel(self.master)

        if modal:
            window.grab_set()
        if transient:
            window.transient()

        MessageWindow(window, title, msg, width, height)

        if wait:
            self.master.wait_window(window)

        return window


class OCRSettings:
    def __init__(self, master):
        self.master = master
        center_window(self.master, 500, 450)
        self.master.title("OCR选项")
        self.master.iconbitmap("favico.ico")
        self.master.resizable(False, False)
        # self.master.protocol("WM_DELETE_WINDOW", self.__save_config)  # 接管关闭事件

        self.lf_baidu = None
        self.lf_tencent = None
        self.list_api_list = None  # 百度 API 列表
        self.list_language_list = None  # 百度识别语言列表

        self.str_bd_api_key = StringVar(value=Global.config.get_value("bd_api_key"))  # 百度 API Key
        self.str_bd_secret_key = StringVar(value=Global.config.get_value("bd_secret_key"))  # 百度 Secret Key
        self.str_bd_ocr_api = StringVar(value="")  # 百度 OCR API
        self.str_bd_ocr_lang = StringVar(value="")  # 百度 字幕语言
        self.str_tx_app_id = StringVar(value=Global.config.get_value("tx_app_id"))  # 腾讯 AppID
        self.str_tx_app_key = StringVar(value=Global.config.get_value("tx_app_key"))  # 腾讯 AppKey
        # self.experience = IntVar(value=Global.config.get_value("experience"))
        self.experience = IntVar(value=0)

        self.__init_widgets()
        self.__load_list()
        self.__apply_exp()

    def __init_widgets(self):
        # 百度OCR相关设置
        self.lf_baidu = ttk.LabelFrame(self.master, text=" 百度OCR ")
        self.lf_baidu.pack(fill="both", expand=True, padx=10, pady=10)
        self.lf_baidu.grid_columnconfigure(1, weight=1)
        ttk.Label(self.lf_baidu, text="API Key: ").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        ttk.Entry(self.lf_baidu, textvariable=self.str_bd_api_key).grid(row=0, column=1, padx=10, sticky="ew")

        ttk.Label(self.lf_baidu, text="Secret Key: ").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        ttk.Entry(self.lf_baidu, textvariable=self.str_bd_secret_key).grid(row=1, column=1, padx=10, sticky="ew")
        ttk.Label(self.lf_baidu, text="API: ").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.list_api_list = ttk.Combobox(self.lf_baidu, textvariable=self.str_bd_ocr_api, state="readonly")
        self.list_api_list.grid(row=2, column=1, padx=10, sticky="ew")
        ttk.Label(self.lf_baidu, text="字幕语言: ").grid(row=3, column=0, padx=10, pady=10, sticky="e")
        self.list_language_list = ttk.Combobox(self.lf_baidu, textvariable=self.str_bd_ocr_lang, state="readonly")
        self.list_language_list.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

        # 腾讯OCR相关设置
        self.lf_tencent = ttk.LabelFrame(self.master, text=" 腾讯OCR ")
        self.lf_tencent.pack(fill="both", expand=True, padx=10, pady=5)
        self.lf_tencent.grid_columnconfigure(1, weight=1)
        ttk.Label(self.lf_tencent, text="AppID: ", state="disabled").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        ttk.Entry(self.lf_tencent, textvariable=self.str_tx_app_id, state="disabled").grid(row=0, column=1, padx=10, sticky="ew")
        ttk.Label(self.lf_tencent, text="AppKey: ", state="disabled").grid(row=1, column=0, padx=10, pady=10)
        ttk.Entry(self.lf_tencent, textvariable=self.str_tx_app_key, state="disabled").grid(row=1, column=1, padx=10, sticky="ew")

        """
        # 使用共享API
        lf_exp = ttk.LabelFrame(self.master, text=" 使用共享API（仅供体验使用） ")
        lf_exp.pack(fill="x", padx=10, pady=5)
        ttk.Checkbutton(lf_exp, text="使用腾讯OCR共享API", variable=self.experience, onvalue=1, offvalue=0,
                        command=self.__apply_exp, state="disabled").pack(side="top", fill="x", padx=10)
        ttk.Label(lf_exp, text="仅供体验使用，不保证稳定性且QPS为1，建议及时更换为自己的API", foreground="red", state="disabled")\
            .pack(side="top", fill="x", padx=10)
        """

        # 保存和说明
        fr_save = ttk.Frame(self.master)
        fr_save.pack(fill="x", padx=10, pady=5)
        ttk.Button(fr_save, text="保存", command=self.__save_config).pack(pady=5)

    def __load_list(self):
        self.list_api_list["value"] = list(Global.BD_API.keys())
        self.list_language_list["value"] = list(Global.BD_Lang.keys())
        self.str_bd_ocr_api.set(dict(zip(Global.BD_API.values(), Global.BD_API.keys()))
                                [Global.config.get_value("bd_ocr_api")])
        self.str_bd_ocr_lang.set(dict(zip(Global.BD_Lang.values(), Global.BD_Lang.keys()))
                                 [Global.config.get_value("bd_ocr_lang")])

    def __apply_exp(self):
        """
        if self.experience.get() == 0:
            for child in self.lf_baidu.winfo_children() + self.lf_tencent.winfo_children():
                child.configure(state="normal")
                child.configure(state="normal")
            return

        for child in self.lf_baidu.winfo_children() + self.lf_tencent.winfo_children():
            child.configure(state="disabled")
            child.configure(state="disabled")
        """

    def __save_config(self):
        if (self.str_bd_api_key.get() == "" or self.str_bd_secret_key.get() == "") and \
                (self.str_tx_app_id.get() == "" or self.str_tx_app_key.get() == "") and self.experience.get() == 0:
            self.show_message_box("警告", "请填写OCR引擎的相关信息, 否则将无法进行字幕识别", "warning")

        Global.config.set_api_info(self.str_bd_api_key.get(), self.str_bd_secret_key.get(),
                                   Global.BD_API[self.str_bd_ocr_api.get()], Global.BD_Lang[self.str_bd_ocr_lang.get()],
                                   self.str_tx_app_id.get(), self.str_tx_app_key.get(), self.experience.get())
        Global.config.save_json()
        self.master.destroy()  # 关闭窗口

    @staticmethod
    def show_message_box(title, text, icon="info", type_="ok"):
        messagebox.showinfo(title, text, icon=icon, type=type_)


class MessageWindow:
    def __init__(self, master, title, msg, width, height):
        self.master = master
        center_window(self.master, width, height)
        self.master.title(title)
        self.master.iconbitmap("favico.ico")
        self.master.resizable(False, False)

        self.__init_widgets(msg)

    def __init_widgets(self, text):
        fr_message = ttk.Frame(self.master)
        fr_message.pack(fill="both", expand=True, padx=10, pady=10)
        ttk.Label(fr_message, text=text).pack(fill="y", expand=True)

        fr_button = ttk.Frame(self.master)
        fr_button.pack(fill="x", padx=10, pady=10)
        ttk.Button(fr_button, text="确定", command=self.master.destroy).pack()


class ChildThreading(Thread):
    def __init__(self, _func, _callback=None):
        super(ChildThreading, self).__init__()
        self._function = _func
        self._callback = _callback
        self._result = None

    def run(self):
        try:
            self._result = self._function()
            if self._result and self._callback is not None:
                self._callback()
        except:
            sys.excepthook(*sys.exc_info())


def center_window(_window, _w, _h):
    _ws = _window.winfo_screenwidth()
    _hs = _window.winfo_screenheight()
    _x = (_ws - _w) / 2
    _y = (_hs - _h) / 2
    _window.geometry("%dx%d+%d+%d" % (_w, _h, _x, _y))
