import cv2
from ultralytics import YOLO

model = YOLO("yolov8n.pt")
img_path = r"C:\Users\WINDOWS 11\.gemini\antigravity-ide\brain\8d0edfed-a44f-45b6-b892-8676fe5e7503\media__1788499137763.png"
img = cv2.imread(img_path)

# Test with different conf thresholds
for conf_thresh in [0.25, 0.20, 0.15, 0.10]:
    results = model(img, classes=[0], conf=conf_thresh, verbose=False)
    boxes = results[0].boxes
    print(f"Conf threshold {conf_thresh} -> {len(boxes)} detections")
    for box in boxes:
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        conf = float(box.conf[0])
        print(f"   Person at cx={(x1+x2)/2:.1f}, cy={y2:.1f}, conf={conf:.2f}")
