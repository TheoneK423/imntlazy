# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Run

```bash
pip install PySide6 opencv-python pyinstaller

# Development (needs admin terminal)
python run.py

# Build single exe
pyinstaller imntlazy.spec --noconfirm --distpath dist
# Output: dist/imntlazy.exe (~122MB)
```

The app requests admin rights via `uac_admin=True` in the PyInstaller spec. On dev runs, `main.py` self-elevates via `ShellExecuteW(runas)`.

Settings: `%APPDATA%\imntlazy\settings.json`

## Architecture

**Stack:** Python 3.12 + PySide6 (Qt) + OpenCV + PyInstaller. All features run locally.

**Layer model:**

- `imntlazy/ui/` — Qt widgets. `Dashboard` is the main control panel shown on startup (closing it hides to tray, doesn't quit). `Overlay` is the fullscreen face-detection alert.
- `imntlazy/core/` — Pure logic: `FocusSession` orchestrates the five features, `FocusStateMachine` enforces the state cycle, `CountdownTimer` wraps QTimer, `WindowRestrictor` and `WebsiteBlocker` are self-contained.
- `imntlazy/win32/` — ctypes-based Windows API calls (`window_enum.py`, `hosts_file.py`, `input_blocker.py`). No PySide6 dependency here.
- `imntlazy/models/` — `AppSettings` (dataclass, JSON), `FocusState` enum, `WhitelistEntry` dataclass.
- `imntlazy/app.py` — `ImntlazyApp` class: owns the QSystemTrayIcon, Dashboard, all Core components, FocusSession. Wires signals/slots between them.

**State machine:** `FocusStateMachine` enforces `Idle → Working ↔ Break → Ended` (+ `Paused` from `Working`). Invalid transitions raise `ValueError`; `FocusSession._transition()` catches and ignores.

**Threading:** Qt's signal/slot mechanism handles cross-thread dispatch. `CountdownTimer` uses `QTimer` (runs on main event loop). `FaceDetector` uses `QTimer` for scheduling; OpenCV capture runs synchronously on the timer tick (fast enough that it doesn't block the UI). `WindowRestrictor` uses `QTimer` for polling.

**Hosts file:** `hosts_file.py` wraps blocked entries in `# imntlazy Block Begin` / `# imntlazy Block End` markers. Stale markers from a crash are auto-cleaned on next startup.

## Layout pattern

Qt layout managers (`QVBoxLayout`, `QHBoxLayout`, `QFormLayout`) handle all positioning. Never hand-calculate pixel coordinates. Use `setMinimumSize()` instead of `setFixedSize()` to allow DPI scaling. Use QSS stylesheets for colors and styling on `Dashboard` — other dialogs use native platform look.

## Five features

| Feature | Key module | Mechanism |
|---------|-----------|-----------|
| Window restriction | `core/window_restrictor.py` + `win32/window_enum.py` | `QTimer` polls `EnumWindows` every 500ms, minimizes non-whitelisted via `ShowWindow(SW_MINIMIZE)` |
| Website blocking | `core/website_blocker.py` + `win32/hosts_file.py` | Appends `127.0.0.1` entries with marker comments, then `ipconfig /flushdns` |
| Timed focus (45+15 min) | `core/focus_session.py` + `core/state_machine.py` | Cyclic QTimer-driven state transitions; restrictions lift during Break |
| Exit confirmation | `ui/exit_confirm.py` | String match against `AppSettings.exit_confirmation_phrase` |
| Face detection + alert | `core/face_detector.py` + `ui/overlay.py` + `win32/input_blocker.py` | OpenCV Haar Cascade every 1-2s; 10 consecutive misses → fullscreen marching-ants overlay (0.33 Hz amber→cyan→purple), blocks all input via `SetWindowsHookEx` |
