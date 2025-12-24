"""
二维码智能分析系统 - 方案8: 多模型集成

集成多种检测方法，通过投票、加权融合等策略提高准确率和鲁棒性
"""

import sys
import io

# 设置标准输出编码为UTF-8（Windows兼容）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import cv2
import numpy as np
from pyzbar import pyzbar
from typing import List, Dict, Any, Optional, Tuple
import os


class QRCodeAnalyzerEnsemble:
    """基于多模型集成的二维码分析器"""

    def __init__(self,
                 use_pyzbar: bool = True,
                 use_opencv_detector: bool = True,
                 use_wechat_detector: bool = True,
                 fusion_strategy: str = 'voting',
                 min_votes: int = 2):
        """
        初始化集成分析器

        Args:
            use_pyzbar: 使用pyzbar检测器
            use_opencv_detector: 使用OpenCV QRCode检测器
            use_wechat_detector: 使用WeChat QRCode检测器
            fusion_strategy: 融合策略 ('voting', 'weighted', 'union', 'intersection')
            min_votes: 最小投票数（voting策略）
        """
        # 清晰度阈值
        self.clarity_thresholds = {
            'clear': 500,
            'slight_blur': 200,
            'medium_blur': 50
        }

        # 对比度阈值
        self.contrast_threshold = 50

        # 检测器配置
        self.use_pyzbar = use_pyzbar
        self.use_opencv_detector = use_opencv_detector
        self.use_wechat_detector = use_wechat_detector

        # 融合策略
        self.fusion_strategy = fusion_strategy
        self.min_votes = min_votes

        # 初始化检测器
        self.detectors = {}

        if use_opencv_detector:
            try:
                self.detectors['opencv'] = cv2.QRCodeDetector()
                print("✓ OpenCV QRCode检测器已加载")
            except Exception as e:
                print(f"✗ OpenCV QRCode检测器加载失败: {e}")

        if use_wechat_detector:
            try:
                # WeChat QRCode检测器需要模型文件
                # 从 https://github.com/WeChatCV/opencv_3rdparty 下载
                model_dir = "./wechat_qrcode_models"
                if os.path.exists(model_dir):
                    detector_proto = os.path.join(model_dir, "detect.prototxt")
                    detector_model = os.path.join(model_dir, "detect.caffemodel")
                    sr_proto = os.path.join(model_dir, "sr.prototxt")
                    sr_model = os.path.join(model_dir, "sr.caffemodel")

                    self.detectors['wechat'] = cv2.wechat_qrcode_WeChatQRCode(
                        detector_proto, detector_model, sr_proto, sr_model
                    )
                    print("✓ WeChat QRCode检测器已加载")
                else:
                    print(f"✗ WeChat模型文件不存在: {model_dir}")
            except Exception as e:
                print(f"✗ WeChat QRCode检测器加载失败: {e}")

        if use_pyzbar:
            print("✓ pyzbar检测器已启用")

    def detect_with_pyzbar(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """使用pyzbar检测二维码"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            qr_codes = pyzbar.decode(gray)

            detections = []
            for qr in qr_codes:
                x, y, w, h = qr.rect
                detections.append({
                    'bbox': {'x': x, 'y': y, 'width': w, 'height': h},
                    'data': qr.data.decode('utf-8', errors='ignore'),
                    'type': qr.type,
                    'detector': 'pyzbar',
                    'confidence': 1.0
                })

            return detections
        except Exception as e:
            print(f"pyzbar检测失败: {e}")
            return []

    def detect_with_opencv(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """使用OpenCV检测二维码"""
        if 'opencv' not in self.detectors:
            return []

        try:
            detector = self.detectors['opencv']
            data, points, _ = detector.detectAndDecode(image)

            detections = []
            if data and points is not None:
                points = points[0].astype(int)
                x = int(points[:, 0].min())
                y = int(points[:, 1].min())
                w = int(points[:, 0].max() - x)
                h = int(points[:, 1].max() - y)

                detections.append({
                    'bbox': {'x': x, 'y': y, 'width': w, 'height': h},
                    'data': data,
                    'type': 'QRCODE',
                    'detector': 'opencv',
                    'confidence': 0.9,
                    'points': points.tolist()
                })

            return detections
        except Exception as e:
            print(f"OpenCV检测失败: {e}")
            return []

    def detect_with_wechat(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """使用WeChat检测器检测二维码"""
        if 'wechat' not in self.detectors:
            return []

        try:
            detector = self.detectors['wechat']
            data_list, points_list = detector.detectAndDecode(image)

            detections = []
            for data, points in zip(data_list, points_list):
                if data:
                    points = points.reshape(-1, 2).astype(int)
                    x = int(points[:, 0].min())
                    y = int(points[:, 1].min())
                    w = int(points[:, 0].max() - x)
                    h = int(points[:, 1].max() - y)

                    detections.append({
                        'bbox': {'x': x, 'y': y, 'width': w, 'height': h},
                        'data': data,
                        'type': 'QRCODE',
                        'detector': 'wechat',
                        'confidence': 0.95,
                        'points': points.tolist()
                    })

            return detections
        except Exception as e:
            print(f"WeChat检测失败: {e}")
            return []

    def detect_with_contours(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """使用传统计算机视觉方法检测二维码区域"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image

            # 二值化
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # 形态学操作
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
            closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)

            # 查找轮廓
            contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            detections = []
            for contour in contours:
                area = cv2.contourArea(contour)

                # 过滤小面积
                if area < 1000:
                    continue

                # 计算边界框
                x, y, w, h = cv2.boundingRect(contour)

                # 检查是否接近正方形（二维码特征）
                aspect_ratio = float(w) / h
                if 0.7 < aspect_ratio < 1.3:  # 近似正方形
                    # 验证是否真的是二维码
                    roi = gray[y:y+h, x:x+w]
                    if self._validate_qr_region(roi):
                        detections.append({
                            'bbox': {'x': x, 'y': y, 'width': w, 'height': h},
                            'data': '',
                            'type': 'QRCODE',
                            'detector': 'contour',
                            'confidence': 0.7
                        })

            return detections
        except Exception as e:
            print(f"轮廓检测失败: {e}")
            return []

    def _validate_qr_region(self, roi: np.ndarray) -> bool:
        """验证区域是否可能是二维码"""
        if roi.size == 0:
            return False

        # 检查边缘密度（二维码边缘丰富）
        edges = cv2.Canny(roi, 50, 150)
        edge_density = np.count_nonzero(edges) / edges.size

        # 检查颜色分布（二维码黑白分布较均匀）
        _, binary = cv2.threshold(roi, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        black_ratio = np.count_nonzero(binary == 0) / binary.size

        # 二维码特征：边缘密度高，黑白比例接近
        return edge_density > 0.1 and 0.3 < black_ratio < 0.7

    def calculate_iou(self, bbox1: Dict[str, int], bbox2: Dict[str, int]) -> float:
        """计算两个边界框的IoU（交并比）"""
        x1_1, y1_1 = bbox1['x'], bbox1['y']
        x2_1, y2_1 = x1_1 + bbox1['width'], y1_1 + bbox1['height']

        x1_2, y1_2 = bbox2['x'], bbox2['y']
        x2_2, y2_2 = x1_2 + bbox2['width'], y1_2 + bbox2['height']

        # 计算交集
        x_left = max(x1_1, x1_2)
        y_top = max(y1_1, y1_2)
        x_right = min(x2_1, x2_2)
        y_bottom = min(y2_1, y2_2)

        if x_right < x_left or y_bottom < y_top:
            return 0.0

        intersection = (x_right - x_left) * (y_bottom - y_top)

        # 计算并集
        area1 = bbox1['width'] * bbox1['height']
        area2 = bbox2['width'] * bbox2['height']
        union = area1 + area2 - intersection

        return intersection / union if union > 0 else 0.0

    def fuse_detections(self, all_detections: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        融合多个检测器的结果

        Args:
            all_detections: 所有检测器的检测结果列表

        Returns:
            融合后的检测结果
        """
        if not all_detections:
            return []

        # 展平所有检测结果
        flat_detections = []
        for detections in all_detections:
            flat_detections.extend(detections)

        if not flat_detections:
            return []

        if self.fusion_strategy == 'voting':
            return self._fuse_by_voting(flat_detections)
        elif self.fusion_strategy == 'weighted':
            return self._fuse_by_weighted(flat_detections)
        elif self.fusion_strategy == 'union':
            return self._fuse_by_union(flat_detections)
        elif self.fusion_strategy == 'intersection':
            return self._fuse_by_intersection(flat_detections)
        else:
            return flat_detections

    def _fuse_by_voting(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """投票融合策略"""
        if not detections:
            return []

        # 将相似的检测结果聚类
        clusters = []

        for detection in detections:
            matched = False

            for cluster in clusters:
                # 检查是否与簇中的检测结果相似（IoU > 0.5）
                if self.calculate_iou(detection['bbox'], cluster[0]['bbox']) > 0.5:
                    cluster.append(detection)
                    matched = True
                    break

            if not matched:
                clusters.append([detection])

        # 只保留投票数达到阈值的簇
        fused_results = []

        for cluster in clusters:
            if len(cluster) >= self.min_votes:
                # 取簇中所有检测的平均边界框
                avg_bbox = self._average_bbox([d['bbox'] for d in cluster])

                # 取最高置信度的数据
                best_detection = max(cluster, key=lambda d: d.get('confidence', 0))

                fused_results.append({
                    'bbox': avg_bbox,
                    'data': best_detection['data'],
                    'type': best_detection['type'],
                    'detectors': [d['detector'] for d in cluster],
                    'num_votes': len(cluster),
                    'confidence': sum(d.get('confidence', 0) for d in cluster) / len(cluster),
                    'fusion_method': 'voting'
                })

        return fused_results

    def _fuse_by_weighted(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """加权融合策略"""
        # 检测器权重
        weights = {
            'wechat': 1.0,
            'pyzbar': 0.9,
            'opencv': 0.85,
            'contour': 0.6
        }

        # 聚类相似检测
        clusters = []

        for detection in detections:
            matched = False

            for cluster in clusters:
                if self.calculate_iou(detection['bbox'], cluster[0]['bbox']) > 0.5:
                    cluster.append(detection)
                    matched = True
                    break

            if not matched:
                clusters.append([detection])

        # 加权融合每个簇
        fused_results = []

        for cluster in clusters:
            # 计算加权平均边界框
            total_weight = sum(weights.get(d['detector'], 0.5) for d in cluster)

            weighted_x = sum(d['bbox']['x'] * weights.get(d['detector'], 0.5) for d in cluster) / total_weight
            weighted_y = sum(d['bbox']['y'] * weights.get(d['detector'], 0.5) for d in cluster) / total_weight
            weighted_w = sum(d['bbox']['width'] * weights.get(d['detector'], 0.5) for d in cluster) / total_weight
            weighted_h = sum(d['bbox']['height'] * weights.get(d['detector'], 0.5) for d in cluster) / total_weight

            # 取最高权重检测器的数据
            best_detection = max(cluster, key=lambda d: weights.get(d['detector'], 0.5))

            fused_results.append({
                'bbox': {
                    'x': int(weighted_x),
                    'y': int(weighted_y),
                    'width': int(weighted_w),
                    'height': int(weighted_h)
                },
                'data': best_detection['data'],
                'type': best_detection['type'],
                'detectors': [d['detector'] for d in cluster],
                'confidence': sum(d.get('confidence', 0) * weights.get(d['detector'], 0.5) for d in cluster) / total_weight,
                'fusion_method': 'weighted'
            })

        return fused_results

    def _fuse_by_union(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """并集融合策略 - 保留所有检测"""
        # 去重相似检测
        unique_detections = []

        for detection in detections:
            is_duplicate = False

            for existing in unique_detections:
                if self.calculate_iou(detection['bbox'], existing['bbox']) > 0.7:
                    is_duplicate = True
                    # 保留置信度更高的
                    if detection.get('confidence', 0) > existing.get('confidence', 0):
                        unique_detections.remove(existing)
                        unique_detections.append(detection)
                    break

            if not is_duplicate:
                unique_detections.append(detection)

        for det in unique_detections:
            det['fusion_method'] = 'union'

        return unique_detections

    def _fuse_by_intersection(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """交集融合策略 - 只保留多个检测器都检测到的"""
        if not detections:
            return []

        # 要求至少被所有检测器检测到
        min_required = len([d for d in [self.use_pyzbar, self.use_opencv_detector, self.use_wechat_detector] if d])

        # 聚类
        clusters = []

        for detection in detections:
            matched = False

            for cluster in clusters:
                if self.calculate_iou(detection['bbox'], cluster[0]['bbox']) > 0.5:
                    cluster.append(detection)
                    matched = True
                    break

            if not matched:
                clusters.append([detection])

        # 只保留检测器数量足够的簇
        fused_results = []

        for cluster in clusters:
            unique_detectors = set(d['detector'] for d in cluster)

            if len(unique_detectors) >= min(min_required, self.min_votes):
                avg_bbox = self._average_bbox([d['bbox'] for d in cluster])
                best_detection = max(cluster, key=lambda d: d.get('confidence', 0))

                fused_results.append({
                    'bbox': avg_bbox,
                    'data': best_detection['data'],
                    'type': best_detection['type'],
                    'detectors': list(unique_detectors),
                    'confidence': sum(d.get('confidence', 0) for d in cluster) / len(cluster),
                    'fusion_method': 'intersection'
                })

        return fused_results

    def _average_bbox(self, bboxes: List[Dict[str, int]]) -> Dict[str, int]:
        """计算边界框的平均值"""
        avg_x = int(sum(b['x'] for b in bboxes) / len(bboxes))
        avg_y = int(sum(b['y'] for b in bboxes) / len(bboxes))
        avg_w = int(sum(b['width'] for b in bboxes) / len(bboxes))
        avg_h = int(sum(b['height'] for b in bboxes) / len(bboxes))

        return {'x': avg_x, 'y': avg_y, 'width': avg_w, 'height': avg_h}

    def calculate_area_ratio(self, bbox: Dict[str, int], image_shape: tuple) -> Dict[str, Any]:
        """计算二维码面积占比"""
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
        """计算清晰度"""
        x, y, w, h = bbox['x'], bbox['y'], bbox['width'], bbox['height']

        h_img, w_img = image.shape[:2]
        x1 = max(0, x)
        y1 = max(0, y)
        x2 = min(w_img, x + w)
        y2 = min(h_img, y + h)

        qr_region = image[y1:y2, x1:x2]

        if qr_region.size == 0:
            return {
                'clarity_score': 0,
                'clarity_level': 3,
                'clarity_class': '重度模糊'
            }

        gray = cv2.cvtColor(qr_region, cv2.COLOR_BGR2GRAY) if len(qr_region.shape) == 3 else qr_region

        # Laplacian方差
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        laplacian_var = laplacian.var()

        # 分类
        if laplacian_var > self.clarity_thresholds['clear']:
            clarity_level = 0
            clarity_class = '清晰'
        elif laplacian_var > self.clarity_thresholds['slight_blur']:
            clarity_level = 1
            clarity_class = '轻度模糊'
        elif laplacian_var > self.clarity_thresholds['medium_blur']:
            clarity_level = 2
            clarity_class = '中度模糊'
        else:
            clarity_level = 3
            clarity_class = '重度模糊'

        return {
            'clarity_score': float(laplacian_var),
            'clarity_level': clarity_level,
            'clarity_class': clarity_class
        }

    def calculate_color_contrast(self, image: np.ndarray, bbox: Dict[str, int]) -> Dict[str, Any]:
        """计算颜色对比度"""
        x, y, w, h = bbox['x'], bbox['y'], bbox['width'], bbox['height']

        h_img, w_img = image.shape[:2]
        x1 = max(0, x)
        y1 = max(0, y)
        x2 = min(w_img, x + w)
        y2 = min(h_img, y + h)

        qr_region = image[y1:y2, x1:x2]

        if qr_region.size == 0:
            return {
                'contrast_score': 0,
                'has_good_contrast': False,
                'color_contrast_class': '与背景颜色相近'
            }

        # 背景区域
        padding = 20
        bg_x1 = max(0, x - padding)
        bg_y1 = max(0, y - padding)
        bg_x2 = min(w_img, x + w + padding)
        bg_y2 = min(h_img, y + h + padding)

        bg_region = image[bg_y1:bg_y2, bg_x1:bg_x2]

        # 灰度对比度
        gray_qr = cv2.cvtColor(qr_region, cv2.COLOR_BGR2GRAY)
        gray_bg = cv2.cvtColor(bg_region, cv2.COLOR_BGR2GRAY)

        qr_mean = gray_qr.mean()
        bg_mean = gray_bg.mean()

        contrast_score = abs(qr_mean - bg_mean)
        has_good_contrast = contrast_score > self.contrast_threshold

        return {
            'contrast_score': float(contrast_score),
            'has_good_contrast': has_good_contrast,
            'color_contrast_class': '与背景颜色不相近' if has_good_contrast else '与背景颜色相近'
        }

    def analyze_image(self, image_path: str) -> List[Dict[str, Any]]:
        """分析图像中的二维码"""
        image = cv2.imread(image_path)

        if image is None:
            print(f"错误: 无法读取图像 {image_path}")
            return []

        # 使用所有检测器检测
        all_detections = []

        if self.use_pyzbar:
            detections = self.detect_with_pyzbar(image)
            if detections:
                all_detections.append(detections)
                print(f"  pyzbar检测到 {len(detections)} 个二维码")

        if self.use_opencv_detector:
            detections = self.detect_with_opencv(image)
            if detections:
                all_detections.append(detections)
                print(f"  OpenCV检测到 {len(detections)} 个二维码")

        if self.use_wechat_detector:
            detections = self.detect_with_wechat(image)
            if detections:
                all_detections.append(detections)
                print(f"  WeChat检测到 {len(detections)} 个二维码")

        # 添加轮廓检测作为补充
        contour_detections = self.detect_with_contours(image)
        if contour_detections:
            all_detections.append(contour_detections)
            print(f"  轮廓检测到 {len(contour_detections)} 个候选区域")

        # 融合检测结果
        fused_detections = self.fuse_detections(all_detections)

        print(f"  融合后: {len(fused_detections)} 个二维码")

        # 分析每个检测到的二维码
        results = []

        for detection in fused_detections:
            bbox = detection['bbox']

            # 计算面积占比
            area_info = self.calculate_area_ratio(bbox, image.shape)

            # 计算清晰度
            clarity_info = self.calculate_clarity(image, bbox)

            # 计算颜色对比度
            contrast_info = self.calculate_color_contrast(image, bbox)

            # 组合结果
            result = {
                'image_path': image_path,
                'bbox': bbox,
                'qr_data': detection.get('data', ''),
                **area_info,
                **clarity_info,
                **contrast_info,
                'detectors_used': detection.get('detectors', []),
                'num_votes': detection.get('num_votes', 1),
                'fusion_method': detection.get('fusion_method', 'none'),
                'detection_confidence': detection.get('confidence', 1.0)
            }

            results.append(result)

        return results

    def batch_analyze(self, image_paths: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """批量分析"""
        results = {}

        for i, image_path in enumerate(image_paths, 1):
            print(f"\n分析第 {i}/{len(image_paths)} 张图片: {image_path}")

            try:
                result = self.analyze_image(image_path)
                results[image_path] = result
            except Exception as e:
                print(f"分析失败: {e}")
                results[image_path] = []

        return results


def main():
    """主函数 - 使用示例"""
    print("=" * 60)
    print("二维码智能分析系统 - 多模型集成方案")
    print("=" * 60)

    # 创建集成分析器
    analyzer = QRCodeAnalyzerEnsemble(
        use_pyzbar=True,
        use_opencv_detector=True,
        use_wechat_detector=False,  # 需要模型文件
        fusion_strategy='voting',
        min_votes=2
    )

    # 测试单张图片
    test_image = "../sample_data/clear/clear_qr_1.jpg"

    if os.path.exists(test_image):
        print(f"\n分析测试图片: {test_image}\n")

        results = analyzer.analyze_image(test_image)

        if results:
            for i, result in enumerate(results, 1):
                print(f"\n{'='*40}")
                print(f"二维码 #{i}:")
                print(f"{'='*40}")
                print(f"  位置: ({result['bbox']['x']}, {result['bbox']['y']})")
                print(f"  尺寸: {result['bbox']['width']} x {result['bbox']['height']}")
                print(f"  面积占比: {result['area_ratio_percent']:.2f}%")
                print(f"  大于5%: {'是' if result['area_larger_than_5_percent'] else '否'}")
                print(f"  清晰度: {result['clarity_class']} (评分: {result['clarity_score']:.2f})")
                print(f"  颜色对比: {result['color_contrast_class']}")
                print(f"  检测器: {', '.join(result['detectors_used'])}")
                print(f"  投票数: {result['num_votes']}")
                print(f"  融合方法: {result['fusion_method']}")
                print(f"  置信度: {result['detection_confidence']:.3f}")
        else:
            print("未检测到二维码")
    else:
        print(f"测试图片不存在: {test_image}")
        print("请确保已生成示例数据")


if __name__ == "__main__":
    main()
