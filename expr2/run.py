import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

# MNIST CNN
class MNISTModel(nn.Module):
    def __init__(self):
        super(MNISTModel, self).__init__()
        # 第一层卷积：输入 1 通道，输出 16 通道，卷积核 5x5
        self.conv1 = nn.Conv2d(1, 16, kernel_size=5, stride=1, padding=2)
        self.relu1 = nn.ReLU()
        self.pool1 = nn.MaxPool2d(kernel_size=2, stride=2) # 输出 14x14
        
        # 第二层卷积：输入 16 通道，输出 32 通道，卷积核 5x5
        self.conv2 = nn.Conv2d(16, 32, kernel_size=5, stride=1, padding=2)
        self.relu2 = nn.ReLU()
        self.pool2 = nn.MaxPool2d(kernel_size=2, stride=2) # 输出 7x7
        
        # 全连接分类层：32 * 7 * 7 = 1568 -> 10 个分类
        self.fc1 = nn.Linear(32 * 7 * 7, 128)
        self.relu3 = nn.ReLU()
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = self.pool1(self.relu1(self.conv1(x)))
        x = self.pool2(self.relu2(self.conv2(x)))
        x = x.view(x.size(0), -1)
        x = self.relu3(self.fc1(x))
        x = self.fc2(x)
        return x

# MNIST 数据集
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])

train_dataset = datasets.MNIST(root='./data', train=True, download=True, transform=transform)
train_loader = DataLoader(dataset=train_dataset, batch_size=64, shuffle=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = MNISTModel().to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

model.train()
for epoch in range(3):
    running_loss = 0.0
    for i, (images, labels) in enumerate(train_loader):
        images, labels = images.to(device), labels.to(device)
        
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item()
    print(f"Epoch [{epoch+1}/3], Loss: {running_loss / len(train_loader):.4f}")

model.eval()
dummy_input = torch.randn(1, 1, 28, 28, device=device)

onnx_filename = "mnist-12.onnx"
torch.onnx.export(
    model,
    dummy_input,
    onnx_filename,
    export_params=True,
    opset_version=12,
    do_constant_folding=True,
    input_names=['Input3'],
    output_names=['Plus214_Output_0'],
    dynamic_axes={
        'Input3': {0: 'batch_size'},
        'Plus214_Output_0': {0: 'batch_size'}
    }
)

print(f"导出 ONNX 模型: {onnx_filename}")