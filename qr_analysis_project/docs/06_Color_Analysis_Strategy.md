# 06. 颜色对比度分析策略 (Color Analysis Strategy)

## 1. 目标
判断二维码颜色与背景颜色是否相近（Color Similarity）。

## 2. 分析步骤

### 2.1 区域采样
- **前景 (Foreground)**：二维码中心的采样点，或通过二值化掩膜（Mask）提取深色像素区域。
- **背景 (Background)**：二维码边界框向外扩展 10% 的区域，或者二维码内部的浅色像素区域。

### 2.2 颜色空间转换
RGB 空间不符合人类视觉感知，建议转换到 **Lab 颜色空间** (CIELAB)。
- **L**: 亮度
- **a**: 红绿分量
- **b**: 黄蓝分量

### 2.3 提取主色
使用 K-Means 聚类算法将区域内的颜色聚类为 2 类（前景与背景）。
```python
def get_dominant_colors(roi, k=2):
    pixels = roi.reshape((-1, 3))
    pixels = np.float32(pixels)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    return centers # 返回两个主色中心
```

### 2.4 色差计算 (Delta E)
计算两个主色中心在 Lab 空间下的欧氏距离或 CIE76 色差公式。

$$ \Delta E = \sqrt{(L_1-L_2)^2 + (a_1-a_2)^2 + (b_1-b_2)^2} $$

### 2.5 判定标准
| 分类 | 描述 | 判据 |
| :--- | :--- | :--- |
| **相近 (Similar)** | 对比度低，难以识别 | $\Delta E < 30$ (经验值) |
| **不相近 (Distinct)** | 对比度高，易于识别 | $\Delta E \ge 30$ |

*注：对于黑白二维码，$\Delta E$ 通常极大（>80）；对于深灰配黑，$\Delta E$ 可能小于 20。*
