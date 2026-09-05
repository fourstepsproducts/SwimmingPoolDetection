import cv2
import numpy as np

img_path = r"C:\Users\WINDOWS 11\.gemini\antigravity-ide\brain\4214b2c9-acdd-4546-81b9-a8a696ac3f69\media__1787294620366.jpg"
img = cv2.imread(img_path)

x = 500
print(f"--- BGR values along x = {x} for y = 55 to 75 ---")
for y in range(55, 75):
    b, g, r = img[y, x]
    print(f"  y = {y}: BGR=({b}, {g}, {r})")
