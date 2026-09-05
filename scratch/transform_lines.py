import numpy as np
import json

# Affine transformation parameters
sx_x, sx_y, tx = 1.871319, -0.007996, 4.55
sy_x, sy_y, ty = -0.000934, 1.868201, -22.54

def map_pt(pt):
    x, y = pt["x"], pt["y"]
    vx = x * sx_x + y * sx_y + tx
    vy = x * sy_x + y * sy_y + ty
    return {"x": round(vx, 1), "y": round(vy, 1)}

# Coordinates in screenshot (1024x555)
# 1. Blue water boundary (pool polygon)
# Top-Left, Top-Right, Bottom-Right, Bottom-Left corners, with some middle points to match visual curves exactly
blue_screenshot = [
    {"x": 410, "y": 58},   # Top-Left corner
    {"x": 545, "y": 55},   # Top-Mid-Left
    {"x": 680, "y": 52},   # Top-Right corner
    {"x": 835, "y": 138},  # Mid-Right
    {"x": 990, "y": 225},  # Bottom-Right corner
    {"x": 635, "y": 242},  # Mid-Bottom
    {"x": 280, "y": 260},  # Bottom-Left corner
    {"x": 345, "y": 159}   # Mid-Left
]

# 2. Red Line:
red_screenshot = [
    {"x": 410, "y": 73},
    {"x": 478, "y": 66},
    {"x": 545, "y": 62},
    {"x": 612, "y": 63},
    {"x": 680, "y": 67}
]

# 3. Orange Line:
orange_screenshot = [
    {"x": 384, "y": 109},
    {"x": 468, "y": 94},
    {"x": 550, "y": 86},
    {"x": 635, "y": 91},
    {"x": 720, "y": 96}
]

# 4. Green Line:
green_screenshot = [
    {"x": 351, "y": 153},
    {"x": 435, "y": 156},
    {"x": 528, "y": 149},
    {"x": 640, "y": 143},
    {"x": 780, "y": 123}
]

# Transform
blue_mapped = [map_pt(pt) for pt in blue_screenshot]
red_mapped = [map_pt(pt) for pt in red_screenshot]
orange_mapped = [map_pt(pt) for pt in orange_screenshot]
green_mapped = [map_pt(pt) for pt in green_screenshot]

# Output in JSON format
pool_calibration = {
    "waterBoundary": blue_mapped,
    "layerLineRed": red_mapped,
    "layerLineOrange": orange_mapped,
    "layerLineGreen": green_mapped
}

print(json.dumps(pool_calibration, indent=2))
