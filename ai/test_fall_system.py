import cv2
import time
from ultralytics import YOLO

from ai.posture_classifier import PostureClassifier
from ai.fusion import FusionSystem
from ai.telegram_notifier import TelegramNotifier

import random

model = YOLO("yolo11n-pose.pt")
classifier = PostureClassifier()
fusion = FusionSystem()

telegram = TelegramNotifier(
    token="YOUR_BOT_TOKEN",
    chat_id="YOUR_CHAT_ID"
)

if result["fall"]:

    filename = (
        f"images/captures/"
        f"fall_{int(time.time())}.jpg"
    )

    cv2.imwrite(
        filename,
        annotated
    )

    telegram.send_photo(
        filename,
        caption=
        f"⚠️ FALL DETECTED\n"
        f"POSTURE={posture}\n"
        f"SCORE={result['score']}"
    )
fusion = FusionSystem(telegram)

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

while True:

    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, verbose=False)

    posture = "UNKNOWN"

    if len(results[0].keypoints.xy):

        keypoints = results[0].keypoints.xy[0].cpu().numpy()

        posture = classifier.classify(keypoints)

    from mqtt.mqtt_receiver import sensor_data

    result = fusion.process(sensor_data, posture)

    annotated = results[0].plot()

    cv2.putText(
        annotated,
        f"POSTURE: {posture}",
        (30, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0,255,0),
        2
    )

    cv2.putText(
        annotated,
        f"SCORE: {result['score']}",
        (30, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0,255,255),
        2
    )

    cv2.putText(
        annotated,
        f"FALL: {result['fall']}",
        (30, 120),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0,0,255),
        2
    )

    cv2.imshow("FALL DETECTION SYSTEM", annotated)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()