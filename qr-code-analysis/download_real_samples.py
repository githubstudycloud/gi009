"""
自动下载真实二维码图片

从多个免费来源下载真实的二维码图片：
- Unsplash API (需要API key，但有免费额度)
- Pexels API (需要API key，完全免费)
- 直接下载公开可用的二维码图片
"""

import sys
import io

# 设置标准输出编码为UTF-8（Windows兼容）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import os
import time
from urllib.parse import urlencode
import hashlib


class RealQRImageDownloader:
    """真实二维码图片下载器"""

    def __init__(self, output_dir="real_data"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # 创建分类目录
        self.categories = {
            'product': os.path.join(output_dir, 'product_qr'),
            'poster': os.path.join(output_dir, 'poster_qr'),
            'phone': os.path.join(output_dir, 'phone_qr'),
            'clear': os.path.join(output_dir, 'clear_qr'),
            'blurred': os.path.join(output_dir, 'blurred_qr'),
            'mixed': os.path.join(output_dir, 'mixed_qr'),
        }

        for path in self.categories.values():
            os.makedirs(path, exist_ok=True)

    def download_from_url(self, url, category='mixed', filename=None):
        """
        从URL下载图片

        Args:
            url: 图片URL
            category: 分类
            filename: 文件名（可选）

        Returns:
            保存的文件路径或None
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            # 生成文件名
            if not filename:
                # 使用URL的哈希作为文件名
                url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
                filename = f"qr_{url_hash}.jpg"

            # 确保文件名有正确的扩展名
            if not filename.endswith(('.jpg', '.jpeg', '.png')):
                filename += '.jpg'

            # 保存路径
            if category in self.categories:
                filepath = os.path.join(self.categories[category], filename)
            else:
                filepath = os.path.join(self.output_dir, filename)

            # 保存文件
            with open(filepath, 'wb') as f:
                f.write(response.content)

            print(f"✓ 已下载: {filename}")
            return filepath

        except Exception as e:
            print(f"✗ 下载失败 {url}: {e}")
            return None

    def download_from_pexels(self, api_key, query='qr code', per_page=15):
        """
        从Pexels下载图片（需要API key）

        免费注册: https://www.pexels.com/api/

        Args:
            api_key: Pexels API key
            query: 搜索关键词
            per_page: 每次请求的图片数量

        Returns:
            下载的文件路径列表
        """
        print(f"\n从Pexels下载图片 (关键词: {query})...")

        url = "https://api.pexels.com/v1/search"
        headers = {
            'Authorization': api_key
        }
        params = {
            'query': query,
            'per_page': per_page,
            'orientation': 'landscape'
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            downloaded = []
            for i, photo in enumerate(data.get('photos', []), 1):
                img_url = photo['src']['large']
                photographer = photo['photographer'].replace(' ', '_')
                filename = f"pexels_{photographer}_{photo['id']}.jpg"

                filepath = self.download_from_url(img_url, 'mixed', filename)
                if filepath:
                    downloaded.append(filepath)

                time.sleep(0.5)  # 避免请求过快

            print(f"Pexels下载完成: {len(downloaded)}/{per_page} 张")
            return downloaded

        except requests.exceptions.RequestException as e:
            print(f"Pexels API错误: {e}")
            if "401" in str(e):
                print("提示: 请检查API key是否正确")
            return []

    def download_from_unsplash(self, api_key, query='qr code', per_page=10):
        """
        从Unsplash下载图片（需要API key）

        免费注册: https://unsplash.com/developers

        Args:
            api_key: Unsplash Access Key
            query: 搜索关键词
            per_page: 每次请求的图片数量

        Returns:
            下载的文件路径列表
        """
        print(f"\n从Unsplash下载图片 (关键词: {query})...")

        url = "https://api.unsplash.com/search/photos"
        params = {
            'query': query,
            'per_page': per_page,
            'client_id': api_key
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            downloaded = []
            for i, photo in enumerate(data.get('results', []), 1):
                img_url = photo['urls']['regular']
                username = photo['user']['username']
                photo_id = photo['id']
                filename = f"unsplash_{username}_{photo_id}.jpg"

                filepath = self.download_from_url(img_url, 'mixed', filename)
                if filepath:
                    downloaded.append(filepath)

                time.sleep(0.5)

            print(f"Unsplash下载完成: {len(downloaded)}/{per_page} 张")
            return downloaded

        except requests.exceptions.RequestException as e:
            print(f"Unsplash API错误: {e}")
            if "401" in str(e):
                print("提示: 请检查Access Key是否正确")
            return []

    def download_public_samples(self):
        """
        下载一些公开可用的二维码示例图片

        这些是一些已知的公开二维码图片URL
        """
        print("\n下载公开示例图片...")

        # 这里列出一些公开可用的二维码图片URL
        # 注意：这些URL可能会失效，仅作示例
        public_urls = [
            # 维基百科的QR码示例
            "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/QR_code_for_mobile_English_Wikipedia.svg/1200px-QR_code_for_mobile_English_Wikipedia.svg.png",

            # GitHub上的示例
            "https://raw.githubusercontent.com/zxing/zxing/master/core/src/test/resources/blackbox/qrcode-1/01.png",
            "https://raw.githubusercontent.com/zxing/zxing/master/core/src/test/resources/blackbox/qrcode-1/02.png",
            "https://raw.githubusercontent.com/zxing/zxing/master/core/src/test/resources/blackbox/qrcode-1/03.png",

            # QR码生成器的样本
            "https://api.qrserver.com/v1/create-qr-code/?size=500x500&data=https://github.com",
            "https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=Hello%20World&bgcolor=ff0000&color=ffffff",
        ]

        downloaded = []
        for i, url in enumerate(public_urls, 1):
            filename = f"public_sample_{i}.png"
            filepath = self.download_from_url(url, 'clear', filename)
            if filepath:
                downloaded.append(filepath)
            time.sleep(0.5)

        print(f"公开示例下载完成: {len(downloaded)} 张")
        return downloaded

    def download_qr_api_samples(self, texts=None):
        """
        使用QR码生成API创建一些测试样本

        Args:
            texts: 要编码的文本列表
        """
        print("\n生成QR码API样本...")

        if texts is None:
            texts = [
                "https://github.com",
                "https://www.example.com",
                "Sample QR Code",
                "https://www.google.com",
                "Test Data 12345",
            ]

        downloaded = []
        for i, text in enumerate(texts, 1):
            # 使用免费的QR码生成API
            url = f"https://api.qrserver.com/v1/create-qr-code/?size=400x400&data={requests.utils.quote(text)}"

            filename = f"api_generated_{i}.png"
            filepath = self.download_from_url(url, 'clear', filename)
            if filepath:
                downloaded.append(filepath)
            time.sleep(0.3)

        print(f"API生成样本完成: {len(downloaded)} 张")
        return downloaded


def main():
    """主函数"""
    print("=" * 60)
    print("真实二维码图片下载器")
    print("=" * 60)

    downloader = RealQRImageDownloader("real_data")

    all_downloaded = []

    # 1. 下载公开示例
    public_samples = downloader.download_public_samples()
    all_downloaded.extend(public_samples)

    # 2. 生成API样本
    api_samples = downloader.download_qr_api_samples()
    all_downloaded.extend(api_samples)

    # 3. 尝试从Pexels下载（需要API key）
    print("\n" + "-" * 60)
    print("从Pexels下载 (需要API key)")
    print("免费注册: https://www.pexels.com/api/")
    print("-" * 60)

    pexels_key = input("请输入Pexels API key (直接回车跳过): ").strip()
    if pexels_key:
        pexels_samples = downloader.download_from_pexels(pexels_key, 'qr code', 15)
        all_downloaded.extend(pexels_samples)
    else:
        print("已跳过Pexels下载")

    # 4. 尝试从Unsplash下载（需要API key）
    print("\n" + "-" * 60)
    print("从Unsplash下载 (需要Access Key)")
    print("免费注册: https://unsplash.com/developers")
    print("-" * 60)

    unsplash_key = input("请输入Unsplash Access Key (直接回车跳过): ").strip()
    if unsplash_key:
        unsplash_samples = downloader.download_from_unsplash(unsplash_key, 'qr code', 10)
        all_downloaded.extend(unsplash_samples)
    else:
        print("已跳过Unsplash下载")

    # 统计
    print("\n" + "=" * 60)
    print("下载完成！")
    print("=" * 60)
    print(f"总计下载: {len(all_downloaded)} 张图片")
    print(f"保存位置: {downloader.output_dir}")

    # 显示各类别统计
    print("\n各类别统计:")
    for category, path in downloader.categories.items():
        count = len([f for f in os.listdir(path) if f.endswith(('.jpg', '.png'))])
        if count > 0:
            print(f"  {category}: {count} 张")


def download_with_api_keys():
    """使用预设的API keys下载（需要用户提供）"""
    print("=" * 60)
    print("真实二维码图片下载器 - API模式")
    print("=" * 60)

    # API配置
    config = {
        'pexels_api_key': '',  # 在这里填入你的Pexels API key
        'unsplash_access_key': '',  # 在这里填入你的Unsplash Access Key
    }

    downloader = RealQRImageDownloader("real_data")

    all_downloaded = []

    # 下载公开示例
    public_samples = downloader.download_public_samples()
    all_downloaded.extend(public_samples)

    # 生成API样本
    api_samples = downloader.download_qr_api_samples()
    all_downloaded.extend(api_samples)

    # 从Pexels下载
    if config['pexels_api_key']:
        queries = ['qr code', 'barcode', 'product package']
        for query in queries:
            samples = downloader.download_from_pexels(
                config['pexels_api_key'],
                query,
                per_page=10
            )
            all_downloaded.extend(samples)
            time.sleep(2)

    # 从Unsplash下载
    if config['unsplash_access_key']:
        queries = ['qr code', 'scan qr code', 'qr code payment']
        for query in queries:
            samples = downloader.download_from_unsplash(
                config['unsplash_access_key'],
                query,
                per_page=8
            )
            all_downloaded.extend(samples)
            time.sleep(2)

    print("\n" + "=" * 60)
    print("下载完成！")
    print("=" * 60)
    print(f"总计: {len(all_downloaded)} 张图片")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--api":
        download_with_api_keys()
    else:
        main()
