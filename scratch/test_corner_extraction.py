import numpy as np

def get_quad_corners(pts):
    pts = np.array(pts, dtype=np.float32)
    # Sort by X
    sorted_x = pts[np.argsort(pts[:, 0])]
    left_half = sorted_x[:len(pts)//2]
    right_half = sorted_x[len(pts)//2:]
    
    P_TL = left_half[np.argmin(left_half[:, 1])]
    P_BL = left_half[np.argmax(left_half[:, 1])]
    
    P_TR = right_half[np.argmin(right_half[:, 1])]
    P_BR = right_half[np.argmax(right_half[:, 1])]
    
    return P_TL, P_TR, P_BR, P_BL

pts_822 = [(182, 62), (326, 58), (470, 54), (633, 145), (797, 237), (422, 255), (47, 274), (114, 168)]
P_TL, P_TR, P_BR, P_BL = get_quad_corners(pts_822)

print("P_TL (Top-Left):", P_TL)
print("P_TR (Top-Right):", P_TR)
print("P_BR (Bottom-Right):", P_BR)
print("P_BL (Bottom-Left):", P_BL)
