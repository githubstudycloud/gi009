# 二维码智能分析系统

一个功能强大的二维码质量分析工具，支持面积检测、清晰度分类和颜色对比度评估。

## 功能特性

- **面积占比检测**：自动计算二维码占图片总面积的比例，判断是否大于5%
- **清晰度分类**：将二维码清晰度分为4个等级
  - 清晰
  - 轻度模糊
  - 中度模糊
  - 重度模糊
- **颜色对比度分析**：评估二维码与背景的颜色差异
  - 与背景颜色不相近
  - 与背景颜色相近
- **批量处理**：支持同时分析多张图片
- **详细报告**：生成完整的分析报告和统计信息

## 目录结构

```
qr-code-analysis/
├── 解决方案文档.md          # 详细的技术方案文档（11种方案）
├── qr_analyzer_basic.py      # 基础实现示例代码
├── requirements.txt          # Python依赖包
├── README.md                 # 本文件
└── examples/                 # 示例图片（需自行添加）
    ├── example_qr_code.jpg
    ├── image1.jpg
    └── image2.jpg
```

## 安装

### 1. 克隆或下载项目

```bash
cd qr-code-analysis
```

### 2. 创建虚拟环境（推荐）

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

#### 基础版本（方案1）
```bash
pip install opencv-python numpy pyzbar Pillow
```

#### 完整版本（所有方案）
```bash
pip install -r requirements.txt
```

### 4. 安装系统依赖

#### Windows
- 下载并安装 [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
- pyzbar 需要 zbar DLL，可以从 [这里](http://zbar.sourceforge.net/) 下载

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install libzbar0
```

#### macOS
```bash
brew install zbar
```

## 快速开始

### 基础用法

```python
from qr_analyzer_basic import QRCodeAnalyzer

# 创建分析器
analyzer = QRCodeAnalyzer()

# 分析单张图片
result = analyzer.analyze_image("example_qr_code.jpg")

# 打印结果
for qr in result:
    print(f"面积占比: {qr['area_ratio_percent']}%")
    print(f"大于5%: {qr['area_larger_than_5_percent']}")
    print(f"清晰度: {qr['clarity_class']}")
    print(f"颜色对比: {qr['color_contrast_class']}")
```

### 批量分析

```python
# 准备图片列表
image_list = [
    "image1.jpg",
    "image2.jpg",
    "image3.jpg"
]

# 批量分析
batch_results = analyzer.batch_analyze(image_list)

# 保存结果
analyzer.save_results(batch_results, "results.json")

# 生成汇总报告
report = analyzer.generate_summary_report(batch_results)
print(report)
```

### 命令行使用

```python
# 运行示例程序
python qr_analyzer_basic.py
```

## 返回数据结构

```json
{
  "qr_data": "https://example.com",
  "qr_type": "QRCODE",
  "bbox": {
    "x": 100,
    "y": 150,
    "width": 200,
    "height": 200
  },
  "area_ratio_percent": 7.5,
  "area_larger_than_5_percent": true,
  "qr_area_pixels": 40000,
  "total_area_pixels": 533333,
  "clarity_class": "清晰",
  "clarity_level": 1,
  "clarity_score": 650.23,
  "sobel_score": 45.67,
  "color_contrast_class": "与背景颜色不相近",
  "has_good_contrast": true,
  "contrast_score": 78.45,
  "gray_contrast": 85.3,
  "rgb_contrast": 92.1,
  "hsv_contrast": 58.7
}
```

## 技术方案

本项目提供了**11种不同的技术实现方案**，详见 `解决方案文档.md`：

1. **OpenCV + pyzbar 基础方案** ⭐ 当前实现
2. **YOLOv8 深度学习检测方案**
3. **传统计算机视觉 + 形态学分析**
4. **WeChat OpenCV 专用检测器**
5. **机器学习 + 多特征融合**
6. **CNN端到端深度学习方案**
7. **轻量级边缘计算方案**
8. **多模型集成方案**
9. **基于质量评估算法的方案**
10. **云端API方案**
11. **Vision Transformer方案**

### 方案选择建议

| 场景 | 推荐方案 |
|------|----------|
| 快速原型/POC | 方案1 或 方案10 |
| 产品级应用 | 方案2 或 方案4 |
| 移动端/嵌入式 | 方案7 |
| 最高准确率 | 方案8（集成） |
| 资源受限 | 方案1 或 方案3 |

## 参数调优

### 清晰度阈值

在 `QRCodeAnalyzer` 类中修改：

```python
self.clarity_thresholds = {
    'clear': 500,           # 清晰（可调整）
    'slight_blur': 200,     # 轻度模糊
    'medium_blur': 50       # 中度模糊
}
```

### 对比度阈值

```python
self.contrast_threshold = 50  # 调整此值
```

建议根据实际数据集进行校准。

## 性能优化建议

1. **批量处理**：使用 `batch_analyze()` 而不是循环调用 `analyze_image()`
2. **图像预处理**：降低图像分辨率可以提高处理速度
3. **多线程/多进程**：对于大量图片，可使用并行处理
4. **GPU加速**：深度学习方案可使用GPU加速（需安装 `torch+cuda`）

## 常见问题

### Q1: pyzbar 无法检测到二维码

**A:** 可能原因：
- 二维码太小或太模糊
- 图像质量差
- zbar库未正确安装

解决方案：
- 尝试提高图像分辨率
- 使用其他方案（如方案2 YOLOv8）
- 检查系统依赖是否安装完整

### Q2: 清晰度分类不准确

**A:** 建议：
- 收集真实数据样本
- 调整 `clarity_thresholds` 阈值
- 使用方案5（机器学习）或方案6（深度学习）

### Q3: 如何处理旋转的二维码

**A:**
- pyzbar 支持任意角度旋转的二维码检测
- 如果检测失败，可尝试图像旋转预处理

### Q4: 性能太慢怎么办

**A:**
- 使用方案7（轻量级边缘计算）
- 降低图像分辨率
- 使用GPU加速（深度学习方案）
- 考虑使用云端API（方案10）

## 高级功能

### 自定义分析指标

```python
class CustomQRCodeAnalyzer(QRCodeAnalyzer):
    def _assess_clarity(self, gray, qr):
        # 自定义清晰度评估逻辑
        result = super()._assess_clarity(gray, qr)
        # 添加额外的评估指标
        return result
```

### 集成到Web服务

```python
from flask import Flask, request, jsonify

app = Flask(__name__)
analyzer = QRCodeAnalyzer()

@app.route('/analyze', methods=['POST'])
def analyze():
    file = request.files['image']
    file.save('temp.jpg')
    result = analyzer.analyze_image('temp.jpg')
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
```

## 测试

运行测试：

```bash
pytest tests/
```

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交 Issue。

## 更新日志

### v1.0.0 (2024-12-24)
- 初始版本发布
- 实现基础分析功能
- 提供11种技术方案文档

## 参考资料

- [OpenCV Documentation](https://docs.opencv.org/)
- [pyzbar Documentation](https://pypi.org/project/pyzbar/)
- [QR Code Specification](https://www.qrcode.com/en/about/standards.html)
- [Image Quality Assessment](https://en.wikipedia.org/wiki/Image_quality)

## 致谢

感谢所有开源项目的贡献者！
