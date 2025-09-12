import cv2
import numpy as np
import subprocess
import os
import sys
from pathlib import Path
from ultralytics import YOLO
from utils.sort import Sort
from utils.visualization import overlay_heatmap
from utils.helpers import centroid_from_bbox, update_velocities

class VideoProcessor:
    def __init__(self, model_path="yolov8n.pt"):
        """Initialize the video processor with YOLO model"""
        self.model = YOLO(model_path)
        self.allowed_classes = {"person", "sports ball"}
        
    def process_video(self, input_path, output_path, trail_len=30, heatmap=False):
        """
        Process video with YOLO tracking and ball trajectory prediction
        
        Args:
            input_path (str): Path to input video
            output_path (str): Path to save processed video
            trail_len (int): Length of trajectory trails
            heatmap (bool): Whether to overlay heatmap
            
        Returns:
            dict: Processing results and statistics
        """
        try:
            # Open input video
            cap = cv2.VideoCapture(input_path)
            if not cap.isOpened():
                raise ValueError(f"Cannot open video: {input_path}")

            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Setup output video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

            # Initialize tracker and buffers
            tracker = Sort(max_age=8, min_hits=1, iou_threshold=0.3)
            trails, velocities, labels = {}, {}, {}
            heatmap_accum = np.zeros((height, width), dtype=np.float32)
            
            # Processing statistics
            stats = {
                'total_frames': total_frames,
                'processed_frames': 0,
                'players_detected': set(),
                'ball_detections': 0,
                'processing_fps': 0
            }
            
            frame_count = 0
            start_time = cv2.getTickCount()

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # Run YOLO inference
                results = self.model(frame, verbose=False)[0]
                detections = []
                cls_map = {}

                # Process detections
                for box in results.boxes:
                    cls_id = int(box.cls[0])
                    cls_name = self.model.names[cls_id]
                    
                    if cls_name in self.allowed_classes:
                        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                        conf = float(box.conf[0])
                        detections.append([x1, y1, x2, y2, conf])
                        cls_map[(x1, y1, x2, y2)] = cls_name

                detections = np.array(detections)
                
                # Update tracker
                if len(detections) > 0:
                    tracked = tracker.update(detections)
                else:
                    tracked = []

                # Process tracked objects
                vis_frame = frame.copy()
                for x1, y1, x2, y2, tid in tracked:
                    tid = int(tid)
                    cx, cy = centroid_from_bbox((int(x1), int(y1), int(x2 - x1), int(y2 - y1)))

                    # Save class name
                    bbox_key = (int(x1), int(y1), int(x2), int(y2))
                    label = cls_map.get(bbox_key, "object")
                    labels[tid] = label

                    # Update trails
                    trails.setdefault(tid, []).append((cx, cy))
                    trails[tid] = trails[tid][-trail_len:]

                    # Update velocities
                    velocities[tid] = update_velocities(trails[tid], fps)

                    # Update statistics
                    if label == "person":
                        stats['players_detected'].add(tid)
                    elif label == "sports ball":
                        stats['ball_detections'] += 1

                    # Heatmap accumulation
                    if heatmap:
                        heatmap_accum[cy, cx] += 1

                    # Draw trajectory trails
                    for i in range(1, len(trails[tid])):
                        cv2.line(vis_frame, trails[tid][i - 1], trails[tid][i], (0, 255, 0), 2)

                    # Draw velocity text
                    vx, vy = velocities[tid]
                    cv2.putText(vis_frame, f"v=({vx:.1f},{vy:.1f})", (cx, cy - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                    # Ball trajectory prediction
                    if label == "sports ball":
                        for step in range(1, 20):  # predict 20 frames ahead
                            fx, fy = int(cx + vx * step), int(cy + vy * step)
                            if 0 <= fx < width and 0 <= fy < height:
                                cv2.circle(vis_frame, (fx, fy), 2, (0, 0, 255), -1)

                    # Draw bounding box and label
                    color = (255, 0, 0) if label == "person" else (0, 255, 255)
                    cv2.rectangle(vis_frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                    cv2.putText(vis_frame, f"{label} ID{tid}", (int(x1), int(y1) - 5),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                # Overlay heatmap if enabled
                if heatmap:
                    vis_frame = overlay_heatmap(vis_frame, heatmap_accum, alpha=0.45)

                # Write frame to output video
                out.write(vis_frame)
                frame_count += 1

            # Calculate final statistics
            end_time = cv2.getTickCount()
            processing_time = (end_time - start_time) / cv2.getTickFrequency()
            stats['processed_frames'] = frame_count
            stats['processing_fps'] = frame_count / processing_time if processing_time > 0 else 0
            stats['players_detected'] = len(stats['players_detected'])
            stats['processing_time'] = processing_time

            # Cleanup
            cap.release()
            out.release()
            cv2.destroyAllWindows()

            return {
                'success': True,
                'output_path': output_path,
                'stats': stats
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

def process_video_file(input_path, output_path, **kwargs):
    """Convenience function to process a video file"""
    processor = VideoProcessor()
    return processor.process_video(input_path, output_path, **kwargs)

if __name__ == "__main__":
    # Test the processor
    if len(sys.argv) != 3:
        print("Usage: python video_processor.py <input_video> <output_video>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    result = process_video_file(input_path, output_path, heatmap=True)
    
    if result['success']:
        print(f"✅ Video processed successfully!")
        print(f"Output: {result['output_path']}")
        print(f"Stats: {result['stats']}")
    else:
        print(f"❌ Error processing video: {result['error']}")
        sys.exit(1)
