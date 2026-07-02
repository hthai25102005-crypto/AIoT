HỆ THỐNG PHÁT HIỆN TÉ NGÃ AIoT SỬ DỤNG YOLO11 POSE VÀ CẢM BIẾN MPU6050
1. Giới thiệu

Hệ thống được xây dựng nhằm phát hiện sự kiện té ngã của con người trong thời gian thực bằng cách kết hợp giữa thị giác máy tính (Computer Vision) và cảm biến quán tính (IMU).

Khác với các hệ thống chỉ sử dụng camera hoặc chỉ sử dụng cảm biến, hệ thống này áp dụng phương pháp Sensor Fusion, kết hợp dữ liệu từ:

Camera USB Dahua Z2
YOLO11 Pose Estimation
ESP32
MPU6050
MQTT
Telegram Bot

để tăng độ chính xác và giảm cảnh báo giả.

2. Kiến trúc hệ thống
                USB Camera
                     │
                     ▼
            YOLO11 Pose Detector
                     │
                     ▼
           Posture Classifier
                     │
                     ▼
            Fall Score Engine
                     ▲
                     │
        ESP32 + MPU6050 Sensor
                     │
                  MQTT Broker
                     │
                     ▼
              Dashboard AIoT
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
    Telegram Bot          Event Logging
3. Thành phần phần cứng
Thiết bị	Chức năng
Laptop Windows	Chạy AI
GTX 1650	Tăng tốc YOLO
Webcam Dahua Z2	Thu hình
ESP32 DevKit	Gateway IoT
MPU6050	Gia tốc + Gyroscope
WiFi	Truyền MQTT
4. Thành phần phần mềm
Python 3.10
OpenCV
Ultralytics YOLO11
Torch CUDA
MQTT
Tkinter + CustomTkinter
Pillow
NumPy
5. Chức năng chính
5.1 Camera Realtime
Hiển thị video trực tiếp
FPS realtime
Overlay kết quả AI
5.2 Pose Detection

YOLO11 Pose nhận dạng 17 keypoints:

Head
Shoulder
Elbow
Wrist
Hip
Knee
Ankle
5.3 Posture Classification

Phân loại thành:

Standing
Sitting
Lying
Unknown
5.4 Sensor Monitoring

ESP32 nhận dữ liệu MPU6050:

AX
AY
AZ
Magnitude

Sau đó gửi MQTT về máy tính.

5.5 Fall Score Engine

Điểm té ngã được tính dựa trên:

Pose Score
+
Acceleration Score
+
Orientation Score
+
Motion Score
=
Fall Score

Giá trị:

0–100

Ngưỡng:

Score < 40
→ Normal

40–65
→ Warning

>65
→ Fall Detected
5.6 Telegram Notification

Khi phát hiện té ngã:

Hệ thống tự động gửi:

Thời gian
Tư thế
Fall Score
Magnitude
Ảnh chụp hiện trường
6. Dashboard

Dashboard hiển thị realtime:

✓ Camera

✓ FPS

✓ Pose

✓ Fall Score

✓ MPU6050

✓ Alert

✓ Risk Chart

✓ Event Log

✓ System Status

7. Luồng hoạt động
Camera
      │
      ▼
YOLO11 Pose
      │
      ▼
Posture Classification
      │
      ▼
Fall Score Engine
      ▲
      │
MPU6050
      │
      ▼
MQTT
      │
      ▼
Decision
      │
      ├────Normal
      │
      └────Fall
              │
              ▼
 Telegram Alert
8. Kết quả thực nghiệm
Thử nghiệm
Trạng thái	Kết quả
Đứng	Nhận dạng chính xác
Ngồi	Nhận dạng chính xác
Nằm	Nhận dạng chính xác
Té ngã	Phát hiện thành công
Hiệu năng

Thiết bị thử nghiệm:

CPU Intel
NVIDIA GTX1650
Webcam Dahua Z2

Kết quả:

Thông số	Giá trị
Độ phân giải	1280×720
FPS Dashboard	18–22 FPS
YOLO Device	CUDA
MQTT Delay	<100 ms
Telegram Delay	2–4 s
9. Ưu điểm
Phát hiện realtime.
Kết hợp AI và IoT.
Có cảnh báo Telegram.
Dashboard trực quan.
Hoạt động ổn định trên GPU tầm trung.
Có khả năng mở rộng.
10. Hạn chế
Phụ thuộc góc đặt camera.
Điều kiện ánh sáng ảnh hưởng đến Pose Detection.
Chưa hỗ trợ nhiều người cùng lúc.
Chưa tối ưu đa luồng hoàn toàn.
11. Hướng phát triển
Multi-thread Camera Pipeline.
Tracking nhiều người.
TensorRT tăng FPS.
ESP32 BLE.
Cloud Database.
Mobile App.
Dashboard Web.
Phân tích hành vi dài hạn.
Cảnh báo qua Zalo/SMS.
AI nhận diện bất tỉnh.
12. Cấu trúc thư mục
FallDetectionAIoT
│
├── ai
│   ├── pose_detector.py
│   ├── posture_classifier.py
│   └── fall_score_engine.py
│
├── gui
│   ├── dashboard.py
│   ├── camera_panel.py
│   ├── sensor_bar.py
│   └── status_panel.py
│
├── mqtt
│   └── mqtt_receiver.py
│
├── models
│   └── yolo11n-pose.pt
│
├── images
│   └── captures
│
├── telegram_notifier.py
│
├── main.py
│
└── README.md
Kết luận

Hệ thống đã xây dựng thành công mô hình phát hiện té ngã thời gian thực bằng cách kết hợp giữa thị giác máy tính và cảm biến IoT. Việc sử dụng YOLO11 Pose cùng dữ liệu từ MPU6050 giúp nâng cao độ tin cậy so với giải pháp chỉ dùng camera hoặc chỉ dùng cảm biến. Kết quả thử nghiệm cho thấy hệ thống có khả năng phát hiện các trạng thái đứng, ngồi, nằm và té ngã, đồng thời gửi cảnh báo tự động qua Telegram với độ trễ thấp. Kiến trúc hiện tại cũng tạo nền tảng thuận lợi để mở rộng lên các hệ thống giám sát thông minh trong tương lai.