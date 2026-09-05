import cv2
import numpy as np

img_path = r"C:\Users\WINDOWS 11\.gemini\antigravity-ide\brain\4214b2c9-acdd-4546-81b9-a8a696ac3f69\media__1787294620366.jpg"
img = cv2.imread(img_path)

x = 500
print(f"--- Profiling G, R, B relations along x = {x} for y = 150 to 350 ---")
for y in range(150, 350):
    b, g, r = img[y, x]
    # Look for green line: g should be significantly larger than r, and g should be close to or larger than b
    # Also look for the blue line or other colors
    is_interesting = False
    name = ""
    
    # Green check: g is much larger than r, and g is close to or larger than b
    if g > r + 30 and g > b - 20 and g > 110:
        is_interesting = True
        name = "GREENISH"
        
    if is_interesting or (y % 10 == 0):
        print(f"  y = {y}: BGR=({b}, {g}, {r}) -> {name}")
