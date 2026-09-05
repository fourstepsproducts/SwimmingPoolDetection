import cv2
import numpy as np
import json

def get_ordered_curve(mask_path, color_name):
    mask = cv2.imread(mask_path, 0)
    ys, xs = np.where(mask > 0)
    if len(xs) == 0:
        print(f"No points for {color_name}")
        return []
    
    # Group by X coordinate and get average Y
    pts_dict = {}
    for x, y in zip(xs, ys):
        if x not in pts_dict:
            pts_dict[x] = []
        pts_dict[x].append(y)
        
    sorted_xs = sorted(pts_dict.keys())
    
    # We want to output about 15-20 points to define a smooth curve.
    # Let's clean noise first (discard outliers using median filtering)
    cleaned_pts = []
    for x in sorted_xs:
        cleaned_pts.append((x, int(np.median(pts_dict[x]))))
        
    # Subsample to keep the configuration clean and compact
    step = max(1, len(cleaned_pts) // 15)
    subsampled = cleaned_pts[::step]
    if cleaned_pts[-1] not in subsampled:
        subsampled.append(cleaned_pts[-1])
        
    formatted = [{"x": int(pt[0]), "y": int(pt[1])} for pt in subsampled]
    print(f"// {color_name} curve ({len(formatted)} points):")
    print(json.dumps(formatted))
    return formatted

get_ordered_curve("scratch/red_mask.png", "Red Line (Zone 3/Deep)")
get_ordered_curve("scratch/orange_mask.png", "Orange Line (Zone 2/Medium)")
get_ordered_curve("scratch/green_mask.png", "Green Line (Zone 1/Shallow)")
