import cv2
import numpy as np

img_path = r"C:\Users\WINDOWS 11\.gemini\antigravity-ide\brain\4214b2c9-acdd-4546-81b9-a8a696ac3f69\media__1787294620366.jpg"
img = cv2.imread(img_path)

# Let's inspect BGR along x = 500 for y = 50 to 450
x = 500
print(f"--- BGR Profile along x = {x} ---")
for y in range(50, 450, 5):
    b, g, r = img[y, x]
    # Check if this pixel has a saturated color:
    # Red: high R, low B & G
    # Orange: high R, medium G, low B
    # Green: high G, low R & B
    # Blue: high B, low R & G
    color_type = "Background"
    if r > 120 and g < 100 and b < 100:
        color_type = "RED"
    elif r > 120 and 70 <= g <= 170 and b < 100:
        color_type = "ORANGE"
    elif g > 110 and r < 100 and b < 100:
        color_type = "GREEN"
    elif b > 120 and r < 100 and g < 100:
        color_type = "BLUE"
        
    if color_type != "Background":
        print(f"  y = {y}: BGR=({b}, {g}, {r}) -> {color_type}")
