import cv2
import numpy as np

# Load original image
input_path = r"C:\Users\WINDOWS 11\.gemini\antigravity-ide\brain\8d0edfed-a44f-45b6-b892-8676fe5e7503\media__1788499137763.png"
img = cv2.imread(input_path)

poly_red = np.array([[182, 62], [470, 54], [579, 115], [137, 133]], np.int32)
poly_yellow = np.array([[137, 133], [579, 115], [688, 176], [92, 203]], np.int32)
poly_green = np.array([[92, 203], [688, 176], [797, 237], [47, 274]], np.int32)

# Swimmers (foot/center position in pool):
swimmers = [
    ("Swimmer 1 (PERSON-05)", 253, 115),
    ("Swimmer 2 (PERSON-02)", 408, 110),
    ("Swimmer 3 (Head middle)", 345, 120),
    ("Swimmer 4 (PERSON-04)", 163, 152),
    ("Swimmer 5 (Swimmer left back)", 138, 175),
    ("Swimmer 6 (Swimmer sitting left)", 168, 240),
    ("Swimmer 7 (Swimmer lower left)", 148, 260),
    ("Swimmer 8 (PERSON-06 in tube)", 565, 195),
    ("Swimmer 9 (PERSON-01 right)", 705, 190),
]

counts = {"Red": 0, "Yellow": 0, "Green": 0}

for name, x, y in swimmers:
    in_red = cv2.pointPolygonTest(poly_red, (float(x), float(y)), False) >= 0
    in_yellow = cv2.pointPolygonTest(poly_yellow, (float(x), float(y)), False) >= 0
    in_green = cv2.pointPolygonTest(poly_green, (float(x), float(y)), False) >= 0
    
    zone = "Unknown"
    if in_red:
        zone = "Level 3 — Red"
        counts["Red"] += 1
    elif in_yellow:
        zone = "Level 2 — Yellow"
        counts["Yellow"] += 1
    elif in_green:
        zone = "Level 1 — Green"
        counts["Green"] += 1
        
    print(f"{name} at ({x}, {y}) -> {zone}")

print("\nTotal Counts:", counts)
print("Total swimmers in pool:", sum(counts.values()))
