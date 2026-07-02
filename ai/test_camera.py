import cv2

for i in range(3):
    cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
    if cap.isOpened():
        print(f"Camera index {i} OK")
        break
    cap.release()
else:
    cap = cv2.VideoCapture(0, cv2.CAP_MSMF)
    if not cap.isOpened():
        print("Khong tim thay camera nao")
        exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Camera read failed")
        break

    cv2.imshow("Webcam", frame)
    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()