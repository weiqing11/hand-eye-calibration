import numpy as np
import os

# === 路径配置 ===
# 输入数据路径
LEFT_CALIB_DATA = '/home/agilex/Deployment_agilex/cobot_magic/collect_data/data/20250909/april_tag/episode_2.hdf5'
RIGHT_CALIB_DATA = '/home/agilex/Deployment_agilex/cobot_magic/collect_data/data/20250909/april_tag/episode_3.hdf5'
VERIFY_DATA = "/home/agilex/Deployment_agilex/cobot_magic/collect_data/data/stack_bowls_two/clean/episode_0.hdf5"

# 输出路径
RESULT_DIR = 'results'
CALIB_RESULT_FILE = os.path.join(RESULT_DIR, 'calibration_matrix.json')

# === 硬件参数 ===
# AprilTag 边长 (米)
APRILTAG_SIZE = 0.069375
# AprilTag 检测家族
TAG_FAMILY = 'tag36h11'

# 相机内参 (fx, fy, cx, cy)
CAMERA_INTRINSICS_MATRIX = np.array([
    [489.0217, 0.0, 311.8682, 0],
    [0.0, 489.0217, 212.1527, 0],
    [0.0, 0.0, 1.0, 0],
])

def get_camera_params():
    """返回用于 detector 的参数列表 [fx, fy, cx, cy]"""
    return [
        CAMERA_INTRINSICS_MATRIX[0, 0],
        CAMERA_INTRINSICS_MATRIX[1, 1],
        CAMERA_INTRINSICS_MATRIX[0, 2],
        CAMERA_INTRINSICS_MATRIX[1, 2]
    ]