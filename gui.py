# -*- coding: UTF-8 -*-

import threading
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import dialog
from PIL import Image, ImageTk
from opencv import *
from subtitle import get_subtitle


class Gui:
    def __init__(self, master):
        self.master = master
        self.init_widgets()
        Config.set_default()
        self.load_list()

    def init_widgets(self):
        style = ttk.Style()
        style.configure("button_style", foreground="black", background="#3E4149")

        self.tab_control = ttk.Notebook(self.master)
        self.tab_control.pack(fill="both", expand=True)

        # 开始标签页 Start
        tab_start = ttk.Frame(self.tab_control)
        self.tab_control.add(tab_start, text="开始")

        # 选择目录
        lf_file_path = ttk.LabelFrame(tab_start, text=" 视频目录 ")
        lf_file_path.pack(fill="x", padx=10, pady=5)

        self.str_file_path = StringVar()
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
        # 开始标签页 End

        # 设置标签页 Start
        tab_settings = ttk.Frame(self.tab_control)
        self.tab_control.add(tab_settings, text="设置")
        self.tab_control.tab(1, state="disabled")  # 禁用标签页

        # 文件信息
        lf_file_info = ttk.LabelFrame(tab_settings, text=" 文件信息 ")
        lf_file_info.pack(fill="x", padx=10, pady=5)
        lf_file_info.grid_columnconfigure(1, weight=1)

        self.str_file_name = StringVar()
        ttk.Label(lf_file_info, text="文件名：").grid(row=0, column=0, padx=10)
        ttk.Label(lf_file_info, textvariable=self.str_file_name).grid(row=0, column=1, padx=10, sticky="ns")
        self.str_file_resolution = StringVar()
        ttk.Label(lf_file_info, text="分辨率：").grid(row=1, column=0, padx=10)
        ttk.Label(lf_file_info, textvariable=self.str_file_resolution).grid(row=1, column=1, padx=10, sticky="ns")

        # 字幕区域及二值化效果预览
        self.lf_preview = ttk.LabelFrame(tab_settings, text=" 字幕区域及二值化效果预览 ")
        self.lf_preview.pack(fill="both", expand=True, padx=10, pady=5, side="left")
        self.lb_preview = Label(self.lf_preview, image=None)
        self.lb_preview.pack(fill="both", expand=True)

        # 参数调整
        lf_params_adjust = ttk.LabelFrame(tab_settings, text=" 参数调整 ")
        lf_params_adjust.pack(padx=10, pady=5, side="right")
        ttk.Label(lf_params_adjust, text="字幕区域(Y方向)：").grid(row=0, padx=10, pady=5)
        ttk.Label(lf_params_adjust, text="从").grid(row=1, padx=10)

        self.i_y_from = IntVar()
        ttk.Entry(lf_params_adjust, width=10, textvariable=self.i_y_from).grid(row=2, padx=10)
        self.scale_y_from = Scale(lf_params_adjust, from_=0, to=0, resolution=10, showvalue=False, orient="horizontal",
                                  variable=self.i_y_from, command=self.load_preview)
        self.scale_y_from.grid(row=3, padx=10)

        ttk.Label(lf_params_adjust, text="到").grid(row=4, padx=10, pady=5)

        self.i_y_to = IntVar()
        ttk.Entry(lf_params_adjust, width=10, textvariable=self.i_y_to).grid(row=5, padx=10)
        self.scale_y_to = Scale(lf_params_adjust, from_=0, to=0, resolution=10, showvalue=False, orient="horizontal",
                                variable=self.i_y_to, command=self.load_preview)
        self.scale_y_to.grid(row=6, padx=10)

        ttk.Label(lf_params_adjust, text="二值化阈值：").grid(row=7, padx=10, pady=5)

        self.i_binary_threshold = IntVar()
        ttk.Entry(lf_params_adjust, width=10, textvariable=self.i_binary_threshold).grid(row=8, padx=10)
        scale_binary_threshold = Scale(lf_params_adjust, from_=0, to=255, resolution=5, showvalue=False,
                                       orient="horizontal", variable=self.i_binary_threshold, command=self.load_preview)
        scale_binary_threshold.grid(row=9, padx=10)
        # 设置标签页 End

        # 提取标签页 Start
        tab_extract = ttk.Frame(self.tab_control)
        self.tab_control.add(tab_extract, text="提取")
        self.tab_control.tab(2, state="disabled")  # 禁用标签页

        # 时间轴识别
        lf_timeline = ttk.LabelFrame(tab_extract, text=" 时间轴识别 ")
        lf_timeline.pack(fill="both", expand=True, padx=10, pady=10)
        lf_timeline.grid_columnconfigure(1, weight=1)

        self.str_current_tl = StringVar()
        ttk.Label(lf_timeline, text="当前：").grid(row=0, column=0, padx=10, pady=10)
        ttk.Label(lf_timeline, textvariable=self.str_current_tl).grid(row=0, column=1, padx=10, sticky="ns")
        self.i_process_tl = StringVar()
        ttk.Label(lf_timeline, text="进度：").grid(row=1, column=0, padx=10, pady=10)
        ttk.Label(lf_timeline, textvariable=self.i_process_tl).grid(row=1, column=1, padx=10, sticky="ns")

        # 字幕识别
        lf_subtitle = ttk.LabelFrame(tab_extract, text=" 字幕识别 ")
        lf_subtitle.pack(fill="both", expand=True, padx=10, pady=10)
        lf_subtitle.grid_columnconfigure(1, weight=1)

        self.str_current_st = StringVar()
        ttk.Label(lf_subtitle, text="当前：").grid(row=0, column=0, padx=10, pady=10)
        ttk.Label(lf_subtitle, textvariable=self.str_current_st).grid(row=0, column=1, padx=10, sticky="ns")
        self.i_process_st = StringVar()
        ttk.Label(lf_subtitle, text="进度：").grid(row=1, column=0, padx=10, pady=10)
        ttk.Label(lf_subtitle, textvariable=self.i_process_st).grid(row=1, column=1, padx=10, sticky="ns")

        # 开始提取
        lf_begin = ttk.LabelFrame(tab_extract, text=" 开始提取 ")
        lf_begin.pack(fill="both", expand=True, padx=10, pady=10)

        self.b_begin = ttk.Button(lf_begin, text="开始提取", command=self.start_extract)
        self.b_begin.pack(padx=10, pady=10, side="left")
        self.error_message = StringVar()
        self.lb_ststus = ttk.Label(lf_begin, textvariable=self.error_message, foreground="red")
        self.lb_ststus.pack(fill="x", padx=10, pady=10)
        # 提取标签页 End

    def load_list(self):
        self.str_file_path.set(Config.get_value("video_dir"))
        video_list = os.listdir(Config.get_value("video_dir"))
        self.list_file_list.delete(0, "end")
        for item in video_list:
            self.list_file_list.insert("end", item)

    def open_dir(self):
        # 调用askdirectory方法打开目录
        _file_path = filedialog.askdirectory(title="选择目录", initialdir=Config.get_value("current_dir"))
        if _file_path != "":
            Config.set_video_dir(_file_path)
            self.load_list()

    def load_video(self):
        _name = self.list_file_list.get(self.list_file_list.curselection())
        Config.set_video_name(_name)

        if not test_file():
            dialog.Dialog(self.master, {"title": "错误", "text": "文件打开失败，请检查格式或编码", "bitmap": "error",
                                        "default": 0, "strings": ["确定"]})
            return
        elif Config.get_value("video_suffix") not in Config.Types:
            dialog.Dialog(self.master, {"title": "警告", "text": "文件格式并非常见视频格式，可能导致程序不稳定",
                                        "bitmap": "warning", "default": 0, "strings": ["确定"]})

        self.tab_control.tab(1, state="normal")  # 启用标签页
        self.tab_control.tab(2, state="normal")
        self.tab_control.select(1)
        self.load_settings()

    def load_settings(self):
        _w, _h, _fc = get_video_info()
        Config.set_video_info(_w, _h, _fc)
        self.str_file_name.set(Config.get_value("video_name") + Config.get_value("video_suffix"))
        self.str_file_resolution.set("%s x %s" % (_w, _h))
        self.scale_y_from.configure(to=_h)
        self.scale_y_to.configure(to=_h)
        self.i_y_from.set(int(_h * 0.83))
        self.i_y_to.set(_h)
        self.i_binary_threshold.set(Config.get_value("binary_threshold"))

        self.i_current_frame = IntVar()
        self.i_current_frame.set(int(_fc / 2))
        self.scale_frame = Scale(self.lf_preview, from_=0, to=(_fc - 1), resolution=5, showvalue=True, orient="horizontal",
                                 variable=self.i_current_frame, command=self.load_preview)
        self.scale_frame.pack(fill="x", side="bottom")

        self.load_preview(None)

    def load_preview(self, _v):
        Config.set_params(self.i_y_from.get(), self.i_y_to.get(), self.i_binary_threshold.get())
        _img = get_frame(self.i_current_frame.get(), self.i_y_from.get(), self.i_y_to.get(),
                         self.i_binary_threshold.get())
        self.img = ImageTk.PhotoImage(Image.fromarray(_img))
        self.lb_preview.configure(image=self.img)

    def start_extract(self):
        self.b_begin.configure(state="disabled")  # 禁用按钮

        task_timeline = MyThread(get_timeline, self.continue_extract, self)
        task_timeline.setDaemon(True)
        task_timeline.start()

    def continue_extract(self):
        subtitle_result = get_subtitle(self)
        self.b_begin.configure(state="normal")  # 启用按钮
        if subtitle_result:
            self.lb_ststus.configure(foreground="green")
            self.error_message.set("完成!")


class MyThread(threading.Thread):
    def __init__(self, func, callback, gui):
        super(MyThread, self).__init__()
        self.func = func
        self.gui = gui
        self.callback = callback

    def run(self):
        self.result = self.func(self.gui)
        if self.result:
            self.callback()

    def get_result(self):
        threading.Thread.join(self)
        try:
            return self.result  # 如果子线程不使用join方法，此处可能会报没有self.result的错误
        except Exception:
            return None
