import cv2
import numpy as np

bg_sub = cv2.createBackgroundSubtractorMOG2(history=300, varThreshold=25, detectShadows=False)

def detect_bboxes(gray_frame, min_area=150):
    fg = bg_sub.apply(gray_frame)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, kernel, iterations=1)
    fg = cv2.dilate(fg, kernel, iterations=2)

    contours, _ = cv2.findContours(fg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = []
    for c in contours:
        if cv2.contourArea(c) < min_area:
            continue
        x,y,w,h = cv2.boundingRect(c)
        boxes.append((x,y,w,h))
    return boxes

def centroid_from_bbox(bbox):
    x, y, w, h = bbox
    return x + w // 2, y + h // 2
"""
def update_velocities(trail, fps):
    if len(trail) < 2: return 0.0
    (x0,y0), (x1,y1) = trail[-2], trail[-1]
    dist = ((x1-x0)**2 + (y1-y0)**2) ** 0.5
    return dist * fps  # pixels/sec
"""


def update_velocities(trail, fps):
    if len(trail) >= 2:
        (x1, y1), (x2, y2) = trail[-2], trail[-1]
        vx = (x2 - x1) * fps
        vy = (y2 - y1) * fps
        return (vx, vy)
    return (0.0, 0.0)

