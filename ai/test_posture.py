import cv2
import numpy as np

from ultralytics import YOLO

from posture_classifier import (
    PostureClassifier
)

model = YOLO(
    "yolo11n-pose.pt"
)

classifier = (
    PostureClassifier()
)

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

    annotated = frame.copy()

    if len(results[0].keypoints.xy):

        keypoints = (
            results[0]
            .keypoints
            .xy[0]
            .cpu()
            .numpy()
        )

        posture = (
            classifier.classify(
                keypoints
            )
        )

        annotated = (
            results[0]
            .plot()
        )

        cv2.putText(
            annotated,
            posture,
            (30,50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0,0,255),
            3
        )

    cv2.imshow(
        "POSTURE",
        annotated
    )

    if cv2.waitKey(1)==27:
        break

cap.release()
cv2.destroyAllWindows()