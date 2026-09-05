import cv2
import numpy as np

input_path = r"C:\Users\WINDOWS 11\.gemini\antigravity-ide\brain\8d0edfed-a44f-45b6-b892-8676fe5e7503\media__1788499137763.png"
img = cv2.imread(input_path)

# Define pool polygon
pts_pool = np.array([[182, 62], [470, 54], [797, 237], [47, 274]], np.int32)

# Check point in polygon function
def is_in_pool(x, y):
    return cv2.pointPolygonTest(pts_pool, (float(x), float(y)), False) >= 0

# Let's inspect all people in the image and their coordinates:

# 1. Deck people (OUTSIDE pool):
# - Man standing on left patio/deck: x=55, y=170 -> OUTSIDE
# - Child on deck far left: x=75, y=230 -> OUTSIDE (on concrete edge)
# - People walking far left path: x=135, y=70; x=170, y=75 -> OUTSIDE

# 2. People INSIDE the pool (swimmers):
# Let's check each person in the water:

# Swimmer 1 (PERSON-05 in original): head/body at x=253, y=115 -> In pool
# Swimmer 2 (PERSON-02 in original): head/body at x=408, y=110 -> In pool
# Swimmer 3 (Head floating near middle): x=350, y=120 -> In pool (small head between person 5 and 2)
# Swimmer 4 (PERSON-04 in original): x=163, y=152 -> In pool
# Swimmer 5 (Swimmer left behind person 04): x=138, y=175 -> In pool
# Swimmer 6 (Swimmer sitting/wading near left corner): x=168, y=240 -> In pool
# Swimmer 7 (Swimmer lower left): x=148, y=260 -> In pool
# Swimmer 8 (PERSON-06 in pink tube): x=565, y=195 -> In pool
# Swimmer 9 (PERSON-01 far right): x=705, y=190 -> In pool

print("Testing point in pool:")
for name, (x, y) in [
    ("Person-05 (x=253, y=115)", (253, 115)),
    ("Person-02 (x=408, y=110)", (408, 110)),
    ("Person-04 (x=163, y=152)", (163, 152)),
    ("Person-06 (x=565, y=195)", (565, 195)),
    ("Person-01 (x=705, y=190)", (705, 190)),
]:
    print(name, "-> In pool:", is_in_pool(x, y))
