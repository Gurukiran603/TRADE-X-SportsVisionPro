import cv2
import numpy as np

def draw_tracks(frame, tracked, trails, velocities, fps):
    for x1,y1,x2,y2,tid in tracked:
        tid = int(tid)
        x1,y1,x2,y2 = map(int, (x1,y1,x2,y2))
        cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)

        v = velocities.get(tid, 0.0)
        cv2.putText(frame, f"ID:{tid}", (x1, y1-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
        cv2.putText(frame, f"{v:.1f}px/s", (x1, y2+15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255,255,255), 1)

        pts = trails.get(tid, [])
        for i in range(1, len(pts)):
            cv2.line(frame, pts[i-1], pts[i], (0,0,255), 2)
        if pts:
            cv2.circle(frame, pts[-1], 4, (0,255,255), -1)
    return frame

def overlay_heatmap(frame, heatmap, alpha=0.5):
    hmap = heatmap.copy()
    if hmap.max() > 0:
        hmap = (hmap / hmap.max() * 255).astype(np.uint8)
    colored = cv2.applyColorMap(hmap, cv2.COLORMAP_JET)
    return cv2.addWeighted(frame, 1-alpha, colored, alpha, 0)

"""


import cv2

def init_trails():
    return {}

def draw_tracks(frame, tracks, trails, color=(0, 255, 0)):
    
  #  Draws bounding boxes and trajectory lines for players & ball.
    
    for trk in tracks:
        x1, y1, x2, y2, obj_id = [int(i) for i in trk]

        # Draw bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, f"ID:{obj_id}", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Center point of the object
        center = (int((x1 + x2) / 2), int((y1 + y2) / 2))

        # Update trails
        if obj_id not in trails:
            trails[obj_id] = []
        trails[obj_id].append(center)

        # Draw trajectory line
        for j in range(1, len(trails[obj_id])):
            cv2.line(frame, trails[obj_id][j-1], trails[obj_id][j], (0, 0, 255), 2)

    return frame
"""