import argparse
import h5py
import numpy as np
import json
import os
import cv2
from config import settings
from utils import data_loader, geometry, visualizer

# 定义轨迹窗口大小 (显示过去多少帧)
TRAJECTORY_WINDOW = 60 

def verify_dual_arm(h5_path, calib_data, intrinsics, output_dir):
    print(f"Verifying data: {h5_path}")
    print(f"Output directory: {output_dir}")
    print(f"Trajectory mode: Gradient Line (Window size: {TRAJECTORY_WINDOW})")
    
    # 1. 准备配置
    # 将原来的固定 color 改为 matplotlib 的 colormap 名称
    arms_config = []
    
    if "left" in calib_data:
        T_matrix = np.array(calib_data["left"]["Shah"])
        arms_config.append({
            "name": "left",
            "T_base2cam": T_matrix, 
            "colormap": "Purples", # 使用紫色系渐变
            "label": "L"
        })
        
    if "right" in calib_data:
        T_matrix = np.array(calib_data["right"]["Shah"])
        arms_config.append({
            "name": "right",
            "T_base2cam": T_matrix,
            "colormap": "Oranges", # 使用橙色系渐变
            "label": "R"
        })

    if not arms_config:
        print("No calibration data found in result file.")
        return

    # 2. 读取数据并预计算所有像素坐标
    with h5py.File(h5_path, 'r') as f:
        total_frames = f["observations/images/cam_high"].shape[0]
        arm_pixels_map = {}
        
        for arm in arms_config:
            name = arm["name"]
            key = f"eef_pose/puppet_eef_pose/{name}_eef_4D"
            if key not in f: continue
                
            # Base 系坐标 -> Cam 系坐标
            pos_base = f[key][:, :3]
            N = pos_base.shape[0]
            pos_base_homo = np.hstack((pos_base, np.ones((N, 1))))
            pos_cam = (arm["T_base2cam"] @ pos_base_homo.T).T[:, :3]
            
            # Cam 系 3D -> 图像 2D
            pixels = geometry.project_points_3d_to_2d(pos_cam, intrinsics)
            arm_pixels_map[name] = pixels
            print(f"Processed {name} arm: {N} frames.")

        # 3. 绘图循环 (采样验证)
        # 采样 15 帧进行验证，覆盖整个流程
        sample_steps = np.linspace(TRAJECTORY_WINDOW, total_frames-2, 15, dtype=int)
        # 确保包含最后一帧
        if total_frames -1 not in sample_steps:
             sample_steps = np.append(sample_steps, total_frames-1)

        for t in sample_steps:
            img_data = f["observations/images/cam_high"][t]
            img = data_loader.decode_image(img_data)
            if img is None: continue
            
            vis_img = img.copy()
            
            # 定义当前轨迹窗口的范围 [start, end)
            start_idx = t
            end_idx = min(total_frames - 1, t + TRAJECTORY_WINDOW)
            
            # --- 绘制轨迹线 (先画线，在底下) ---
            for arm in arms_config:
                name = arm["name"]
                if name not in arm_pixels_map: continue
                
                all_pixels = arm_pixels_map[name]
                # 截取当前窗口的轨迹段
                path_segment = all_pixels[start_idx:end_idx]
                
                # 调用新的渐变线绘制函数
                vis_img = visualizer.draw_gradient_path(
                    vis_img, path_segment, arm["colormap"])

            # --- 绘制当前位置标记 (后画点，在顶层) ---
            for arm in arms_config:
                name = arm["name"]
                if name not in arm_pixels_map: continue
                
                all_pixels = arm_pixels_map[name]
                # 获取当前时刻 t 的像素点
                if t < len(all_pixels):
                    current_pixel = all_pixels[t]
                    vis_img = visualizer.draw_current_marker(
                        vis_img, current_pixel, arm["colormap"], arm["label"])
            
            # 添加帧数信息
            cv2.putText(vis_img, f"Frame: {t}/{total_frames}", (30, vis_img.shape[0]-30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

            # 保存
            visualizer.save_image(vis_img, f"verify_gradient_t{t:04d}.png", output_dir)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--calib-file", default=settings.CALIB_RESULT_FILE)
    args = parser.parse_args()
    
    if not os.path.exists(args.calib_file):
        print("Calibration file not found! Please run calibrate.py first.")
        return
        
    with open(args.calib_file, 'r') as f:
        calib_data = json.load(f)
    
    output_dir = os.path.join(settings.RESULT_DIR, 'verification_gradient')
    os.makedirs(output_dir, exist_ok=True)
    
    # 确保这里使用的 HDF5 文件路径是正确的验证数据路径
    verify_dual_arm(settings.VERIFY_DATA, calib_data, 
                   settings.CAMERA_INTRINSICS_MATRIX, output_dir)

if __name__ == "__main__":
    main()