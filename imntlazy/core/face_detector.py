import os
import sys
import cv2
from PySide6.QtCore import QTimer, QObject, Signal
from ..models import AppSettings

NORMAL_INTERVAL_MS = 1000
NORMAL_MISS_THRESHOLD = 10
URGENT_INTERVAL_MS = 500
NORMAL_HIT_THRESHOLD = 2
MIN_FACE_AREA_RATIO = 0.025
MIN_FACE_SIZE = 96


def _get_cascade_path() -> str:
    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root:
        bundled = os.path.join(
            bundle_root, "imntlazy", "resources", "haarcascade_frontalface_default.xml"
        )
        if os.path.exists(bundled):
            return bundled
    resource_path = os.path.join(os.path.dirname(__file__), "..", "resources",
                                 "haarcascade_frontalface_default.xml")
    cascade_path = os.path.abspath(resource_path)
    if os.path.exists(cascade_path):
        return cascade_path
    alt = os.path.join(os.getcwd(), "resources", "haarcascade_frontalface_default.xml")
    return alt


def _get_eye_cascade_path() -> str:
    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root:
        bundled = os.path.join(
            bundle_root, "imntlazy", "resources", "haarcascade_eye_tree_eyeglasses.xml"
        )
        if os.path.exists(bundled):
            return bundled

    eye_path = os.path.join(cv2.data.haarcascades, "haarcascade_eye_tree_eyeglasses.xml")
    if os.path.exists(eye_path):
        return eye_path

    fallback = os.path.join(cv2.data.haarcascades, "haarcascade_eye.xml")
    if os.path.exists(fallback):
        return fallback

    return ""


class FaceDetector(QObject):
    face_detected = Signal()
    face_lost = Signal()

    def __init__(self, settings: AppSettings, parent=None):
        super().__init__(parent)
        self._settings = settings
        self._capture = None
        self._cascade = None
        self._eye_cascade = None
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._check)
        self._consecutive_misses = 0
        self._consecutive_hits = 0
        self._active = False
        self._urgent = False

    def initialize(self) -> bool:
        try:
            cascade_path = _get_cascade_path()
            if not os.path.exists(cascade_path):
                return False
            self._cascade = cv2.CascadeClassifier(cascade_path)
            if self._cascade.empty():
                self._cascade = None
                return False
            eye_cascade_path = _get_eye_cascade_path()
            if eye_cascade_path:
                eye_cascade = cv2.CascadeClassifier(eye_cascade_path)
                if not eye_cascade.empty():
                    self._eye_cascade = eye_cascade
            self._capture = cv2.VideoCapture(0)
            if not self._capture.isOpened():
                self._capture.release()
                self._capture = None
                return False
            return True
        except Exception:
            return False

    def start_monitoring(self):
        if not self._settings.face_detection_enabled:
            return
        if self._active:
            return
        self._active = True
        self._consecutive_misses = 0
        self._consecutive_hits = 0
        self._urgent = False
        if self._capture is None or self._cascade is None:
            self.initialize()
        self._schedule_next()

    def stop_monitoring(self):
        self._active = False
        self._urgent = False
        self._timer.stop()

    def set_urgent(self, enabled: bool):
        if self._urgent == enabled:
            return
        self._urgent = enabled
        self._consecutive_misses = 0
        self._consecutive_hits = 0
        if self._active:
            self._schedule_next()

    def _schedule_next(self):
        if not self._active:
            return
        self._timer.start(URGENT_INTERVAL_MS if self._urgent else NORMAL_INTERVAL_MS)

    def _check(self):
        if not self._active:
            return
        present = self._capture_and_detect()

        if self._urgent:
            if present:
                self._consecutive_hits = 0
                self._consecutive_misses = 0
                self.face_detected.emit()
        else:
            if present:
                self._consecutive_hits += 1
                if self._consecutive_hits >= NORMAL_HIT_THRESHOLD:
                    self._consecutive_misses = 0
            else:
                self._consecutive_hits = 0
                self._consecutive_misses += 1
                if self._consecutive_misses == NORMAL_MISS_THRESHOLD:
                    self.face_lost.emit()

        self._schedule_next()

    def _capture_and_detect(self) -> bool:
        if self._capture is None or self._cascade is None:
            self.initialize()
        if self._capture is None or self._cascade is None:
            return False
        try:
            ret, frame = self._capture.read()
            if not ret or frame is None or frame.size == 0:
                return False
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)
            frame_h, frame_w = gray.shape[:2]
            min_face_area = frame_w * frame_h * MIN_FACE_AREA_RATIO
            faces = self._cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=6,
                minSize=(MIN_FACE_SIZE, MIN_FACE_SIZE),
            )
            for (x, y, w, h) in faces:
                if w * h < min_face_area:
                    continue
                if self._has_eyes(gray, x, y, w, h):
                    return True
            return False
        except Exception:
            return False

    def _has_eyes(self, gray, x: int, y: int, w: int, h: int) -> bool:
        if self._eye_cascade is None:
            return True

        roi = gray[y:y + h, x:x + w]
        if roi.size == 0:
            return False

        eyes = self._eye_cascade.detectMultiScale(
            roi,
            scaleFactor=1.1,
            minNeighbors=4,
            minSize=(18, 18),
        )
        return len(eyes) > 0

    def release(self):
        self.stop_monitoring()
        if self._capture:
            self._capture.release()
            self._capture = None
