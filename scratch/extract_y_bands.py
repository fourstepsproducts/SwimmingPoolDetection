import cv2
import numpy as np
import json

img_path = r"C:\Users\WINDOWS 11\.gemini\antigravity-ide\brain\4214b2c9-acdd-4546-81b9-a8a696ac3f69\media__1787294620366.jpg"
img = cv2.imread(img_path)
h, w, _ = img.shape

# Convert to HSV and select highly saturated pixels
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
s_channel = hsv[:, :, 1]
v_channel = hsv[:, :, 2]

# Bounding box of the pool area to filter out background noise
# Pool spans from x=280 to x=970, y=50 to y=480
mask_sat = (s_channel > 100) & (v_channel > 100)

def extract_line_in_y_band(ymin, ymax, min_x, max_x, color_hue_check=None):
    # Find pixels inside the Y band and X span
    ys, xs = np.where(mask_sat)
    pts = []
    for x, y in zip(xs, ys):
        if ymin <= y <= ymax and min_x <= x <= max_x:
            # Optional check to filter out water reflections if hue check is provided
            pts.append((x, y))
            
    if not pts:
        return []
        
    # Group by X and take median Y
    x_map = {}
    for x, y in pts:
        if x not in x_map:
            x_map[x] = []
        x_map[x].append(y)
        
    sorted_xs = sorted(x_map.keys())
    cleaned_pts = []
    for x in sorted_xs:
        # Filter outliers
        y_vals = x_map[x]
        med_y = np.median(y_vals)
        valid_ys = [y for y in y_vals if abs(y - med_y) < 5]
        if valid_ys:
            cleaned_pts.append((x, int(np.mean(valid_ys))))
            
    # Subsample to keep coordinates clean
    if not cleaned_pts:
        return []
    step = max(1, len(cleaned_pts) // 15)
    subsampled = cleaned_pts[::step]
    if cleaned_pts[-1] not in subsampled:
        subsampled.append(cleaned_pts[-1])
        
    return [{"x": int(p[0]), "y": int(p[1])} for p in subsampled]

# Segment the three lines by their physical Y bands in the 1024x555 image:
# 1. Red Line (Top): y is around 50 to 80, spans x=410 to x=680
red_line = extract_line_in_y_band(50, 75, 410, 680)

# 2. Orange Line (Middle): y is around 80 to 120, spans x=380 to x=720
orange_line = extract_line_in_y_band(80, 110, 380, 720)

# 3. Green Line (Bottom): y is around 200 to 270, spans x=340 to x=810
# For green, let's filter specifically for green hues (HSV Hue in 35-85) to avoid blue water/swimmer pixels
mask_green_sat = mask_sat & (hsv[:, :, 0] >= 35) & (hsv[:, :, 0] <= 85)
ys_g, xs_g = np.where(mask_green_sat)
g_pts = []
for x, y in zip(xs_g, ys_g):
    if 200 <= y <= 270 and 340 <= x <= 810:
        g_pts.append((x, y))
x_map_g = {}
for x, y in g_pts:
    if x not in x_map_g:
        x_map_g[x] = []
    x_map_g[x].append(y)
sorted_xs_g = sorted(x_map_g.keys())
cleaned_g = []
for x in sorted_xs_g:
    y_vals = x_map_g[x]
    med_y = np.median(y_vals)
    valid_ys = [y for y in y_vals if abs(y - med_y) < 5]
    if valid_ys:
        cleaned_g.append((x, int(np.mean(valid_ys))))
green_line = []
if cleaned_g:
    step = max(1, len(cleaned_g) // 15)
    subsampled_g = cleaned_g[::step]
    if cleaned_g[-1] not in subsampled_g:
        subsampled_g.append(cleaned_g[-1])
    green_line = [{"x": int(p[0]), "y": int(p[1])} for p in subsampled_g]

print("// Red Line:")
print(json.dumps(red_line))
print("// Orange Line:")
print(json.dumps(orange_line))
print("// Green Line:")
print(json.dumps(green_line))
