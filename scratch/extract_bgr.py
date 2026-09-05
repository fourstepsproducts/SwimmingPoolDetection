import cv2
import numpy as np

img_path = r"C:\Users\WINDOWS 11\.gemini\antigravity-ide\brain\4214b2c9-acdd-4546-81b9-a8a696ac3f69\media__1787294620366.jpg"
img = cv2.imread(img_path)

h, w, c = img.shape

# Since the image is 1024x555, but the video resolution is 1920x1080,
# let's look at the actual coordinates drawn in the image.
# We will use simple thresholding in BGR to isolate the lines.
# Blue line: B > 150, G < 120, R < 120
blue_mask = (img[:, :, 0] > 140) & (img[:, :, 1] < 120) & (img[:, :, 2] < 100)

# Red line: R > 150, G < 100, B < 100
red_mask = (img[:, :, 2] > 140) & (img[:, :, 1] < 100) & (img[:, :, 0] < 100)

# Orange line: R > 150, G in [100, 190], B < 100
orange_mask = (img[:, :, 2] > 150) & (img[:, :, 1] > 100) & (img[:, :, 1] < 190) & (img[:, :, 0] < 100)

# Green line: G > 140, R < 120, B < 120
green_mask = (img[:, :, 1] > 130) & (img[:, :, 2] < 120) & (img[:, :, 0] < 120)

def get_line_pts(mask):
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return []
    
    # Sort by X
    pts_by_x = {}
    for x, y in zip(xs, ys):
        if x not in pts_by_x:
            pts_by_x[x] = []
        pts_by_x[x].append(y)
        
    sorted_xs = sorted(pts_by_x.keys())
    res = []
    # Subsample xs to have a smooth curve
    # Keep about 10-15 points per curve
    step = max(1, len(sorted_xs) // 12)
    for i in range(0, len(sorted_xs), step):
        x = sorted_xs[i]
        y = int(np.mean(pts_by_x[x]))
        res.append((x, y))
    # Make sure we add the last point
    if sorted_xs[-1] not in [r[0] for r in res]:
        res.append((sorted_xs[-1], int(np.mean(pts_by_x[sorted_xs[-1]]))))
    return res

print("Blue Points (Water Area outer boundaries):")
print(get_line_pts(blue_mask))

print("\nRed Line Points (Zone 3/Deep):")
print(get_line_pts(red_mask))

print("\nOrange Line Points (Zone 2/Medium):")
print(get_line_pts(orange_mask))

print("\nGreen Line Points (Zone 1/Shallow):")
print(get_line_pts(green_mask))
