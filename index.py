# -*- coding: UTF-8 -*-

from tkinter import *
from gui import Gui


def main():
    window = Tk()
    window.title("视频时间轴及字幕提取")
    window.geometry("600x400")
    Gui(window)
    window.mainloop()


if __name__ == "__main__":
    main()
