import cv2
import numpy as np

img_path = r"C:\Users\WINDOWS 11\.gemini\antigravity-ide\brain\4214b2c9-acdd-4546-81b9-a8a696ac3f69\media__1787294620366.jpg"
img = cv2.imread(img_path)

h, w, c = img.shape

# Let's inspect the coordinates of specific features in the image:
# The blue line represents the pool water region outer boundary. Let's find its exact vertices by looking at the contours.
# Since it is blue, let's look at B channel.
b = img[:, :, 0].astype(float)
g = img[:, :, 1].astype(float)
r = img[:, :, 2].astype(float)

# Blue pixels should have high B compared to G and R
blue_mask = (b > 130) & (b - r > 40) & (b - g > 40)
# Let's clean the mask using morphological operations
kernel = np.ones((3,3), np.uint8)
blue_mask = cv2.morphologyEx(blue_mask.astype(np.uint8) * 255, cv2.MORPH_CLOSE, kernel)

# Find contours of blue mask
contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
print(f"Found {len(contours)} blue contours.")
for idx, cnt in enumerate(contours):
    area = cv2.contourArea(cnt)
    if area > 100:
        print(f"Contour {idx} area: {area:.1f}, points: {len(cnt)}")
        # Approximate the polygon to get clean vertices
        eps = 0.01 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, eps, True)
        print("Approx vertices:")
        for pt in approx:
            print(f"  {pt[0][0]}, {pt[0][1]}")
