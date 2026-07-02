from ultralytics import YOLO
import cv2

print("Loading model...")

model = YOLO("yolo11n-pose.pt")

print("Model loaded!")

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

while True:

    ret, frame = cap.read()

    if not ret:
        break

    results = model(frame, verbose=False)

    frame = results[0].plot()

    cv2.imshow("YOLO11 Pose", frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()