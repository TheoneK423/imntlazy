import json
import os
from dataclasses import dataclass, field
from enum import Enum, auto


class FocusState(Enum):
    IDLE = auto()
    WORKING = auto()
    BREAK = auto()
    PAUSED = auto()
    ENDED = auto()


@dataclass
class WhitelistEntry:
    window_title: str = ""
    process_name: str = ""
    match_by_title: bool = True


@dataclass
class AppSettings:
    whitelisted_windows: list[WhitelistEntry] = field(default_factory=list)
    blocked_domains: list[str] = field(default_factory=lambda: [
        "zhihu.com", "bilibili.com", "youtube.com"
    ])
    work_duration_minutes: int = 45
    break_duration_minutes: int = 15
    total_focus_duration_minutes: int = 180
    exit_confirmation_phrase: str = (
        "我宣布放弃工作并承担可能导致的不好后果并承认我是一个拖延症懒鬼"
    )
    face_detection_enabled: bool = True
    face_check_interval_min: int = 1
    face_check_interval_max: int = 2
    face_miss_threshold: int = 10
    beep_on_alert: bool = True
    beep_interval_seconds: int = 10

    @staticmethod
    def settings_path() -> str:
        appdata = os.environ.get("APPDATA", "")
        path = os.path.join(appdata, "imntlazy", "settings.json")
        return path

    @classmethod
    def load(cls) -> "AppSettings":
        path = cls.settings_path()
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                settings = cls()
                # Restore whitelist entries
                if "whitelisted_windows" in data:
                    settings.whitelisted_windows = [
                        WhitelistEntry(**w) for w in data["whitelisted_windows"]
                    ]
                for key, value in data.items():
                    if key != "whitelisted_windows" and hasattr(settings, key):
                        setattr(settings, key, value)
                return settings
        except Exception:
            pass
        return cls()

    def save(self) -> None:
        path = self.settings_path()
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            d = self.__dict__.copy()
            d["whitelisted_windows"] = [w.__dict__ for w in self.whitelisted_windows]
            with open(path, "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
