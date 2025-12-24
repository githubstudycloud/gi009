# 03. 方案 A：传统计算机视觉方案 (Traditional CV Approach)

## 1. 概述
本方案使用经典的图像处理技术和开源解码库（如 Pyzbar 或 ZBar）进行二维码检测。这种方法速度快，无需GPU，依赖少，适合在普通CPU服务器或边缘设备上运行。

## 2. 技术实现细节

### 2.1 检测与定位
- **库**：`pyzbar`
- **原理**：基于寻找定位图案（Finder Patterns）的几何特征。
- **代码片段示意**：
  ```python
  from pyzbar.pyzbar import decode
  import cv2
  
  def detect_qr_traditional(image):
      decoded_objects = decode(image)
      if not decoded_objects:
          return None
      # 获取第一个检测到的二维码
      obj = decoded_objects[0]
      rect = obj.rect # (x, y, w, h)
      return rect
  ```

### 2.2 优势
- **轻量级**：安装包小，内存占用低。
- **速度快**：对于清晰、标准的二维码，检测速度极快（毫秒级）。
- **成熟稳定**：经过多年验证，标准场景下可靠性高。

### 2.3 局限性
- **抗干扰能力弱**：对于严重模糊、遮挡、变形或艺术化的二维码，检测率可能较低。
- **依赖清晰度**：如果二维码本身很模糊，可能直接无法检测到位置，从而无法进行后续的“模糊度分析”（这是一个悖论：太模糊导致检测不到，检测不到就无法分析模糊度）。

### 2.4 针对本项目的适用性
适合作为**初筛方案**。如果 Pyzbar 能检测到，说明二维码质量尚可；如果检测不到，可能需要回退到基于深度学习的方案来强制提取区域。
