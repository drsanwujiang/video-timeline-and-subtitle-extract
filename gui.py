# -*- coding: UTF-8 -*-

import shutil
import threading
from tkinter import *
from tkinter import (ttk, filedialog, dialog)
from PIL import Image, ImageTk
from opencv import *
from subtitle import (get_subtitle_jd, get_subtitle_bd)
from gl import Global


class Gui:
    def __init__(self, master):
        self.master = master
        self.current_dir = Global.config.get_value("current_dir")

        # 定义控件
        self.tab_control = None  # Notebook
        self.list_file_list = None  # 文件列表
        self.lb_preview = None  # 二值化结果预览图片
        self.scale_y_from = None  # 字幕区域上限滑块
        self.scale_y_to = None  # 字幕区域下限滑块
        self.scale_frame = None  # 当前预览帧滑块
        self.b_begin_tl = None  # 时间轴-开始提取按钮
        self.b_begin_st = None  # 字幕-开始提取按钮

        # 定义绑定变量
        self.str_file_path = StringVar()  # FilePath
        self.str_file_name = StringVar()  # FileName
        self.str_file_resolution = StringVar()  # 分辨率
        self.i_current_frame = IntVar()  # 当前帧
        self.i_y_from = IntVar()  # 字幕区域上限
        self.i_y_to = IntVar()  # 字幕区域下限
        self.i_binary_threshold = IntVar()  # 二值化阈值
        self.str_current_tl = StringVar()  # 时间轴-当前帧
        self.str_process_tl = StringVar()  # 时间轴-进度
        self.str_errmsg_tl = StringVar()  # 时间轴-错误信息
        self.str_current_st = StringVar()  # 字幕-当前帧
        self.str_process_st = StringVar()  # 字幕-进度
        self.str_errmsg_st = StringVar()  # 字幕-错误信息

        # 将预览图像定义为全局变量防止被回收
        self.img = None

        self.init_widgets()  # 初始化控件
        self.load_list()  # 加载文件列表

    def init_widgets(self):
        self.tab_control = ttk.Notebook(self.master)
        self.tab_control.pack(fill="both", expand=True)

        self.init_start()  # 加载开始标签页
        self.init_settings()  # 加载设置标签页
        self.init_extract()  # 加载提取标签页

    def init_start(self):  # 开始标签页
        tab_start = ttk.Frame(self.tab_control)
        self.tab_control.add(tab_start, text="开始")

        # 选择目录
        lf_file_path = ttk.LabelFrame(tab_start, text=" 视频目录 ")
        lf_file_path.pack(fill="x", padx=10, pady=5)

        e_file_path = ttk.Entry(lf_file_path, textvariable=self.str_file_path)
        e_file_path.pack(fill="x", expand=True, padx=10, pady=5, side="left")
        b_file_path = ttk.Button(lf_file_path, text="选择目录...", command=self.open_dir)
        b_file_path.pack(padx=10, pady=10, side="left")

        # 文件列表
        lf_file_list = ttk.LabelFrame(tab_start, text=" 文件列表 ")
        lf_file_list.pack(fill="both", expand=True, padx=10, pady=5)

        self.list_file_list = Listbox(lf_file_list, selectmode="single")
        self.list_file_list.pack(fill="both", expand=True, padx=10, pady=5)
        scroll_file_list_y = Scrollbar(self.list_file_list, orient="vertical", command=self.list_file_list.yview)
        scroll_file_list_x = Scrollbar(self.list_file_list, orient="horizontal", command=self.list_file_list.xview)
        scroll_file_list_y.pack(side="right", fill="y")
        scroll_file_list_x.pack(side="bottom", fill="x")
        self.list_file_list.configure(yscrollcommand=scroll_file_list_y.set)
        self.list_file_list.configure(xscrollcommand=scroll_file_list_x.set)

        # 读取文件
        fr_load = ttk.Frame(tab_start)
        fr_load.pack(fill="x", padx=10, pady=5)
        b_load = ttk.Button(fr_load, text="读取", command=self.load_video)
        b_load.pack()

    def init_settings(self):  # 设置标签页
        tab_settings = ttk.Frame(self.tab_control)
        self.tab_control.add(tab_settings, text="设置")
        self.tab_control.tab(1, state="disabled")  # 禁用标签页

        # 文件信息
        lf_file_info = ttk.LabelFrame(tab_settings, text=" 文件信息 ")
        lf_file_info.pack(fill="x", padx=10, pady=5)
        lf_file_info.grid_columnconfigure(1, weight=1)
        ttk.Label(lf_file_info, text="文件名：").grid(row=0, column=0, padx=10)
        ttk.Label(lf_file_info, textvariable=self.str_file_name).grid(row=0, column=1, padx=10)
        ttk.Label(lf_file_info, text="分辨率：").grid(row=1, column=0, padx=10)
        ttk.Label(lf_file_info, textvariable=self.str_file_resolution).grid(row=1, column=1, padx=10)

        # 参数调整
        lf_params_adjust = ttk.LabelFrame(tab_settings, text=" 参数调整 ")
        lf_params_adjust.pack(fill="x", padx=10, pady=5)

        fr_param1 = Frame(lf_params_adjust)
        fr_param1.pack(fill="x", padx=10)
        ttk.Label(fr_param1, text="字幕区域起点：", width=15).pack(side="left")
        self.scale_y_from = Scale(fr_param1, from_=0, to=0, resolution=10, showvalue=True, orient="horizontal",
                                  variable=self.i_y_from)
        self.scale_y_from.pack(fill="x", side="right", expand=True)
        self.scale_y_from.bind("<ButtonRelease-1>", self.async_load_preview)

        fr_param2 = Frame(lf_params_adjust)
        fr_param2.pack(fill="x", padx=10)
        ttk.Label(fr_param2, text="字幕区域终点：", width=15).pack(side="left")
        self.scale_y_to = Scale(fr_param2, from_=0, to=0, resolution=10, showvalue=True, orient="horizontal",
                                variable=self.i_y_to)
        self.scale_y_to.pack(fill="x", side="right", expand=True)
        self.scale_y_to.bind("<ButtonRelease-1>", self.async_load_preview)

        fr_param3 = Frame(lf_params_adjust)
        fr_param3.pack(fill="x", padx=10)
        ttk.Label(fr_param3, text="二值化阈值：", width=15).pack(side="left")
        scale_bth = Scale(fr_param3, from_=150, to=255, resolution=1, showvalue=True, orient="horizontal",
                          variable=self.i_binary_threshold)
        scale_bth.pack(fill="x", side="right", expand=True)
        scale_bth.bind("<ButtonRelease-1>", self.async_load_preview)

        # 字幕区域及二值化效果预览
        lf_preview = ttk.LabelFrame(tab_settings, text=" 字幕区域及二值化效果预览 ")
        lf_preview.pack(fill="both", expand=True, padx=10, pady=5)
        self.lb_preview = Label(lf_preview, image=None)
        self.lb_preview.pack(fill="both", expand=True)
        self.scale_frame = Scale(lf_preview, from_=0, to=0, resolution=10, showvalue=True, orient="horizontal",
                                 variable=self.i_current_frame)
        self.scale_frame.pack(fill="x", padx=10, side="bottom")
        self.scale_frame.bind("<ButtonRelease-1>", self.async_load_preview)

    def init_extract(self):  # 提取标签页
        tab_extract = ttk.Frame(self.tab_control)
        self.tab_control.add(tab_extract, text="提取")
        self.tab_control.tab(2, state="disabled")  # 禁用标签页

        # 时间轴提取
        lf_timeline = ttk.LabelFrame(tab_extract, text=" 时间轴提取 ")
        lf_timeline.pack(fill="both", expand=True, padx=10, pady=10)
        lf_timeline.grid_columnconfigure(1, weight=1)
        ttk.Label(lf_timeline, text="当前：").grid(row=0, column=0, padx=10, pady=10)
        ttk.Label(lf_timeline, textvariable=self.str_current_tl).grid(row=0, column=1, padx=10, sticky="ns")
        ttk.Label(lf_timeline, text="进度：").grid(row=1, column=0, padx=10, pady=10)
        ttk.Label(lf_timeline, textvariable=self.str_process_tl).grid(row=1, column=1, padx=10, sticky="ns")
        self.b_begin_tl = ttk.Button(lf_timeline, text="开始提取", command=self.start_extract)
        self.b_begin_tl.grid(row=2, column=0, padx=10, pady=10)
        ttk.Label(lf_timeline, textvariable=self.str_errmsg_tl, foreground="red").grid(row=2, column=1, padx=10,
                                                                                       pady=10)

        # 字幕识别
        lf_subtitle = ttk.LabelFrame(tab_extract, text=" 字幕识别 ")
        lf_subtitle.pack(fill="both", expand=True, padx=10, pady=10)
        lf_subtitle.grid_columnconfigure(1, weight=1)
        ttk.Label(lf_subtitle, text="当前：").grid(row=0, column=0, padx=10, pady=10)
        ttk.Label(lf_subtitle, textvariable=self.str_current_st).grid(row=0, column=1, padx=10, sticky="ns")
        ttk.Label(lf_subtitle, text="进度：").grid(row=1, column=0, padx=10, pady=10)
        ttk.Label(lf_subtitle, textvariable=self.str_process_st).grid(row=1, column=1, padx=10, sticky="ns")
        self.b_begin_st = ttk.Button(lf_subtitle, text="开始识别", command=self.start_recognize, state="disabled")
        self.b_begin_st.grid(row=2, column=0, padx=10, pady=10)
        ttk.Label(lf_subtitle, textvariable=self.str_errmsg_st, foreground="red").grid(row=2, column=1, padx=10,
                                                                                       pady=10)

    def open_dir(self):
        # 调用askdirectory方法打开目录
        _file_path = filedialog.askdirectory(title="选择目录", initialdir=self.current_dir)
        if _file_path != "":
            Global.config.set_video_dir(_file_path)
            self.load_list()

    def load_list(self):
        self.str_file_path.set(Global.config.get_value("video_dir"))

        try:
            video_list = os.listdir(Global.config.get_value("video_dir"))
            self.list_file_list.delete(0, "end")
            for item in video_list:
                self.list_file_list.insert("end", item)
        except:
            self.list_file_list.delete(0, "end")

    def load_video(self):
        _name = self.list_file_list.get(self.list_file_list.curselection())
        Global.config.set_video_name(_name)

        if not test_file():
            self.show_dialog("错误", "文件打开失败，请检查格式或编码", "error")
            return
        elif Global.config.get_value("video_suffix") not in Global.Types:
            self.show_dialog("警告", "文件格式并非常见视频格式，可能导致程序不稳定", "warning")

        self.tab_control.tab(1, state="normal")  # 启用标签页
        self.tab_control.tab(2, state="normal")
        self.tab_control.select(1)
        self.load_settings()

    def load_settings(self):
        # 加载指定文件的信息 以及默认参数
        _w, _h, _fc, _fps = get_video_info()
        Global.config.set_video_info(_w, _h, _fc, _fps)  # 保存当前视频信息
        self.str_file_name.set(Global.config.get_value("video_name") + Global.config.get_value("video_suffix"))
        self.str_file_resolution.set("%s x %s" % (_w, _h))
        self.scale_frame.configure(to=(_fc - 1))
        self.scale_y_from.configure(to=_h)
        self.scale_y_to.configure(to=_h)
        self.i_current_frame.set(int(_fc / 2))
        self.i_y_from.set(int(_h * 0.83))
        self.i_y_to.set(_h)
        self.i_binary_threshold.set(Global.config.get_value("binary_threshold"))
        self.i_current_frame.set(int(_fc / 2))

        self.async_load_preview()

    def async_load_preview(self, _e=None):
        # 开启子线程
        task_timeline = MyThread(self.load_preview)
        task_timeline.setDaemon(True)
        task_timeline.start()

    def load_preview(self):
        # 保存更改后的参数
        Global.config.set_params(self.i_y_from.get(), self.i_y_to.get(), self.i_binary_threshold.get())

        # 加载图片预览
        _img = get_frame(self.i_current_frame.get(), self.i_y_from.get(), self.i_y_to.get(),
                         self.i_binary_threshold.get())

        if isinstance(_img, int):
            _w, _h, _, _ = get_video_info()
            self.i_y_from.set(int(_h * 0.83))
            self.i_y_to.set(_h)
            self.show_dialog("错误", "字幕区域设置错误!", "error")
            self.load_preview()
            return False

        self.img = ImageTk.PhotoImage(Image.fromarray(_img))
        self.lb_preview.configure(image=self.img)

        return True

    def start_extract(self):
        self.update_current_tl("")
        self.update_process_tl("")
        self.update_errmsg_tl("")
        self.b_begin_tl.configure(state="disabled")  # 禁用按钮
        self.b_begin_st.configure(state="disabled")  # 禁用按钮

        # 检查目录是否存在
        if os.path.exists(Global.config.get_value("binary_tmp")):
            try:
                shutil.rmtree(Global.config.get_value("binary_tmp"))
            except:
                self.b_begin_tl.configure(state="normal")  # 启用按钮
                self.update_errmsg_tl("无法删除临时图片目录! 请手动删除 binary_tmp 目录!")
                self.show_dialog("错误", "无法删除临时图片目录! 请手动删除 binary_tmp 目录!", "error")
                return

        os.makedirs(Global.config.get_value("binary_tmp"))

        if not (os.path.exists(Global.config.get_value("output_dir"))):
            os.makedirs(Global.config.get_value("output_dir"))

        # 开启子线程
        task_timeline = MyThread(get_timeline, lambda: self.b_begin_st.configure(state="normal"))
        task_timeline.setDaemon(True)
        task_timeline.start()

    def start_recognize(self):
        self.update_current_st("")
        self.update_process_st("")
        self.update_errmsg_st("")
        self.b_begin_st.configure(state="disabled")  # 禁用按钮

        # 开启子线程
        task_timeline = MyThread(get_subtitle_jd)
        task_timeline.setDaemon(True)
        task_timeline.start()

    def show_dialog(self, title, text, bitmap):
        dialog.Dialog(self.master,
                      {"title": title, "text": text, "bitmap": bitmap, "default": 0, "strings": ["确定"]})

    def update_current_tl(self, _msg):
        self.str_current_tl.set(_msg)

    def update_process_tl(self, _msg):
        self.str_process_tl.set(_msg)

    def update_errmsg_tl(self, _errmsg):
        self.str_errmsg_tl.set(_errmsg)

    def update_current_st(self, _msg):
        self.str_current_st.set(_msg)

    def update_process_st(self, _msg):
        self.str_process_st.set(_msg)

    def update_errmsg_st(self, _errmsg):
        self.str_errmsg_st.set(_errmsg)


class MyThread(threading.Thread):
    def __init__(self, func, callback=None):
        super(MyThread, self).__init__()
        self.function = func
        self.callback = callback
        self.result = None

    def run(self):
        self.result = self.function()
        if self.result and self.callback is not None:
            self.callback()
