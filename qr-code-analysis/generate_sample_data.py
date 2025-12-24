"""
生成二维码示例数据

这个脚本会自动生成各种类型的二维码测试图片：
- 不同大小（小/中/大）
- 不同清晰度（清晰/轻度模糊/中度模糊/重度模糊）
- 不同背景对比度（高对比/低对比）
- 不同面积占比
"""

import sys
import io

# 设置标准输出编码为UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import cv2
import numpy as np
import qrcode
from PIL import Image, ImageDraw, ImageFilter
import os
from typing import Tuple, List
import random


class QRCodeSampleGenerator:
    """二维码示例数据生成器"""

    def __init__(self, output_dir="sample_data"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # 创建子目录
        self.categories = {
            'clear': os.path.join(output_dir, 'clear'),
            'blurred': os.path.join(output_dir, 'blurred'),
            'small': os.path.join(output_dir, 'small'),
            'large': os.path.join(output_dir, 'large'),
            'low_contrast': os.path.join(output_dir, 'low_contrast'),
            'mixed': os.path.join(output_dir, 'mixed')
        }

        for path in self.categories.values():
            os.makedirs(path, exist_ok=True)

    def generate_qr_code(self, data: str, size: int = 200) -> Image.Image:
        """
        生成二维码图像

        Args:
            data: 二维码内容
            size: 二维码大小

        Returns:
            PIL Image对象
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img = qr_img.resize((size, size), Image.Resampling.LANCZOS)

        return qr_img

    def create_background(self, width: int, height: int,
                         bg_type: str = "solid") -> Image.Image:
        """
        创建背景图像

        Args:
            width: 宽度
            height: 高度
            bg_type: 背景类型 (solid, gradient, texture, photo)

        Returns:
            PIL Image对象
        """
        if bg_type == "solid":
            # 纯色背景
            color = random.choice([
                (255, 255, 255),  # 白色
                (240, 240, 240),  # 浅灰
                (200, 200, 200),  # 灰色
                (255, 200, 200),  # 浅红
                (200, 255, 200),  # 浅绿
                (200, 200, 255),  # 浅蓝
            ])
            bg = Image.new('RGB', (width, height), color)

        elif bg_type == "gradient":
            # 渐变背景
            bg = Image.new('RGB', (width, height))
            draw = ImageDraw.Draw(bg)
            for i in range(height):
                color_value = int(200 + (i / height) * 55)
                draw.line([(0, i), (width, i)],
                         fill=(color_value, color_value, color_value))

        elif bg_type == "texture":
            # 纹理背景
            bg = Image.new('RGB', (width, height), (220, 220, 220))
            draw = ImageDraw.Draw(bg)
            for _ in range(100):
                x = random.randint(0, width)
                y = random.randint(0, height)
                size = random.randint(10, 50)
                color = tuple(random.randint(200, 255) for _ in range(3))
                draw.ellipse([x, y, x+size, y+size], fill=color, outline=color)

        elif bg_type == "photo":
            # 模拟照片背景
            bg = Image.new('RGB', (width, height))
            pixels = np.random.randint(100, 200, (height, width, 3), dtype=np.uint8)
            bg = Image.fromarray(pixels)

        else:
            bg = Image.new('RGB', (width, height), (255, 255, 255))

        return bg

    def apply_blur(self, image: Image.Image, blur_level: str) -> Image.Image:
        """
        对图像应用模糊效果

        Args:
            image: 原始图像
            blur_level: 模糊等级 (slight, medium, heavy)

        Returns:
            模糊后的图像
        """
        if blur_level == "slight":
            return image.filter(ImageFilter.GaussianBlur(radius=1))
        elif blur_level == "medium":
            return image.filter(ImageFilter.GaussianBlur(radius=3))
        elif blur_level == "heavy":
            return image.filter(ImageFilter.GaussianBlur(radius=6))
        else:
            return image

    def place_qr_on_background(self, qr_img: Image.Image, bg: Image.Image,
                               position: str = "center") -> Image.Image:
        """
        将二维码放置在背景上

        Args:
            qr_img: 二维码图像
            bg: 背景图像
            position: 位置 (center, random, top-left, etc.)

        Returns:
            合成后的图像
        """
        bg_copy = bg.copy()
        qr_width, qr_height = qr_img.size
        bg_width, bg_height = bg.size

        if position == "center":
            x = (bg_width - qr_width) // 2
            y = (bg_height - qr_height) // 2
        elif position == "random":
            x = random.randint(0, max(0, bg_width - qr_width))
            y = random.randint(0, max(0, bg_height - qr_height))
        elif position == "top-left":
            x = 20
            y = 20
        elif position == "bottom-right":
            x = bg_width - qr_width - 20
            y = bg_height - qr_height - 20
        else:
            x = (bg_width - qr_width) // 2
            y = (bg_height - qr_height) // 2

        bg_copy.paste(qr_img, (x, y))
        return bg_copy

    def adjust_contrast(self, image: Image.Image, qr_color: Tuple[int, int, int],
                       bg_mean_color: Tuple[int, int, int]) -> Image.Image:
        """
        调整二维码颜色以实现低对比度

        Args:
            image: 图像
            qr_color: 二维码颜色
            bg_mean_color: 背景平均颜色

        Returns:
            调整后的图像
        """
        # 将二维码颜色调整为与背景相近
        img_array = np.array(image)

        # 找到黑色二维码区域（接近黑色）
        black_mask = np.all(img_array < 50, axis=2)

        # 替换为与背景相近的颜色
        similar_color = tuple(int(c * 0.8) for c in bg_mean_color)
        img_array[black_mask] = similar_color

        return Image.fromarray(img_array)

    def generate_clear_samples(self, count: int = 10):
        """生成清晰的二维码样本"""
        print(f"生成 {count} 个清晰二维码样本...")

        for i in range(count):
            data = f"https://example.com/clear/{i}"
            qr_size = random.randint(150, 300)
            qr_img = self.generate_qr_code(data, qr_size)

            # 创建背景
            bg_width, bg_height = 800, 600
            bg = self.create_background(bg_width, bg_height, "solid")

            # 放置二维码
            final_img = self.place_qr_on_background(qr_img, bg, "random")

            # 保存
            output_path = os.path.join(self.categories['clear'],
                                      f"clear_qr_{i+1}.jpg")
            final_img.save(output_path, quality=95)

        print(f"✓ 清晰样本已保存到: {self.categories['clear']}")

    def generate_blurred_samples(self, count: int = 12):
        """生成模糊的二维码样本"""
        print(f"生成 {count} 个模糊二维码样本...")

        blur_levels = ["slight", "medium", "heavy", "slight"]
        blur_names = ["轻度模糊", "中度模糊", "重度模糊", "轻度模糊"]

        for i in range(count):
            data = f"https://example.com/blur/{i}"
            qr_size = random.randint(150, 250)
            qr_img = self.generate_qr_code(data, qr_size)

            # 创建背景
            bg = self.create_background(800, 600, "solid")
            final_img = self.place_qr_on_background(qr_img, bg, "center")

            # 应用模糊
            blur_level = blur_levels[i % len(blur_levels)]
            final_img = self.apply_blur(final_img, blur_level)

            # 保存
            blur_name = blur_names[i % len(blur_names)]
            output_path = os.path.join(self.categories['blurred'],
                                      f"blurred_qr_{blur_name}_{i+1}.jpg")
            final_img.save(output_path, quality=85)

        print(f"✓ 模糊样本已保存到: {self.categories['blurred']}")

    def generate_small_samples(self, count: int = 8):
        """生成小尺寸二维码样本（面积 < 5%）"""
        print(f"生成 {count} 个小尺寸二维码样本...")

        for i in range(count):
            data = f"https://example.com/small/{i}"
            qr_size = random.randint(50, 120)  # 小尺寸
            qr_img = self.generate_qr_code(data, qr_size)

            # 大背景
            bg = self.create_background(1200, 900, "gradient")
            final_img = self.place_qr_on_background(qr_img, bg, "random")

            # 保存
            output_path = os.path.join(self.categories['small'],
                                      f"small_qr_{i+1}.jpg")
            final_img.save(output_path, quality=90)

        print(f"✓ 小尺寸样本已保存到: {self.categories['small']}")

    def generate_large_samples(self, count: int = 8):
        """生成大尺寸二维码样本（面积 > 5%）"""
        print(f"生成 {count} 个大尺寸二维码样本...")

        for i in range(count):
            data = f"https://example.com/large/{i}"
            qr_size = random.randint(300, 500)  # 大尺寸
            qr_img = self.generate_qr_code(data, qr_size)

            # 相对较小的背景
            bg = self.create_background(800, 600, "texture")
            final_img = self.place_qr_on_background(qr_img, bg, "center")

            # 保存
            output_path = os.path.join(self.categories['large'],
                                      f"large_qr_{i+1}.jpg")
            final_img.save(output_path, quality=90)

        print(f"✓ 大尺寸样本已保存到: {self.categories['large']}")

    def generate_low_contrast_samples(self, count: int = 10):
        """生成低对比度二维码样本"""
        print(f"生成 {count} 个低对比度二维码样本...")

        for i in range(count):
            data = f"https://example.com/contrast/{i}"
            qr_size = random.randint(150, 250)
            qr_img = self.generate_qr_code(data, qr_size)

            # 创建灰色背景
            bg_color = random.randint(100, 180)
            bg = Image.new('RGB', (800, 600), (bg_color, bg_color, bg_color))

            # 放置二维码
            final_img = self.place_qr_on_background(qr_img, bg, "center")

            # 调整对比度
            final_img = self.adjust_contrast(final_img, (0, 0, 0),
                                            (bg_color, bg_color, bg_color))

            # 保存
            output_path = os.path.join(self.categories['low_contrast'],
                                      f"low_contrast_qr_{i+1}.jpg")
            final_img.save(output_path, quality=90)

        print(f"✓ 低对比度样本已保存到: {self.categories['low_contrast']}")

    def generate_mixed_samples(self, count: int = 15):
        """生成混合场景样本（多个二维码、复杂背景等）"""
        print(f"生成 {count} 个混合场景样本...")

        for i in range(count):
            # 创建复杂背景
            bg = self.create_background(1000, 800,
                                       random.choice(["texture", "photo", "gradient"]))

            # 放置多个二维码
            num_qrs = random.randint(1, 3)
            for j in range(num_qrs):
                data = f"https://example.com/mixed/{i}/qr{j}"
                qr_size = random.randint(100, 250)
                qr_img = self.generate_qr_code(data, qr_size)

                bg = self.place_qr_on_background(qr_img, bg, "random")

            # 可能添加模糊
            if random.random() < 0.3:
                bg = self.apply_blur(bg, "slight")

            # 保存
            output_path = os.path.join(self.categories['mixed'],
                                      f"mixed_qr_{i+1}.jpg")
            bg.save(output_path, quality=85)

        print(f"✓ 混合场景样本已保存到: {self.categories['mixed']}")

    def generate_all(self):
        """生成所有类型的样本"""
        print("=" * 60)
        print("开始生成二维码示例数据")
        print("=" * 60)

        self.generate_clear_samples(10)
        self.generate_blurred_samples(12)
        self.generate_small_samples(8)
        self.generate_large_samples(8)
        self.generate_low_contrast_samples(10)
        self.generate_mixed_samples(15)

        print("\n" + "=" * 60)
        print("✓ 所有示例数据生成完成！")
        print("=" * 60)

        # 统计信息
        total_images = 0
        for category, path in self.categories.items():
            count = len([f for f in os.listdir(path) if f.endswith('.jpg')])
            total_images += count
            print(f"  {category}: {count} 张图片")

        print(f"\n总计: {total_images} 张测试图片")
        print(f"位置: {self.output_dir}")

    def generate_readme(self):
        """生成示例数据说明文档"""
        readme_content = """# 二维码示例数据说明

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
"""

        readme_path = os.path.join(self.output_dir, "README.md")
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)

        print(f"\n✓ 说明文档已生成: {readme_path}")


def main():
    """主函数"""
    # 检查依赖
    try:
        import qrcode
    except ImportError:
        print("错误: 需要安装 qrcode 库")
        print("请运行: pip install qrcode[pil]")
        return

    # 创建生成器
    generator = QRCodeSampleGenerator("sample_data")

    # 生成所有样本
    generator.generate_all()

    # 生成说明文档
    generator.generate_readme()

    print("\n使用方法:")
    print("  python qr_analyzer_basic.py")
    print("  或者在代码中使用 batch_analyze() 方法测试这些图片")


if __name__ == "__main__":
    main()
