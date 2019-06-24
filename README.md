# 视频字幕及时间轴提取

## 或许能帮你：

### 1、识别字幕的时间轴
通过计算前后帧的汉明距离，判断是否相同帧，进而由相同帧得出字幕时间轴。

### 2、利用OCR识别字幕
将指定字幕区域二值化增加识别准确度，之后利用OCR精准识别字幕。

需要网络连接，目前使用的是京东OCR，下一步是使用tesseract-ocr

## 如何使用
### 环境
Windows 系统（Linux, macOS 未经测试, 但是理论上没有问题）

Python 3.x（Python 2.x 的许多语法和 3.x 不一样, 无法使用）

OpenCV, Pillow:

    pip install opencv-python Pillow

### 获取代码
方法一：

    git clone https://github.com/drsanwujiang/video-timeline-and-subtitle-extract.git

方法二：右上角 - clone or download - download zip

### 申请京东OCR
https://neuhub.jd.com/ai/api/ocr/general

在京东AI开放平台注册，创建通用文字识别应用得到 APP_KEY 、 SECRET_KEY ，就可以用了。

每天免费调用50000次，QPS是2。

### 配置
打开 config.ini ，在 APP_KEY 、 SECRET_KEY 后填写自己的 APP_KEY 、 SECRET_KEY

如果需要永久修改参数，则直接更改 config.ini 文件中的值即可

否则请在程序窗口中移动滑块更改

### 参数说明：
    jpg_quality = 40  # 图片输出质量, 0~100, 除非视频清晰度不高，否则无需调太高
    probability = 0.66  # OCR可信度下限, 0~1, 低于此可信度的识别结果将被忽略
    similarity = 0.66  # 字幕相似度下限, 0~1, 低于此相似度的字幕将被认为不是同一字幕
    y_from = 900  # 字幕区域起点, 0~视频高度, 默认值为视频高度的六分之五（例如1080就是900）, 可根据情况在本文件或者程序中调整
    y_to = 1080  # 字幕区域终点, y_from~视频高度（默认到视频底部）
    binary_threshold = 250  # 二值化阈值, 0~255, 尽量使二值化的结果只有文字
    
其中，字幕区域起终点固定为视频高度的六分之五和视频底部，二值化阈值可以在程序中预览效果

### 执行
1.创建 video 文件夹，把视频文件放进去。

2.执行 index.py

3.选择视频文件

4.适当调整字幕区域和二值化阈值并预览效果，确保字幕清晰且不泛白

5.开始提取，结束后在 output 文件夹查看结果