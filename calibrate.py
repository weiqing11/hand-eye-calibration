import argparse
import h5py
import cv2
import numpy as np
import json
import os
from tqdm import tqdm
from pupil_apriltags import Detector

from config import settings
from utils import data_loader, geometry, visualizer

def run_calibration(arm_name, h5_path, detector, intrinsics_params, debug=False):
    print(f"\nProcessing {arm_name.upper()} arm...")
    
    # 存储用于标定的列表
    R_gripper2base, t_gripper2base = [], []
    R_target2cam, t_target2cam = [], []
    
    valid_frames = 0
    
    with h5py.File(h5_path, "r") as f:
        total_frames = f["observations/images/cam_high"].shape[0]
        
        # 每100帧采样一次
        for t in tqdm(range(0, total_frames, 100)):
            img, pos, quat = data_loader.load_pose_and_image(f, t, arm_name)
            if img is None: continue
                
            # 1. AprilTag 检测
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            detections = detector.detect(gray, estimate_tag_pose=True, 
                                       camera_params=intrinsics_params, 
                                       tag_size=settings.APRILTAG_SIZE)
            
            if len(detections) != 1:
                if debug:
                    vis = visualizer.draw_detection(img, detections[0] if detections else None, "FAIL")
                    visualizer.save_image(vis, f"{t}_fail.png", os.path.join(settings.RESULT_DIR, 'debug'))
                continue
                
            # 2. 收集数据: Tag -> Camera
            det = detections[0]
            R_target2cam.append(det.pose_R)
            t_target2cam.append(det.pose_t.reshape(3, 1))
            
            # 3. 收集数据: Gripper -> Base
            # 原始数据是 Base -> Gripper
            T_base2gripper = geometry.pose_to_matrix(pos, quat)
            # 转换为 Gripper -> Base (因为 calibrateHandEye 需要这个方向)
            T_gripper2base = geometry.invert_transform(T_base2gripper)
            
            R_gripper2base.append(T_gripper2base[:3, :3])
            t_gripper2base.append(T_gripper2base[:3, 3].reshape(3,1))
            
            valid_frames += 1

    if valid_frames < 5:
        print(f"Not enough valid frames for {arm_name}.")
        return None

    # 4. 执行手眼标定 (使用 Shah 和 Li 方法)
    methods = [
        (cv2.CALIB_ROBOT_WORLD_HAND_EYE_SHAH, "Shah"),
        (cv2.CALIB_ROBOT_WORLD_HAND_EYE_LI, "Li")
    ]
    
    results = {}
    
    print(f"Calibrating {arm_name} with {len(R_gripper2base)} frames...")
    
    for method_enum, method_name in methods:
        try:
            R_cam2base_cv, t_cam2base_cv = cv2.calibrateHandEye(
                R_gripper2base=R_gripper2base,
                t_gripper2base=t_gripper2base,
                R_target2cam=R_target2cam,
                t_target2cam=t_target2cam,
                method=method_enum
            )
            
            # 这里的 R_cam2base_cv 实际上是 Base -> Cam 的变换 (OpenCV 定义)
            T_base2cam = np.eye(4)
            T_base2cam[:3, :3] = R_cam2base_cv
            T_base2cam[:3, 3] = t_cam2base_cv.flatten()
            
            # 求逆得到 Cam -> Base (即 T_cam2base)
            T_cam2base = geometry.invert_transform(T_base2cam)
            
            results[method_name] = T_cam2base.tolist()
            
            # 计算行列式验证 (原代码功能)
            det = np.linalg.det(T_cam2base[:3, :3])
            print(f"  [{method_name}] det={det:.6f}")
            
        except Exception as e:
            print(f"  [{method_name}] Failed: {e}")

    return results # 返回包含 Shah 和 Li 的字典

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", default="both", choices=["left", "right", "both"])
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    detector = Detector(families=settings.TAG_FAMILY)
    cam_params = settings.get_camera_params()
    
    results = {}
    
    # === 处理 Left Arm ===
    if args.arm in ["left", "both"]:
        # 注意：这里返回的 T 现在是一个字典，例如 {'Shah': [[...]], 'Li': [[...]]}
        T_dict = run_calibration("left", settings.LEFT_CALIB_DATA, detector, cam_params, args.debug)
        
        if T_dict is not None:
            results["left"] = T_dict 
            
            # 打印结果供查看
            print("Left Arm Calibration Results:")
            for method, matrix in T_dict.items():
                print(f"  [{method}] Matrix:\n{np.array(matrix)}")

    # === 处理 Right Arm ===
    if args.arm in ["right", "both"]:
        T_dict = run_calibration("right", settings.RIGHT_CALIB_DATA, detector, cam_params, args.debug)
        
        if T_dict is not None:
            results["right"] = T_dict
            
            print("Right Arm Calibration Results:")
            for method, matrix in T_dict.items():
                print(f"  [{method}] Matrix:\n{np.array(matrix)}")

    # === 保存结果 ===
    os.makedirs(settings.RESULT_DIR, exist_ok=True)
    with open(settings.CALIB_RESULT_FILE, 'w') as f:
        # results 结构现在是: {'left': {'Shah': [...], 'Li': [...]}, 'right': ...}
        json.dump(results, f, indent=4)
        
    print(f"\nResults saved to {settings.CALIB_RESULT_FILE}")

if __name__ == "__main__":
    main()