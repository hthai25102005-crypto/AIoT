import os, sys, warnings, traceback, time as _time
import numpy as np
import cv2

os.environ["ULTRALYTICS_VERBOSE"] = "FALSE"
os.environ["YOLO_VERBOSE"] = "FALSE"
warnings.filterwarnings("ignore")

_devnull = open(os.devnull, "w")
_old_stderr = sys.stderr
sys.stderr = _devnull
from ultralytics import YOLO
sys.stderr = _old_stderr

_DEVICE = "cpu"
try:
    import torch
    if torch.cuda.is_available():
        _DEVICE = "cuda:0"
        print(f"[Pose] GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("[Pose] CPU mode")
except ImportError:
    print("[Pose] No torch, using CPU")

# MediaPipe se duoc import khi can (tranh treo startup)
_HAS_MP = False

_COCO_NAMES = [
    "nose", "l_eye", "r_eye", "l_ear", "r_ear",
    "l_shoulder", "r_shoulder", "l_elbow", "r_elbow",
    "l_wrist", "r_wrist", "l_hip", "r_hip",
    "l_knee", "r_knee", "l_ankle", "r_ankle"
]

# MediaPipe 33 -> COCO 17
_MP_TO_COCO = {
    0: 0, 11: 5, 12: 6, 23: 11, 24: 12,
    25: 13, 26: 14, 27: 15, 28: 16,
}

_mp_pose_instance = None
_mp_mod = None


def _get_mp_pose():
    global _mp_pose_instance, _HAS_MP, _mp_mod
    if _mp_pose_instance is None:
        if not _HAS_MP:
            try:
                import mediapipe as mp
                _mp_mod = mp
                _HAS_MP = True
            except ImportError:
                return None
        try:
            _mp_pose_instance = _mp_mod.solutions.pose.Pose(
                static_image_mode=False, model_complexity=0,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
        except Exception as e:
            with open("error_debug.log", "a", encoding="utf-8") as f:
                f.write(f"[{_time.strftime('%H:%M:%S')}] MP init err: {e}\n")
                traceback.print_exc(file=f)
    return _mp_pose_instance


def _mp_keypoints(frame):
    pose = _get_mp_pose()
    if pose is None:
        return None
    try:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = pose.process(rgb)
        if res.pose_landmarks is None:
            return None
        h, w = frame.shape[:2]
        kp = np.zeros((17, 2), dtype=np.float32)
        for mp_i, coco_i in _MP_TO_COCO.items():
            lm = res.pose_landmarks.landmark[mp_i]
            kp[coco_i] = [lm.x * w, lm.y * h]
        return kp
    except Exception:
        return None


class _FakeResult:
    def __init__(self, kp_array):
        self.keypoints = _FakeKeypoints(kp_array)

    def plot(self):
        return None


class _FakeKeypoints:
    def __init__(self, kp_array):
        self.xy = [kp_array]

    def __len__(self):
        return 1


class PoseDetector:
    def __init__(self):
        self.model = None
        self.conf = 0.5
        self.iou = 0.5

        for p in ["models/yolo11n-pose.pt", "yolo11n-pose.pt"]:
            if os.path.exists(p):
                model_path = p
                break
        else:
            model_path = "yolo11n-pose.pt"

        try:
            print(f"[Pose] Loading YOLO: {model_path}")
            self.model = YOLO(model_path, verbose=False)
            task = getattr(self.model, "task", "unknown")
            if task != "pose":
                print(f"[Pose] YOLO task={task}, switching to MP")
                self.model = None
        except Exception as e:
            print(f"[Pose] YOLO load failed: {e}")
            self.model = None

        if self.model is not None:
            print(f"[Pose] YOLO ready | device={_DEVICE}")
        elif _HAS_MP:
            print("[Pose] Using MediaPipe fallback")
        else:
            print("[Pose] WARNING: khong co pose detector!")

    def detect(self, frame):
        if frame is None or not isinstance(frame, np.ndarray):
            return []
        if frame.size == 0 or frame.ndim != 3:
            return []

        # YOLO path
        if self.model is not None:
            try:
                results = self.model.predict(
                    source=frame, conf=self.conf, iou=self.iou,
                    verbose=False, device=_DEVICE, augment=False,
                )
                if results is not None and len(results) > 0:
                    return results
            except Exception as e:
                with open("error_debug.log", "a", encoding="utf-8") as f:
                    f.write(f"[{_time.strftime('%H:%M:%S')}] YOLO fail, fallback MP: {e}\n")
                self.model = None

        # MediaPipe fallback
        kp = _mp_keypoints(frame)
        if kp is not None:
            return [_FakeResult(kp)]
        return []

    def annotate(self, frame, results):
        try:
            if hasattr(results, 'plot') and results.plot() is not None:
                return results.plot()
        except Exception:
            pass
        return frame
