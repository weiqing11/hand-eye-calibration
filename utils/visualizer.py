import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

def get_gradient_colors(colormap_name, n_steps, start_intensity=0.3, end_intensity=1.0):
    """
    生成渐变色列表 (用于 OpenCV BGR 格式)
    :param colormap_name: matplotlib 色板名称 (e.g., 'Purples', 'Oranges')
    :param n_steps: 需要多少种颜色 (对应轨迹段数)
    :param start_intensity: 起始颜色的强度 (0.0-1.0)，避免太淡看不见
    :param end_intensity: 结束颜色的强度 (0.0-1.0)
    """
    cmap = plt.get_cmap(colormap_name)
    # 生成从淡到深的颜色索引
    indices = np.linspace(start_intensity, end_intensity, n_steps)
    # 获取 RGBA 颜色
    colors_rgba = cmap(indices)
    # 转换为 OpenCV 需要的 BGR 格式 (0-255)
    # matplotlib 返回的是 [R, G, B, A] 0-1 float
    # OpenCV 需要 (B, G, R) 0-255 int
    colors_bgr = [
        (int(c[2] * 255), int(c[1] * 255), int(c[0] * 255)) 
        for c in colors_rgba
    ]
    return colors_bgr

def draw_gradient_path(img_bgr: np.ndarray, path_pixels: np.ndarray, colormap_name: str):
    """
    绘制渐变色的连续轨迹线
    :param img_bgr: 底图
    :param path_pixels: 轨迹点坐标数组 (N, 2)
    :param colormap_name: 色板名称
    """
    if len(path_pixels) < 2:
        return img_bgr
        
    vis_img = img_bgr.copy()
    h, w = vis_img.shape[:2]
    
    num_segments = len(path_pixels) - 1
    # 获取渐变色列表，颜色数量等于线段数量
    colors = get_gradient_colors(colormap_name, num_segments)
    
    # 遍历点对，绘制线段
    for i in range(num_segments):
        pt1 = path_pixels[i]
        pt2 = path_pixels[i+1]
        
        # 简单的边界检查，确保起点或终点至少有一个在图内才绘制
        if (0 <= pt1[0] < w and 0 <= pt1[1] < h) or \
           (0 <= pt2[0] < w and 0 <= pt2[1] < h):
            
            start_pt = (int(pt1[0]), int(pt1[1]))
            end_pt = (int(pt2[0]), int(pt2[1]))
            
            # 线条粗细随时间轻微增加，增强动态感
            thickness = 2 + int(i / num_segments * 2) 
            
            cv2.line(vis_img, start_pt, end_pt, colors[i], thickness=thickness, lineType=cv2.LINE_AA)
            
    return vis_img

# --- 以下是辅助绘图函数 ---

def draw_current_marker(img_bgr: np.ndarray, current_pixel: np.ndarray, 
                        colormap_name: str, label: str):
    """绘制当前位置的大圆点和标签"""
    vis_img = img_bgr.copy()
    h, w = vis_img.shape[:2]
    
    # 获取该色板最深的颜色作为标记色
    marker_color = get_gradient_colors(colormap_name, 1, start_intensity=1.0)[0]
    
    cx, cy = int(current_pixel[0]), int(current_pixel[1])
    
    if 0 <= cx < w and 0 <= cy < h:
        # 画外圈辉光效果
        # cv2.circle(vis_img, (cx, cy), 12, marker_color, 2, cv2.LINE_AA)
        # 画实心点
        cv2.circle(vis_img, (cx, cy), 8, marker_color, -1, cv2.LINE_AA)
        # 画文字
        cv2.putText(vis_img, label, (cx + 15, cy + 5),
                   cv2.FONT_HERSHEY_DUPLEX, 0.8, marker_color, 2, cv2.LINE_AA)
                   
    return vis_img

def draw_detection(img: np.ndarray, detection, tag_id: str):
    """绘制 AprilTag 检测框"""
    vis = img.copy()
    corners = detection.corners.astype(int)
    cv2.polylines(vis, [corners], True, (50, 255, 50), 2, cv2.LINE_AA)
    center = tuple(detection.center.astype(int))
    cv2.circle(vis, center, 4, (0, 0, 255), -1)
    cv2.putText(vis, str(tag_id), (center[0]+10, center[1]), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (50, 255, 50), 2)
    return vis

def save_image(img: np.ndarray, filename: str, directory: str):
    """保存图片"""
    if not os.path.exists(directory):
        os.makedirs(directory)
    path = os.path.join(directory, filename)
    cv2.imwrite(path, img)
    print(f"Saved: {path}")