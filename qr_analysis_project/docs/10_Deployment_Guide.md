# 10. 实施路线图与部署 (Implementation Roadmap & Deployment)

## 1. 开发阶段规划
1.  **Phase 1: 原型验证 (Day 1-2)**
    - 搭建 Python 环境。
    - 调通 WeChatQRCode 检测。
    - 实现基础的面积计算和拉普拉斯方差计算。
2.  **Phase 2: 算法调优 (Day 3-4)**
    - 收集样本数据。
    - 调整清晰度阈值 (Threshold Calibration)。
    - 优化颜色聚类算法，确保背景提取准确。
3.  **Phase 3: 工程化封装 (Day 5)**
    - 设计 API 接口类。
    - 编写 Dockerfile。
    - 编写单元测试。

## 2. 部署环境
- **Docker 容器化**：
  ```dockerfile
  FROM python:3.9-slim
  
  RUN apt-get update && apt-get install -y \
      libgl1-mesa-glx \
      libglib2.0-0
  
  COPY requirements.txt .
  RUN pip install -r requirements.txt
  
  COPY . /app
  WORKDIR /app
  
  CMD ["python", "app.py"]
  ```

- **硬件要求**：
  - **CPU**: 2 Core+ (推荐 AVX 指令集支持，加速 OpenCV)。
  - **RAM**: 2GB+ (图像处理需要较大内存缓冲区)。
  - **GPU**: 可选，本项目方案主要基于 CPU 优化，非必须。

## 3. 依赖库 (requirements.txt)
```text
opencv-python-headless>=4.5.0
opencv-contrib-python-headless>=4.5.0
numpy
scikit-learn  # 用于 K-Means
scikit-image
flask         # 如果需要 API 服务
```
