import numpy as np
from collections import deque
from ai.geometry import calculate_angle


class PostureClassifier:

    def __init__(self, smooth_frames=5):
        self._history = deque(maxlen=smooth_frames)

    def classify(self, keypoints):
        try:
            # keypoints layout: 0=nose, 5=left_shoulder, 6=right_shoulder,
            # 7=left_elbow, 8=right_elbow, 9=left_wrist, 10=right_wrist,
            # 11=left_hip, 12=right_hip, 13=left_knee, 14=right_knee,
            # 15=left_ankle, 16=right_ankle

            # -- shoulders --
            ls = keypoints[5]; rs = keypoints[6]
            shoulder_c = (ls + rs) / 2

            # -- hips --
            lh = keypoints[11]; rh = keypoints[12]
            hip_c = (lh + rh) / 2

            # -- knees --
            lk = keypoints[13]; rk = keypoints[14]

            # -- ankles --
            la = keypoints[15]; ra = keypoints[16]

            # ======= ANGLES =======
            torso_angle = calculate_angle(shoulder_c, hip_c,
                                          np.array([hip_c[0], hip_c[1] - 10]))
            left_leg = calculate_angle(hip_c, lk, la)
            right_leg = calculate_angle(hip_c, rk, ra)
            leg_angle = max(left_leg, right_leg)

            # ======= BODY RATIO =======
            xs = keypoints[:, 0]; ys = keypoints[:, 1]
            w = np.max(xs) - np.min(xs)
            h = max(np.max(ys) - np.min(ys), 1)
            ratio = w / h

            # ======= ORIENTATION =======
            dx = hip_c[0] - shoulder_c[0]
            dy = hip_c[1] - shoulder_c[1]
            orientation = np.degrees(np.arctan2(abs(dy), abs(dx)))

            # ======= KNEE BEND (phat hien ngoi) =======
            knee_bend = min(
                calculate_angle(hip_c, lk, np.array([lk[0], lk[1] + 10])),
                calculate_angle(hip_c, rk, np.array([rk[0], rk[1] + 10]))
            )

            # knee-to-hip height ratio (ngoi thi dau goi cao hon)
            hip_y = min(lh[1], rh[1])
            knee_y = max(lk[1], rk[1])
            ankle_y = max(la[1], ra[1])
            leg_height_ratio = (knee_y - hip_y) / max(ankle_y - hip_y, 1)

            # ======= CLASSIFY =======
            # Rule 1: nam ngang
            if orientation < 30 or ratio > 1.40:
                posture = "LYING"
            # Rule 2: ngoi (goi gay > 120 do hoac ty le chan cao)
            elif knee_bend > 120 and leg_height_ratio > 0.45:
                posture = "SITTING"
            elif leg_angle > 120 and leg_height_ratio > 0.40:
                posture = "SITTING"
            elif torso_angle < 100:
                posture = "SITTING"
            else:
                posture = "STANDING"

            # ======= SMOOTH =======
            self._history.append(posture)
            posture = self._smoothed()

            return posture

        except Exception:
            return "UNKNOWN"

    def _smoothed(self):
        if not self._history:
            return "UNKNOWN"
        counts = {}
        for p in self._history:
            counts[p] = counts.get(p, 0) + 1
        return max(counts, key=counts.get)
