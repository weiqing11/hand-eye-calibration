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
