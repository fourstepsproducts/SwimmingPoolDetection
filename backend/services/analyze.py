import sys
import json
import os
import cv2
import numpy as np
from ultralytics import YOLO

REFERENCE_WIDTH = 1920.0
REFERENCE_HEIGHT = 1080.0

DEFAULT_POOL_CORNERS = [
    {"x": 745.0, "y": 75.0},
    {"x": 1275.0, "y": 75.0},
    {"x": 1775.0, "y": 405.0},
    {"x": 560.0, "y": 430.0},
]


def normalize_pool_corners(raw_points):
    if not raw_points:
        return DEFAULT_POOL_CORNERS

    points = []
    for pt in raw_points:
        if isinstance(pt, dict):
            x = float(pt.get("x", pt.get("X", 0.0)))
            y = float(pt.get("y", pt.get("Y", 0.0)))
            points.append({"x": x, "y": y})
        elif isinstance(pt, (list, tuple)) and len(pt) >= 2:
            points.append({"x": float(pt[0]), "y": float(pt[1])})

    if len(points) < 4:
        return DEFAULT_POOL_CORNERS

    if len(points) >= 4:
        ordered = [points[0], points[1], points[2], points[3]]
        if len(points) >= 8:
            ordered = [points[0], points[2], points[4], points[6]]
        return ordered

    return points[:4]


def build_pool_polygons(pool_corners, frame_w, frame_h):
    scale_x = frame_w / REFERENCE_WIDTH
    scale_y = frame_h / REFERENCE_HEIGHT

    p_tl = np.array([pool_corners[0]["x"] * scale_x, pool_corners[0]["y"] * scale_y], dtype=np.float32)
    p_tr = np.array([pool_corners[1]["x"] * scale_x, pool_corners[1]["y"] * scale_y], dtype=np.float32)
    p_br = np.array([pool_corners[2]["x"] * scale_x, pool_corners[2]["y"] * scale_y], dtype=np.float32)
    p_bl = np.array([pool_corners[3]["x"] * scale_x, pool_corners[3]["y"] * scale_y], dtype=np.float32)

    left_divider_1 = p_tl + (1.0 / 3.0) * (p_bl - p_tl)
    right_divider_1 = p_tr + (1.0 / 3.0) * (p_br - p_tr)
    left_divider_2 = p_tl + (2.0 / 3.0) * (p_bl - p_tl)
    right_divider_2 = p_tr + (2.0 / 3.0) * (p_br - p_tr)

    poly_red = np.array([p_tl, p_tr, right_divider_1, left_divider_1], dtype=np.int32)
    poly_yellow = np.array([left_divider_1, right_divider_1, right_divider_2, left_divider_2], dtype=np.int32)
    poly_green = np.array([left_divider_2, right_divider_2, p_br, p_bl], dtype=np.int32)
    poly_pool = np.array([p_tl, p_tr, p_br, p_bl], dtype=np.int32)

    return {
        "pool": poly_pool,
        "red": poly_red,
        "yellow": poly_yellow,
        "green": poly_green,
        "divider_1_left": left_divider_1,
        "divider_1_right": right_divider_1,
        "divider_2_left": left_divider_2,
        "divider_2_right": right_divider_2,
    }


def draw_pool_markings(frame, polygons):
    overlay = frame.copy()

    cv2.fillPoly(overlay, [polygons["red"]], (40, 40, 220))
    cv2.fillPoly(overlay, [polygons["yellow"]], (0, 200, 255))
    cv2.fillPoly(overlay, [polygons["green"]], (0, 200, 70))

    marked = cv2.addWeighted(overlay, 0.18, frame, 0.82, 0)
    cv2.polylines(marked, [polygons["pool"]], True, (255, 0, 0), 2, cv2.LINE_AA)
    cv2.line(marked, tuple(polygons["divider_1_left"].astype(int)), tuple(polygons["divider_1_right"].astype(int)), (255, 0, 0), 2, cv2.LINE_AA)
    cv2.line(marked, tuple(polygons["divider_2_left"].astype(int)), tuple(polygons["divider_2_right"].astype(int)), (255, 0, 0), 2, cv2.LINE_AA)

    return marked


def process_frame(img, model, calibration=None):
    img_h, img_w, _ = img.shape
    results = model(img, classes=[0], conf=0.15, verbose=False)

    detections = []
    zone_counts = {"zone1": 0, "zone2": 0, "zone3": 0}

    pool_corners = DEFAULT_POOL_CORNERS
    if calibration and "waterBoundary" in calibration and len(calibration["waterBoundary"]) >= 4:
        pool_corners = normalize_pool_corners(calibration["waterBoundary"])

    polygons = build_pool_polygons(pool_corners, img_w, img_h)
    marked_frame = draw_pool_markings(img.copy(), polygons)

    for result in results:
        boxes = result.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            cx = (x1 + x2) / 2.0
            cy_bottom = y2
            cy_center = (y1 + y2) / 2.0

            dist_bottom = cv2.pointPolygonTest(polygons["pool"], (cx, cy_bottom), False)
            dist_center = cv2.pointPolygonTest(polygons["pool"], (cx, cy_center), False)

            if dist_bottom < 0 and dist_center < 0:
                continue

            eval_pt = (cx, cy_bottom) if dist_bottom >= 0 else (cx, cy_center)

            dist_red = cv2.pointPolygonTest(polygons["red"], eval_pt, False)
            dist_yellow = cv2.pointPolygonTest(polygons["yellow"], eval_pt, False)
            dist_green = cv2.pointPolygonTest(polygons["green"], eval_pt, False)

            if dist_red >= 0:
                zone = "ZONE_3"
                risk = "HIGH RISK (DEEP)"
                zone_counts["zone3"] += 1
            elif dist_yellow >= 0:
                zone = "ZONE_2"
                risk = "MEDIUM RISK"
                zone_counts["zone2"] += 1
            elif dist_green >= 0:
                zone = "ZONE_1"
                risk = "LOW RISK (SHALLOW)"
                zone_counts["zone1"] += 1
            else:
                zone = "ZONE_1"
                risk = "LOW RISK (SHALLOW)"
                zone_counts["zone1"] += 1

            detections.append({
                "zone": zone,
                "riskLevel": risk,
                "position": {
                    "x": round((cx / img_w) * 100, 2),
                    "y": round((cy_bottom / img_h) * 100, 2)
                }
            })

    overall_risk = "SAFE"
    if zone_counts["zone3"] > 0:
        overall_risk = "CRITICAL"
    elif zone_counts["zone2"] > 0:
        overall_risk = "WARNING"

    return detections, zone_counts, overall_risk, marked_frame


def get_video_writer(output_path, fps, width, height):
    codecs = [('avc1', '.mp4'), ('H264', '.mp4'), ('mp4v', '.mp4')]
    for codec, ext in codecs:
        fourcc = cv2.VideoWriter_fourcc(*codec)
        test_path = output_path + '_temp' + ext
        out = cv2.VideoWriter(test_path, fourcc, fps, (width, height))
        opened = out.isOpened()
        out.release()
        if os.path.exists(test_path):
            try:
                os.remove(test_path)
            except OSError:
                pass
        if opened:
            actual_path = output_path + ext
            writer = cv2.VideoWriter(actual_path, fourcc, fps, (width, height))
            return writer, actual_path

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    actual_path = output_path + '.mp4'
    writer = cv2.VideoWriter(actual_path, fourcc, fps, (width, height))
    return writer, actual_path


def main():
    if len(sys.argv) < 2:
        print(f"RESULT: {json.dumps({'success': False, 'error': 'No file path specified.'})}", flush=True)
        return

    media_path = sys.argv[1]

    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(os.path.dirname(script_dir), "config", "poolCalibration.json")

    calibration = None
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                calibration = json.load(f)
        except Exception as e:
            print(f"DEBUG: Failed to load poolCalibration.json: {str(e)}")

    if not os.path.exists(media_path):
        print(f"RESULT: {json.dumps({'success': False, 'error': f'File not found at: {media_path}'})}", flush=True)
        return

    ext = os.path.splitext(media_path)[1].lower()
    is_video = ext in ['.mp4', '.mov', '.avi', '.mkv', '.webm']

    try:
        model = YOLO("yolov8n.pt")

        if not is_video:
            img = cv2.imread(media_path)
            if img is None:
                print(f"RESULT: {json.dumps({'success': False, 'error': 'Could not open or decode the image file.'})}", flush=True)
                return

            detections, zone_counts, overall_risk, marked_frame = process_frame(img, model, calibration)
            dir_name = os.path.dirname(media_path)
            file_name = os.path.basename(media_path)
            base_name, _ = os.path.splitext(file_name)
            output_filename = f"processed-{base_name}.jpg"
            output_path = os.path.join(dir_name, output_filename)
            cv2.imwrite(output_path, marked_frame)

            output = {
                "success": True,
                "mediaType": "image",
                "processedUrl": f"/uploads/{output_filename}",
                "imageWidth": img.shape[1],
                "imageHeight": img.shape[0],
                "occupancy": len(detections),
                "zones": zone_counts,
                "overallRisk": overall_risk,
                "detections": detections
            }
            print(f"RESULT: {json.dumps(output)}", flush=True)

        else:
            cap = cv2.VideoCapture(media_path)
            if not cap.isOpened():
                print(f"RESULT: {json.dumps({'success': False, 'error': 'Could not open the video file.'})}", flush=True)
                return

            fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            dir_name = os.path.dirname(media_path)
            file_name = os.path.basename(media_path)
            base_name, _ = os.path.splitext(file_name)
            output_base = os.path.join(dir_name, f"processed-{base_name}")

            process_every_n = os.environ.get('PROCESS_EVERY_N_FRAMES')
            process_fps = os.environ.get('PROCESS_FPS')

            if process_every_n:
                try:
                    stride = int(process_every_n)
                except ValueError:
                    stride = 30
            elif process_fps:
                try:
                    stride = max(1, int(fps / float(process_fps)))
                except ValueError:
                    stride = 30
            else:
                stride = 30

            if stride < 1:
                stride = 1

            writer_fps = max(1.0, fps / stride)
            writer, final_output_path = get_video_writer(output_base, writer_fps, width, height)
            if not writer.isOpened():
                print(f"RESULT: {json.dumps({'success': False, 'error': 'Could not initialize video writer.'})}", flush=True)
                cap.release()
                return

            frame_stats = []
            processed_count = 0
            total_frames_est = max(1, total_frames)
            frame_idx = 0

            while True:
                if frame_idx % stride == 0:
                    ret, frame = cap.read()
                    if not ret:
                        break

                    detections, zone_counts, overall_risk, marked_frame = process_frame(frame, model, calibration)
                    frame_stats.append({
                        "frameIndex": frame_idx,
                        "occupancy": len(detections),
                        "zones": zone_counts,
                        "overallRisk": overall_risk,
                        "detections": detections
                    })
                    writer.write(marked_frame)
                    processed_count += 1

                    progress_pct = 0
                    if total_frames_est > 0:
                        progress_pct = min(99, int((frame_idx / total_frames_est) * 100))

                    progress_info = {
                        "progress": progress_pct,
                        "framesProcessed": processed_count,
                        "peopleDetected": len(detections)
                    }
                    print(f"PROGRESS: {json.dumps(progress_info)}", flush=True)
                else:
                    ret = cap.grab()
                    if not ret:
                        break
                frame_idx += 1

            cap.release()
            writer.release()

            latest_frame = frame_stats[-1] if frame_stats else {
                "occupancy": 0,
                "zones": {"zone1": 0, "zone2": 0, "zone3": 0},
                "overallRisk": "SAFE",
                "detections": []
            }

            output = {
                "success": True,
                "mediaType": "video",
                "processedUrl": f"/uploads/{os.path.basename(final_output_path)}",
                "imageWidth": width,
                "imageHeight": height,
                "occupancy": latest_frame["occupancy"],
                "zones": latest_frame["zones"],
                "overallRisk": latest_frame["overallRisk"],
                "detections": latest_frame["detections"],
                "frameStats": frame_stats
            }
            print(f"RESULT: {json.dumps(output)}", flush=True)

    except Exception as e:
        print(f"RESULT: {json.dumps({'success': False, 'error': str(e)})}", flush=True)


if __name__ == "__main__":
    main()
