import cv2
import numpy as np
import json

img_path = r"C:\Users\WINDOWS 11\.gemini\antigravity-ide\brain\4214b2c9-acdd-4546-81b9-a8a696ac3f69\media__1787294620366.jpg"
img = cv2.imread(img_path)
h, w, _ = img.shape

# Find all green pixels in the band
ys, xs = np.where(
    (img[:, :, 1] > 120) & 
    (img[:, :, 0] < 110) & 
    (img[:, :, 2] < 110)
)

pts = []
for x, y in zip(xs, ys):
    if 115 <= y <= 165 and 350 <= x <= 780:
        pts.append((x, y))

# Group by X and take median Y
x_map = {}
for x, y in pts:
    if x not in x_map:
        x_map[x] = []
    x_map[x].append(y)

sorted_xs = sorted(x_map.keys())
cleaned_pts = []
for x in sorted_xs:
    y_vals = x_map[x]
    med_y = np.median(y_vals)
    valid_ys = [y for y in y_vals if abs(y - med_y) < 5]
    if valid_ys:
        cleaned_pts.append((x, int(np.mean(valid_ys))))

green_line = []
if cleaned_pts:
    step = max(1, len(cleaned_pts) // 15)
    subsampled = cleaned_pts[::step]
    if cleaned_pts[-1] not in subsampled:
        subsampled.append(cleaned_pts[-1])
    green_line = [{"x": int(p[0]), "y": int(p[1])} for p in subsampled]

print("// Green Line:")
print(json.dumps(green_line))
