"""
二维码智能分析系统 - 基础实现示例
实现方案1：OpenCV + pyzbar 基础方案
"""

import cv2
from pyzbar import pyzbar
import numpy as np
from typing import List, Dict, Any
import json


class QRCodeAnalyzer:
    """二维码分析器 - 基础实现"""

    def __init__(self):
        """初始化分析器"""
        # 清晰度分类阈值
        self.clarity_thresholds = {
            'clear': 500,           # 清晰
            'slight_blur': 200,     # 轻度模糊
            'medium_blur': 50       # 中度模糊
        }

        # 颜色对比度阈值
        self.contrast_threshold = 50

    def analyze_image(self, image_path: str) -> List[Dict[str, Any]]:
        """
        分析图片中的二维码

        Args:
            image_path: 图片路径

        Returns:
            分析结果列表，每个二维码一个字典
        """
        # 读取图像
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"无法读取图片: {image_path}")

        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 检测并解码二维码
        qr_codes = pyzbar.decode(gray)

        if not qr_codes:
            print(f"警告: 在图片 {image_path} 中未检测到二维码")
            return []

        results = []
        for qr in qr_codes:
            result = self._analyze_single_qr(image, gray, qr)
            results.append(result)

        return results

    def _analyze_single_qr(self, image: np.ndarray, gray: np.ndarray,
                          qr: pyzbar.Decoded) -> Dict[str, Any]:
        """
        分析单个二维码

        Args:
            image: 原始彩色图像
            gray: 灰度图像
            qr: pyzbar解码结果

        Returns:
            分析结果字典
        """
        # 1. 计算面积占比
        area_info = self._calculate_area_ratio(image, qr)

        # 2. 评估清晰度
        clarity_info = self._assess_clarity(gray, qr)

        # 3. 分析颜色对比度
        contrast_info = self._assess_color_contrast(image, gray, qr)

        # 合并结果
        result = {
            "qr_data": qr.data.decode('utf-8', errors='ignore'),
            "qr_type": qr.type,
            "bbox": {
                "x": qr.rect.left,
                "y": qr.rect.top,
                "width": qr.rect.width,
                "height": qr.rect.height
            },
            **area_info,
            **clarity_info,
            **contrast_info
        }

        return result

    def _calculate_area_ratio(self, image: np.ndarray,
                             qr: pyzbar.Decoded) -> Dict[str, Any]:
        """
        计算二维码面积占比

        Args:
            image: 原始图像
            qr: 二维码信息

        Returns:
            包含面积信息的字典
        """
        qr_area = qr.rect.width * qr.rect.height
        total_area = image.shape[0] * image.shape[1]
        area_ratio = (qr_area / total_area) * 100

        return {
            "area_ratio_percent": round(area_ratio, 2),
            "area_larger_than_5_percent": area_ratio > 5,
            "qr_area_pixels": qr_area,
            "total_area_pixels": total_area
        }

    def _assess_clarity(self, gray: np.ndarray,
                       qr: pyzbar.Decoded) -> Dict[str, Any]:
        """
        评估二维码清晰度

        使用拉普拉斯方差方法

        Args:
            gray: 灰度图像
            qr: 二维码信息

        Returns:
            包含清晰度信息的字典
        """
        # 提取二维码区域
        x, y, w, h = qr.rect.left, qr.rect.top, qr.rect.width, qr.rect.height
        qr_region = gray[y:y+h, x:x+w]

        # 计算拉普拉斯方差（清晰度指标）
        laplacian = cv2.Laplacian(qr_region, cv2.CV_64F)
        laplacian_var = laplacian.var()

        # 计算Sobel梯度（辅助指标）
        sobelx = cv2.Sobel(qr_region, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(qr_region, cv2.CV_64F, 0, 1, ksize=3)
        sobel_magnitude = np.sqrt(sobelx**2 + sobely**2)
        sobel_mean = np.mean(sobel_magnitude)

        # 分类清晰度
        if laplacian_var > self.clarity_thresholds['clear']:
            clarity_class = "清晰"
            clarity_level = 1
        elif laplacian_var > self.clarity_thresholds['slight_blur']:
            clarity_class = "轻度模糊"
            clarity_level = 2
        elif laplacian_var > self.clarity_thresholds['medium_blur']:
            clarity_class = "中度模糊"
            clarity_level = 3
        else:
            clarity_class = "重度模糊"
            clarity_level = 4

        return {
            "clarity_class": clarity_class,
            "clarity_level": clarity_level,
            "clarity_score": round(laplacian_var, 2),
            "sobel_score": round(sobel_mean, 2)
        }

    def _assess_color_contrast(self, image: np.ndarray, gray: np.ndarray,
                              qr: pyzbar.Decoded) -> Dict[str, Any]:
        """
        评估二维码与背景的颜色对比度

        Args:
            image: 原始彩色图像
            gray: 灰度图像
            qr: 二维码信息

        Returns:
            包含对比度信息的字典
        """
        x, y, w, h = qr.rect.left, qr.rect.top, qr.rect.width, qr.rect.height

        # 提取二维码区域
        qr_region_gray = gray[y:y+h, x:x+w]
        qr_region_color = image[y:y+h, x:x+w]

        # 提取背景区域（二维码周围的区域）
        margin = 20
        y1 = max(0, y - margin)
        y2 = min(gray.shape[0], y + h + margin)
        x1 = max(0, x - margin)
        x2 = min(gray.shape[1], x + w + margin)

        bg_region_gray = gray[y1:y2, x1:x2]
        bg_region_color = image[y1:y2, x1:x2]

        # 计算灰度对比度
        qr_mean_gray = np.mean(qr_region_gray)
        bg_mean_gray = np.mean(bg_region_gray)
        gray_contrast = abs(qr_mean_gray - bg_mean_gray)

        # 计算RGB对比度
        qr_mean_rgb = np.mean(qr_region_color, axis=(0, 1))
        bg_mean_rgb = np.mean(bg_region_color, axis=(0, 1))
        rgb_contrast = np.linalg.norm(qr_mean_rgb - bg_mean_rgb)

        # 计算HSV对比度
        qr_hsv = cv2.cvtColor(qr_region_color, cv2.COLOR_BGR2HSV)
        bg_hsv = cv2.cvtColor(bg_region_color, cv2.COLOR_BGR2HSV)
        qr_mean_hsv = np.mean(qr_hsv, axis=(0, 1))
        bg_mean_hsv = np.mean(bg_hsv, axis=(0, 1))
        hsv_contrast = np.linalg.norm(qr_mean_hsv - bg_mean_hsv)

        # 综合对比度评分
        contrast_score = (gray_contrast * 0.3 + rgb_contrast * 0.4 +
                         hsv_contrast * 0.3)

        # 分类
        if contrast_score > self.contrast_threshold:
            contrast_class = "与背景颜色不相近"
            has_good_contrast = True
        else:
            contrast_class = "与背景颜色相近"
            has_good_contrast = False

        return {
            "color_contrast_class": contrast_class,
            "has_good_contrast": has_good_contrast,
            "contrast_score": round(contrast_score, 2),
            "gray_contrast": round(gray_contrast, 2),
            "rgb_contrast": round(rgb_contrast, 2),
            "hsv_contrast": round(hsv_contrast, 2)
        }

    def batch_analyze(self, image_paths: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        批量分析多张图片

        Args:
            image_paths: 图片路径列表

        Returns:
            字典，键为图片路径，值为分析结果列表
        """
        results = {}

        for i, path in enumerate(image_paths, 1):
            print(f"处理 {i}/{len(image_paths)}: {path}")
            try:
                result = self.analyze_image(path)
                results[path] = result
            except Exception as e:
                print(f"错误: 处理 {path} 时出错 - {str(e)}")
                results[path] = {"error": str(e)}

        return results

    def save_results(self, results: Dict[str, Any], output_path: str):
        """
        保存分析结果到JSON文件

        Args:
            results: 分析结果
            output_path: 输出文件路径
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"结果已保存到: {output_path}")

    def generate_summary_report(self, results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        生成汇总报告

        Args:
            results: 批量分析结果

        Returns:
            汇总报告字典
        """
        total_images = len(results)
        total_qr_codes = 0

        area_stats = {"larger_than_5%": 0, "smaller_or_equal_5%": 0}
        clarity_stats = {"清晰": 0, "轻度模糊": 0, "中度模糊": 0, "重度模糊": 0}
        contrast_stats = {"与背景颜色不相近": 0, "与背景颜色相近": 0}

        for path, qr_list in results.items():
            if isinstance(qr_list, list):
                total_qr_codes += len(qr_list)

                for qr_result in qr_list:
                    # 面积统计
                    if qr_result.get('area_larger_than_5_percent'):
                        area_stats["larger_than_5%"] += 1
                    else:
                        area_stats["smaller_or_equal_5%"] += 1

                    # 清晰度统计
                    clarity = qr_result.get('clarity_class', '')
                    if clarity in clarity_stats:
                        clarity_stats[clarity] += 1

                    # 对比度统计
                    contrast = qr_result.get('color_contrast_class', '')
                    if contrast in contrast_stats:
                        contrast_stats[contrast] += 1

        report = {
            "summary": {
                "total_images_processed": total_images,
                "total_qr_codes_detected": total_qr_codes,
                "average_qr_per_image": round(total_qr_codes / total_images, 2) if total_images > 0 else 0
            },
            "area_distribution": area_stats,
            "clarity_distribution": clarity_stats,
            "contrast_distribution": contrast_stats
        }

        return report


def main():
    """主函数 - 示例用法"""

    # 创建分析器实例
    analyzer = QRCodeAnalyzer()

    # 示例1: 分析单张图片
    print("=" * 60)
    print("示例1: 分析单张图片")
    print("=" * 60)

    try:
        result = analyzer.analyze_image("example_qr_code.jpg")

        for i, qr in enumerate(result, 1):
            print(f"\n二维码 #{i}:")
            print(f"  内容: {qr['qr_data']}")
            print(f"  位置: x={qr['bbox']['x']}, y={qr['bbox']['y']}, " +
                  f"w={qr['bbox']['width']}, h={qr['bbox']['height']}")
            print(f"  面积占比: {qr['area_ratio_percent']}%")
            print(f"  是否大于5%: {qr['area_larger_than_5_percent']}")
            print(f"  清晰度: {qr['clarity_class']} (评分: {qr['clarity_score']})")
            print(f"  颜色对比: {qr['color_contrast_class']} (评分: {qr['contrast_score']})")
    except Exception as e:
        print(f"示例1失败: {e}")

    # 示例2: 批量分析
    print("\n" + "=" * 60)
    print("示例2: 批量分析多张图片")
    print("=" * 60)

    image_list = [
        "image1.jpg",
        "image2.jpg",
        "image3.jpg"
    ]

    try:
        batch_results = analyzer.batch_analyze(image_list)

        # 保存结果
        analyzer.save_results(batch_results, "qr_analysis_results.json")

        # 生成汇总报告
        report = analyzer.generate_summary_report(batch_results)

        print("\n汇总报告:")
        print(json.dumps(report, ensure_ascii=False, indent=2))

        # 保存报告
        analyzer.save_results(report, "qr_analysis_summary.json")

    except Exception as e:
        print(f"示例2失败: {e}")


if __name__ == "__main__":
    main()
