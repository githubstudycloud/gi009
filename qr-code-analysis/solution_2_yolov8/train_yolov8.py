"""
YOLOv8模型训练脚本

用于训练专门的二维码检测YOLOv8模型
"""

import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from ultralytics import YOLO
import os
import yaml


def prepare_dataset_yaml(data_dir: str = "./qr_dataset") -> str:
    """
    准备数据集配置文件

    Args:
        data_dir: 数据集目录

    Returns:
        配置文件路径
    """
    # 数据集结构:
    # qr_dataset/
    #   ├── images/
    #   │   ├── train/
    #   │   └── val/
    #   └── labels/
    #       ├── train/
    #       └── val/

    config = {
        'path': os.path.abspath(data_dir),
        'train': 'images/train',
        'val': 'images/val',
        'nc': 1,  # 类别数量：1（二维码）
        'names': ['qr_code']  # 类别名称
    }

    config_path = os.path.join(data_dir, 'qr_dataset.yaml')

    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False)

    print(f"数据集配置已保存: {config_path}")
    return config_path


def train_yolov8(
    data_yaml: str,
    model_size: str = 'n',
    epochs: int = 100,
    imgsz: int = 640,
    batch: int = 16,
    project: str = 'qr_detection',
    name: str = 'yolov8_qr'
):
    """
    训练YOLOv8模型

    Args:
        data_yaml: 数据集配置文件路径
        model_size: 模型大小 (n/s/m/l/x)
        epochs: 训练轮数
        imgsz: 图像尺寸
        batch: 批次大小
        project: 项目名称
        name: 实验名称
    """
    print("=" * 60)
    print("开始训练YOLOv8二维码检测模型")
    print("=" * 60)

    # 加载预训练模型
    model_name = f'yolov8{model_size}.pt'
    print(f"\n加载预训练模型: {model_name}")
    model = YOLO(model_name)

    # 开始训练
    print(f"\n训练配置:")
    print(f"  数据集: {data_yaml}")
    print(f"  模型大小: {model_size}")
    print(f"  训练轮数: {epochs}")
    print(f"  图像尺寸: {imgsz}")
    print(f"  批次大小: {batch}")

    results = model.train(
        data=data_yaml,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        project=project,
        name=name,
        patience=20,  # 早停耐心值
        save=True,
        device='cuda' if __import__('torch').cuda.is_available() else 'cpu',
        workers=4,
        pretrained=True,
        optimizer='AdamW',
        verbose=True,
        seed=42,
        deterministic=True,
        single_cls=True,  # 单类别检测
        rect=False,
        cos_lr=True,
        close_mosaic=10,
        amp=True,  # 自动混合精度
        fraction=1.0,
        profile=False,
        freeze=None,
        lr0=0.01,
        lrf=0.01,
        momentum=0.937,
        weight_decay=0.0005,
        warmup_epochs=3.0,
        warmup_momentum=0.8,
        warmup_bias_lr=0.1,
        box=7.5,
        cls=0.5,
        dfl=1.5,
        pose=12.0,
        kobj=1.0,
        label_smoothing=0.0,
        nbs=64,
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        degrees=0.0,
        translate=0.1,
        scale=0.5,
        shear=0.0,
        perspective=0.0,
        flipud=0.0,
        fliplr=0.5,
        mosaic=1.0,
        mixup=0.0,
        copy_paste=0.0
    )

    print("\n训练完成！")
    print(f"最佳模型保存在: {project}/{name}/weights/best.pt")

    return results


def validate_model(model_path: str, data_yaml: str):
    """
    验证训练好的模型

    Args:
        model_path: 模型路径
        data_yaml: 数据集配置文件
    """
    print("\n" + "=" * 60)
    print("验证模型性能")
    print("=" * 60)

    model = YOLO(model_path)
    results = model.val(data=data_yaml)

    print("\n验证结果:")
    print(f"  mAP50: {results.box.map50:.4f}")
    print(f"  mAP50-95: {results.box.map:.4f}")
    print(f"  Precision: {results.box.mp:.4f}")
    print(f"  Recall: {results.box.mr:.4f}")

    return results


def export_model(model_path: str, format: str = 'onnx'):
    """
    导出模型为其他格式

    Args:
        model_path: 模型路径
        format: 导出格式 (onnx/torchscript/tflite/edgetpu/tfjs等)
    """
    print(f"\n导出模型为 {format} 格式...")

    model = YOLO(model_path)
    model.export(format=format)

    print(f"模型已导出为 {format} 格式")


def create_sample_annotations():
    """
    创建示例标注文件说明
    """
    annotation_example = """
# YOLO标注格式说明

每个图像对应一个txt文件，文件名相同。
每行表示一个目标，格式为：

class_id x_center y_center width height

其中：
- class_id: 类别ID（二维码为0）
- x_center, y_center: 边界框中心点坐标（归一化到0-1）
- width, height: 边界框宽高（归一化到0-1）

示例：
0 0.5 0.5 0.3 0.3

这表示图像中有一个二维码，中心在图像中心，宽高为图像尺寸的30%。

# 如何生成标注

1. 使用LabelImg标注工具：
   pip install labelImg
   labelImg

2. 选择YOLO格式输出

3. 标注所有二维码，保存txt文件

4. 组织数据集结构：
   qr_dataset/
     ├── images/
     │   ├── train/  (训练图像)
     │   └── val/    (验证图像)
     └── labels/
         ├── train/  (训练标注)
         └── val/    (验证标注)

5. 运行训练脚本
"""

    with open("ANNOTATION_GUIDE.txt", 'w', encoding='utf-8') as f:
        f.write(annotation_example)

    print("标注指南已保存: ANNOTATION_GUIDE.txt")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='YOLOv8二维码检测模型训练')
    parser.add_argument('--data', type=str, default='./qr_dataset',
                       help='数据集目录')
    parser.add_argument('--model-size', type=str, default='n',
                       choices=['n', 's', 'm', 'l', 'x'],
                       help='模型大小')
    parser.add_argument('--epochs', type=int, default=100,
                       help='训练轮数')
    parser.add_argument('--batch', type=int, default=16,
                       help='批次大小')
    parser.add_argument('--imgsz', type=int, default=640,
                       help='图像尺寸')
    parser.add_argument('--validate', action='store_true',
                       help='验证模型')
    parser.add_argument('--model', type=str,
                       help='要验证的模型路径')
    parser.add_argument('--export', type=str,
                       choices=['onnx', 'torchscript', 'tflite'],
                       help='导出模型格式')
    parser.add_argument('--create-guide', action='store_true',
                       help='创建标注指南')

    args = parser.parse_args()

    if args.create_guide:
        create_sample_annotations()
        return

    if args.validate:
        if not args.model:
            print("错误: 验证模式需要指定 --model 参数")
            return

        data_yaml = prepare_dataset_yaml(args.data)
        validate_model(args.model, data_yaml)
        return

    if args.export:
        if not args.model:
            print("错误: 导出模式需要指定 --model 参数")
            return

        export_model(args.model, args.export)
        return

    # 训练模式
    if not os.path.exists(args.data):
        print(f"错误: 数据集目录不存在: {args.data}")
        print("\n请先准备数据集，或使用 --create-guide 查看标注指南")
        return

    # 准备数据集配置
    data_yaml = prepare_dataset_yaml(args.data)

    # 开始训练
    train_yolov8(
        data_yaml=data_yaml,
        model_size=args.model_size,
        epochs=args.epochs,
        batch=args.batch,
        imgsz=args.imgsz
    )


if __name__ == "__main__":
    # 如果没有命令行参数，显示帮助信息
    if len(sys.argv) == 1:
        print("YOLOv8二维码检测模型训练脚本")
        print("\n使用示例:")
        print("  1. 创建标注指南:")
        print("     python train_yolov8.py --create-guide")
        print("\n  2. 训练模型:")
        print("     python train_yolov8.py --data ./qr_dataset --epochs 100")
        print("\n  3. 验证模型:")
        print("     python train_yolov8.py --validate --model best.pt --data ./qr_dataset")
        print("\n  4. 导出模型:")
        print("     python train_yolov8.py --export onnx --model best.pt")
        print("\n使用 --help 查看所有参数")
    else:
        main()
