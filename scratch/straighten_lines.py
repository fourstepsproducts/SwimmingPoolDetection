import cv2
import numpy as np

input_path = r"C:\Users\WINDOWS 11\.gemini\antigravity-ide\brain\8d0edfed-a44f-45b6-b892-8676fe5e7503\media__1788499137763.png"
output_path = r"C:\Users\WINDOWS 11\.gemini\antigravity-ide\brain\8d0edfed-a44f-45b6-b892-8676fe5e7503\straightened_lines_perfect_final.png"

img = cv2.imread(input_path)
h, w, _ = img.shape

# Detect all orange and green line pixels across the pool area
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# Orange pixels (Hue 5..25)
orange_mask = cv2.inRange(hsv, np.array([5, 80, 80]), np.array([25, 255, 255]))

# Green line pixels (Hue 35..85, Sat 80..255, Val 80..255)
green_mask = cv2.inRange(hsv, np.array([30, 80, 80]), np.array([85, 255, 255]))

# Define inpaint mask for old wavy lines
inpaint_mask = np.zeros((h, w), dtype=np.uint8)

# Orange line region: y in [95..120], x in [140..530]
inpaint_mask[95:120, 140:530] = orange_mask[95:120, 140:530]

# Green line region: y in [120..175], x in [130..585]
inpaint_mask[120:175, 130:585] = green_mask[120:175, 130:585]

# Protect text label backgrounds (dark green boxes with white/gray text like "PERSON-04 | POOL | 28%")
# Text label for PERSON-04 is at y: 135..145, x: 152..252
# Text label for PERSON-05 is at y: 116..128, x: 242..342
# Text label for PERSON-02 is at y: 114..126, x: 392..492
label_mask = np.zeros((h, w), dtype=bool)
label_mask[135:145, 152:252] = True
label_mask[116:128, 242:342] = True
label_mask[114:126, 392:492] = True

# Do not inpaint text labels
inpaint_mask[label_mask] = 0

# Dilate inpaint mask to catch anti-aliased fringes of old wavy lines completely
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
inpaint_mask = cv2.dilate(inpaint_mask, kernel, iterations=2)
inpaint_mask[label_mask] = 0

# Inpaint water background seamlessly removing all old wavy line remnants
clean_img = cv2.inpaint(img, inpaint_mask, 3, cv2.INPAINT_TELEA)

result = clean_img.copy()

# Draw perfectly straight, clean, precise Orange line
orange_start = (152, 108)
orange_end = (518, 102)
orange_color = (20, 140, 245) # Crisp BGR Orange
cv2.line(result, orange_start, orange_end, orange_color, 2, cv2.LINE_AA)

# Draw perfectly straight, clean, precise Green line
green_start = (132, 162)
green_end = (578, 128)
green_color = (0, 230, 0) # Crisp BGR Safety Green
cv2.line(result, green_start, green_end, green_color, 2, cv2.LINE_AA)

# Re-draw/restore detection box outlines for PERSON-04 (x=152..172, y=145..172)
# Bounding box for PERSON-04 swimmer:
cv2.rectangle(result, (152, 145), (172, 172), (0, 230, 0), 1, cv2.LINE_AA)

cv2.imwrite(output_path, result)
print(f"Saved perfect final straight line image to {output_path}")
