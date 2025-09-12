

import argparse
import cv2
import numpy as np
#from sort import Sort
from utils.sort import Sort
from utils.visualization import draw_tracks, overlay_heatmap
from utils.helpers import detect_bboxes, centroid_from_bbox, update_velocities

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, help="Path to input video")
    p.add_argument("--output", default="out.mp4", help="Path to write output video")
    p.add_argument("--show", action="store_true", help="Show live window")
    p.add_argument("--heatmap", action="store_true", help="Enable heatmap overlay")
    p.add_argument("--trail_len", type=int, default=30, help="Trajectory trail length")
    p.add_argument("--min_area", type=int, default=150, help="Min contour area for detection")
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

    tracker = Sort(max_age=8, min_hits=1, iou_threshold=0.3)
    trails, velocities = {}, {}
    heatmap_accum = np.zeros((h, w), dtype=np.float32)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        bboxes = detect_bboxes(gray, min_area=args.min_area)

        dets = np.array([[x, y, x+w, y+h, 1.0] for (x,y,w,h) in bboxes])
        #tracked = tracker.update(dets)
        
        if dets is not None and len(dets) > 0:
            tracked = tracker.update(dets)
        else:
            tracked = []
        
        
        for x1,y1,x2,y2,tid in tracked:
            tid = int(tid)
            cx, cy = centroid_from_bbox((int(x1), int(y1), int(x2-x1), int(y2-y1)))
            trails.setdefault(tid, []).append((cx, cy))
            trails[tid] = trails[tid][-args.trail_len:]
            velocities[tid] = update_velocities(trails[tid], fps)
            if args.heatmap: heatmap_accum[cy, cx] += 1

        vis = draw_tracks(frame.copy(), tracked, trails, velocities, fps)
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
