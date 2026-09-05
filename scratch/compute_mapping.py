import cv2
import numpy as np

screenshot_path = r"C:\Users\WINDOWS 11\.gemini\antigravity-ide\brain\4214b2c9-acdd-4546-81b9-a8a696ac3f69\media__1787294620366.jpg"
video_path = "backend/uploads/processed-pool-1787292819708-293409003.mp4"

screenshot = cv2.imread(screenshot_path)
cap = cv2.VideoCapture(video_path)
ret, video_frame = cap.read()
cap.release()

if video_frame is None:
    print("Could not load video frame.")
    exit(1)

# original video is 1920x1080
v_h, v_w, _ = video_frame.shape
s_h, s_w, _ = screenshot.shape
print(f"Video frame: {v_w}x{v_h}, Screenshot: {s_w}x{s_h}")

# We will use SIFT / ORB to find matching keypoints and calculate the homography
orb = cv2.ORB_create(nfeatures=5000)
kp1, des1 = orb.detectAndCompute(screenshot, None)
kp2, des2 = orb.detectAndCompute(video_frame, None)

bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
matches = bf.match(des1, des2)
matches = sorted(matches, key=lambda x: x.distance)

# Extract matching point coordinates
pts_s = []
pts_v = []
for m in matches[:100]:
    pts_s.append(kp1[m.queryIdx].pt)
    pts_v.append(kp2[m.trainIdx].pt)

pts_s = np.array(pts_s, dtype=np.float32)
pts_v = np.array(pts_v, dtype=np.float32)

# Estimate affine transform: Video_Pt = A * Screenshot_Pt + t
M, inliers = cv2.estimateAffine2D(pts_s, pts_v)
if M is not None:
    print("Exact Affine Mapping found:")
    print(f"  video_x = screenshot_x * {M[0, 0]:.6f} + screenshot_y * {M[0, 1]:.6f} + {M[0, 2]:.2f}")
    print(f"  video_y = screenshot_x * {M[1, 0]:.6f} + screenshot_y * {M[1, 1]:.6f} + {M[1, 2]:.2f}")
    
    # Test mapping some screenshot coordinates to original video coordinates:
    def map_pt(sx, sy):
        vx = sx * M[0, 0] + sy * M[0, 1] + M[0, 2]
        vy = sx * M[1, 0] + sy * M[1, 1] + M[1, 2]
        return round(vx, 1), round(vy, 1)
        
    print("\nMapped Corners (original 1920x1080 video grid):")
    print(f"  Top-Left (410, 58) -> {map_pt(410, 58)}")
    print(f"  Top-Right (680, 52) -> {map_pt(680, 52)}")
    print(f"  Bottom-Right (990, 225) -> {map_pt(990, 225)}")
    print(f"  Bottom-Left (280, 260) -> {map_pt(280, 260)}")
else:
    print("Could not find exact affine mapping.")
