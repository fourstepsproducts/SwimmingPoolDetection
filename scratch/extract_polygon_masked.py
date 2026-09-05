import cv2
import numpy as np
import json

img_path = r"C:\Users\WINDOWS 11\.gemini\antigravity-ide\brain\4214b2c9-acdd-4546-81b9-a8a696ac3f69\media__1787294620366.jpg"
img = cv2.imread(img_path)
h, w, _ = img.shape

# Approximate pool polygon in 1024x555 image coordinates
pool_polygon = np.array([
    [280, 470],  # Bottom-Left
    [965, 410],  # Bottom-Right
    [660, 100],  # Top-Right
    [400, 125]   # Top-Left
], dtype=np.int32)

# Create a mask of the pool polygon
pool_mask = np.zeros((h, w), dtype=np.uint8)
cv2.fillPoly(pool_mask, [pool_polygon], 255)

hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
h_channel = hsv[:, :, 0]
s_channel = hsv[:, :, 1]
v_channel = hsv[:, :, 2]

# Saturation filter + inside pool polygon mask
mask_base = (s_channel > 120) & (pool_mask > 0)

def get_ordered_line(mask, step=15):
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return []
    x_map = {}
    for x, y in zip(xs, ys):
        if x not in x_map:
            x_map[x] = []
        x_map[x].append(y)
    sorted_xs = sorted(x_map.keys())
    pts = []
    for x in sorted_xs:
        y_vals = x_map[x]
        med_y = np.median(y_vals)
        valid_ys = [y for y in y_vals if abs(y - med_y) < 10]
        if valid_ys:
            pts.append((x, int(np.mean(valid_ys))))
    if not pts:
        return []
    subsampled = pts[::step]
    if pts[-1] not in subsampled:
        subsampled.append(pts[-1])
    return [{"x": int(p[0]), "y": int(p[1])} for p in subsampled]

# 1. Red Line (HSV Hue: 0-8 or 170-180)
mask_red = mask_base & ((h_channel <= 8) | (h_channel >= 170))
red_line = get_ordered_line(mask_red, step=20)

# 2. Orange Line (HSV Hue: 9-22)
mask_orange = mask_base & (h_channel >= 9) & (h_channel <= 22)
orange_line = get_ordered_line(mask_orange, step=20)

# 3. Green Line (HSV Hue: 35-85)
mask_green = mask_base & (h_channel >= 35) & (h_channel <= 85)
green_line = get_ordered_line(mask_green, step=25)

# For the Blue boundary, let's trace the boundary polygon directly.
# Since the blue line is drawn over the pool water boundary in the reference image,
# let's extract the blue mask points inside a slightly expanded region.
mask_blue = (s_channel > 80) & (h_channel >= 100) & (h_channel <= 140)
# Clean blue mask using morphology
kernel = np.ones((5,5), np.uint8)
mask_blue_clean = cv2.morphologyEx(mask_blue.astype(np.uint8) * 255, cv2.MORPH_CLOSE, kernel)
# Find the contours
contours, _ = cv2.findContours(mask_blue_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
largest_blue = max(contours, key=cv2.contourArea)
eps = 0.005 * cv2.arcLength(largest_blue, True)
approx_blue = cv2.approxPolyDP(largest_blue, eps, True)
blue_poly_pts = [{"x": int(pt[0][0]), "y": int(pt[0][1])} for pt in approx_blue]

print("// Red Line:")
print(json.dumps(red_line))
print("// Orange Line:")
print(json.dumps(orange_line))
print("// Green Line:")
print(json.dumps(green_line))
print("// Blue Outline:")
print(json.dumps(blue_poly_pts))
