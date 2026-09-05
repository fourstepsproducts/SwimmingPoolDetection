import cv2
import numpy as np

pool_points = {
    "A": {"x": 600.0, "y": 300.0},
    "B": {"x": 1320.0, "y": 300.0},
    "C": {"x": 1800.0, "y": 950.0},
    "D": {"x": 120.0, "y": 950.0}
}

img_w = 1920.0
img_h = 1080.0

pts_src = np.array([
    [pool_points["D"]["x"], pool_points["D"]["y"]], # D
    [pool_points["C"]["x"], pool_points["C"]["y"]], # C
    [pool_points["B"]["x"], pool_points["B"]["y"]], # B
    [pool_points["A"]["x"], pool_points["A"]["y"]]  # A
], dtype=np.float32)

pts_dst = np.array([
    [0.0, 300.0],
    [100.0, 300.0],
    [100.0, 0.0],
    [0.0, 0.0]
], dtype=np.float32)

M = cv2.getPerspectiveTransform(pts_src, pts_dst)

# Test point 1: Bottom center (Near Camera, between D and C)
# D is at (120, 950), C is at (1800, 950) -> Center is (960, 950)
pt_near = np.array([[[960.0, 900.0]]], dtype=np.float32)
res_near = cv2.perspectiveTransform(pt_near, M)
tx_near, ty_near = res_near[0][0][0], res_near[0][0][1]
v_near = 1.0 - (ty_near / 300.0)

# Test point 2: Top center (Far End, between A and B)
# A is at (600, 300), B is at (1320, 300) -> Center is (960, 300)
pt_far = np.array([[[960.0, 350.0]]], dtype=np.float32)
res_far = cv2.perspectiveTransform(pt_far, M)
tx_far, ty_far = res_far[0][0][0], res_far[0][0][1]
v_far = 1.0 - (ty_far / 300.0)

print(f"Near Point (960, 900) -> ty: {ty_near:.2f}, v: {v_near:.4f} (expected: near 0.0/Zone 1)")
print(f"Far Point (960, 350) -> ty: {ty_far:.2f}, v: {v_far:.4f} (expected: near 1.0/Zone 3)")
