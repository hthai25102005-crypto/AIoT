import cv2
from ultralytics import YOLO

print("Loading YOLO11 Pose...")

model = YOLO("yolo11n-pose.pt")

print("Model Loaded!")

cap = cv2.VideoCapture(
    0,
    cv2.CAP_DSHOW
)

while True:

    ret, frame = cap.read()

    if not ret:
        break

    results = model(
        frame,
        verbose=False
    )

    annotated_frame = results[0].plot()

    cv2.imshow(
        "YOLO11 Pose",
        annotated_frame
    )

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()