import sys, os, ctypes, queue, logging, time, threading, traceback as tb_mod
import cv2, numpy as np

# === CHAN STDERR ===
_kernel32 = ctypes.windll.kernel32
_nul_handle = _kernel32.CreateFileW("nul", 0x40000000, 3, None, 3, 0x80, None)
_kernel32.SetStdHandle(-12, _nul_handle)
try:
    _nul_fd = os.open(os.devnull, os.O_WRONLY); os.dup2(_nul_fd, 2); os.close(_nul_fd)
except: pass
sys.stderr = open(os.devnull, "w")
sys.__stderr__ = sys.stderr
for _n in ['ultralytics','yolo','PIL','torch','transformers','huggingface','matplotlib']:
    _lg = logging.getLogger(_n); _lg.handlers=[]; _lg.propagate=False; _lg.setLevel(100)
os.environ['ULTRALYTICS_VERBOSE']='FALSE'; os.environ['YOLO_VERBOSE']='FALSE'
os.environ['TF_CPP_MIN_LOG_LEVEL']='3'

def _global_excepthook(exc_type, exc_value, exc_tb):
    with open("error_debug.log","a",encoding="utf-8") as f:
        f.write(f"[{time.strftime('%H:%M:%S')}] UNCAUGHT {exc_type.__name__}: {exc_value}\n")
        tb_mod.print_tb(exc_tb,file=f); f.write("\n")
sys.excepthook = _global_excepthook

# === IMPORTS ===
from mqtt.mqtt_receiver import sensor_data
try:
    from ai.vlm_analyzer import VLMAnalyzer; _HAS_VLM = True
except: _HAS_VLM = False
from gui.dashboard import Dashboard
from ai.pose_detector import PoseDetector
from ai.posture_classifier import PostureClassifier
from ai.fall_score_engine import FallScoreEngine
from telegram_utils.telegram_bot import send_alert
print("[OK] Import done")

# === INIT ===
pose_detector = PoseDetector()
classifier = PostureClassifier()
fall_engine = FallScoreEngine()
print("[OK] Models loaded")

os.makedirs("images/captures", exist_ok=True)

posture = "UNKNOWN"
_last_alert_time = 0
ALERT_COOLDOWN = 15
frame_queue = queue.Queue(maxsize=1)
raw_frame_queue = queue.Queue(maxsize=2)
display_queue = queue.Queue(maxsize=2)
_cam_ok = False
vlm = None; vlm_ready = threading.Event()
VN = {"STANDING":"DUNG","SITTING":"NGOI","LYING":"NAM","UNKNOWN":"KHONG RO"}

# === CAMERA ===
cap = None
_cam_lock = threading.Lock()

def open_camera():
    global cap, _cam_ok
    for idx in [0, 1]:
        for api in [cv2.CAP_MSMF, cv2.CAP_DSHOW, 0]:
            try:
                c = cv2.VideoCapture(idx, api) if api else cv2.VideoCapture(idx)
                if c.isOpened():
                    c.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
                    c.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
                    c.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                    w = int(c.get(cv2.CAP_PROP_FRAME_WIDTH))
                    h = int(c.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    print(f"[CAM] Trying camera {idx} api={api}: opened, {w}x{h}")
                    with _cam_lock:
                        cap = c
                        _cam_ok = True
                    print(f"[OK] Camera {idx} api={api}: {w}x{h}")
                    return
            except: pass
    print("[WARN] No camera found! Using fallback mode.")
    _cam_ok = False

# Mo camera ngay luong chinh (thu default backend truoc)
print("[CAM] Opening camera...")
open_camera()
if not _cam_ok:
    print("[CAM] Direct open failed, trying thread...")
    def _init_camera():
        global cap, _cam_ok
        try: open_camera()
        except: _cam_ok = False
    threading.Thread(target=_init_camera, daemon=True).start()
    time.sleep(2)

print(f"[CAM] Status: _cam_ok={_cam_ok}")

# === CAMERA CAPTURE THREAD ===
_cam_restart = threading.Event()
_last_frame_time = time.time()

# === CAMERA READER ===
_reader_id = 0  # tang moi lan restart, reader tu dong thoat neu ID mismatch

def raw_camera_reader(rid):
    """Doc frame lien tuc. Tu dong thoat neu rid khong khop voi _reader_id."""
    global cap, _cam_ok, _last_frame_time
    fail_count = 0
    warmup = 0
    while True:
        if rid != _reader_id:
            return  # Da co reader moi
        if not _cam_ok:
            time.sleep(0.5)
            continue
        try:
            ret, frame = cap.read()
            if not ret or frame is None:
                fail_count += 1
                if fail_count > 5:
                    break
                time.sleep(0.05)
                continue
            fail_count = 0
            if warmup < 10:
                warmup += 1
                continue
            _last_frame_time = time.time()
            try: raw_frame_queue.put_nowait(frame)
            except queue.Full: pass
            try: frame_queue.put_nowait(frame)
            except queue.Full: pass
        except:
            break
    _cam_ok = False

def _start_reader():
    global _reader_id
    _reader_id += 1
    rid = _reader_id
    t = threading.Thread(target=raw_camera_reader, args=(rid,), daemon=True, name="raw-cam")
    t.start()
    return t

reader_thread = _start_reader()

def camera_watchdog():
    global cap, _cam_ok, _last_frame_time, reader_thread
    while True:
        time.sleep(2)
        if not _cam_ok:
            continue
        if time.time() - _last_frame_time > 6:
            print("[WARN] Camera frozen >6s, restarting...")
            _cam_ok = False
            time.sleep(0.5)
            open_camera()
            if _cam_ok:
                _last_frame_time = time.time()
                reader_thread = _start_reader()

threading.Thread(target=camera_watchdog, daemon=True, name="cam-watchdog").start()

def yolo_worker():
    global posture, _yolo_ok
    while True:
        try:
            frame = frame_queue.get(timeout=0.5)
            while True:
                try: frame = frame_queue.get_nowait()
                except queue.Empty: break
        except queue.Empty: continue
        _yolo_ok = True
        try: results = pose_detector.detect(frame)
        except: results = None
        if results and len(results) > 0:
            for r in results:
                try:
                    if r.keypoints is None or len(r.keypoints.xy) == 0: continue
                    kp = r.keypoints.xy[0]
                    if hasattr(kp,'cpu'): kp = kp.cpu().numpy()
                    p = classifier.classify(kp)
                    if p != "UNKNOWN": posture = p; break
                except: pass
        score = fall_engine.update(sensor_data, posture)
        fall = fall_engine.is_fall(score)
        mag = sensor_data.get("mag", 0)
        ax = sensor_data.get("ax", 0)
        ay = sensor_data.get("ay", 0)
        az = sensor_data.get("az", 9.8)
        gx = sensor_data.get("gx", 0)
        gy = sensor_data.get("gy", 0)
        gz = sensor_data.get("gz", 0)
        try:
            display_queue.put_nowait((frame, score, fall, mag, ax, ay, az, gx, gy, gz, posture))
        except queue.Full: pass

threading.Thread(target=yolo_worker, daemon=True).start()

# === VLM ===
def load_vlm():
    global vlm
    if not _HAS_VLM: return
    try:
        vlm = VLMAnalyzer(); vlm_ready.set(); print("[VLM] Ready")
    except Exception as e: print(f"[VLM] Load failed: {e}")
threading.Thread(target=load_vlm, daemon=True).start()
print("[OK] Threads started")

# === GUI UPDATE ===
UPDATE_MS = 50
def update():
    global _last_alert_time
    try:
        now = time.time()
        fps = 1 / (now - update._prev + 1e-6)
        update._prev = now

        # Lay frame tu camera truc tiep (khong qua YOLO)
        frame = None
        try: frame = raw_frame_queue.get_nowait()
        except queue.Empty: pass
        if frame is not None:
            while True:
                try: frame = raw_frame_queue.get_nowait()
                except queue.Empty: break

        # Lay YOLO results rieng
        score, fall, mag, ax, ay, az, gx, gy, gz, pose_now = 0, False, 0, 0, 0, 9.8, 0, 0, 0, "UNKNOWN"
        try:
            _, _s, _f, _mag, _ax, _ay, _az, _gx, _gy, _gz, _p = display_queue.get_nowait()
            # Doc frame moi nhat
            while True:
                try: _, _s, _f, _mag, _ax, _ay, _az, _gx, _gy, _gz, _p = display_queue.get_nowait()
                except queue.Empty: break
            score, fall, mag, ax, ay, az, gx, gy, gz, pose_now = _s, _f, _mag, _ax, _ay, _az, _gx, _gy, _gz, _p
        except queue.Empty: pass

        # Gui alert Telegram
        if fall and (now - _last_alert_time) > ALERT_COOLDOWN and frame is not None:
            _last_alert_time = now
            try:
                filename = f"images/captures/fall_{int(now)}.jpg"
                cv2.imwrite(filename, frame)
                msg = f"TE NGA\nTu the: {VN.get(pose_now,pose_now)}\nDiem: {score:.2f}\nMAG: {mag:.2f}"
                try: send_alert(msg, filename)
                except: pass
                if vlm_ready.is_set():
                    threading.Thread(target=lambda: _vlm(filename), daemon=True).start()
                ts = time.strftime("%H:%M:%S")
                app.log.add_event(f"[{ts}] {VN.get(pose_now,pose_now)} score={score:.0f}")
            except Exception as e:
                with open("error_debug.log","a",encoding="utf-8") as f:
                    f.write(f"[{time.strftime('%H:%M:%S')}] alert: {e}\n")

        # Cap nhat GUI
        try:
            if frame is not None:
                app.update_camera(frame)
            app.update_status(fall)
            app.update_info(pose_now, score, mag, fps, ax, ay, az, gx, gy, gz)
        except Exception as e:
            with open("error_debug.log","a",encoding="utf-8") as f:
                f.write(f"[{time.strftime('%H:%M:%S')}] gui_update: {e}\n")

        root.after(UPDATE_MS, update)
    except Exception as e:
        with open("error_debug.log","a",encoding="utf-8") as f:
            f.write(f"[{time.strftime('%H:%M:%S')}] update: {e}\n")
            tb_mod.print_exc(file=f)
        root.after(UPDATE_MS, update)

def _vlm(filename):
    try:
        r = vlm.analyze(filename); send_alert(f"[VLM] {r}")
    except: pass

update._prev = time.time()
print("[OK] Starting GUI...")
import tkinter as tk
root = tk.Tk()
app = Dashboard(root)
print("[OK] App running")
root.after(UPDATE_MS, update)
root.mainloop()
if cap: cap.release()
cv2.destroyAllWindows()
