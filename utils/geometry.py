import numpy as np
from scipy.spatial.transform import Rotation as Rot

def pose_to_matrix(position: np.ndarray, quaternion_wxyz: np.ndarray) -> np.ndarray:
    """
    将位置和四元数转换为 4x4 变换矩阵 T_base2gripper
    输入 quaternion_wxyz: [w, x, y, z]
    """
    # SciPy 需要 [x, y, z, w]
    quat_scipy = np.array([quaternion_wxyz[1], quaternion_wxyz[2], quaternion_wxyz[3], quaternion_wxyz[0]])
    rot = Rot.from_quat(quat_scipy)
    
    T = np.eye(4)
    T[:3, :3] = rot.as_matrix()
    T[:3, 3] = position
    return T

def invert_transform(T: np.ndarray) -> np.ndarray:
    """计算逆变换矩阵"""
    R = T[:3, :3]
    t = T[:3, 3]
    T_inv = np.eye(4)
    T_inv[:3, :3] = R.T
    T_inv[:3, 3] = -R.T @ t
    return T_inv

def project_points_3d_to_2d(points_3d: np.ndarray, intrinsics: np.ndarray) -> np.ndarray:
    """
    3D 点 (Cam系) -> 2D 像素
    points_3d: (N, 3)
    intrinsics: (3, 3) 或 (3, 4)
    """
    if len(points_3d) == 0:
        return np.array([])
        
    N = points_3d.shape[0]
    # 构造齐次坐标 (N, 4)
    points_homo = np.hstack((points_3d, np.ones((N, 1))))
    
    # 确保内参是 3x4
    if intrinsics.shape == (3, 3):
        K = np.hstack((intrinsics, np.zeros((3, 1))))
    else:
        K = intrinsics

    # 投影 (3, 4) @ (4, N) -> (3, N)
    px_homo = K @ points_homo.T
    px_homo = px_homo.T # (N, 3)
    
    # 归一化 u = x/z, v = y/z
    z = px_homo[:, 2:3]
    # 避免除以0
    z[z == 0] = 1e-5
    
    pixels = px_homo[:, :2] / z
    return pixels