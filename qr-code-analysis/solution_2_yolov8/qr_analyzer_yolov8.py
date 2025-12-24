"""
二维码智能分析系统 - 方案2: YOLOv8深度学习检测

使用YOLOv8目标检测模型进行二维码检测和分析
优势：高准确率，适合复杂场景
"""

import sys
import io

# 设置标准输出编码为UTF-8（Windows兼容）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import cv2
import numpy as np
from ultralytics import YOLO
from pyzbar import pyzbar
import os
from typing import List, Dict, Any, Optional


class QRCodeAnalyzerYOLOv8:
    """基于YOLOv8的二维码分析器"""

    def __init__(self, model_path: str = None, confidence_threshold: float = 0.5):
        """
        初始化分析器

        Args:
            model_path: YOLOv8模型路径，如果为None则使用预训练模型
            confidence_threshold: 检测置信度阈值
        """
        # 清晰度阈值
        self.clarity_thresholds = {
            'clear': 500,           # 清晰
            'slight_blur': 200,     # 轻度模糊
            'medium_blur': 50       # 中度模糊
        }

        # 对比度阈值
        self.contrast_threshold = 50

        # 置信度阈值
        self.confidence_threshold = confidence_threshold

        # 加载YOLOv8模型
        if model_path and os.path.exists(model_path):
            print(f"加载自定义YOLOv8模型: {model_path}")
            self.model = YOLO(model_path)
        else:
            print("使用YOLOv8预训练模型（yolov8n.pt）")
            print("注意: 预训练模型未专门训练二维码，建议使用自定义训练的模型")
            self.model = YOLO('yolov8n.pt')

    def detect_qr_with_yolo(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        使用YOLOv8检测二维码位置

        Args:
            image: 输入图像（BGR格式）

        Returns:
            检测到的二维码边界框列表
        """
        results = self.model(image, conf=self.confidence_threshold)

        qr_detections = []

        for result in results:
            boxes = result.boxes
            for box in boxes:
                # 获取边界框坐标
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])

                # 注意: 如果是自定义训练的模型，需要确保class_id对应二维码类别
                # 预训练模型可能无法直接识别二维码，这里作为演示

                qr_detections.append({
                    'bbox': {
                        'x': int(x1),
                        'y': int(y1),
                        'width': int(x2 - x1),
                        'height': int(y2 - y1)
                    },
                    'confidence': confidence,
                    'class_id': class_id
                })

        return qr_detections

    def detect_qr_with_pyzbar(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        使用pyzbar检测二维码（备用方法）

        Args:
            image: 输入图像（BGR格式）

        Returns:
            检测到的二维码信息列表
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        qr_codes = pyzbar.decode(gray)

        detections = []
        for qr in qr_codes:
            x, y, w, h = qr.rect
            detections.append({
                'bbox': {'x': x, 'y': y, 'width': w, 'height': h},
                'data': qr.data.decode('utf-8', errors='ignore'),
                'type': qr.type
            })

        return detections

    def calculate_area_ratio(self, bbox: Dict[str, int], image_shape: tuple) -> Dict[str, Any]:
        """
        计算二维码面积占比

        Args:
            bbox: 边界框字典
            image_shape: 图像形状 (height, width, channels)

        Returns:
            面积信息字典
        """
        image_height, image_width = image_shape[:2]
        image_area = image_height * image_width

        qr_area = bbox['width'] * bbox['height']
        ratio = (qr_area / image_area) * 100

        return {
            'qr_area_pixels': qr_area,
            'image_area_pixels': image_area,
            'area_ratio_percent': ratio,
            'area_larger_than_5_percent': ratio > 5.0
        }

    def calculate_clarity(self, image: np.ndarray, bbox: Dict[str, int]) -> Dict[str, Any]:
        """
        计算二维码区域的清晰度

        使用多种方法综合评估：
        1. Laplacian方差（边缘锐度）
        2. Sobel梯度强度
        3. 高频能量比例

        Args:
            image: 输入图像
            bbox: 二维码边界框

        Returns:
            清晰度信息字典
        """
        x, y, w, h = bbox['x'], bbox['y'], bbox['width'], bbox['height']

        # 确保坐标在有效范围内
        h_img, w_img = image.shape[:2]
        x1 = max(0, x)
        y1 = max(0, y)
        x2 = min(w_img, x + w)
        y2 = min(h_img, y + h)

        # 提取二维码区域
        qr_region = image[y1:y2, x1:x2]

        if qr_region.size == 0:
            return {
                'clarity_score': 0,
                'clarity_level': 3,
                'clarity_class': '重度模糊',
                'method': 'invalid_region'
            }

        # 转换为灰度图
        if len(qr_region.shape) == 3:
            gray = cv2.cvtColor(qr_region, cv2.COLOR_BGR2GRAY)
        else:
            gray = qr_region

        # 方法1: Laplacian方差
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        laplacian_var = laplacian.var()

        # 方法2: Sobel梯度
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        sobel_magnitude = np.sqrt(sobelx**2 + sobely**2)
        sobel_mean = sobel_magnitude.mean()

        # 方法3: 频域分析（高频能量）
        f_transform = np.fft.fft2(gray)
        f_shift = np.fft.fftshift(f_transform)
        magnitude_spectrum = np.abs(f_shift)

        # 计算高频能量占比
        rows, cols = gray.shape
        crow, ccol = rows // 2, cols // 2
        mask = np.ones((rows, cols), dtype=np.uint8)
        r = min(rows, cols) // 4
        center = (crow, ccol)
        cv2.circle(mask, center, r, 0, -1)

        high_freq_energy = np.sum(magnitude_spectrum * mask)
        total_energy = np.sum(magnitude_spectrum)
        high_freq_ratio = high_freq_energy / (total_energy + 1e-6)

        # 综合评分（加权平均）
        clarity_score = (
            laplacian_var * 0.5 +
            sobel_mean * 2.0 +
            high_freq_ratio * 500
        )

        # 分类
        if clarity_score > self.clarity_thresholds['clear']:
            clarity_level = 0
            clarity_class = '清晰'
        elif clarity_score > self.clarity_thresholds['slight_blur']:
            clarity_level = 1
            clarity_class = '轻度模糊'
        elif clarity_score > self.clarity_thresholds['medium_blur']:
            clarity_level = 2
            clarity_class = '中度模糊'
        else:
            clarity_level = 3
            clarity_class = '重度模糊'

        return {
            'clarity_score': float(clarity_score),
            'clarity_level': clarity_level,
            'clarity_class': clarity_class,
            'laplacian_variance': float(laplacian_var),
            'sobel_mean': float(sobel_mean),
            'high_freq_ratio': float(high_freq_ratio),
            'method': 'multi_method'
        }

    def calculate_color_contrast(self, image: np.ndarray, bbox: Dict[str, int]) -> Dict[str, Any]:
        """
        计算二维码与背景的颜色对比度

        Args:
            image: 输入图像
            bbox: 二维码边界框

        Returns:
            对比度信息字典
        """
        x, y, w, h = bbox['x'], bbox['y'], bbox['width'], bbox['height']

        h_img, w_img = image.shape[:2]
        x1 = max(0, x)
        y1 = max(0, y)
        x2 = min(w_img, x + w)
        y2 = min(h_img, y + h)

        # 提取二维码区域
        qr_region = image[y1:y2, x1:x2]

        if qr_region.size == 0:
            return {
                'contrast_score': 0,
                'has_good_contrast': False,
                'color_contrast_class': '与背景颜色相近'
            }

        # 提取背景区域（二维码周围区域）
        padding = 20
        bg_x1 = max(0, x - padding)
        bg_y1 = max(0, y - padding)
        bg_x2 = min(w_img, x + w + padding)
        bg_y2 = min(h_img, y + h + padding)

        bg_region = image[bg_y1:bg_y2, bg_x1:bg_x2]

        # 创建mask排除二维码区域
        mask = np.ones(bg_region.shape[:2], dtype=np.uint8)
        qr_mask_x1 = x1 - bg_x1
        qr_mask_y1 = y1 - bg_y1
        qr_mask_x2 = x2 - bg_x1
        qr_mask_y2 = y2 - bg_y1
        mask[qr_mask_y1:qr_mask_y2, qr_mask_x1:qr_mask_x2] = 0

        # 计算二维码和背景的颜色特征
        gray_qr = cv2.cvtColor(qr_region, cv2.COLOR_BGR2GRAY)
        gray_bg = cv2.cvtColor(bg_region, cv2.COLOR_BGR2GRAY)

        qr_mean = gray_qr.mean()
        bg_mean = cv2.mean(gray_bg, mask=mask)[0]

        # 灰度对比度
        gray_contrast = abs(qr_mean - bg_mean)

        # RGB对比度
        qr_rgb = cv2.mean(qr_region)[:3]
        bg_rgb = cv2.mean(bg_region, mask=mask)[:3]
        rgb_contrast = np.linalg.norm(np.array(qr_rgb) - np.array(bg_rgb))

        # HSV对比度
        hsv_qr = cv2.cvtColor(qr_region, cv2.COLOR_BGR2HSV)
        hsv_bg = cv2.cvtColor(bg_region, cv2.COLOR_BGR2HSV)
        hsv_qr_mean = cv2.mean(hsv_qr)[:3]
        hsv_bg_mean = cv2.mean(hsv_bg, mask=mask)[:3]
        hsv_contrast = abs(hsv_qr_mean[2] - hsv_bg_mean[2])  # V通道对比度

        # 综合评分
        contrast_score = (gray_contrast + rgb_contrast / 3 + hsv_contrast) / 3

        has_good_contrast = contrast_score > self.contrast_threshold

        return {
            'contrast_score': float(contrast_score),
            'has_good_contrast': has_good_contrast,
            'color_contrast_class': '与背景颜色不相近' if has_good_contrast else '与背景颜色相近',
            'gray_contrast': float(gray_contrast),
            'rgb_contrast': float(rgb_contrast),
            'hsv_contrast': float(hsv_contrast)
        }

    def analyze_image(self, image_path: str, use_yolo: bool = True) -> List[Dict[str, Any]]:
        """
        分析图像中的二维码

        Args:
            image_path: 图像文件路径
            use_yolo: 是否使用YOLO检测（True）或使用pyzbar（False）

        Returns:
            分析结果列表
        """
        # 读取图像
        image = cv2.imread(image_path)

        if image is None:
            print(f"错误: 无法读取图像 {image_path}")
            return []

        # 检测二维码
        if use_yolo:
            detections = self.detect_qr_with_yolo(image)
        else:
            detections = self.detect_qr_with_pyzbar(image)

        if not detections:
            # 如果YOLO没检测到，尝试用pyzbar
            if use_yolo:
                print("YOLOv8未检测到二维码，尝试使用pyzbar...")
                detections = self.detect_qr_with_pyzbar(image)

        # 分析每个检测到的二维码
        results = []

        for detection in detections:
            bbox = detection['bbox']

            # 计算面积占比
            area_info = self.calculate_area_ratio(bbox, image.shape)

            # 计算清晰度
            clarity_info = self.calculate_clarity(image, bbox)

            # 计算颜色对比度
            contrast_info = self.calculate_color_contrast(image, bbox)

            # 尝试解码二维码内容
            qr_data = detection.get('data', '')
            if not qr_data:
                # 如果没有数据，尝试用pyzbar解码该区域
                x, y, w, h = bbox['x'], bbox['y'], bbox['width'], bbox['height']
                qr_region = image[y:y+h, x:x+w]
                gray_region = cv2.cvtColor(qr_region, cv2.COLOR_BGR2GRAY)
                decoded = pyzbar.decode(gray_region)
                if decoded:
                    qr_data = decoded[0].data.decode('utf-8', errors='ignore')

            # 组合结果
            result = {
                'image_path': image_path,
                'bbox': bbox,
                'detection_method': 'yolov8' if use_yolo else 'pyzbar',
                'qr_data': qr_data,
                **area_info,
                **clarity_info,
                **contrast_info
            }

            if 'confidence' in detection:
                result['detection_confidence'] = detection['confidence']

            results.append(result)

        return results

    def batch_analyze(self, image_paths: List[str], use_yolo: bool = True) -> Dict[str, List[Dict[str, Any]]]:
        """
        批量分析多张图像

        Args:
            image_paths: 图像路径列表
            use_yolo: 是否使用YOLO检测

        Returns:
            字典，键为图像路径，值为分析结果列表
        """
        results = {}

        for i, image_path in enumerate(image_paths, 1):
            print(f"分析第 {i}/{len(image_paths)} 张图片: {image_path}")

            try:
                result = self.analyze_image(image_path, use_yolo=use_yolo)
                results[image_path] = result
            except Exception as e:
                print(f"分析失败: {e}")
                results[image_path] = []

        return results

    def visualize_results(self, image_path: str, results: List[Dict[str, Any]],
                         output_path: Optional[str] = None):
        """
        可视化分析结果

        Args:
            image_path: 原始图像路径
            results: 分析结果
            output_path: 输出图像路径（可选）
        """
        image = cv2.imread(image_path)

        if image is None:
            print(f"无法读取图像: {image_path}")
            return

        for i, result in enumerate(results):
            bbox = result['bbox']
            x, y, w, h = bbox['x'], bbox['y'], bbox['width'], bbox['height']

            # 根据清晰度选择颜色
            clarity_level = result.get('clarity_level', 0)
            if clarity_level == 0:
                color = (0, 255, 0)  # 绿色 - 清晰
            elif clarity_level == 1:
                color = (0, 255, 255)  # 黄色 - 轻度模糊
            elif clarity_level == 2:
                color = (0, 165, 255)  # 橙色 - 中度模糊
            else:
                color = (0, 0, 255)  # 红色 - 重度模糊

            # 绘制边界框
            cv2.rectangle(image, (x, y), (x + w, y + h), color, 3)

            # 添加文本标签
            label = f"QR#{i+1} {result.get('clarity_class', '')}"
            cv2.putText(image, label, (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # 保存或显示
        if output_path:
            cv2.imwrite(output_path, image)
            print(f"结果已保存: {output_path}")
        else:
            cv2.imshow("QR Code Analysis", image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()


def main():
    """主函数 - 使用示例"""
    print("=" * 60)
    print("二维码智能分析系统 - YOLOv8方案")
    print("=" * 60)

    # 创建分析器（使用pyzbar作为fallback）
    analyzer = QRCodeAnalyzerYOLOv8()

    # 测试单张图片
    test_image = "../sample_data/clear/clear_qr_1.jpg"

    if os.path.exists(test_image):
        print(f"\n分析测试图片: {test_image}")

        # 使用pyzbar检测（因为未训练专门的YOLOv8模型）
        results = analyzer.analyze_image(test_image, use_yolo=False)

        if results:
            for i, result in enumerate(results, 1):
                print(f"\n二维码 #{i}:")
                print(f"  位置: ({result['bbox']['x']}, {result['bbox']['y']})")
                print(f"  尺寸: {result['bbox']['width']} x {result['bbox']['height']}")
                print(f"  面积占比: {result['area_ratio_percent']:.2f}%")
                print(f"  大于5%: {'是' if result['area_larger_than_5_percent'] else '否'}")
                print(f"  清晰度: {result['clarity_class']} (评分: {result['clarity_score']:.2f})")
                print(f"  颜色对比: {result['color_contrast_class']}")
                print(f"  检测方法: {result['detection_method']}")
        else:
            print("未检测到二维码")
    else:
        print(f"测试图片不存在: {test_image}")
        print("请确保已生成示例数据")


if __name__ == "__main__":
    main()
