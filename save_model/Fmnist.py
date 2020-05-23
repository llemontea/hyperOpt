import torch.nn as nn

class mnistNet(nn.Module):
    def __init__(self):
        super(mnistNet, self).__init__()
        self.conv2d = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size = 5),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2)
        )
        self.fc=nn.Sequential(
            nn.Linear(64 * 3 * 3, 84),
            nn.Dropout2d(0.5),
            nn.Linear(84, 10)
        )

    def forward(self, img):
        features = self.conv2d(img)
        outputs = self.fc(features.view(features.shape[0], -1))
        return outputs

net = mnistNet()