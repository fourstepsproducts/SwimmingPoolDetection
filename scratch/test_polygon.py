import cv2
import numpy as np
from ultralytics import YOLO

model = YOLO("yolov8n.pt")
video_path = "backend/uploads/processed-pool-1787292819708-293409003.mp4"
cap = cv2.VideoCapture(video_path)

pool_points = {
    "A": {"x": 530.0, "y": 160.0},
    "B": {"x": 1380.0, "y": 160.0},
    "C": {"x": 1520.0, "y": 480.0},
    "D": {"x": 350.0, "y": 480.0}
}

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

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

# The pool water polygon for cv2.pointPolygonTest
poly = pts_src.astype(np.int32)

frame_idx = 0
while frame_idx < 100:
    ret, frame = cap.read()
    if not ret:
        break
    
    if frame_idx % 30 == 0:
        results = model(frame, classes=[0], verbose=False)
        print(f"--- Frame {frame_idx} ---")
        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                cx = (x1 + x2) / 2.0
                cy = y2
                
                # Check if inside polygon
                pt = (cx, cy)
                dist = cv2.pointPolygonTest(poly, pt, False)
                inside = dist >= 0
                
                if inside:
                    # Homography transform
                    pt_img = np.array([[[cx, cy]]], dtype=np.float32)
                    pt_pool = cv2.perspectiveTransform(pt_img, M)
                    tx = pt_pool[0][0][0]
                    ty = pt_pool[0][0][1]
                    v = 1.0 - (ty / 300.0)
                    
                    zone = "ZONE 3"
                    if v < 0.3333:
                        zone = "ZONE 1"
                    elif v < 0.6666:
                        zone = "ZONE 2"
                        
                    print(f"  INSIDE: pt=({cx:.1f}, {cy:.1f}), v={v:.4f} -> {zone}")
                else:
                    print(f"  OUTSIDE: pt=({cx:.1f}, {cy:.1f})")
                    
    frame_idx += 10

cap.release()
