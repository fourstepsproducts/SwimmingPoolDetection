import cv2
from ultralytics import YOLO

model = YOLO("yolov8n.pt")
video_path = "backend/uploads/processed-pool-1787292819708-293409003.mp4"
cap = cv2.VideoCapture(video_path)

coords = []
frame_idx = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    if frame_idx % 30 == 0:
        results = model(frame, classes=[0], verbose=False)
        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                cx = (x1 + x2) / 2.0
                cy = y2
                coords.append((cx, cy))
    frame_idx += 1

cap.release()

print(f"Total detections: {len(coords)}")
if coords:
    xs = [c[0] for c in coords]
    ys = [c[1] for c in coords]
    print(f"X range: {min(xs):.1f} to {max(xs):.1f}")
    print(f"Y range: {min(ys):.1f} to {max(ys):.1f}")
    # Print sorted Y coordinates to see distribution
    ys_sorted = sorted(ys)
    print("Y percentiles:")
    for pct in [0, 10, 25, 50, 75, 90, 100]:
        idx = int((len(ys_sorted) - 1) * pct / 100)
        print(f"  {pct}%: {ys_sorted[idx]:.1f}")
