import cv2
import numpy as np
import json

img_path = r"C:\Users\WINDOWS 11\.gemini\antigravity-ide\brain\4214b2c9-acdd-4546-81b9-a8a696ac3f69\media__1787294620366.jpg"
img = cv2.imread(img_path)
h, w, _ = img.shape

hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
h_channel = hsv[:, :, 0]
s_channel = hsv[:, :, 1]
v_channel = hsv[:, :, 2]

# Define precise masks for the colored lines
# Since the lines are drawn by hand with saturated colors:
mask_red = ((h_channel <= 8) | (h_channel >= 170)) & (s_channel > 120) & (v_channel > 120)
mask_orange = (h_channel >= 9) & (h_channel <= 22) & (s_channel > 120) & (v_channel > 120)
mask_green = (h_channel >= 35) & (h_channel <= 85) & (s_channel > 100) & (v_channel > 100)
mask_blue = (h_channel >= 100) & (h_channel <= 140) & (s_channel > 120) & (v_channel > 120)

# Clean masks (morphological closing/opening to remove gaps and small spots)
kernel = np.ones((3,3), np.uint8)

def clean_mask(mask):
    mask = cv2.morphologyEx(mask.astype(np.uint8) * 255, cv2.MORPH_CLOSE, kernel)
    return cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

m_red = clean_mask(mask_red)
m_orange = clean_mask(mask_orange)
m_green = clean_mask(mask_green)
m_blue = clean_mask(mask_blue)

# For Red, Orange, and Green, we extract the skeleton and find points
def extract_ordered_points(mask, min_x, max_x, step=25):
    # Find all coordinates in the mask
    ys, xs = np.where(mask > 0)
    if len(xs) == 0:
        return []
    
    # Filter points to only be within the x range of the pool
    valid_pts = []
    for x, y in zip(xs, ys):
        if min_x <= x <= max_x:
            valid_pts.append((x, y))
            
    if not valid_pts:
        return []
        
    # Group by X and take median Y
    x_dict = {}
    for x, y in valid_pts:
        if x not in x_dict:
            x_dict[x] = []
        x_dict[x].append(y)
        
    sorted_xs = sorted(x_dict.keys())
    pts = []
    for x in sorted_xs:
        pts.append((x, int(np.median(x_dict[x]))))
        
    # Subsample points
    subsampled = pts[::step]
    if pts[-1] not in subsampled:
        subsampled.append(pts[-1])
        
    return [{"x": int(pt[0]), "y": int(pt[1])} for pt in subsampled]

# We know the pool region x ranges:
# Red line: far end, spans x=415 to x=680
# Orange line: middle-far, spans x=388 to x=720
# Green line: middle-near, spans x=348 to x=810
# Blue line: outer boundary, we'll extract it using contour approximation

red_line = extract_ordered_points(m_red, 410, 690, step=15)
orange_line = extract_ordered_points(m_orange, 380, 730, step=20)
green_line = extract_ordered_points(m_green, 340, 820, step=25)

# Blue Outline: Find the largest contour in the blue mask
contours, _ = cv2.findContours(m_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
largest_blue = max(contours, key=cv2.contourArea)
eps = 0.005 * cv2.arcLength(largest_blue, True)
approx_blue = cv2.approxPolyDP(largest_blue, eps, True)
blue_outline = [{"x": int(pt[0][0]), "y": int(pt[0][1])} for pt in approx_blue]

print("// Red Line:")
print(json.dumps(red_line))
print("// Orange Line:")
print(json.dumps(orange_line))
print("// Green Line:")
print(json.dumps(green_line))
print("// Blue Outline:")
print(json.dumps(blue_outline))
