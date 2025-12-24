# 二维码示例数据说明

## 目录结构

```
sample_data/
├── clear/              清晰二维码（10张）
├── blurred/            模糊二维码（12张）
├── small/              小尺寸二维码（8张，面积<5%）
├── large/              大尺寸二维码（8张，面积>5%）
├── low_contrast/       低对比度二维码（10张）
└── mixed/              混合场景（15张，多个二维码或复杂背景）
```

## 数据集特点

### 1. clear/ - 清晰二维码
- 高清晰度
- 高对比度
- 适合测试基本检测功能

### 2. blurred/ - 模糊二维码
- 包含轻度、中度、重度模糊
- 用于测试清晰度分类算法
- 文件名包含模糊等级标识

### 3. small/ - 小尺寸二维码
- 二维码占图片面积 < 5%
- 用于测试面积占比检测
- 背景较大

### 4. large/ - 大尺寸二维码
- 二维码占图片面积 > 5%
- 二维码在图片中占主要位置

### 5. low_contrast/ - 低对比度二维码
- 二维码颜色与背景相近
- 用于测试颜色对比度分析
- 检测难度较高

### 6. mixed/ - 混合场景
- 一张图片可能包含多个二维码
- 复杂背景（纹理、渐变等）
- 可能包含模糊效果
- 最接近真实应用场景

## 使用建议

1. **快速测试**: 使用 `clear/` 目录
2. **清晰度测试**: 使用 `blurred/` 目录
3. **面积检测测试**: 使用 `small/` 和 `large/` 目录
4. **对比度测试**: 使用 `low_contrast/` 目录
5. **综合测试**: 使用 `mixed/` 目录
6. **完整测试**: 使用所有目录

## 测试命令示例

```python
from qr_analyzer_basic import QRCodeAnalyzer
import glob

analyzer = QRCodeAnalyzer()

# 测试清晰二维码
clear_images = glob.glob("sample_data/clear/*.jpg")
results = analyzer.batch_analyze(clear_images)
analyzer.save_results(results, "results_clear.json")

# 测试所有类型
all_images = glob.glob("sample_data/**/*.jpg", recursive=True)
all_results = analyzer.batch_analyze(all_images)
report = analyzer.generate_summary_report(all_results)
print(report)
```

## 数据集统计

- 总计: 63张测试图片
- 涵盖6种不同场景
- 多种大小、清晰度、对比度组合

## 注意事项

这些图片是自动生成的测试数据，用于：
- 功能验证
- 性能测试
- 算法调优

在实际应用中，建议使用真实场景的二维码图片进行测试。
