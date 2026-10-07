import urllib.request

onnx_url = "https://github.com/onnx/models/raw/main/validated/vision/classification/mnist/model/mnist-12.onnx"
model_path = "mnist-12.onnx"
urllib.request.urlretrieve(onnx_url, model_path)