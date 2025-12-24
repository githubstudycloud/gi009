# 08. API 接口设计与数据结构 (API Design & Data Schema)

## 1. 接口定义
假设服务以 RESTful API 形式提供。

- **Endpoint**: `POST /api/v1/analyze/qr`
- **Content-Type**: `multipart/form-data`
- **Body**: `file` (Image binary)

## 2. 响应结构 (JSON)

```json
{
  "status": "success",
  "meta": {
    "image_width": 1920,
    "image_height": 1080,
    "image_area": 2073600
  },
  "data": {
    "detected": true,
    "count": 1,
    "primary_qr": {
      "location": {
        "polygon": [[100, 100], [400, 100], [400, 400], [100, 400]],
        "area_pixels": 90000,
        "area_ratio": 0.0434,
        "area_check": {
          "passed": false,
          "threshold": 0.05,
          "message": "QR code area is too small (4.34% < 5%)"
        }
      },
      "clarity": {
        "score": 150.5,
        "class": "Moderately Blurred",
        "level_code": 3  // 1:Clear, 2:Mild, 3:Moderate, 4:Severe
      },
      "color": {
        "contrast_delta_e": 85.2,
        "class": "High Contrast", // 与背景不相近
        "is_similar_to_bg": false,
        "dominant_color_fg": [10, 10, 10], // RGB
        "dominant_color_bg": [250, 250, 250] // RGB
      }
    }
  }
}
```

## 3. 错误响应
当未检测到二维码时：
```json
{
  "status": "success", // 请求本身成功，只是业务上没找到
  "data": {
    "detected": false,
    "message": "No QR code detected in the image."
  }
}
```
