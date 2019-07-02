# -*- coding: UTF-8 -*-

from tkinter import Tk
from gl import Global
from config import Config
from gui import Gui


def main():
    Global.config = Config()
    window = Tk()
    window.title("视频时间轴及字幕提取")
    window.geometry("500x400")
    Global.gui = Gui(window)
    window.mainloop()


if __name__ == "__main__":
    main()
