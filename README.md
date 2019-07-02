# 视频字幕及时间轴提取

## 能帮助你：

### 1、识别字幕的时间轴
通过帧差法判断是否相同帧，进而由相同帧得出字幕时间轴

计算时间轴对应帧的 SSIM ，合并相同的时间轴

### 2、利用OCR识别字幕
将指定字幕区域二值化得到只包含字幕的图片，之后利用OCR精准识别字幕

目前使用京东OCR的接口，但效果不佳，所以近期将引入百度OCR

下一阶段的目标是引入 tesseract-ocr

## 如何使用
### 环境
Windows 系统（Linux, macOS 未经测试, 但是理论上没有问题）

Python 3.x

OpenCV, Pillow, skimage:

    pip install opencv-python Pillow scikit-image

### 获取代码
方法一：

    git clone https://github.com/drsanwujiang/video-timeline-and-subtitle-extract.git

方法二：右上角 - clone or download - download zip

### 申请京东OCR
https://neuhub.jd.com/ai/api/ocr/general

在京东AI开放平台注册，创建通用文字识别应用得到 APP_KEY 、 SECRET_KEY

每天免费调用50000次，QPS是2。

### 配置
打开 config.ini ，在 APP_KEY 、 SECRET_KEY 后填写自己的 APP_KEY 、 SECRET_KEY

[params] 部分是默认参数

### 参数说明：
    jpg_quality = 40  # 图片输出质量, 0~100, 如果视频清晰度不高，可以适当调高
    probability = 0.66  # OCR可信度下限, 0~1, 低于此可信度的识别结果将被忽略
    binary_threshold = 250  # 二值化阈值, 150~255, 调整数值并尽量使结果只有文字

### 执行
1.创建 videos 文件夹，把视频文件放进去

2.运行 index.pyw

3.选择视频文件

4.适当调整字幕区域和二值化阈值并预览效果，确保字幕清晰不泛白

5.开始提取，结束后在 output 文件夹查看结果