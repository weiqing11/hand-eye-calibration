🤖 Hand-Eye Calibration & Verification Toolkit
这是一个用于双臂机器人系统的手眼标定（Hand-Eye Calibration）与可视化验证工具箱。

本项目支持 Robot-World-Hand-Eye（眼在手外/相机固定在基座）模式，通过解析 HDF5 格式的机器人数据（包含图像和四元数位姿），利用 AprilTag 进行标定，并提供带有渐变色轨迹的高级可视化验证功能。

✨ 主要特性
双臂支持：支持左臂、右臂单独或同时标定。

多算法对比：集成 OpenCV 的多种手眼标定算法（Shah, Li），自动计算并保存结果。

HDF5 数据流：直接读取机器人采集的 HDF5 数据集，无需手动提取图片。

高级可视化验证：

渐变色轨迹：使用 Matplotlib 色板生成随时间渐变的轨迹线，直观展示运动方向。

平滑绘制：支持抗锯齿线段绘制。

当前点高亮：动态标记当前帧的机械臂位置。

模块化设计：配置、数据加载、几何计算、可视化分离，易于扩展和维护。

📂 项目结构
hand_eye_project/
├── config/
│   ├── __init__.py
│   └── settings.py          # ⚙️ 全局配置 (路径、内参、Tag尺寸)
├── utils/
│   ├── __init__.py
│   ├── data_loader.py       # 📥 HDF5 读取与图像解码
│   ├── geometry.py          # 📐 坐标变换、四元数处理、3D投影
│   └── visualizer.py        # 🎨 渐变绘图、标注工具
├── results/                 # 💾 输出目录 (JSON结果 & 验证图片)
├── calibrate.py             # 🚀 标定主程序
├── verify.py                # ✅ 验证主程序
├── requirements.txt         # 📦 依赖列表
└── README.md                # 📖 说明文档

🛠️ 安装与环境
安装依赖

pip install -r requirements.txt

依赖库说明

pupil-apriltags: 高性能 AprilTag 检测库。

scipy: 用于空间旋转和四元数计算。

h5py: 处理机器人录制的数据集。

opencv-python, matplotlib, numpy, tqdm.

⚙️ 配置说明
在使用前，请打开 config/settings.py 修改以下关键参数：

# config/settings.py

# === 数据路径 ===
# 用于标定的数据 (必须包含清晰的 AprilTag)
LEFT_CALIB_DATA = '/path/to/your/left_arm_calib_data.hdf5'
RIGHT_CALIB_DATA = '/path/to/your/right_arm_calib_data.hdf5'

# 用于验证的数据 (任意包含机械臂运动的数据)
VERIFY_DATA = '/path/to/your/verification_data.hdf5'

# === 硬件参数 ===
APRILTAG_SIZE = 0.069375  # Tag 边长 (米)
TAG_FAMILY = 'tag36h11'   # Tag 类型

# 相机内参矩阵
CAMERA_INTRINSICS_MATRIX = np.array([...])

🚀 使用指南 
运行 calibrate.py 计算相机到基座的变换矩阵。

# 标定双臂 (默认)
python calibrate.py --arm both

# 仅标定左臂
python calibrate.py --arm left

# 开启 Debug 模式 (保存检测失败的图片)
python calibrate.py --arm both --debug

输出：结果将保存为 results/calibration_matrix.json。

内容：包含不同算法（Shah, Li）计算出的变换矩阵。

运行 verify.py 读取标定结果，并将机械臂轨迹投影到相机图像上进行验证。

python verify.py

输入：自动读取 results/calibration_matrix.json 和配置中的 VERIFY_DATA。

输出：验证图片保存在 results/verification_gradient/ 目录下。

效果：

🟣 左臂：紫色渐变轨迹。

🟠 右臂：橙色渐变轨迹。

轨迹颜色由浅入深，代表时间流逝方向。