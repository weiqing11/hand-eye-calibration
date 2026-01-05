# 🤖 Dual-Arm Hand-Eye Calibration & Verification Toolkit

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

这是一个专为双臂机器人设计的工程化**手眼标定（Hand-Eye Calibration）**与**可视化验证**工具箱。

本项目针对 **Robot-World-Hand-Eye (眼在手外/相机固定)** 模式设计，直接解析机器人采集的 `.hdf5` 数据文件，利用 AprilTag 进行高精度标定，并提供**渐变色轨迹投影**功能，用于直观验证标定结果的准确性。

## ✨ 核心特性

- **🦾 双臂支持**：支持左臂、右臂单独标定或双臂同时标定。
- **🧮 多算法集成**：内置 OpenCV 的多种标定算法（Shah, Li），同时计算并保存，方便对比。
- **📥 HDF5 原生支持**：直接读取机器人录制的 HDF5 数据集（支持压缩图像），无需繁琐的图片提取步骤。
- **🌈 高级可视化验证**：
  - **渐变色轨迹**：轨迹颜色随时间从浅变深（紫色/橙色系），直观展示运动方向和速度。
  - **动态标注**：实时标记当前帧的机械臂位置。
  - **抗锯齿绘制**：生成高质量的验证图片，轨迹平滑清晰。
- **🧩 模块化架构**：配置、数据加载、几何计算与可视化分离，结构清晰，易于维护。

## 📂 项目结构

```text
hand_eye_project/
├── config/
│   ├── __init__.py
│   └── settings.py          # ⚙️ 全局配置 (路径、内参、Tag尺寸等)
├── utils/
│   ├── __init__.py
│   ├── data_loader.py       # 📥 HDF5 读取与图像解码
│   ├── geometry.py          # 📐 空间坐标变换、四元数处理
│   └── visualizer.py        # 🎨 渐变绘图与标注工具
├── results/                 # 💾 输出目录 (自动生成)
│   ├── calibration_matrix.json  # 标定结果文件
│   └── verification_gradient/   # 验证图片输出
├── calibrate.py             # 🚀 标定主程序
├── verify.py                # ✅ 验证主程序
├── requirements.txt         # 📦 依赖列表
└── README.md                # 📖 说明文档
```
## ⚙️ 配置说明
在使用前，请务必修改 config/settings.py 文件以适配您的硬件和数据路径：
```text
# config/settings.py 示例

# === 数据路径 ===
# 标定数据 (必须包含清晰的 AprilTag)
LEFT_CALIB_DATA = '/path/to/your/left_arm_calib_data.hdf5'
RIGHT_CALIB_DATA = '/path/to/your/right_arm_calib_data.hdf5'

# 验证数据 (任意包含机械臂运动的数据，用于画轨迹)
VERIFY_DATA = '/path/to/your/verification_data.hdf5'

# === 硬件参数 ===
APRILTAG_SIZE = 0.069375  # Tag 边长 (单位: 米)
TAG_FAMILY = 'tag36h11'   # Tag 家族类型

# 相机内参 (fx, fy, cx, cy)
CAMERA_INTRINSICS_MATRIX = np.array([
    [489.02, 0.0, 311.86, 0],
    [0.0, 489.02, 212.15, 0],
    [0.0, 0.0, 1.0, 0],
])
```
## 🚀 快速开始
### 1. 执行标定
运行 calibrate.py 计算相机到基座的变换矩阵。程序会自动检测 AprilTag 并计算 Base 到 Camera 的变换。
```text
# 标定双臂 (推荐)
python calibrate.py --arm both

# 仅标定左臂
python calibrate.py --arm left

# 调试模式 (保存检测失败的图片到 results/debug，用于排查Tag是否清晰)
python calibrate.py --arm both --debug
```
成功运行后，标定结果将保存至 results/calibration_matrix.json。
### 2. 执行验证
运行 verify.py，读取标定结果，并将机械臂的 3D 轨迹投影到 2D 相机图像上。
```text
python verify.py
```
程序会自动读取上一步生成的 JSON 文件。

验证图片将保存在 results/verification_gradient/ 目录下。

效果说明：

- **左臂**：显示为紫色 (Purple) 渐变轨迹。

- **右臂**：显示为橙色 (Orange) 渐变轨迹。

- **轨迹方向**：颜色由浅（过去）到深（现在）。
## 📋 数据格式要求
本项目默认支持以下 HDF5 数据结构（常见于 Agilex/ALOHA 机器人数据）：

图像数据: observations/images/cam_high (JPEG 压缩格式或原始数组)

机械臂位姿:

- **左臂键名**: eef_pose/puppet_eef_pose/left_eef_4D

- **右臂键名**: eef_pose/puppet_eef_pose/right_eef_4D

- **位姿格式**: [x, y, z, qw, qx, qy, qz] (位置 + 四元数)

注意: 如果您的 HDF5 键名不同，请修改 utils/data_loader.py 中的 load_pose_and_image 函数。 注意: 如果您的四元数格式是 [x, y, z, w]，请修改 utils/geometry.py 中的 pose_to_matrix 函数。
## ❓ 常见问题 (FAQ)
- **Q1**: 验证图片中的轨迹与实际物体对不上，偏差很大？
- A: 请按以下顺序检查：

config/settings.py 中的相机内参是否准确（非常重要）。

APRILTAG_SIZE 单位必须是米。

检查 utils/geometry.py 中的四元数顺序是否与数据一致（默认处理为 [w, x, y, z] 转 [x, y, z, w]）。

- **Q2**: 报错 AttributeError: 'NoneType' object has no attribute 'corners'？
- A: 这通常意味着在某些帧中没有检测到 AprilTag。请确保标定数据中 Tag 清晰可见，且没有被手遮挡。建议使用 --debug 模式查看具体哪一帧检测失败。

- **Q3**: 为什么生成的图片中没有轨迹线？
- A: 可能是因为在当前时间窗口 (TRAJECTORY_WINDOW=60) 内，机械臂处于相机视野之外。尝试调整 verify.py 中的采样帧数或窗口大小。
## 📄 License
此项目遵循 MIT 开源协议。
