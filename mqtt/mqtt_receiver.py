import json
import time
import threading
import paho.mqtt.client as mqtt

# ==================================
# GLOBAL SENSOR DATA (mo rong)
# ==================================

sensor_data = {
    "ax": 0.0, "ay": 0.0, "az": 9.8,
    "gx": 0.0, "gy": 0.0, "gz": 0.0,
    "mag": 9.8, "gyro": 0.0,
    "temp": 25.0,
    "pitch": 0.0, "roll": 0.0,
    "impact": 0.0, "delta": 0.0,
    "seq": 0, "ts": 0,
    "connected": False,
    "timestamp": time.time()
}

# ==================================
# FILTER
# ==================================

_history = []
_MAX_HISTORY = 5
_last_mag = 9.8


def smooth(values):
    if not values:
        return 0
    return sum(values) / len(values)


def on_message(client, userdata, msg):
    global sensor_data, _history, _last_mag

    try:
        payload = json.loads(msg.payload.decode())

        ax = float(payload.get("ax", 0))
        ay = float(payload.get("ay", 0))
        az = float(payload.get("az", 9.8))

        gx = float(payload.get("gx", 0))
        gy = float(payload.get("gy", 0))
        gz = float(payload.get("gz", 0))

        mag = float(payload.get("mag", 9.8))
        gyro = float(payload.get("gyro", 0))
        temp = float(payload.get("temp", 25.0))
        pitch = float(payload.get("pitch", 0))
        roll = float(payload.get("roll", 0))
        seq = int(payload.get("seq", 0))
        ts = int(payload.get("ts", 0))

        # ==========================
        # FILTER MAG
        # ==========================
        _history.append(mag)
        if len(_history) > _MAX_HISTORY:
            _history.pop(0)

        mag_smooth = smooth(_history)

        delta = abs(mag_smooth - _last_mag)
        _last_mag = mag_smooth

        # ==========================
        # UPDATE DATA (in-place de main.py thay doi)
        # ==========================
        sensor_data.update({
            "ax": ax, "ay": ay, "az": az,
            "gx": gx, "gy": gy, "gz": gz,
            "mag": mag_smooth,
            "gyro": gyro,
            "temp": temp,
            "pitch": pitch, "roll": roll,
            "impact": mag,
            "delta": delta,
            "seq": seq, "ts": ts,
            "connected": True,
            "timestamp": time.time()
        })

    except Exception as e:
        print("[MQTT ERROR]", e)


def start_mqtt():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_message = on_message

    try:
        client.connect("localhost", 1883, 60)
        client.subscribe("fall/sensor")
        client.loop_start()
        print("[MQTT] Connected")
    except Exception as e:
        print("[MQTT] Failed", e)


def watchdog():
    global sensor_data
    while True:
        now = time.time()
        if (now - sensor_data["timestamp"]) > 5:
            sensor_data["connected"] = False
        time.sleep(1)


threading.Thread(target=start_mqtt, daemon=True).start()
threading.Thread(target=watchdog, daemon=True).start()
