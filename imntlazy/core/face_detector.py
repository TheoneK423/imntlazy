import os
import cv2
from PySide6.QtCore import QTimer, QObject, Signal
from ..models import AppSettings

NORMAL_INTERVAL_MS = 1000
NORMAL_MISS_THRESHOLD = 10
URGENT_INTERVAL_MS = 500


def _get_cascade_path() -> str:
    resource_path = os.path.join(os.path.dirname(__file__), "..", "resources",
                                 "haarcascade_frontalface_default.xml")
    cascade_path = os.path.abspath(resource_path)
    if os.path.exists(cascade_path):
        return cascade_path
    alt = os.path.join(os.getcwd(), "resources", "haarcascade_frontalface_default.xml")
    return alt


class FaceDetector(QObject):
    face_detected = Signal()
    face_lost = Signal()

    def __init__(self, settings: AppSettings, parent=None):
        super().__init__(parent)
        self._settings = settings
        self._capture = None
        self._cascade = None
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._check)
        self._consecutive_misses = 0
        self._active = False
        self._urgent = False

    def initialize(self) -> bool:
        try:
            cascade_path = _get_cascade_path()
            if not os.path.exists(cascade_path):
                return False
            self._cascade = cv2.CascadeClassifier(cascade_path)
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
        if self._capture is None and not self.initialize():
            return
        if self._active:
            return
        self._active = True
        self._consecutive_misses = 0
        self._urgent = False
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
                self._consecutive_misses = 0
                self.face_detected.emit()
        else:
            if present:
                self._consecutive_misses = 0
            else:
                self._consecutive_misses += 1
                if self._consecutive_misses == NORMAL_MISS_THRESHOLD:
                    self.face_lost.emit()

        self._schedule_next()

    def _capture_and_detect(self) -> bool:
        if self._capture is None or self._cascade is None:
            return True
        try:
            ret, frame = self._capture.read()
            if not ret or frame is None or frame.size == 0:
                return True
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)
            faces = self._cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=4,
                minSize=(60, 60),
            )
            return len(faces) > 0
        except Exception:
            return True

    def release(self):
        self.stop_monitoring()
        if self._capture:
            self._capture.release()
            self._capture = None
