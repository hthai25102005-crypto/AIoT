import os
import sys
import warnings

os.environ["TRANSFORMERS_VERBOSE"] = "FALSE"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
warnings.filterwarnings("ignore")

_devnull = open(os.devnull, "w")
_old_stderr = sys.stderr
sys.stderr = _devnull

from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch

sys.stderr = _old_stderr


class VLMAnalyzer:
    def __init__(self):
        _stderr = sys.stderr
        sys.stderr = open(os.devnull, "w")
        try:
            self.processor = BlipProcessor.from_pretrained(
                "Salesforce/blip-image-captioning-base"
            )
            self.model = BlipForConditionalGeneration.from_pretrained(
                "Salesforce/blip-image-captioning-base"
            )
        finally:
            sys.stderr = _stderr
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        print(f"[VLM] Loaded on {self.device}")

    def generate_caption(self, image_path):
        image = Image.open(image_path).convert("RGB")
        raw = self.processor(image, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in raw.items()}
        out = self.model.generate(
            **inputs, max_new_tokens=80, num_beams=3
        )
        caption = self.processor.decode(out[0], skip_special_tokens=True)
        return caption

    def build_report(self, caption):
        c = caption.lower()

        # Phan tich noi dung caption
        has_person = any(w in c for w in ["person", "man", "woman", "people", "child", "boy", "girl"])
        on_floor = any(w in c for w in ["floor", "ground", "lying", "lying down", "laying"])
        sitting = "sitting" in c
        standing = "standing" in c
        on_bed = any(w in c for w in ["bed", "couch", "sofa", "chair", "table"])
        injured = any(w in c for w in ["injury", "hurt", "blood", "pain", "unconscious"])
        room = any(w in c for w in ["room", "indoor", "kitchen", "bathroom", "bedroom", "living"])
        outdoor = any(w in c for w in ["outdoor", "street", "sidewalk", "garden", "park"])

        # Xac dinh tinh huong
        if has_person and on_floor and not on_bed:
            situation = "Phat hien mot nguoi dang nam tren san nha"
            emergency = "CAO"
            action = "Can kiem tra va ho tro ngay lap tuc"
            if injured:
                situation += " va co dau hieu bi thuong"
                emergency = "KHAI CAP"
                action = "Goi cap cuu ngay"
        elif has_person and sitting:
            situation = "Phat hien mot nguoi dang ngoi"
            emergency = "THAP"
            action = "Theo doi tinh hinh"
        elif has_person and standing:
            situation = "Phat hien mot nguoi dang dung"
            emergency = "THAP"
            action = "Khong co dau hieu bat thuong"
        elif has_person and on_bed:
            situation = "Phat hien mot nguoi dang nam tren giuong/ghe"
            emergency = "THAP"
            action = "Khong co nguy hiem"
        elif not has_person:
            situation = "Khong phat hien nguoi trong anh"
            emergency = "THAP"
            action = "Khong can xu ly"
        else:
            situation = "Dang phan tich hinh anh"
            emergency = "TRUNG BINH"
            action = "Can kiem tra them thong tin"

        if outdoor:
            situation += " (ben ngoai troi)"
        if room:
            situation += " (trong nha)"

        report = (
            f"[VLM - PHAN TICH HINH ANH]\n"
            f"Mo ta: {caption}\n"
            f"Nhan xet: {situation}\n"
            f"Muc do khan cap: {emergency}\n"
            f"Khuyen nghi: {action}\n"
        )
        return report

    def analyze(self, image_path):
        caption = self.generate_caption(image_path)
        report = self.build_report(caption)
        return report
