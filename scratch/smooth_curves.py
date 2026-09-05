import numpy as np
import json

# Current wobbly coordinates
red_wobbly = [
    {"x": 771.2, "y": 113.5},
    {"x": 898.5, "y": 100.3},
    {"x": 1023.9, "y": 92.8},
    {"x": 1149.3, "y": 94.6},
    {"x": 1276.5, "y": 102.0}
]

orange_wobbly = [
    {"x": 722.3, "y": 180.7},
    {"x": 879.6, "y": 152.6},
    {"x": 1033.1, "y": 137.6},
    {"x": 1192.1, "y": 146.9},
    {"x": 1351.1, "y": 156.1}
]

green_wobbly = [
    {"x": 660.2, "y": 263.0},
    {"x": 817.3, "y": 268.5},
    {"x": 991.4, "y": 255.3},
    {"x": 1201.1, "y": 244.0},
    {"x": 1463.2, "y": 206.5}
]

def smooth_line(points, num_output_pts=15):
    xs = np.array([pt["x"] for pt in points])
    ys = np.array([pt["y"] for pt in points])
    
    # Fit a 2nd degree polynomial: y = ax^2 + bx + c
    coeffs = np.polyfit(xs, ys, 2)
    
    # Generate smooth points
    xmin, xmax = min(xs), max(xs)
    smooth_xs = np.linspace(xmin, xmax, num_output_pts)
    smooth_ys = np.polyval(coeffs, smooth_xs)
    
    return [{"x": round(float(x), 1), "y": round(float(y), 1)} for x, y in zip(smooth_xs, smooth_ys)]

red_smooth = smooth_line(red_wobbly)
orange_smooth = smooth_line(orange_wobbly)
green_smooth = smooth_line(green_wobbly)

print("// Red Smooth:")
print(json.dumps(red_smooth))
print("// Orange Smooth:")
print(json.dumps(orange_smooth))
print("// Green Smooth:")
print(json.dumps(green_smooth))
