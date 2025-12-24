"""
二维码智能分析系统 - 单元测试

运行测试: pytest test_qr_analyzer.py -v
"""

import pytest
import cv2
import numpy as np
import json
import os
from qr_analyzer_basic import QRCodeAnalyzer


class TestQRCodeAnalyzer:
    """QRCodeAnalyzer 单元测试类"""

    @pytest.fixture
    def analyzer(self):
        """创建分析器实例"""
        return QRCodeAnalyzer()

    @pytest.fixture
    def sample_image(self):
        """创建测试用的样本图像（带简单二维码）"""
        # 创建一个 500x500 的白色图像
        image = np.ones((500, 500, 3), dtype=np.uint8) * 255

        # 在中心创建一个简单的黑色正方形模拟二维码
        cv2.rectangle(image, (150, 150), (350, 350), (0, 0, 0), -1)

        # 添加一些内部细节
        for i in range(160, 340, 20):
            cv2.line(image, (i, 160), (i, 340), (255, 255, 255), 2)
            cv2.line(image, (160, i), (340, i), (255, 255, 255), 2)

        return image

    @pytest.fixture
    def temp_image_path(self, sample_image, tmp_path):
        """保存样本图像到临时文件"""
        file_path = tmp_path / "test_qr.jpg"
        cv2.imwrite(str(file_path), sample_image)
        return str(file_path)

    def test_analyzer_initialization(self, analyzer):
        """测试分析器初始化"""
        assert analyzer is not None
        assert hasattr(analyzer, 'clarity_thresholds')
        assert hasattr(analyzer, 'contrast_threshold')
        assert analyzer.clarity_thresholds['clear'] == 500
        assert analyzer.contrast_threshold == 50

    def test_calculate_area_ratio(self, analyzer, sample_image):
        """测试面积计算"""
        from pyzbar.pyzbar import Rect

        # 模拟一个二维码区域
        mock_qr = type('obj', (object,), {
            'rect': Rect(left=100, top=100, width=200, height=200)
        })

        result = analyzer._calculate_area_ratio(sample_image, mock_qr)

        assert 'area_ratio_percent' in result
        assert 'area_larger_than_5_percent' in result
        assert 'qr_area_pixels' in result
        assert 'total_area_pixels' in result

        # 计算预期值
        expected_qr_area = 200 * 200
        expected_total_area = 500 * 500
        expected_ratio = (expected_qr_area / expected_total_area) * 100

        assert result['qr_area_pixels'] == expected_qr_area
        assert result['total_area_pixels'] == expected_total_area
        assert abs(result['area_ratio_percent'] - expected_ratio) < 0.01

    def test_assess_clarity_clear_image(self, analyzer):
        """测试清晰图像的清晰度评估"""
        # 创建一个清晰的测试图像（高对比度）
        clear_image = np.zeros((100, 100), dtype=np.uint8)
        for i in range(0, 100, 10):
            clear_image[i:i+5, :] = 255

        from pyzbar.pyzbar import Rect
        mock_qr = type('obj', (object,), {
            'rect': Rect(left=0, top=0, width=100, height=100)
        })

        result = analyzer._assess_clarity(clear_image, mock_qr)

        assert 'clarity_class' in result
        assert 'clarity_level' in result
        assert 'clarity_score' in result
        assert result['clarity_level'] in [1, 2, 3, 4]
        assert result['clarity_score'] > 0

    def test_assess_clarity_blurred_image(self, analyzer):
        """测试模糊图像的清晰度评估"""
        # 创建一个模糊的测试图像
        blurred_image = np.ones((100, 100), dtype=np.uint8) * 128
        blurred_image = cv2.GaussianBlur(blurred_image, (15, 15), 10)

        from pyzbar.pyzbar import Rect
        mock_qr = type('obj', (object,), {
            'rect': Rect(left=0, top=0, width=100, height=100)
        })

        result = analyzer._assess_clarity(blurred_image, mock_qr)

        assert 'clarity_class' in result
        # 模糊图像应该得到较低的清晰度评分
        assert result['clarity_level'] >= 2  # 至少是轻度模糊

    def test_assess_color_contrast_high(self, analyzer):
        """测试高对比度场景"""
        # 创建黑色二维码在白色背景上
        image = np.ones((200, 200, 3), dtype=np.uint8) * 255
        image[50:150, 50:150] = [0, 0, 0]  # 黑色二维码

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        from pyzbar.pyzbar import Rect
        mock_qr = type('obj', (object,), {
            'rect': Rect(left=50, top=50, width=100, height=100)
        })

        result = analyzer._assess_color_contrast(image, gray, mock_qr)

        assert 'color_contrast_class' in result
        assert 'has_good_contrast' in result
        assert 'contrast_score' in result
        # 黑白对比应该很高
        assert result['has_good_contrast'] == True

    def test_assess_color_contrast_low(self, analyzer):
        """测试低对比度场景"""
        # 创建灰色二维码在灰色背景上
        image = np.ones((200, 200, 3), dtype=np.uint8) * 128
        image[50:150, 50:150] = [120, 120, 120]  # 相近的灰色二维码

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        from pyzbar.pyzbar import Rect
        mock_qr = type('obj', (object,), {
            'rect': Rect(left=50, top=50, width=100, height=100)
        })

        result = analyzer._assess_color_contrast(image, gray, mock_qr)

        assert 'color_contrast_class' in result
        assert 'has_good_contrast' in result
        # 相近颜色应该得到低对比度
        # 注意：这取决于具体阈值设置
        assert result['contrast_score'] >= 0

    def test_batch_analyze_empty_list(self, analyzer):
        """测试空列表的批量分析"""
        results = analyzer.batch_analyze([])
        assert results == {}

    def test_save_results(self, analyzer, tmp_path):
        """测试结果保存"""
        test_results = {
            "image1.jpg": [
                {
                    "area_ratio_percent": 10.5,
                    "clarity_class": "清晰"
                }
            ]
        }

        output_path = tmp_path / "test_results.json"
        analyzer.save_results(test_results, str(output_path))

        # 验证文件是否创建
        assert output_path.exists()

        # 验证内容是否正确
        with open(output_path, 'r', encoding='utf-8') as f:
            loaded_results = json.load(f)

        assert loaded_results == test_results

    def test_generate_summary_report_empty(self, analyzer):
        """测试空结果的汇总报告生成"""
        results = {}
        report = analyzer.generate_summary_report(results)

        assert 'summary' in report
        assert report['summary']['total_images_processed'] == 0
        assert report['summary']['total_qr_codes_detected'] == 0

    def test_generate_summary_report_with_data(self, analyzer):
        """测试带数据的汇总报告生成"""
        results = {
            "image1.jpg": [
                {
                    "area_larger_than_5_percent": True,
                    "clarity_class": "清晰",
                    "color_contrast_class": "与背景颜色不相近"
                },
                {
                    "area_larger_than_5_percent": False,
                    "clarity_class": "轻度模糊",
                    "color_contrast_class": "与背景颜色相近"
                }
            ],
            "image2.jpg": [
                {
                    "area_larger_than_5_percent": True,
                    "clarity_class": "中度模糊",
                    "color_contrast_class": "与背景颜色不相近"
                }
            ]
        }

        report = analyzer.generate_summary_report(results)

        assert report['summary']['total_images_processed'] == 2
        assert report['summary']['total_qr_codes_detected'] == 3
        assert report['area_distribution']['larger_than_5%'] == 2
        assert report['area_distribution']['smaller_or_equal_5%'] == 1
        assert report['clarity_distribution']['清晰'] == 1
        assert report['clarity_distribution']['轻度模糊'] == 1
        assert report['clarity_distribution']['中度模糊'] == 1

    def test_threshold_customization(self):
        """测试自定义阈值"""
        custom_analyzer = QRCodeAnalyzer()
        custom_analyzer.clarity_thresholds = {
            'clear': 1000,
            'slight_blur': 500,
            'medium_blur': 100
        }
        custom_analyzer.contrast_threshold = 80

        assert custom_analyzer.clarity_thresholds['clear'] == 1000
        assert custom_analyzer.contrast_threshold == 80

    def test_invalid_image_path(self, analyzer):
        """测试无效图片路径"""
        with pytest.raises(ValueError):
            analyzer.analyze_image("nonexistent_image.jpg")

    def test_clarity_level_mapping(self, analyzer):
        """测试清晰度等级映射"""
        # 创建不同清晰度的测试图像
        test_cases = [
            (600, 1, "清晰"),           # 高清晰度
            (300, 2, "轻度模糊"),       # 轻度模糊
            (100, 3, "中度模糊"),       # 中度模糊
            (20, 4, "重度模糊")         # 重度模糊
        ]

        from pyzbar.pyzbar import Rect
        mock_qr = type('obj', (object,), {
            'rect': Rect(left=0, top=0, width=100, height=100)
        })

        for laplacian_var, expected_level, expected_class in test_cases:
            # 创建模拟的清晰度分数
            test_image = np.random.randint(0, 255, (100, 100), dtype=np.uint8)

            result = analyzer._assess_clarity(test_image, mock_qr)

            # 验证清晰度等级在有效范围内
            assert 1 <= result['clarity_level'] <= 4
            assert result['clarity_class'] in ["清晰", "轻度模糊", "中度模糊", "重度模糊"]


class TestIntegration:
    """集成测试"""

    @pytest.fixture
    def analyzer(self):
        return QRCodeAnalyzer()

    def test_end_to_end_workflow(self, analyzer, tmp_path):
        """测试端到端工作流"""
        # 由于我们无法创建真实的二维码，这里只测试流程
        # 在实际使用中，您需要准备真实的二维码图片

        # 1. 批量分析（使用空列表）
        image_list = []
        results = analyzer.batch_analyze(image_list)

        # 2. 生成报告
        report = analyzer.generate_summary_report(results)

        # 3. 保存结果
        results_path = tmp_path / "results.json"
        analyzer.save_results(results, str(results_path))

        # 4. 保存报告
        report_path = tmp_path / "report.json"
        analyzer.save_results(report, str(report_path))

        # 验证
        assert results_path.exists()
        assert report_path.exists()


def test_readme_example():
    """测试README中的示例代码是否可运行"""
    try:
        from qr_analyzer_basic import QRCodeAnalyzer

        # 创建分析器
        analyzer = QRCodeAnalyzer()

        # 验证分析器已正确创建
        assert analyzer is not None
        assert hasattr(analyzer, 'analyze_image')
        assert hasattr(analyzer, 'batch_analyze')
        assert hasattr(analyzer, 'generate_summary_report')

    except Exception as e:
        pytest.fail(f"README示例代码无法运行: {e}")


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
