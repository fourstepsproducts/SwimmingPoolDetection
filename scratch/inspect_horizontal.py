import cv2
import numpy as np

img_path = r"C:\Users\WINDOWS 11\.gemini\antigravity-ide\brain\4214b2c9-acdd-4546-81b9-a8a696ac3f69\media__1787294620366.jpg"
img = cv2.imread(img_path)
h, w, _ = img.shape

# Scan along the middle horizontal row y = h // 2
y = h // 2
print(f"--- Horizontal scan at y = {y} ---")
# Print the first 50 and last 50 pixels
print("First 20 pixels:")
for x in range(0, 20):
    b, g, r = img[y, x]
    print(f"  x = {x}: BGR=({b}, {g}, {r})")
    
print("Last 20 pixels:")
for x in range(w - 20, w):
    b, g, r = img[y, x]
    print(f"  x = {x}: BGR=({b}, {g}, {r})")
