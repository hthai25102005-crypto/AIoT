# AIoT Fall Detection System

> Real-time Fall Detection using **YOLO11 Pose**, **ESP32**, **MPU6050**, **MQTT**, and **Telegram**.

---

## Overview

This project implements an AIoT-based fall detection system that combines computer vision and inertial sensor data to improve fall detection accuracy. The system performs real-time posture estimation using **YOLO11 Pose**, fuses pose information with **MPU6050** sensor data, and automatically sends alerts through **Telegram** when a fall is detected.

### Key Features

- 🎥 Real-time human pose estimation using YOLO11 Pose
- 📡 ESP32 + MPU6050 sensor acquisition via MQTT
- 🧠 Sensor fusion with Fall Score Engine
- 📊 Modern real-time monitoring dashboard
- 📷 Automatic image capture during fall events
- 📲 Telegram notifications with event information
- ⚡ CUDA acceleration supported (NVIDIA GPU)

---

## System Architecture

```text
USB Camera
     │
     ▼
YOLO11 Pose Detection
     │
     ▼
Posture Classification
     │
     ▼
Fall Score Engine ◄──────── ESP32 + MPU6050
     │                         │
     │                         ▼
     │                      MQTT Broker
     ▼
Decision Engine
     │
     ├── Dashboard
     ├── Event Log
     └── Telegram Alert
```

---

## Hardware

| Component | Description |
|-----------|-------------|
| USB Camera | Dahua Z2 Webcam |
| ESP32 | Sensor Gateway |
| MPU6050 | Accelerometer & Gyroscope |
| PC/Laptop | AI Processing |
| NVIDIA GTX 1650 | CUDA Inference |

---

## Software

- Python 3.10
- OpenCV
- Ultralytics YOLO11 Pose
- PyTorch CUDA
- MQTT
- Tkinter / CustomTkinter
- Pillow
- NumPy

---

## Project Structure

```text
FallDetectionAIoT/
├── ai/
├── gui/
├── mqtt/
├── models/
├── images/
├── telegram_notifier.py
├── main.py
└── README.md
```

---

## Workflow

1. Capture image from USB camera.
2. Detect human pose using YOLO11 Pose.
3. Read MPU6050 data from ESP32 through MQTT.
4. Compute Fall Score using sensor fusion.
5. Detect fall events.
6. Save captured image.
7. Send Telegram notification.
8. Update dashboard in real time.

---

## Experimental Results

| Item | Result |
|------|--------|
| Standing Detection | ✅ |
| Sitting Detection | ✅ |
| Lying Detection | ✅ |
| Fall Detection | ✅ |
| Dashboard | Stable |
| Telegram Alert | Working |
| MQTT Communication | Stable |

### Test Configuration

| Component | Specification |
|-----------|---------------|
| Camera | 1280×720 |
| GPU | NVIDIA GTX 1650 |
| FPS | ~18–22 FPS |
| OS | Windows 10 |
| Python | 3.10 |

---

## Advantages

- Real-time processing
- AI + IoT integration
- Automatic notification
- User-friendly dashboard
- Expandable architecture

---

## Future Improvements

- Multi-thread camera pipeline
- Multi-person tracking
- TensorRT optimization
- Cloud database integration
- Mobile application
- Web dashboard

---

## Conclusion

The developed AIoT Fall Detection System successfully integrates computer vision and IoT sensing to provide reliable real-time fall detection. By combining YOLO11 Pose estimation with MPU6050 sensor data, the system improves detection reliability and delivers immediate alerts through Telegram while providing an intuitive monitoring dashboard.

---

## Author

**Student:** Hoàng Trung Hải

**Project:** AIoT Fall Detection using YOLO11 Pose and MPU6050
