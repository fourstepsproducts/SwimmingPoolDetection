import cv2
import numpy as np
import json

img_path = r"C:\Users\WINDOWS 11\.gemini\antigravity-ide\brain\4214b2c9-acdd-4546-81b9-a8a696ac3f69\media__1787294620366.jpg"
img = cv2.imread(img_path)
h, w, _ = img.shape

# Convert to HSV
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
h_channel = hsv[:, :, 0]
s_channel = hsv[:, :, 1]
v_channel = hsv[:, :, 2]

# Filter blue pixels (representing the hand-drawn blue outline)
# In BGR, blue is very high B, low G & R
# In HSV, Hue is in [100, 140], Saturation > 120, Value > 120
mask_blue = (h_channel >= 100) & (h_channel <= 140) & (s_channel > 120) & (v_channel > 120)

# Clean mask
kernel = np.ones((5,5), np.uint8)
m_blue = cv2.morphologyEx(mask_blue.astype(np.uint8) * 255, cv2.MORPH_CLOSE, kernel)

# Find contours
contours, _ = cv2.findContours(m_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
largest = max(contours, key=cv2.contourArea)

# Simplify contour to a clean polygon
eps = 0.005 * cv2.arcLength(largest, True)
approx = cv2.approxPolyDP(largest, eps, True)

# Reorder points to start from top-left and go clockwise:
# Top-Left: y is small, x is small-medium
# Top-Right: y is small, x is large-medium
# Bottom-Right: y is large, x is large
# Bottom-Left: y is large, x is small
pts = [list(p[0]) for p in approx]

# Let's print out the raw simplified points first
formatted = [{"x": int(pt[0]), "y": int(pt[1])} for pt in pts]
print("// Blue Boundary Points:")
print(json.dumps(formatted))
