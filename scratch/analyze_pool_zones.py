import cv2
import numpy as np

input_path = r"C:\Users\WINDOWS 11\.gemini\antigravity-ide\brain\8d0edfed-a44f-45b6-b892-8676fe5e7503\media__1788499137763.png"
img = cv2.imread(input_path)
h, w, _ = img.shape
print(f"Dimensions: {w}x{h}")

# The pool boundary in media__1788499137763.png is drawn in bright blue (BGR approx [255, 0, 0] or similar)
# Let's locate the blue boundary pixels to find the 4 corners of the pool polygon
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
# Blue color range in HSV: Hue ~ 100-130, Saturation > 150, Value > 150
blue_mask = cv2.inRange(hsv, np.array([100, 150, 150]), np.array([130, 255, 255]))

ys, xs = np.where(blue_mask > 0)
print(f"Found {len(xs)} blue boundary pixels.")

# Top-Left corner (smallest x, smallest y)
# Top-Right corner (largest x, smallest y)
# Bottom-Right corner (largest x, largest y)
# Bottom-Left corner (smallest x, largest y)
pts = np.column_stack((xs, ys))

# Let's find the convex hull or extreme corners of the blue polygon
hull = cv2.convexHull(pts)
print("Convex hull points:")
for pt in hull:
    print(tuple(pt[0]))
