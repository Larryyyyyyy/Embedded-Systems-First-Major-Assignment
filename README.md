# 嵌入式系统--第一次大作业

武汉大学《嵌入式系统》-- 任课老师**武小平**。

本项目作为课程第一次大作业成果，最终以项目报告形式呈现。

本文档将会说明仓库基本信息、项目报告$Latex$源码、实验源代码和实验复现方案。

## 仓库结构

```
Embedded-Systems-First-Major-Assignment/
├── docs/                         # 项目报告 LaTex 源码 & 图表 & 发布文档
├── expr1/                        # 方案雏形涉及源代码
│   ├── run.py                    # 下载并部署模型 & 获取与板子位于同一网络下的图像 & 完成模型推理
│   ├── CameraWebServer           # 源自开发环境提供示例
│   │   ├── board_config.h        # 改为仅不注释 #define CAMERA_MODEL_ESP32S3_EYE
│   │   ├── CameraWebServer.ino   # 输入与本地环境对应的 Wi-Fi ssid 与密码
│   │   └── ...
├── expr2                         # 初版方案涉及源代码
│   ├── run.py                    # 训练 MNIST 模型
│   ├── pre_run.py                # 直接获取预训练 MNIST 模型
│   └── sketch_oct4a              # 嵌入代码
├── expr3                         # 终版方案涉及源代码
│   └── sketch_oct7a              # 嵌入代码
├── models                        # 参考模型文件
│   ├── mnist-12.onnx             # 初版方案
│   └── fomo_mask_int8.tflite     # 终版方案
├── ModelAssistant                # 引用开源项目, 位于 https://github.com/Seeed-Studio/ModelAssistant
└── README.md                     # 本文档
```

## 环境准备

### 硬件

Esp32S3开发板和Ov2640摄像头。

一根常规TypeC数据线。

### 软件

获取`ArduinoIDE`：

- 官网：[arduino.cc/en/software/](https://www.arduino.cc/en/software/)
- Win64直链：https://downloads.arduino.cc/arduino-ide/arduino-ide_2.3.10_Windows_64bit.exe

开发板管理器地址：

https://github.com/espressif/arduino-esp32/releases/download/3.3.10/package_esp32_index_cn.json

选用的开发板环境：

esp32 by Espressif Systems -- 3.3.10-cn

也可以通过官方仓库获取：

[espressif/arduino-esp32: Arduino core for the ESP32 family of SoCs](https://github.com/espressif/arduino-esp32)

---

使用`Edge Impulse`在线平台：https://www.edgeimpulse.com/

---

根据`ModelAssistant`内`requirements.txt`配置好的`Python`环境。

## 方案雏形

> 在`ArduionIDE`内，选用`ESP32S3 Dev Module`。
>
> 通过TypeC数据线连接电脑与板子面向摄像头视角内靠右的接口。
>
> 需修改板子配置不同于默认配置的地方有：
>
> - `Flash Size`修改为`16MB (128Mb)`
> - `Partition Scheme`修改为`Huge APP (3MB No OTA/1MB SPIFFS)`
> - `PSRAM`修改为`OPI PSRAM`。
>
> 必要时可以重置板子原有程序。

~~上述操作在后续方案中仍需优先进行，在后续方案中不赘述~~

编译并上传位流。

运行`/expr1/run.py`。

## 初版方案

运行`/expr2/run.py`，等待几分钟后获得模型文件`mnist-12.onnx`。

在 Edge Impulse 平台上传该模型，注意模型输入输出信息需要修改：

- `Model input`修改为`Image`。
- `How is your input scaled?`修改为`Pixels ranging 0..1 (not normalized)`。
- `Resize mode`修改为`Fit shortest axis`。
- `Model output`修改为`Classification`。

`Save model`即可，然后选择以`ArduionIDE`形式导出为`.zip`文件。

在`ArduionIDE`内项目$\rightarrow$导入库$\rightarrow$添加 .ZIP 库完成添加即可。

> 本项目代码的 Edge Impulse 项目名为`Test_inferencing`，故我的头文件处理为`#include <Test_inferencing.h>`，复现时请注意修改。

编译并上传位流。

## 终版方案

获取数据集：https://files.seeedstudio.com/sscma/datasets/coco_mask.zip

Clone开源项目`ModelAssistant`。建议将数据集放入该项目根目录。

在该项目根目录内，执行

```shell
python tools/train.py \
    configs/fomo/fomo_mobnetv2_0.35_x8_coco.py \
    --cfg-options \
    data_root=coco_mask/mask/ \
    num_classes=2 \
    train_ann=train/_annotations.coco.json \
    val_ann=valid/_annotations.coco.json \
    train_data=train/ \
    val_data=valid/ \
    epochs=50 \
    height=192 \
    width=192
```

约两个小时后，获得模型文件`fomo_mask_int8.tflite`。

在 Edge Impulse 平台上传该模型，注意模型输入输出信息需要修改：

- `Model input`修改为`Image`。
- `How is your input scaled?`修改为`Pixels ranging 0..1 (not normalized)`。
- `Resize mode`修改为`Fit shortest axis`。
- `Model output`修改为`Object detection`。
- `Output layer`修改为`FOMO`。
- `Output labels (2)`修改为`class 1, class 2`。

`Save model`即可，然后选择以`ArduionIDE`形式导出为`.zip`文件。

在`ArduionIDE`内项目$\rightarrow$导入库$\rightarrow$添加 .ZIP 库完成添加即可。

编译并上传位流。