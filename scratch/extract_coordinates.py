import cv2
import numpy as np
import json

img_path = r"C:\Users\WINDOWS 11\.gemini\antigravity-ide\brain\4214b2c9-acdd-4546-81b9-a8a696ac3f69\media__1787294620366.jpg"
img = cv2.imread(img_path)

h, w, c = img.shape
print(f"Loaded image size: {w}x{h}")

# Convert to HSV to extract colors
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# Define HSV ranges for our colored lines:
# 1. Blue: H in [100, 140], S in [100, 255], V in [50, 255]
lower_blue = np.array([100, 100, 50])
upper_blue = np.array([140, 255, 255])
mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)

# 2. Red: H in [0, 10] or [170, 180], S in [100, 255], V in [50, 255]
lower_red1 = np.array([0, 100, 50])
upper_red1 = np.array([10, 255, 255])
lower_red2 = np.array([170, 100, 50])
upper_red2 = np.array([180, 255, 255])
mask_red = cv2.inRange(hsv, lower_red1, upper_red1) | cv2.inRange(hsv, lower_red2, upper_red2)

# 3. Orange: H in [10, 25], S in [100, 255], V in [100, 255]
lower_orange = np.array([10, 100, 100])
upper_orange = np.array([25, 255, 255])
mask_orange = cv2.inRange(hsv, lower_orange, upper_orange)

# 4. Green: H in [35, 85], S in [50, 255], V in [50, 255]
lower_green = np.array([35, 50, 50])
upper_green = np.array([85, 255, 255])
mask_green = cv2.inRange(hsv, lower_green, upper_green)

# Let's clean the masks to find contours/polylines
def extract_points(mask, step=15):
    # Find all white pixels in the mask
    ys, xs = np.where(mask > 0)
    if len(xs) == 0:
        return []
    
    # We want to group by x coordinate and average y
    pts = {}
    for x, y in zip(xs, ys):
        if x not in pts:
            pts[x] = []
        pts[x].append(y)
    
    unique_xs = sorted(pts.keys())
    # Subsample xs to get a clean polyline
    sampled_xs = unique_xs[::step]
    if unique_xs[-1] not in sampled_xs:
        sampled_xs.append(unique_xs[-1])
        
    result_pts = []
    for x in sampled_xs:
        avg_y = int(np.mean(pts[x]))
        # Scale back to 1024x555 coordinate system
        result_pts.append({"x": int(x), "y": avg_y})
        
    return result_pts

blue_pts = extract_points(mask_blue, step=25)
red_pts = extract_points(mask_red, step=25)
orange_pts = extract_points(mask_orange, step=25)
green_pts = extract_points(mask_green, step=25)

print(f"Blue (Water Boundary) Points: {len(blue_pts)}")
print(json.dumps(blue_pts))
print(f"Red Line Points: {len(red_pts)}")
print(json.dumps(red_pts))
print(f"Orange Line Points: {len(orange_pts)}")
print(json.dumps(orange_pts))
print(f"Green Line Points: {len(green_pts)}")
print(json.dumps(green_pts))
