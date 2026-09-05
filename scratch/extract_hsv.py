import cv2
import numpy as np
import json

img_path = r"C:\Users\WINDOWS 11\.gemini\antigravity-ide\brain\4214b2c9-acdd-4546-81b9-a8a696ac3f69\media__1787294620366.jpg"
img = cv2.imread(img_path)
h, w, _ = img.shape

# Let's write a very precise color detector
# In the image, the drawn lines are very saturated.
# We can convert to HSV and use saturation/value to filter out the background.
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
h_channel = hsv[:, :, 0]
s_channel = hsv[:, :, 1]
v_channel = hsv[:, :, 2]

# Only look at highly saturated pixels to ignore the video frame background
mask_sat = s_channel > 120

def get_ordered_line(hue_min, hue_max, name):
    # Filter pixels by hue and saturation
    mask = mask_sat & (h_channel >= hue_min) & (h_channel <= hue_max)
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return []
        
    # Group by X and find average Y
    x_map = {}
    for x, y in zip(xs, ys):
        if x not in x_map:
            x_map[x] = []
        x_map[x].append(y)
        
    sorted_xs = sorted(x_map.keys())
    pts = []
    # Filter outliers in Y (noise)
    for x in sorted_xs:
        # Keep only y values that are close to the median y for this x
        y_vals = x_map[x]
        med_y = np.median(y_vals)
        valid_ys = [y for y in y_vals if abs(y - med_y) < 10]
        if valid_ys:
            pts.append((x, int(np.mean(valid_ys))))
            
    # Subsample to get a clean polyline of ~15-20 points
    if not pts:
        return []
    step = max(1, len(pts) // 15)
    subsampled = pts[::step]
    if pts[-1] not in subsampled:
        subsampled.append(pts[-1])
        
    formatted = [{"x": int(p[0]), "y": int(p[1])} for p in subsampled]
    print(f"{name} line (x range: {pts[0][0]} to {pts[-1][0]}): {len(formatted)} points")
    print(json.dumps(formatted))
    return formatted

# Hue ranges in OpenCV (0-180):
# Red: 0-10 or 170-180
# Orange: 10-25
# Green: 35-85
# Blue: 100-140

print("--- Ordered Lines Detection ---")
blue_line = get_ordered_line(100, 140, "Blue")
green_line = get_ordered_line(35, 85, "Green")
orange_line = get_ordered_line(10, 25, "Orange")

# Red is split across 0-10 and 170-180. Let's merge them.
mask_red = mask_sat & ((h_channel <= 8) | (h_channel >= 170))
ys_r, xs_r = np.where(mask_red)
x_map_r = {}
for x, y in zip(xs_r, ys_r):
    if x not in x_map_r:
        x_map_r[x] = []
    x_map_r[x].append(y)
sorted_xs_r = sorted(x_map_r.keys())
pts_r = []
for x in sorted_xs_r:
    y_vals = x_map_r[x]
    med_y = np.median(y_vals)
    valid_ys = [y for y in y_vals if abs(y - med_y) < 10]
    if valid_ys:
        pts_r.append((x, int(np.mean(valid_ys))))
if pts_r:
    step = max(1, len(pts_r) // 15)
    subsampled_r = pts_r[::step]
    if pts_r[-1] not in subsampled_r:
        subsampled_r.append(pts_r[-1])
    red_line = [{"x": int(p[0]), "y": int(p[1])} for p in subsampled_r]
    print(f"Red line (x range: {pts_r[0][0]} to {pts_r[-1][0]}): {len(red_line)} points")
    print(json.dumps(red_line))
