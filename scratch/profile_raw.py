import cv2
import numpy as np

img_path = r"C:\Users\WINDOWS 11\.gemini\antigravity-ide\brain\4214b2c9-acdd-4546-81b9-a8a696ac3f69\media__1787294620366.jpg"
img = cv2.imread(img_path)

x = 500
print(f"--- Raw BGR Profile along x = {x} ---")
for y in range(50, 300):
    b, g, r = img[y, x]
    # Check if this pixel is significantly different from the blue water background
    # Water background has high B (e.g. >150), G (e.g. >120) and R (e.g. >50)
    # Let's print pixels that look like drawn lines
    # Red: high R, low B/G
    # Orange: high R, medium G, low B
    # Green: high G, low R/B
    # Blue line: very high B, low R/G (different from water)
    is_line = False
    color_name = "Water/Bg"
    
    # Red drawn line
    if r > 180 and g < 60 and b < 60:
        is_line = True
        color_name = "Drawn RED"
    # Orange drawn line
    elif r > 200 and 100 <= g <= 200 and b < 80:
        is_line = True
        color_name = "Drawn ORANGE"
    # Green drawn line
    elif g > 150 and r < 100 and b < 100:
        is_line = True
        color_name = "Drawn GREEN"
    # Blue drawn line
    elif b > 200 and r < 80 and g < 80:
        is_line = True
        color_name = "Drawn BLUE"
        
    if is_line or (y % 10 == 0):
        print(f"  y = {y}: BGR=({b}, {g}, {r}) -> {color_name}")
