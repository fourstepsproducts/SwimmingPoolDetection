import cv2
import numpy as np

img_path = r"C:\Users\WINDOWS 11\.gemini\antigravity-ide\brain\4214b2c9-acdd-4546-81b9-a8a696ac3f69\media__1787294620366.jpg"
img = cv2.imread(img_path)
h, w, _ = img.shape

# Let's inspect the top and bottom rows to see where the gray menu bars end and the video begins.
# Let's check along x = w // 2
x = w // 2
print(f"--- Vertical scan at x = {x} ---")
for y in range(0, h):
    b, g, r = img[y, x]
    # Check for the white/gray color of the menu bar at the top or bottom
    # Also look at the transition to the video area
    # Print transitions where color changes significantly
    if y < 100 or y > h - 50:
        print(f"  y = {y}: BGR=({b}, {g}, {r})")
