import cv2
import numpy as np

img_path = r"C:\Users\WINDOWS 11\.gemini\antigravity-ide\brain\4214b2c9-acdd-4546-81b9-a8a696ac3f69\media__1787294620366.jpg"
img = cv2.imread(img_path)

h, w, c = img.shape

# Isolate blue
b = img[:, :, 0].astype(float)
g = img[:, :, 1].astype(float)
r = img[:, :, 2].astype(float)

blue_mask = (b > 120) & (b - r > 30) & (b - g > 30)
# Clean mask
kernel = np.ones((3,3), np.uint8)
blue_mask = cv2.morphologyEx(blue_mask.astype(np.uint8) * 255, cv2.MORPH_CLOSE, kernel)

# Find contours
contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# Find the largest contour
cnt = max(contours, key=cv2.contourArea)

print(f"Largest blue contour area: {cv2.contourArea(cnt):.1f}, points: {len(cnt)}")

# Let's approximate the contour using different tolerances to find a clean set of polygon coordinates:
for eps_factor in [0.001, 0.002, 0.005, 0.01]:
    eps = eps_factor * cv2.arcLength(cnt, True)
    approx = cv2.approxPolyDP(cnt, eps, True)
    print(f"Tolerance {eps_factor} -> Vertices: {len(approx)}")
    if len(approx) < 40:
        pts = [list(pt[0]) for pt in approx]
        # Sort or print them in clockwise/counterclockwise contour order
        print(pts)
