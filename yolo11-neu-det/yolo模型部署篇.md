#  yolo模型部署篇

YOLO模型训练之后，我们得到的是PT的文件，PT的模型在windows进行部署使用的时候是比较方便的，但是如果放在移动端的设备上使用效率比较低，并且可能这个模型格式在对应的移动端的设备上不适用。为了解决这个问题，我们需要将yolo模型导出为其他格式的文件，并且需要C++等语言来完成解析和部署。下面我们将会从模型导出，python调用和c++调用三个模型对yolo模型的使用进行解析。

### 模型导出

模型导出之前，需要安装对应的不同的库所对应的文件，安装的指令如下。

![image-20250117142014792](C:\Users\Scm97\AppData\Roaming\Typora\typora-user-images\image-20250117142014792.png)

```
pip install setuptools==58.0.0
pip install ultralytics[export]
pip install ncnn
pip install onnxruntime-gpu
pip install onnxslim
pip install tensorrt
pip insta
```

安装过程如下图所示：

![image-20250117142905968](https://vehicle4cm.oss-cn-beijing.aliyuncs.com/imgs/image-20250117142905968.png)

对于模型的导出，官方提供了export.py文件，这个文件中支持多种格式的导出，导出的方法也非常简单，只需要输入下面的代码， 输入你的模型路径即可完成对应模型的导出。

```python
from ultralytics import YOLO
# Load a model
model = YOLO("yolo11n.pt")  # load an official model
model = YOLO("path/to/best.pt")  # load a custom trained model
# Export the model
model.export(format="onnx")
```

模型导出的过程中，支持下面的参数。本表详细介绍了可用于将YOLO 模型导出为不同格式的配置和选项。这些设置对于优化导出模型的性能、大小以及在不同平台和环境中的兼容性至关重要。正确的配置可确保模型以最佳效率部署到预定应用中。

| 论据        | 类型              | 默认值          | 说明                                                         |
| :---------- | :---------------- | :-------------- | :----------------------------------------------------------- |
| `format`    | `str`             | `'torchscript'` | 导出模型的目标格式，例如 `'onnx'`, `'torchscript'`, `'tensorflow'`或其他，定义与各种部署环境的兼容性。 |
| `imgsz`     | `int` 或 `tuple`  | `640`           | 模型输入所需的图像尺寸。对于正方形图像，可以是一个整数，或者是一个元组 `(height, width)` 了解具体尺寸。 |
| `keras`     | `bool`            | `False`         | 可导出为 Keras 格式 [TensorFlow](https://www.ultralytics.com/glossary/tensorflow)SavedModel的 Keras 格式，提供与TensorFlow serving 和 API 的兼容性。 |
| `optimize`  | `bool`            | `False`         | 在导出到TorchScript 时，应用针对移动设备的优化，可能会减小模型大小并提高性能。 |
| `half`      | `bool`            | `False`         | 启用 FP16（半精度）量化，在支持的硬件上减小模型大小并可能加快推理速度。 |
| `int8`      | `bool`            | `False`         | 激活 INT8 量化，进一步压缩模型并加快推理速度，同时将[精度](https://www.ultralytics.com/glossary/accuracy)损失降至最低，主要用于边缘设备。 |
| `dynamic`   | `bool`            | `False`         | 允许为ONNX 、TensorRT 和OpenVINO 导出动态输入尺寸，提高了处理不同图像尺寸的灵活性。 |
| `simplify`  | `bool`            | `True`          | 简化了ONNX 输出的模型图。 `onnxslim`这可能会提高性能和兼容性。 |
| `opset`     | `int`             | `None`          | 指定ONNX opset 版本，以便与不同的ONNX 解析器和运行时兼容。如果未设置，则使用最新的支持版本。 |
| `workspace` | `float` 或 `None` | `None`          | 为TensorRT 优化设置最大工作区大小（GiB），以平衡内存使用和性能；使用 `None` TensorRT 进行自动分配，最高可达设备最大值。 |
| `nms`       | `bool`            | `False`         | 在CoreML 导出中添加非最大值抑制 (NMS)，这对精确高效的检测后处理至关重要。 |
| `batch`     | `int`             | `1`             | 指定导出模型的批量推理大小，或导出模型将同时处理的图像的最大数量。 `predict` 模式。 |
| `device`    | `str`             | `None`          | 指定导出设备：GPU (`device=0`）、CPU (`device=cpu`)、MPS for Apple silicon (`device=mps`）或NVIDIA Jetson 的 DLA (`device=dla:0` 或 `device=dla:1`). |

调整这些参数可自定义导出过程，以满足特定要求，如部署环境、硬件限制和性能目标。选择合适的格式和设置对于实现模型大小、速度和[准确性](https://www.ultralytics.com/glossary/accuracy)之间的最佳平衡至关重要。

其中，官方支持的格式如下。

YOLO11 可用的导出格式如下表所示。您可以使用 `format` 参数，即 `format='onnx'` 或 `format='engine'`.您可以直接对导出的模型进行预测或验证，即 `yolo predict model=yolo11n.onnx`.导出完成后会显示模型的使用示例。

| 格式                                                         | `format` 论据 | 模型                      | 元数据 | 论据                                                         |
| :----------------------------------------------------------- | :------------ | :------------------------ | :----- | :----------------------------------------------------------- |
| [PyTorch](https://pytorch.org/)                              | -             | `yolo11n.pt`              | ✅      | -                                                            |
| [TorchScript](https://docs.ultralytics.com/zh/integrations/torchscript/) | `torchscript` | `yolo11n.torchscript`     | ✅      | `imgsz`, `optimize`, `batch`                                 |
| [ONNX](https://docs.ultralytics.com/zh/integrations/onnx/)   | `onnx`        | `yolo11n.onnx`            | ✅      | `imgsz`, `half`, `dynamic`, `simplify`, `opset`, `batch`     |
| [OpenVINO](https://docs.ultralytics.com/zh/integrations/openvino/) | `openvino`    | `yolo11n_openvino_model/` | ✅      | `imgsz`, `half`, `dynamic`, `int8`, `batch`                  |
| [TensorRT](https://docs.ultralytics.com/zh/integrations/tensorrt/) | `engine`      | `yolo11n.engine`          | ✅      | `imgsz`, `half`, `dynamic`, `simplify`, `workspace`, `int8`, `batch` |
| [CoreML](https://docs.ultralytics.com/zh/integrations/coreml/) | `coreml`      | `yolo11n.mlpackage`       | ✅      | `imgsz`, `half`, `int8`, `nms`, `batch`                      |
| [TF SavedModel](https://docs.ultralytics.com/zh/integrations/tf-savedmodel/) | `saved_model` | `yolo11n_saved_model/`    | ✅      | `imgsz`, `keras`, `int8`, `batch`                            |
| [TF GraphDef](https://docs.ultralytics.com/zh/integrations/tf-graphdef/) | `pb`          | `yolo11n.pb`              | ❌      | `imgsz`, `batch`                                             |
| [TF 轻型](https://docs.ultralytics.com/zh/integrations/tflite/) | `tflite`      | `yolo11n.tflite`          | ✅      | `imgsz`, `half`, `int8`, `batch`                             |
| [TF 边缘TPU](https://docs.ultralytics.com/zh/integrations/edge-tpu/) | `edgetpu`     | `yolo11n_edgetpu.tflite`  | ✅      | `imgsz`                                                      |
| [TF.js](https://docs.ultralytics.com/zh/integrations/tfjs/)  | `tfjs`        | `yolo11n_web_model/`      | ✅      | `imgsz`, `half`, `int8`, `batch`                             |
| [PaddlePaddle](https://docs.ultralytics.com/zh/integrations/paddlepaddle/) | `paddle`      | `yolo11n_paddle_model/`   | ✅      | `imgsz`, `batch`                                             |
| [MNN](https://docs.ultralytics.com/zh/integrations/mnn/)     | `mnn`         | `yolo11n.mnn`             | ✅      | `imgsz`, `batch`, `int8`, `half`                             |
| [NCNN](https://docs.ultralytics.com/zh/integrations/ncnn/)   | `ncnn`        | `yolo11n_ncnn_model/`     | ✅      | `imgsz`, `half`, `batch`                                     |
| [IMX500](https://docs.ultralytics.com/zh/integrations/sony-imx500/) | `imx`         | `yolov8n_imx_model/`      | ✅      | `imgsz`, `int8`                                              |

## 常见问题

导出完成之后，同样我们可以使用predict.py脚本对导出的模型文件进行预测，执行下列指令完成预测即可。

```bash
yolo predict model=yolo11n.onnx
```

如果要提升模型推理的速度，导出的过程中可以考虑下面的几个参数。

了解和配置导出参数对于优化模型性能至关重要：

- **`format:`** 导出模型的目标格式（例如："......"）、 `onnx`, `torchscript`, `tensorflow`).
- **`imgsz:`** 模型输入所需的图像大小（例如："......"）、 `640` 或 `(height, width)`).
- **`half:`** 启用 FP16 量化，减少模型大小，并可能加快推理速度。
- **`optimize:`** 针对移动或受限环境进行特定优化。
- **`int8:`** 启用 INT8 量化，非常有利于边缘部署。

注意，使用int8量化的时候要看具体的模型是否支持，如果导出格式不支持，量化则无用。

