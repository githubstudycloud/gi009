# 04. 方案 B：深度学习检测方案 (Deep Learning Approach)

## 1. 概述
本方案采用基于卷积神经网络（CNN）的检测器，如 OpenCV 内置的 WeChatQRCode 引擎或 YOLO 模型。这种方案在处理模糊、倾斜、小尺寸或复杂背景下的二维码时表现远优于传统算法。

## 2. 技术选型：WeChatQRCode
OpenCV Contrib 模块中包含的 WeChatQRCode 是腾讯开源的高性能二维码解码库，基于 CNN，专门针对复杂场景优化。

### 2.1 实现逻辑
```python
import cv2

def detect_qr_wechat(image):
    detector = cv2.wechat_qrcode_WeChatQRCode(
        "detect.prototxt", "detect.caffemodel",
        "sr.prototxt", "sr.caffemodel"
    )
    res, points = detector.detectAndDecode(image)
    if not points:
        return None
    # points 包含二维码四个顶点坐标
    return points
```

## 3. 方案对比优势
- **鲁棒性强**：即使二维码非常模糊（本项目重点关注的对象），CNN 依然有很大概念能定位到它。这对于“重度模糊”的样本至关重要。
- **超分辨率**：WeChatQRCode 包含超分（Super Resolution）模型，能自动增强低分辨率二维码。

## 4. 针对本项目的价值
由于本项目需要分析“重度模糊”的二维码，**必须**使用深度学习方案来定位。如果使用传统方案，重度模糊的图片可能直接被判定为“未检测到二维码”，导致无法输出清晰度评级。因此，本方案是实现完整分类体系的关键。
