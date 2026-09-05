import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

input_path = r"C:\Users\WINDOWS 11\.gemini\antigravity-ide\brain\8d0edfed-a44f-45b6-b892-8676fe5e7503\cctv_pool_analysis.png"
output_path = r"C:\Users\WINDOWS 11\.gemini\antigravity-ide\brain\8d0edfed-a44f-45b6-b892-8676fe5e7503\cctv_pool_analysis_final.png"

img = Image.open(input_path).convert("RGBA")
draw = ImageDraw.Draw(img)

# Try loading crisp sans-serif font
font_size_header = 14
font_size_body = 13
font_size_total = 14

try:
    font_header = ImageFont.truetype("arialbd.ttf", font_size_header)
    font_body = ImageFont.truetype("arial.ttf", font_size_body)
    font_bold = ImageFont.truetype("arialbd.ttf", font_size_body)
except:
    font_header = ImageFont.load_default()
    font_body = ImageFont.load_default()
    font_bold = ImageFont.load_default()

# Panel dimensions & position (Upper-left corner)
px, py = 20, 20
pw, ph = 210, 160

# Draw semi-transparent dark HUD panel card (Slate dark rgba(15, 23, 42, 215))
panel_overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
panel_draw = ImageDraw.Draw(panel_overlay)

# Rounded rectangle card
panel_draw.rounded_rectangle([px, py, px + pw, py + ph], radius=8, fill=(15, 23, 42, 215), outline=(255, 255, 255, 40), width=1)

# Render Header: PEOPLE IN POOL
panel_draw.text((px + 16, py + 14), "PEOPLE IN POOL", fill=(255, 255, 255, 240), font=font_header)

# Thin header underline divider
panel_draw.line([(px + 16, py + 36), (px + pw - 16, py + 36)], fill=(255, 255, 255, 30), width=1)

# Row 1: Level 3 — Red: 3
y_row1 = py + 46
panel_draw.rectangle([px + 16, y_row1 + 3, px + 24, y_row1 + 11], fill=(239, 68, 68, 255)) # Red icon
panel_draw.text((px + 32, y_row1), "Level 3 — Red:", fill=(226, 232, 240, 230), font=font_body)
panel_draw.text((px + pw - 28, y_row1), "3", fill=(255, 255, 255, 255), font=font_bold)

# Row 2: Level 2 — Yellow: 2
y_row2 = py + 68
panel_draw.rectangle([px + 16, y_row2 + 3, px + 24, y_row2 + 11], fill=(234, 179, 8, 255)) # Yellow icon
panel_draw.text((px + 32, y_row2), "Level 2 — Yellow:", fill=(226, 232, 240, 230), font=font_body)
panel_draw.text((px + pw - 28, y_row2), "2", fill=(255, 255, 255, 255), font=font_bold)

# Row 3: Level 1 — Green: 4
y_row3 = py + 90
panel_draw.rectangle([px + 16, y_row3 + 3, px + 24, y_row3 + 11], fill=(34, 197, 94, 255)) # Green icon
panel_draw.text((px + 32, y_row3), "Level 1 — Green:", fill=(226, 232, 240, 230), font=font_body)
panel_draw.text((px + pw - 28, y_row3), "4", fill=(255, 255, 255, 255), font=font_bold)

# Thin footer underline divider
panel_draw.line([(px + 16, py + 114), (px + pw - 16, py + 114)], fill=(255, 255, 255, 30), width=1)

# Row 4: Total: 9
y_row4 = py + 124
panel_draw.text((px + 16, y_row4), "Total:", fill=(255, 255, 255, 255), font=font_header)
panel_draw.text((px + pw - 28, y_row4), "9", fill=(255, 255, 255, 255), font=font_header)

# Composite HUD panel over CCTV image
final_composite = Image.alpha_composite(img, panel_overlay)
final_composite.convert("RGB").save(output_path)
print(f"Saved final CCTV pool analysis image to {output_path}")
