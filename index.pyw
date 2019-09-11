# -*- coding: UTF-8 -*-

import sys
import traceback
from tkinter import messagebox
from ttkthemes import ThemedTk
from gl import Global
from config import Config
from opencv import OpenCVUtils
from ocr import OCRUtils
from gui import MainWindow


# 异常处理
def except_handler(_type, _value, _traceback):
    title = "错误"
    text = "出现预料之外的错误!\n\nType: {}\nValue: {}\n{}\n请将此信息告知作者, 谢谢!"\
           .format(_type, _value, "".join(traceback.format_exception(_type, _value, _traceback)))
    messagebox.showinfo(title, text, icon="error", type="ok")


def main():
    sys.excepthook = except_handler  # 使用自定义的异常处理
    Global.config = Config()  # 初始化config
    Global.opencv_utils = OpenCVUtils()  # 初始化opencv_utils
    Global.ocr_utils = OCRUtils()  # 初始化ocr_utils
    window = ThemedTk(theme="arc")  # 加载主题
    Global.gui = MainWindow(window)  # 初始化gui
    window.mainloop()


if __name__ == "__main__":
    main()
