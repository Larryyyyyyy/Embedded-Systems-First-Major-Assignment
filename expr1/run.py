import cv2
import numpy as np
import urllib.request
from torchvision import transforms

onnx_url = "https://github.com/onnx/models/raw/main/validated/vision/classification/mnist/model/mnist-12.onnx"
model_path = "mnist-12.onnx"

# 下载 ONNX 模型
urllib.request.urlretrieve(onnx_url, model_path)

# 加载 ONNX 模型
net = cv2.dnn.readNetFromONNX(model_path)

# 读取图像并输入模型推理
def predict_digit(img_28x28):
    # 归一化并转为 blob 格式 [1, 1, 28, 28]
    blob = cv2.dnn.blobFromImage(img_28x28, 1.0 / 255.0, (28, 28), (0, 0, 0), swapRB=False, crop=False)
    net.setInput(blob)
    outputs = net.forward()
    prediction = np.argmax(outputs)
    confidence = np.max(cv2.softmax(outputs)) if hasattr(cv2, 'softmax') else np.exp(outputs[0][prediction]) / np.sum(np.exp(outputs[0]))
    return prediction, confidence

if __name__ == "__main__":
    # 这是上次实验默认的 ESP32-S3-CAM IP 地址
    ESP32_IP = "192.168.2.17"
    URL = f"http://{ESP32_IP}/capture"

    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])

    while True:
        try:
            # 抓取一帧 JPEG 图像
            img_resp = urllib.request.urlopen(URL, timeout=5)
            img_np = np.array(bytearray(img_resp.read()), dtype=np.uint8)
            frame = cv2.imdecode(img_np, -1)

            if frame is None:
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

            resized = cv2.resize(thresh, (28, 28), interpolation=cv2.INTER_AREA)

            prediction, confidence = predict_digit(resized)

            display_frame = frame.copy()
            text = f"Digit: {prediction} ({confidence*100:.1f}%)"
            cv2.putText(display_frame, text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.imshow("ESP32-S3 Digital Recognition", display_frame)
            cv2.imshow("Model Input (28x28)", cv2.resize(thresh, (280, 280)))

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        except Exception as e:
            print(f"图像获取或推理异常: {e}")
            break

    cv2.destroyAllWindows()
