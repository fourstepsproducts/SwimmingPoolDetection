import cv2
import numpy as np

img_path = r"C:\Users\WINDOWS 11\.gemini\antigravity-ide\brain\4214b2c9-acdd-4546-81b9-a8a696ac3f69\media__1787294620366.jpg"
img = cv2.imread(img_path)
h, w, _ = img.shape

# Let's search for green pixels in the pool region
# Green: G is the maximum channel, and G is significantly larger than R and B.
# E.g. g - r > 20 and g - b > 20
ys, xs = np.where(
    (img[:, :, 1].astype(int) - img[:, :, 2].astype(int) > 30) &
    (img[:, :, 1].astype(int) - img[:, :, 0].astype(int) > 30) &
    (img[:, :, 1] > 100)
)

print(f"Found {len(xs)} green pixels.")
# Group by X and take median Y
x_map = {}
for x, y in zip(xs, ys):
    if 100 <= y <= 400 and 300 <= x <= 950:
        if x not in x_map:
            x_map[x] = []
        x_map[x].append(y)

sorted_xs = sorted(x_map.keys())
cleaned = []
for x in sorted_xs:
    y_vals = x_map[x]
    cleaned.append((x, int(np.median(y_vals))))

# Print the points subsampled
if cleaned:
    step = max(1, len(cleaned) // 15)
    subsampled = cleaned[::step]
    if cleaned[-1] not in subsampled:
        subsampled.append(cleaned[-1])
    print("Green Line Points:")
    print([{"x": int(p[0]), "y": int(p[1])} for p in subsampled])
