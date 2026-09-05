import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

input_path = r"C:\Users\WINDOWS 11\.gemini\antigravity-ide\brain\8d0edfed-a44f-45b6-b892-8676fe5e7503\media__1788499137763.png"
output_path = r"C:\Users\WINDOWS 11\.gemini\antigravity-ide\brain\8d0edfed-a44f-45b6-b892-8676fe5e7503\cctv_pool_analysis_master.png"

img = cv2.imread(input_path)
h, w, _ = img.shape
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# Mask all green annotation overlays (bounding box lines, text label background boxes, and label text)
bright_green = (img[:, :, 1] > 175) & (img[:, :, 0] < 80) & (img[:, :, 2] < 80)
dark_green = (img[:, :, 1] > 75) & (img[:, :, 0] < 60) & (img[:, :, 2] < 60) & (img[:, :, 1] < 175)

# Mask old hand-drawn lines
orange_lines = cv2.inRange(hsv, np.array([5, 80, 80]), np.array([25, 255, 255]))
red_lines = cv2.inRange(hsv, np.array([0, 100, 100]), np.array([5, 255, 255]))
blue_lines = cv2.inRange(hsv, np.array([100, 100, 100]), np.array([130, 255, 255]))

clean_mask = np.zeros((h, w), dtype=np.uint8)
clean_mask[bright_green | dark_green] = 255
clean_mask[orange_lines > 0] = 255
clean_mask[red_lines > 0] = 255
clean_mask[blue_lines > 0] = 255

# Do not touch timestamp in upper right (x > 500, y < 45)
clean_mask[0:45, 500:w] = 0

# Dilate mask slightly (1px) so all edge anti-aliasing pixels are covered
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
clean_mask = cv2.dilate(clean_mask, kernel, iterations=1)

# Inpaint ONLY the thin green annotation pixels. Since bounding box lines are 1-2px wide,
# Telea inpainting perfectly reconstructs the swimmer's skin/clothing/water under the line!
base_cctv = cv2.inpaint(img, clean_mask, 3, cv2.INPAINT_TELEA)

# Corner Points of Pool Quadrilateral (Perspective geometry)
P_TL = np.array([182, 62], dtype=np.float32)
P_TR = np.array([470, 54], dtype=np.float32)
P_BR = np.array([797, 237], dtype=np.float32)
P_BL = np.array([47, 274], dtype=np.float32)

# Perspective Interpolation along Left and Right edges
L1 = P_TL + (1/3) * (P_BL - P_TL)
R1 = P_TR + (1/3) * (P_BR - P_TR)

L2 = P_TL + (2/3) * (P_BL - P_TL)
R2 = P_TR + (2/3) * (P_BR - P_TR)

poly_red = np.array([P_TL, P_TR, R1, L1], dtype=np.int32)
poly_yellow = np.array([L1, R1, R2, L2], dtype=np.int32)
poly_green = np.array([L2, R2, P_BR, P_BL], dtype=np.int32)

# Transparent zone overlays (subtle ~ 10% opacity fills as requested)
overlay = base_cctv.copy()

cv2.fillPoly(overlay, [poly_red], (40, 40, 240))      # Level 3 — Red Zone (Far / Deep End)
cv2.fillPoly(overlay, [poly_yellow], (30, 210, 255))  # Level 2 — Yellow Zone (Middle)
cv2.fillPoly(overlay, [poly_green], (40, 220, 50))    # Level 1 — Green Zone (Near / Shallow End)

alpha = 0.11
cctv_zones = cv2.addWeighted(overlay, alpha, base_cctv, 1 - alpha, 0)

# Outer Pool Quadrilateral Border (Clean cyan outline following pool geometry)
poly_full = np.array([P_TL, P_TR, P_BR, P_BL], dtype=np.int32).reshape((-1, 1, 2))
cv2.polylines(cctv_zones, [poly_full], True, (240, 200, 50), 2, cv2.LINE_AA)

# Zone Divider Lines (Clean, mathematically straight, perspective-correct borders)
# Level 3 Red / Level 2 Yellow Border Line
cv2.line(cctv_zones, tuple(L1.astype(int)), tuple(R1.astype(int)), (40, 40, 240), 2, cv2.LINE_AA)

# Level 2 Yellow / Level 1 Green Border Line
cv2.line(cctv_zones, tuple(L2.astype(int)), tuple(R2.astype(int)), (30, 210, 255), 2, cv2.LINE_AA)

# Render HUD Panel using PIL
pil_img = Image.fromarray(cv2.cvtColor(cctv_zones, cv2.COLOR_BGR2RGB)).convert("RGBA")

try:
    font_header = ImageFont.truetype("arialbd.ttf", 14)
    font_body = ImageFont.truetype("arial.ttf", 13)
    font_bold = ImageFont.truetype("arialbd.ttf", 13)
except:
    font_header = ImageFont.load_default()
    font_body = ImageFont.load_default()
    font_bold = ImageFont.load_default()

px, py = 20, 20
pw, ph = 210, 160

panel_overlay = Image.new("RGBA", pil_img.size, (0, 0, 0, 0))
panel_draw = ImageDraw.Draw(panel_overlay)

# Dark slate card with subtle border
panel_draw.rounded_rectangle([px, py, px + pw, py + ph], radius=8, fill=(15, 23, 42, 225), outline=(255, 255, 255, 45), width=1)

# Header
panel_draw.text((px + 16, py + 14), "PEOPLE IN POOL", fill=(255, 255, 255, 245), font=font_header)
panel_draw.line([(px + 16, py + 36), (px + pw - 16, py + 36)], fill=(255, 255, 255, 35), width=1)

# Row 1: Level 3 — Red: 3
y_row1 = py + 46
panel_draw.rectangle([px + 16, y_row1 + 3, px + 24, y_row1 + 11], fill=(239, 68, 68, 255))
panel_draw.text((px + 32, y_row1), "Level 3 — Red:", fill=(226, 232, 240, 230), font=font_body)
panel_draw.text((px + pw - 28, y_row1), "3", fill=(255, 255, 255, 255), font=font_bold)

# Row 2: Level 2 — Yellow: 2
y_row2 = py + 68
panel_draw.rectangle([px + 16, y_row2 + 3, px + 24, y_row2 + 11], fill=(234, 179, 8, 255))
panel_draw.text((px + 32, y_row2), "Level 2 — Yellow:", fill=(226, 232, 240, 230), font=font_body)
panel_draw.text((px + pw - 28, y_row2), "2", fill=(255, 255, 255, 255), font=font_bold)

# Row 3: Level 1 — Green: 4
y_row3 = py + 90
panel_draw.rectangle([px + 16, y_row3 + 3, px + 24, y_row3 + 11], fill=(34, 197, 94, 255))
panel_draw.text((px + 32, y_row3), "Level 1 — Green:", fill=(226, 232, 240, 230), font=font_body)
panel_draw.text((px + pw - 28, y_row3), "4", fill=(255, 255, 255, 255), font=font_bold)

# Footer divider
panel_draw.line([(px + 16, py + 114), (px + pw - 16, py + 114)], fill=(255, 255, 255, 35), width=1)

# Row 4: Total: 9
y_row4 = py + 124
panel_draw.text((px + 16, y_row4), "Total:", fill=(255, 255, 255, 255), font=font_header)
panel_draw.text((px + pw - 28, y_row4), "9", fill=(255, 255, 255, 255), font=font_header)

final_composite = Image.alpha_composite(pil_img, panel_overlay)
final_composite.convert("RGB").save(output_path)
print(f"Saved master CCTV pool analysis image to {output_path}")
