import h5py
import numpy as np
import cv2
from typing import Tuple, Optional

def decode_image(compressed_data: np.ndarray) -> Optional[np.ndarray]:
    """解码 HDF5 中的压缩图像"""
    try:
        if isinstance(compressed_data, np.ndarray):
            img_data = compressed_data.astype(np.uint8)
        else:
            img_data = np.frombuffer(compressed_data, dtype=np.uint8)
        return cv2.imdecode(img_data, cv2.IMREAD_COLOR)
    except Exception as e:
        print(f"Image decoding failed: {e}")
        return None

def load_pose_and_image(h5_file: h5py.File, timestep: int, arm: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    读取指定时间步的 图像 和 机械臂位姿
    返回: (image, position, quaternion_wxyz)
    """
    # 读取图像
    img_data = h5_file["observations/images/cam_high"][timestep]
    img = decode_image(img_data)
    
    # 读取位姿
    if arm == "left":
        pose = h5_file["eef_pose/puppet_eef_pose/left_eef_4D"][timestep]
    else:
        pose = h5_file["eef_pose/puppet_eef_pose/right_eef_4D"][timestep]
        
    # 解析位姿 (x,y,z, qw,qx,qy,qz, gripper)
    position = pose[0:3]
    # 注意：原始数据是 (qw, qx, qy, qz)，SciPy需要 (qx, qy, qz, qw)
    # 我们这里返回原始格式，在 geometry 中处理转换
    quaternion_wxyz = pose[3:7] 
    
    return img, position, quaternion_wxyz