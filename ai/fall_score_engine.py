import time
import math
from collections import deque


class FallScoreEngine:
    """Phat hien te ngA thong minh.
    Ket hop: accelerometer (free fall + impact) + gyroscope (xoay) + posture.
    """

    FALL_THRESHOLD = 55
    RECOVER_THRESHOLD = 20

    def __init__(self):
        self.prev_posture = "UNKNOWN"
        self.score = 0
        self._in_fall = False
        self._history = deque(maxlen=30)
        self.fall_start_time = None

    def reset(self):
        self.score = 0
        self.fall_start_time = None
        self._in_fall = False

    def verify_fall_duration(self, posture):
        if posture == "LYING":
            if self.fall_start_time is None:
                self.fall_start_time = time.time()
            return (time.time() - self.fall_start_time) >= 3
        self.fall_start_time = None
        return False

    def update(self, sensor_data, posture):
        ax = sensor_data.get("ax", 0)
        ay = sensor_data.get("ay", 0)
        az = sensor_data.get("az", 9.8)
        mag = sensor_data.get("mag", 0)

        # Gyroscope
        gx = sensor_data.get("gx", 0)
        gy = sensor_data.get("gy", 0)
        gz = sensor_data.get("gz", 0)

        # Gia toc tong
        accel = math.sqrt(ax * ax + ay * ay + az * az)
        if accel < 0.5:
            accel = mag

        # Gyroscope magnitude (do xoay)
        gyro_mag = math.sqrt(gx * gx + gy * gy + gz * gz)

        self._history.append({
            "accel": accel, "gyro": gyro_mag,
            "posture": posture, "time": time.time()
        })

        score = 0

        # ==== PHAN TICH CAM BIEN ====
        recent = list(self._history)[-3:]

        has_free_fall = any(h["accel"] < 3.0 for h in list(self._history)[-3:])
        has_impact = any(h["accel"] > 18.0 for h in recent)
        has_strong_impact = any(h["accel"] > 25.0 for h in recent)

        # Phat hien xoay nguoi (te nga thuong xoay > 80 do/s)
        has_rotation = any(h["gyro"] > 80.0 for h in recent)
        has_strong_rotation = any(h["gyro"] > 160.0 for h in recent)

        # ==== PHAN TICH TU THE ====
        is_lying = posture == "LYING"
        transition_to_lying = (
            self.prev_posture in ["STANDING", "SITTING"] and is_lying
        )

        posture_hist = [h["posture"] for h in list(self._history)[-10:]]
        current_lying = posture == "LYING"
        was_up_before = any(
            p in ["STANDING", "SITTING"] for p in posture_hist[:-2]
        )
        rapid_change = current_lying and was_up_before

        # ==== GYROSCOPE BONUS ====
        # Xoay manh + nam gap = te nga rat cao
        if has_strong_rotation and rapid_change:
            bonus = 25
        elif has_rotation and rapid_change:
            bonus = 15
        elif has_strong_rotation:
            bonus = 10
        elif has_rotation:
            bonus = 5
        else:
            bonus = 0

        # ==== TINH DIEM ====
        if has_free_fall and has_impact and is_lying:
            score = 90  # Te that: roi + va cham + nam
        elif has_strong_impact and rapid_change:
            score = 85
        elif has_impact and rapid_change:
            score = 75
        elif has_free_fall and has_rotation:
            score = 70  # Roi + xoay = te
        elif rapid_change and has_rotation:
            score = 65  # Nam gap + xoay = te
        elif rapid_change:
            score = 50  # Nam gap, thieu cam bien
        elif has_impact and is_lying:
            score = 50
        elif has_free_fall:
            score = 40
        elif transition_to_lying:
            score = 15  # Nam tu tu (tap)
        elif is_lying:
            score = 5
        elif has_strong_impact:
            score = 15
        elif has_impact:
            score = 5

        # Cong bonus gyroscope
        score += bonus
        # Thuong nam lau (bat dong sau te)
        if score >= 25 and is_lying and self.verify_fall_duration(posture):
            score += 10

        # ==== PHAT HIEN TE NGAY (sensor-based, truoc khi posture thay doi) ====
        # Accel giam < 5 + gyro > 80 = dang roi + xoay => uu tien cao
        if accel < 5.0 and gyro_mag > 80.0:
            score = max(score, 78)

        score = max(0, min(score, 100))
        self.score = score
        self.prev_posture = posture
        return score

    def is_fall(self, score):
        if self._in_fall:
            self._in_fall = score >= self.RECOVER_THRESHOLD
        else:
            self._in_fall = score >= self.FALL_THRESHOLD
        return self._in_fall
