import cv2
import numpy as np

# Load original image
input_path = r"C:\Users\WINDOWS 11\.gemini\antigravity-ide\brain\8d0edfed-a44f-45b6-b892-8676fe5e7503\media__1788499137763.png"
output_path = r"C:\Users\WINDOWS 11\.gemini\antigravity-ide\brain\8d0edfed-a44f-45b6-b892-8676fe5e7503\clean_geometric_zones.png"

img = cv2.imread(input_path)
h, w, _ = img.shape

# 1. Clean the image: Inpaint old blue polygon lines, old wavy green/orange/red lines, and old YOLO text labels
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# Blue polygon lines (Hue 100..130, Sat > 120, Val > 120)
blue_mask = cv2.inRange(hsv, np.array([100, 120, 120]), np.array([130, 255, 255]))

# Green text/box lines (Hue 35..85)
green_mask = cv2.inRange(hsv, np.array([30, 80, 80]), np.array([85, 255, 255]))

# Orange/Red lines
orange_mask = cv2.inRange(hsv, np.array([5, 80, 80]), np.array([25, 255, 255]))
red_mask1 = cv2.inRange(hsv, np.array([0, 100, 100]), np.array([5, 255, 255]))
red_mask2 = cv2.inRange(hsv, np.array([170, 100, 100]), np.array([180, 255, 255]))

clean_mask = np.zeros((h, w), dtype=np.uint8)
clean_mask[blue_mask > 0] = 255
clean_mask[green_mask > 0] = 255
clean_mask[orange_mask > 0] = 255
clean_mask[red_mask1 > 0] = 255
clean_mask[red_mask2 > 0] = 255

# Do not touch timestamp area (x > 500, y < 45)
clean_mask[0:45, 500:w] = 0

# Protect swimmers (heads, skin, clothing, float tube)
swimmer_mask = np.zeros((h, w), dtype=bool)
swimmer_mask[108:126, 248:260] = True
swimmer_mask[104:124, 400:416] = True
swimmer_mask[118:124, 342:352] = True
swimmer_mask[144:170, 154:170] = True
swimmer_mask[170:180, 135:142] = True
swimmer_mask[235:245, 165:172] = True
swimmer_mask[255:265, 145:152] = True
swimmer_mask[180:215, 550:650] = True
swimmer_mask[160:210, 695:800] = True

clean_mask[swimmer_mask] = 0

# Dilate mask 1px for clean edge inpainting
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
clean_mask = cv2.dilate(clean_mask, kernel, iterations=1)
clean_mask[swimmer_mask] = 0

# Inpaint image to restore pure CCTV footage
clean_bg = cv2.inpaint(img, clean_mask, 3, cv2.INPAINT_TELEA)

# 2. Define the exact 4 corners of the pool quadrilateral
# Top-Left: (182, 62), Top-Right: (470, 54), Bottom-Right: (797, 237), Bottom-Left: (47, 274)
P_TL = np.array([182, 62], dtype=np.float32)
P_TR = np.array([470, 54], dtype=np.float32)
P_BR = np.array([797, 237], dtype=np.float32)
P_BL = np.array([47, 274], dtype=np.float32)

# Perspective Interpolation along Left Edge (P_TL -> P_BL) and Right Edge (P_TR -> P_BR)
L1 = P_TL + (1.0 / 3.0) * (P_BL - P_TL)
R1 = P_TR + (1.0 / 3.0) * (P_BR - P_TR)

L2 = P_TL + (2.0 / 3.0) * (P_BL - P_TL)
R2 = P_TR + (2.0 / 3.0) * (P_BR - P_TR)

poly_red = np.array([P_TL, P_TR, R1, L1], dtype=np.int32)       # Level 3 — Red (Far/Deep End)
poly_yellow = np.array([L1, R1, R2, L2], dtype=np.int32)       # Level 2 — Yellow (Middle)
poly_green = np.array([L2, R2, P_BR, P_BL], dtype=np.int32)    # Level 1 — Green (Near/Shallow End)
poly_pool = np.array([P_TL, P_TR, P_BR, P_BL], dtype=np.int32)   # Entire Pool Quadrilateral

# 3. Transparent Zone Fills (~10% opacity)
overlay = clean_bg.copy()
cv2.fillPoly(overlay, [poly_red], (40, 40, 240))      # Level 3 — Red (BGR Red)
cv2.fillPoly(overlay, [poly_yellow], (30, 210, 255))  # Level 2 — Yellow (BGR Yellow)
cv2.fillPoly(overlay, [poly_green], (40, 220, 50))    # Level 1 — Green (BGR Green)

alpha = 0.10
result = cv2.addWeighted(overlay, alpha, clean_bg, 1.0 - alpha, 0)

# 4. Perfectly Straight Geometric Borders
# Outer Blue Pool Boundary (Clean Blue Line: BGR (255, 80, 0))
cv2.polylines(result, [poly_pool.reshape((-1, 1, 2))], isClosed=True, color=(255, 100, 0), thickness=2, lineType=cv2.LINE_AA)

# Level 3 Red / Level 2 Yellow Divider Line (L1 -> R1)
cv2.line(result, (int(L1[0]), int(L1[1])), (int(R1[0]), int(R1[1])), (40, 40, 240), 2, cv2.LINE_AA)

# Level 2 Yellow / Level 1 Green Divider Line (L2 -> R2)
cv2.line(result, (int(L2[0]), int(L2[1])), (int(R2[0]), int(R2[1])), (30, 210, 255), 2, cv2.LINE_AA)

cv2.imwrite(output_path, result)
print(f"Saved precise geometric zone output to {output_path}")
