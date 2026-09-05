import cv2
import numpy as np

img_path = r"C:\Users\WINDOWS 11\.gemini\antigravity-ide\brain\4214b2c9-acdd-4546-81b9-a8a696ac3f69\media__1787294620366.jpg"
img = cv2.imread(img_path)

h, w, c = img.shape

# Save individual color masks as images to verify our extraction
b = img[:, :, 0].astype(float)
g = img[:, :, 1].astype(float)
r = img[:, :, 2].astype(float)

blue_mask = (b > 120) & (b - r > 30) & (b - g > 30)
red_mask = (r > 130) & (r - b > 35) & (r - g > 35)
orange_mask = (r > 150) & (g > 85) & (g < 170) & (b < 100)
green_mask = (g > 115) & (g - r > 30) & (g - b > 30)

cv2.imwrite("scratch/blue_mask.png", (blue_mask * 255).astype(np.uint8))
cv2.imwrite("scratch/red_mask.png", (red_mask * 255).astype(np.uint8))
cv2.imwrite("scratch/orange_mask.png", (orange_mask * 255).astype(np.uint8))
cv2.imwrite("scratch/green_mask.png", (green_mask * 255).astype(np.uint8))

print("Masks saved to scratch directory.")
