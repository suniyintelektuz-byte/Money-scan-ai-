import cv2
import numpy as np
import easyocr
import re
from PIL import Image
import io
from typing import Optional

reader = easyocr.Reader(['en'], gpu=False)

DENOMINATIONS = [1, 2, 5, 10, 20, 50, 100]

class ScannerService:
    def analyze(self, image_bytes: bytes) -> dict:
        image = self._load_image(image_bytes)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ocr_results = self._run_ocr(image_bytes)
        texts = [item[1] for item in ocr_results]
        denomination = self._detect_denomination(texts)
        serial_number = self._detect_serial_number(texts)
        year = self._detect_year(texts)
        is_genuine, confidence, notes = self._check_genuineness(image, gray, texts)
        return {
            "is_genuine": is_genuine,
            "confidence": round(confidence, 3),
            "denomination": denomination,
            "serial_number": serial_number,
            "year": year,
            "notes": notes,
        }

    def _load_image(self, image_bytes: bytes) -> np.ndarray:
        pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    def _run_ocr(self, image_bytes: bytes):
        return reader.readtext(image_bytes)

    def _detect_denomination(self, texts: list) -> Optional[int]:
        for text in texts:
            clean = text.replace(",", "").replace("$", "").strip()
            try:
                val = int(float(clean))
                if val in DENOMINATIONS:
                    return val
            except ValueError:
                pass
        word_map = {"ONE": 1, "TWO": 2, "FIVE": 5, "TEN": 10,
                    "TWENTY": 20, "FIFTY": 50, "HUNDRED": 100}
        for text in texts:
            if text.upper().strip() in word_map:
                return word_map[text.upper().strip()]
        return None

    def _detect_serial_number(self, texts: list) -> Optional[str]:
        pattern = re.compile(r'^[A-Z]{1,2}\d{8}[A-Z]$')
        for text in texts:
            clean = text.replace(" ", "").upper()
            if pattern.match(clean):
                return clean
        for text in texts:
            found = re.findall(r'[A-Z]{1,2}\d{7,8}[A-Z]', text.upper())
            if found:
                return found[0]
        return None

    def _detect_year(self, texts: list) -> Optional[str]:
        for text in texts:
            years = re.findall(r'\b(18[6-9]\d|19\d{2}|20[0-3]\d)\b', text)
            if years:
                return years[0]
        return None

    def _check_genuineness(self, image, gray, texts):
        score = 0.0
        notes_list = []
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        green_mask = cv2.inRange(hsv, (36, 20, 20), (86, 255, 255))
        green_ratio = np.sum(green_mask > 0) / (image.shape[0] * image.shape[1])
        if green_ratio > 0.05:
            score += 0.35
        else:
            notes_list.append("Yashil rang kam")
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        if laplacian_var > 100:
            score += 0.30
        else:
            notes_list.append("Rasm sifati past")
        if len(texts) >= 5:
            score += 0.20
        else:
            notes_list.append("Matnlar aniq o'qilmadi")
        all_text = " ".join(texts).upper()
        if "FEDERAL" in all_text or "RESERVE" in all_text or "UNITED STATES" in all_text:
            score += 0.15
        else:
            notes_list.append("Rasmiy matnlar topilmadi")
        is_genuine = score >= 0.6
        note = "; ".join(notes_list) if notes_list else "Tekshiruv muvaffaqiyatli"
        return is_genuine, min(score, 1.0), note

scanner_service = ScannerService()
