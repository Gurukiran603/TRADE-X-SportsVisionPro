"""
import argparse
import cv2
import numpy as np
from ultralytics import YOLO
from utils.sort import Sort
from utils.visualization import draw_tracks, init_trails
from ultralytics import YOLO

# Allowed classes: person (0), sports ball (32)
ALLOWED_CLASSES = [0, 32]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help="Path to input video")
    parser.add_argument("--output", type=str, required=True, help="Path to save output video")
    parser.add_argument("--show", action="store_true", help="Show video live")
    args = parser.parse_args()

    # Load YOLOv8 small model
    model = YOLO("yolov8n.pt")  # download automatically

    cap = cv2.VideoCapture(args.input)
    if not cap.isOpened():
        print(f"❌ Cannot open video: {args.input}")
        return

    # Output writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(args.output, fourcc,
                          cap.get(cv2.CAP_PROP_FPS),
                          (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                           int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))

    # Tracker + trails
    tracker = Sort(max_age=15, min_hits=2, iou_threshold=0.2)
    trails = init_trails()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # YOLO inference
        results = model(frame, verbose=False)

        dets = []
        for r in results[0].boxes:
            cls = int(r.cls[0])
            if cls in ALLOWED_CLASSES:  # filter only person & ball
                x1, y1, x2, y2 = map(int, r.xyxy[0])
                conf = float(r.conf[0])
                dets.append([x1, y1, x2, y2, conf])

        dets = np.array(dets)
        if len(dets) == 0:
            tracked = []
        else:
            tracked = tracker.update(dets)

        # Draw results
        frame = draw_tracks(frame, tracked, trails)

        out.write(frame)
        if args.show:
            cv2.imshow("YOLO-SORT Tracker", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"✅ Saved output to {args.output}")

if __name__ == "__main__":
    main()
    
    
    
    ------------------------------------------------



import argparse
import cv2
import numpy as np
from ultralytics import YOLO
from utils.sort import Sort
from utils.visualization import draw_tracks, overlay_heatmap
from utils.helpers import centroid_from_bbox, update_velocities



def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, help="Path to input video")
    p.add_argument("--output", default="out.mp4", help="Path to write output video")
    p.add_argument("--show", action="store_true", help="Show live window")
    p.add_argument("--heatmap", action="store_true", help="Enable heatmap overlay")
    p.add_argument("--trail_len", type=int, default=30, help="Trajectory trail length")
    return p.parse_args()


def main():
    args = parse_args()
    cap = cv2.VideoCapture(args.input)
    if not cap.isOpened():
        raise SystemExit(f"❌ Cannot open input video: {args.input}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    writer = cv2.VideoWriter(
        args.output,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (w, h)
    )

    # Load YOLO model
    model = YOLO("yolov8n.pt")
    allowed_classes = {"person", "sports ball"}

    # Tracker + buffers
    tracker = Sort(max_age=8, min_hits=1, iou_threshold=0.3)
    trails, velocities = {}, {}
    heatmap_accum = np.zeros((h, w), dtype=np.float32)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # YOLO inference
        results = model(frame, verbose=False)[0]
        dets = []
        det_classes = {}  # map track_id -> class

        for box in results.boxes:
            cls_id = int(box.cls[0])
            cls_name = model.names[cls_id]
            if cls_name in allowed_classes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                conf = float(box.conf[0])
                dets.append([x1, y1, x2, y2, conf])
        dets = np.array(dets)

        # Update tracker
        if dets is not None and len(dets) > 0:
            tracked = tracker.update(dets)
        else:
            tracked = []

        # Draw + velocity + trajectory
        vis = frame.copy()
        for x1, y1, x2, y2, tid in tracked:
            tid = int(tid)
            cx, cy = centroid_from_bbox((int(x1), int(y1), int(x2-x1), int(y2-y1)))
            trails.setdefault(tid, []).append((cx, cy))
            trails[tid] = trails[tid][-args.trail_len:]
            velocities[tid] = update_velocities(trails[tid], fps)

            # Heatmap
            if args.heatmap:
                heatmap_accum[cy, cx] += 1

            # Draw trajectory trails
            for i in range(1, len(trails[tid])):
                cv2.line(vis, trails[tid][i - 1], trails[tid][i], (0, 255, 0), 2)

            # Show velocity text
            vx, vy = velocities[tid]
            cv2.putText(vis, f"v=({vx:.1f},{vy:.1f})", (cx, cy - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            # Ball trajectory prediction (future path)
            # Rough check: assume smaller bbox = ball
            if (x2 - x1) < 50 and (y2 - y1) < 50:
                for step in range(1, 15):  # predict next 15 frames
                    fx, fy = int(cx + vx * step), int(cy + vy * step)
                    if 0 <= fx < w and 0 <= fy < h:
                        cv2.circle(vis, (fx, fy), 2, (0, 0, 255), -1)
            
             

            # Draw detection box
            cv2.rectangle(vis, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
            cv2.putText(vis, f"ID {tid}", (int(x1), int(y1) - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        # Overlay heatmap
        if args.heatmap:
            vis = overlay_heatmap(vis, heatmap_accum, alpha=0.45)

        writer.write(vis)
        if args.show:
            cv2.imshow("Tracks", vis)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    writer.release()
    cv2.destroyAllWindows()
    print(f"✅ Done. Output saved to {args.output}")


if __name__ == "__main__":
    main()

"""
import argparse
import cv2
import numpy as np
from ultralytics import YOLO
from utils.sort import Sort
from utils.visualization import overlay_heatmap
from utils.helpers import centroid_from_bbox, update_velocities


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, help="Path to input video")
    p.add_argument("--output", default="out.mp4", help="Path to write output video")
    p.add_argument("--show", action="store_true", help="Show live window")
    p.add_argument("--heatmap", action="store_true", help="Enable heatmap overlay")
    p.add_argument("--trail_len", type=int, default=30, help="Trajectory trail length")
    return p.parse_args()


def main():
    args = parse_args()
    cap = cv2.VideoCapture(args.input)
    if not cap.isOpened():
        raise SystemExit(f"❌ Cannot open input video: {args.input}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    writer = cv2.VideoWriter(
        args.output,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (w, h)
    )

    # Load YOLOv8 model
    model = YOLO("yolov8n.pt")
    allowed_classes = {"person", "sports ball"}

    # Tracker + buffers
    tracker = Sort(max_age=8, min_hits=1, iou_threshold=0.3)
    trails, velocities, labels = {}, {}, {}
    heatmap_accum = np.zeros((h, w), dtype=np.float32)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Run YOLO inference
        results = model(frame, verbose=False)[0]
        dets = []
        cls_map = {}

        for box in results.boxes:
            cls_id = int(box.cls[0])
            cls_name = model.names[cls_id]
            if cls_name in allowed_classes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                conf = float(box.conf[0])
                dets.append([x1, y1, x2, y2, conf])
                cls_map[(x1, y1, x2, y2)] = cls_name

        dets = np.array(dets)
        if len(dets) > 0:
            tracked = tracker.update(dets)
        else:
            tracked = []

        vis = frame.copy()

        for x1, y1, x2, y2, tid in tracked:
            tid = int(tid)
            cx, cy = centroid_from_bbox((int(x1), int(y1), int(x2 - x1), int(y2 - y1)))

            # Save class name
            bbox_key = (int(x1), int(y1), int(x2), int(y2))
            label = cls_map.get(bbox_key, "object")
            labels[tid] = label

            # Trails
            trails.setdefault(tid, []).append((cx, cy))
            trails[tid] = trails[tid][-args.trail_len:]

            # Velocities
            velocities[tid] = update_velocities(trails[tid], fps)

            # Heatmap
            if args.heatmap:
                heatmap_accum[cy, cx] += 1

            # Draw trails
            for i in range(1, len(trails[tid])):
                cv2.line(vis, trails[tid][i - 1], trails[tid][i], (0, 255, 0), 2)

            # Velocity text
            vx, vy = velocities[tid]
            cv2.putText(vis, f"v=({vx:.1f},{vy:.1f})", (cx, cy - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            # Ball forward trajectory prediction
            if label == "sports ball":
                for step in range(1, 20):  # predict 20 frames ahead
                    fx, fy = int(cx + vx * step), int(cy + vy * step)
                    if 0 <= fx < w and 0 <= fy < h:
                        cv2.circle(vis, (fx, fy), 2, (0, 0, 255), -1)

            # Draw bbox + label
            color = (255, 0, 0) if label == "person" else (0, 255, 255)
            cv2.rectangle(vis, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
            cv2.putText(vis, f"{label} ID{tid}", (int(x1), int(y1) - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Overlay heatmap
        if args.heatmap:
            vis = overlay_heatmap(vis, heatmap_accum, alpha=0.45)

        writer.write(vis)
        if args.show:
            cv2.imshow("YOLO Tracker", vis)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    writer.release()
    cv2.destroyAllWindows()
    print(f"✅ Done. Output saved to {args.output}")


if __name__ == "__main__":
    main()
