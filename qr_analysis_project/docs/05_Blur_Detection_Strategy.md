# 05. 清晰度检测算法与阈值 (Blur Detection Strategy)

## 1. 核心算法：拉普拉斯方差 (Variance of Laplacian)
这是图像清晰度评价最常用的无参考指标。原理是清晰图像包含更多的边缘和高频分量，其拉普拉斯变换后的方差较大；模糊图像边缘平滑，方差较小。

### 1.1 计算步骤
1. 将检测并裁剪出的二维码区域转换为灰度图。
2. 使用 3x3 拉普拉斯算子进行卷积。
3. 计算卷积结果的方差。

```python
def calculate_blur_score(image_crop):
    gray = cv2.cvtColor(image_crop, cv2.COLOR_BGR2GRAY)
    score = cv2.Laplacian(gray, cv2.CV_64F).var()
    return score
```

## 2. 分级阈值设定 (Thresholding)
根据经验值（需通过实际数据校准），建议如下分级标准：

| 等级 | 描述 (Description) | 拉普拉斯方差范围 (Score) | 备注 |
| :--- | :--- | :--- | :--- |
| **重度模糊** | Severely Blurred | Score < 100 | 细节几乎完全丢失 |
| **中度模糊** | Moderately Blurred | 100 ≤ Score < 300 | 边缘可见但虚化明显 |
| **轻度模糊** | Mildly Blurred | 300 ≤ Score < 800 | 略微不清晰，可扫码 |
| **清晰** | Clear | Score ≥ 800 | 锐利，非常清晰 |

*注：上述阈值基于标准分辨率图片。如果图片分辨率差异巨大，需要先将裁剪区域 Resize 到统一尺寸（如 256x256）后再计算，以保证指标可比性。*

## 3. 替代/辅助算法
- **Tenengrad 梯度函数**：基于 Sobel 算子，对噪声更敏感，但精度可能更高。
- **频域分析 (FFT)**：分析频谱中高频分量的比例。如果高频分量极少，则为模糊。
