import time
from ai.fall_score_engine import FallScoreEngine


class FusionSystem:

    def __init__(self, telegram=None):
        self.engine = FallScoreEngine()
        self.telegram = telegram

        self.alert_sent = False
        self.last_fall_time = 0

    def process(self, sensor_data, posture):

        score = self.engine.update(sensor_data, posture)
        is_fall = self.engine.is_fall(score)

        current_time = time.time()

        # chống spam alert
        if is_fall and current_time - self.last_fall_time > 5:
            self.last_fall_time = current_time

            if self.telegram:
                try:
                    self.telegram.send_message("🚨 FALL DETECTED")
                except Exception as e:
                    print("[Telegram Error]", e)

        # reset trạng thái
        if not is_fall:
            self.alert_sent = False

        return {
            "score": score,
            "fall": is_fall,
            "posture": posture,
            "mag": sensor_data.get("mag", 0),
            "timestamp": current_time
        }