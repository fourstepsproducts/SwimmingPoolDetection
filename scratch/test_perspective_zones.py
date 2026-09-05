import cv2
import numpy as np

# Load pool calibration coordinates (in 1920x1080 reference resolution)
wb = [
    {"x": 771.3, "y": 85.4},   # 0: Top-Left
    {"x": 1024.0, "y": 79.7},  # 1: Top-Mid
    {"x": 1276.6, "y": 74.0},  # 2: Top-Right
    {"x": 1566.0, "y": 234.5}, # 3: Right-Mid
    {"x": 1855.4, "y": 396.9}, # 4: Bottom-Right
    {"x": 1190.9, "y": 429.0}, # 5: Bottom-Mid
    {"x": 526.4, "y": 462.9},  # 6: Bottom-Left
    {"x": 648.9, "y": 274.2}   # 7: Left-Mid
]

def get_zone_polygons(img_w, img_h):
    scale_x = img_w / 1920.0
    scale_y = img_h / 1080.0
    
    P_TL = np.array([wb[0]["x"] * scale_x, wb[0]["y"] * scale_y], dtype=np.float32)
    P_TR = np.array([wb[2]["x"] * scale_x, wb[2]["y"] * scale_y], dtype=np.float32)
    P_BR = np.array([wb[4]["x"] * scale_x, wb[4]["y"] * scale_y], dtype=np.float32)
    P_BL = np.array([wb[6]["x"] * scale_x, wb[6]["y"] * scale_y], dtype=np.float32)
    
    # 1/3 and 2/3 along Left and Right edges
    L1 = P_TL + (1.0 / 3.0) * (P_BL - P_TL)
    R1 = P_TR + (1.0 / 3.0) * (P_BR - P_TR)
    
    L2 = P_TL + (2.0 / 3.0) * (P_BL - P_TL)
    R2 = P_TR + (2.0 / 3.0) * (P_BR - P_TR)
    
    poly_red = np.array([P_TL, P_TR, R1, L1], dtype=np.int32)
    poly_yellow = np.array([L1, R1, R2, L2], dtype=np.int32)
    poly_green = np.array([L2, R2, P_BR, P_BL], dtype=np.int32)
    poly_pool = np.array([P_TL, P_TR, P_BR, P_BL], dtype=np.int32)
    
    return poly_red, poly_yellow, poly_green, poly_pool, L1, R1, L2, R2

poly_red, poly_yellow, poly_green, poly_pool, L1, R1, L2, R2 = get_zone_polygons(1920, 1080)
print("Red Zone Vertices:\n", poly_red)
print("Yellow Zone Vertices:\n", poly_yellow)
print("Green Zone Vertices:\n", poly_green)
