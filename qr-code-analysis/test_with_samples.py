"""
使用生成的示例数据测试二维码分析系统
"""

import sys
import io

# 设置标准输出编码为UTF-8（Windows兼容）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from qr_analyzer_basic import QRCodeAnalyzer
import glob
import os
import json


def test_category(analyzer, category_name, pattern):
    """测试特定类别的图片"""
    print(f"\n{'='*60}")
    print(f"测试类别: {category_name}")
    print(f"{'='*60}")

    image_files = glob.glob(pattern)

    if not image_files:
        print(f"⚠️  未找到图片: {pattern}")
        return None

    print(f"找到 {len(image_files)} 张图片")

    results = analyzer.batch_analyze(image_files)

    # 统计信息
    stats = {
        'total': len(image_files),
        'detected': 0,
        'area_gt_5': 0,
        'clarity': {'清晰': 0, '轻度模糊': 0, '中度模糊': 0, '重度模糊': 0},
        'contrast': {'与背景颜色不相近': 0, '与背景颜色相近': 0}
    }

    for img_path, qr_list in results.items():
        if isinstance(qr_list, list) and len(qr_list) > 0:
            stats['detected'] += len(qr_list)

            for qr in qr_list:
                if qr.get('area_larger_than_5_percent'):
                    stats['area_gt_5'] += 1

                clarity = qr.get('clarity_class', '')
                if clarity in stats['clarity']:
                    stats['clarity'][clarity] += 1

                contrast = qr.get('color_contrast_class', '')
                if contrast in stats['contrast']:
                    stats['contrast'][contrast] += 1

    # 打印统计
    print(f"\n检测到的二维码总数: {stats['detected']}")
    print(f"面积>5%的二维码数: {stats['area_gt_5']}")

    print(f"\n清晰度分布:")
    for clarity, count in stats['clarity'].items():
        if count > 0:
            print(f"  {clarity}: {count}")

    print(f"\n对比度分布:")
    for contrast, count in stats['contrast'].items():
        if count > 0:
            print(f"  {contrast}: {count}")

    return results, stats


def main():
    """主测试函数"""
    print("="*60)
    print("二维码智能分析系统 - 示例数据测试")
    print("="*60)

    # 检查示例数据是否存在
    if not os.path.exists("sample_data"):
        print("\n⚠️  示例数据不存在！")
        print("请先运行: python generate_sample_data.py")
        return

    # 创建分析器
    analyzer = QRCodeAnalyzer()

    # 测试结果存储
    all_results = {}
    all_stats = {}

    # 测试各个类别
    categories = [
        ("清晰二维码", "sample_data/clear/*.jpg"),
        ("模糊二维码", "sample_data/blurred/*.jpg"),
        ("小尺寸二维码", "sample_data/small/*.jpg"),
        ("大尺寸二维码", "sample_data/large/*.jpg"),
        ("低对比度二维码", "sample_data/low_contrast/*.jpg"),
        ("混合场景", "sample_data/mixed/*.jpg"),
    ]

    for category_name, pattern in categories:
        results, stats = test_category(analyzer, category_name, pattern)
        if results:
            all_results[category_name] = results
            all_stats[category_name] = stats

    # 生成总体报告
    print("\n" + "="*60)
    print("总体统计报告")
    print("="*60)

    total_images = sum(stats['total'] for stats in all_stats.values())
    total_detected = sum(stats['detected'] for stats in all_stats.values())

    print(f"\n总图片数: {total_images}")
    print(f"检测到的二维码总数: {total_detected}")

    # 保存详细结果
    output_dir = "test_results"
    os.makedirs(output_dir, exist_ok=True)

    for category_name, results in all_results.items():
        filename = category_name.replace(" ", "_") + ".json"
        filepath = os.path.join(output_dir, filename)
        analyzer.save_results(results, filepath)
        print(f"\n✓ {category_name}结果已保存: {filepath}")

    # 保存统计摘要
    summary_path = os.path.join(output_dir, "summary.json")
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(all_stats, f, ensure_ascii=False, indent=2)
    print(f"✓ 统计摘要已保存: {summary_path}")

    # 性能测试
    print("\n" + "="*60)
    print("性能测试")
    print("="*60)

    import time

    # 测试单张图片处理时间
    test_image = glob.glob("sample_data/clear/*.jpg")[0]
    start_time = time.time()
    analyzer.analyze_image(test_image)
    end_time = time.time()

    print(f"单张图片处理时间: {(end_time - start_time)*1000:.2f} ms")

    # 测试批量处理时间
    batch_images = glob.glob("sample_data/clear/*.jpg")
    start_time = time.time()
    analyzer.batch_analyze(batch_images)
    end_time = time.time()

    print(f"批量处理{len(batch_images)}张图片: {(end_time - start_time):.2f} 秒")
    print(f"平均每张: {(end_time - start_time)/len(batch_images)*1000:.2f} ms")

    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)


def quick_demo():
    """快速演示示例"""
    print("快速演示 - 分析一张清晰二维码")
    print("-"*60)

    analyzer = QRCodeAnalyzer()

    # 分析第一张清晰图片
    clear_images = glob.glob("sample_data/clear/*.jpg")
    if not clear_images:
        print("未找到示例图片")
        return

    image_path = clear_images[0]
    print(f"分析图片: {image_path}")

    results = analyzer.analyze_image(image_path)

    if results:
        for i, qr in enumerate(results, 1):
            print(f"\n二维码 #{i}:")
            print(f"  📍 位置: ({qr['bbox']['x']}, {qr['bbox']['y']})")
            print(f"  📏 尺寸: {qr['bbox']['width']} x {qr['bbox']['height']}")
            print(f"  📊 面积占比: {qr['area_ratio_percent']:.2f}%")
            print(f"  ✅ 大于5%: {'是' if qr['area_larger_than_5_percent'] else '否'}")
            print(f"  🔍 清晰度: {qr['clarity_class']} (评分: {qr['clarity_score']:.2f})")
            print(f"  🎨 颜色对比: {qr['color_contrast_class']}")
            print(f"  📱 二维码内容: {qr['qr_data'][:50]}...")
    else:
        print("未检测到二维码")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        quick_demo()
    else:
        main()
