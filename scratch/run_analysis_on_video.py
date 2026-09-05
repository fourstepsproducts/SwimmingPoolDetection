import cv2
import numpy as np
import json
from ultralytics import YOLO

model = YOLO("yolov8n.pt")
video_path = "backend/uploads/processed-pool-1787290055522-699167834.mp4"
cap = cv2.VideoCapture(video_path)

pool_points = {
    "A": {"x": 600.0, "y": 300.0},
    "B": {"x": 1320.0, "y": 300.0},
    "C": {"x": 1800.0, "y": 950.0},
    "D": {"x": 120.0, "y": 950.0}
}

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f"Video resolution: {width}x{height}")

ref_w = 1920.0
ref_h = 1080.0
scale_x = width / ref_w
scale_y = height / ref_h

pts_src = np.array([
    [pool_points["D"]["x"] * scale_x, pool_points["D"]["y"] * scale_y], # D
    [pool_points["C"]["x"] * scale_x, pool_points["C"]["y"] * scale_y], # C
    [pool_points["B"]["x"] * scale_x, pool_points["B"]["y"] * scale_y], # B
    [pool_points["A"]["x"] * scale_x, pool_points["A"]["y"] * scale_y]  # A
], dtype=np.float32)

pts_dst = np.array([
    [0.0, 300.0],
    [100.0, 300.0],
    [100.0, 0.0],
    [0.0, 0.0]
], dtype=np.float32)

M = cv2.getPerspectiveTransform(pts_src, pts_dst)

frame_idx = 0
while frame_idx < 100:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Run YOLO
    results = model(frame, classes=[0], verbose=False)
    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            conf = float(box.conf[0])
            cx = (x1 + x2) / 2.0
            cy = y2
            
            # Homography transform
            pt_img = np.array([[[cx, cy]]], dtype=np.float32)
            pt_pool = cv2.perspectiveTransform(pt_img, M)
            tx = pt_pool[0][0][0]
            ty = pt_pool[0][0][1]
            
            v = 1.0 - (ty / 300.0)
            
            print(f"Frame {frame_idx}: Person bottom-center: ({cx:.1f}, {cy:.1f}), tx: {tx:.1f}, ty: {ty:.1f}, v: {v:.4f}")
            
    frame_idx += 10 # skip frames to get different positions

cap.release()
