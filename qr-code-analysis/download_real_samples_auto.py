"""
自动下载真实二维码图片 - 非交互式版本
"""

import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import os
import time
import hashlib


def download_from_url(url, output_path):
    """从URL下载图片"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        with open(output_path, 'wb') as f:
            f.write(response.content)

        return True
    except Exception as e:
        print(f"✗ 下载失败: {e}")
        return False


def main():
    print("=" * 60)
    print("自动下载真实二维码样本")
    print("=" * 60)

    # 创建输出目录
    output_dir = "real_data/downloads"
    os.makedirs(output_dir, exist_ok=True)

    downloaded = 0

    # 1. 下载维基百科QR码示例
    print("\n下载维基百科样本...")
    wiki_urls = [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/QR_code_for_mobile_English_Wikipedia.svg/800px-QR_code_for_mobile_English_Wikipedia.svg.png",
    ]

    for i, url in enumerate(wiki_urls, 1):
        filepath = os.path.join(output_dir, f"wiki_qr_{i}.png")
        if download_from_url(url, filepath):
            print(f"✓ 已下载: wiki_qr_{i}.png")
            downloaded += 1
        time.sleep(0.5)

    # 2. 使用QR码生成API创建不同样式的二维码
    print("\n生成不同样式的QR码...")

    qr_configs = [
        # (数据, 大小, 背景色, 前景色, 描述)
        ("https://github.com", "400x400", "ffffff", "000000", "standard"),
        ("https://www.example.com", "500x500", "ffffff", "000000", "large"),
        ("Sample Text", "300x300", "ffffff", "000000", "small"),
        ("https://www.google.com", "400x400", "f0f0f0", "333333", "gray_bg"),
        ("QR Code Test", "400x400", "e8f4f8", "1a5490", "blue_theme"),
        ("https://www.amazon.com", "350x350", "fff5e6", "cc6600", "orange_theme"),
        ("Product Code: 12345", "450x450", "ffffff", "000000", "product"),
        ("Contact: info@example.com", "400x400", "f5f5f5", "222222", "contact"),
        ("WiFi:WPA;S:MyNetwork;P:password123;;", "400x400", "ffffff", "000000", "wifi"),
        ("https://www.wikipedia.org", "380x380", "ffffff", "000000", "wiki_link"),
    ]

    for i, (data, size, bgcolor, color, desc) in enumerate(qr_configs, 1):
        url = f"https://api.qrserver.com/v1/create-qr-code/?size={size}&data={requests.utils.quote(data)}&bgcolor={bgcolor}&color={color}"
        filepath = os.path.join(output_dir, f"generated_{desc}_{i}.png")

        if download_from_url(url, filepath):
            print(f"✓ 已生成: generated_{desc}_{i}.png")
            downloaded += 1
        time.sleep(0.3)

    # 3. 创建不同错误纠正级别的二维码
    print("\n生成不同错误纠正级别的QR码...")

    ecc_levels = [
        ('L', 'low'),
        ('M', 'medium'),
        ('Q', 'quartile'),
        ('H', 'high'),
    ]

    for level, desc in ecc_levels:
        url = f"https://api.qrserver.com/v1/create-qr-code/?size=400x400&data=Error%20Correction%20Level%20{level}&ecc={level}"
        filepath = os.path.join(output_dir, f"ecc_{desc}_{level}.png")

        if download_from_url(url, filepath):
            print(f"✓ 已生成: ecc_{desc}_{level}.png")
            downloaded += 1
        time.sleep(0.3)

    # 4. 创建不同数据量的二维码（测试复杂度）
    print("\n生成不同数据量的QR码...")

    data_samples = [
        ("Short", "short_data"),
        ("Medium length text for QR code testing purposes", "medium_data"),
        ("Very long text " * 10, "long_data"),
        ("https://www.example.com/very/long/url/path/with/many/segments/for/testing/qr/code/capacity", "long_url"),
    ]

    for i, (data, desc) in enumerate(data_samples, 1):
        url = f"https://api.qrserver.com/v1/create-qr-code/?size=500x500&data={requests.utils.quote(data)}"
        filepath = os.path.join(output_dir, f"data_{desc}_{i}.png")

        if download_from_url(url, filepath):
            print(f"✓ 已生成: data_{desc}_{i}.png")
            downloaded += 1
        time.sleep(0.3)

    # 统计
    print("\n" + "=" * 60)
    print("下载完成！")
    print("=" * 60)
    print(f"总计下载: {downloaded} 张图片")
    print(f"保存位置: {output_dir}")

    # 生成说明文件
    readme_path = os.path.join(output_dir, "README.md")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write("""# 真实二维码样本说明

## 来源

1. **维基百科样本** (wiki_qr_*.png)
   - 来自维基百科公开图片
   - 清晰度高，标准样式

2. **API生成样本** (generated_*.png)
   - 使用QR Server API生成
   - 不同颜色主题
   - 不同尺寸
   - 包含各种真实数据类型

3. **错误纠正级别测试** (ecc_*.png)
   - L: 7% 数据可恢复
   - M: 15% 数据可恢复
   - Q: 25% 数据可恢复
   - H: 30% 数据可恢复

4. **不同数据量测试** (data_*.png)
   - 短数据
   - 中等长度数据
   - 长数据
   - 长URL

## 使用建议

这些图片适合用于:
- 功能测试
- 算法验证
- 性能基准测试
- 教学演示

## 版权说明

- 维基百科图片: CC BY-SA 3.0
- API生成图片: 用于测试和开发用途
""")

    print(f"\n✓ 说明文档已生成: {readme_path}")


if __name__ == "__main__":
    main()
