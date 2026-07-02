from ultralytics import YOLO

model = YOLO("yolo11n-pose.pt")

def detect_pose(frame):

    results = model(frame)

    return results
    