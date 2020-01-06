# 视频时间轴及字幕提取


## 能帮助你：
### 1、识别字幕的时间轴
通过帧差法判断是否相同帧, 进而由相同帧得出字幕时间轴

计算时间轴对应帧的 SSIM , 合并相同的时间轴

### 2、利用OCR识别字幕
将指定字幕区域二值化得到只包含字幕的图片, 之后利用 OCR 精准识别字幕

目前使用百度 OCR , 腾讯 OCR 的接口

有生之年的目标是引入 tesseract-ocr


## 如何使用
### 系统环境
Windows 系统 ( macOS 未经测试, 但是理论上没有问题)

Python 3.x (建议 Python 3.7)

### 获取代码
#### 1.下载 Source code 并手动安装所需模块
在 [Release](https://github.com/drsanwujiang/video-timeline-and-subtitle-extract/releases)
页面下载 Zip 格式的 Source code 并解压

在命令行执行

    pip install setuptools
    pip install opencv-python Pillow scikit-image scipy requests ttkthemes
    
将会自动安装所依赖的模块

#### 2.下载包含完整模块的压缩包 
还可以 [点击这里](https://starcloud.cloud/s/H4JKSsxiD58AaHf)
下载包含完整模块的压缩包，可以无需安装模块直接运行

### 申请OCR
#### 百度OCR
[点击这里](https://console.bce.baidu.com/ai/#/ai/ocr/app/create)
在百度智能云创建文字识别应用, 在应用列表页面可以看到 API Key 和 Secret Key

![百度智能云 应用列表页面](https://starcloud.cloud/s/NTJ5MkgNw6Wdpad/download "百度智能云 应用列表页面")

百度OCR提供多个通用文字识别接口, 虽然官网显示不保证并发, 但是实测 QPS 至少能达到 3:

|   接口   | 通用文字识别 | 通用文字识别(含位置信息版) | 通用文字识别(高精度版) | 通用文字识别(高精度含位置版) | 网络图片文字识别 |
| :------: | :---------: | :----------------------: | :-------------------: | :------------------------: | :--------------:|
| 免费额度 |  50000次/日  |         500次/日         |        500次/日        |          50次/日           |     500次/日    |

因为百度云是按行识别, 所以位置信息不是我们所必需的, 最基本的通用文字识别即可满足大部分需求

其中, 通用文字识别和通用文字识别(高精度版)支持中英文混合, 英文, 葡萄牙语, 法语, 德语, 意大利语, 西班牙语, 俄语, 日语, 韩语 10 钟语言类型

#### 腾讯OCR
[点击这里](https://ai.qq.com/console/application/create-app)
在腾讯AI开放平台创建应用, 在应用信息页面可以看到 APPID 和 APPKEY

![腾讯AI开放平台 应用列表页面](https://starcloud.cloud/s/ad9S3ZKY8NEtF5c/download "腾讯AI开放平台 应用列表页面")

之后点击 **能力库** -> **OCR** -> **通用OCR** 接入能力, **否则** 无法使用OCR

![腾讯AI开放平台 接入能力页面](https://starcloud.cloud/s/zHRnaPyTinWgsbk/download "腾讯AI开放平台 接入能力页面")

注意, 此接口**并不是**腾讯云(cloud.tencent.com)的文字识别 OCR 接口, 腾讯云的接口只有 1000次/月 的免费额度

腾讯AI开放平台 OCR 叫做优图 OCR , 目前是完全免费的状态, 只有QPS的限制

#### 选择哪个?
实际测试来看, 两个 OCR 的表现都很不错, 腾讯 OCR 的精确度略微高于百度但也相差不大, 百度 OCR 的 QPS 能达到 3 但是字幕数量最多也就一千多条, 所以时间也不会相差太多

有中文之外的需求, 直接选择百度OCR

### 使用
* 启动 index.pyw
    + 首次启动会要求输入 OCR 的相关信息, 也可以选择使用共享API进行体验
        + 共享API存在较大QPS限制，建议体验结束后注册并填写自己的API信息
* 选择视频并调整参数
    + 调整字幕区域使其只包含字幕
    + 调整二值化阈值, 尽可能使图片只包含字幕且字幕尽量黑
    + 移动最下方的滚动条查看不同帧的效果
* 开始提取时间轴并识别字幕
    + 时间轴提取完成后会自动开始识别字幕, 字幕识别完成后会输出带时间轴的字幕文件, 后缀为.srt
    + 时间轴提取完成但字幕识别出现错误, 可以直接重新识别字幕, 时间轴信息不会丢失
* 在 output 文件夹查看输出结果

#### 参数调整
在"参数"页面调整的参数不会作为默认值被保存到文件, 如果需要调整这些参数的默认值, 请直接修改 config.json 文件
建议只根据需要修改 binary_threshold 二值化阈值的默认值


## 测试结果
#### 百度OCR 腾讯OCR 识别结果对比:

![百度OCR 腾讯OCR 识别结果对比](https://starcloud.cloud/s/x9W2oaLfsHTTW8B/download "百度OCR 腾讯OCR 识别结果对比")
