import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
psapi = ctypes.windll.psapi

EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

SW_MINIMIZE = 6
SW_RESTORE = 9

user32.EnumWindows.argtypes = [EnumWindowsProc, wintypes.LPARAM]
user32.EnumWindows.restype = wintypes.BOOL
user32.IsWindowVisible.argtypes = [wintypes.HWND]
user32.IsWindowVisible.restype = wintypes.BOOL
user32.IsIconic.argtypes = [wintypes.HWND]
user32.IsIconic.restype = wintypes.BOOL
user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetWindowTextW.restype = ctypes.c_int
user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
user32.GetWindowThreadProcessId.restype = wintypes.DWORD
user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
user32.ShowWindow.restype = wintypes.BOOL
user32.SetForegroundWindow.argtypes = [wintypes.HWND]
user32.SetForegroundWindow.restype = wintypes.BOOL
user32.GetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int]
user32.GetWindowLongW.restype = ctypes.c_long

GWL_EXSTYLE = -20
WS_EX_TOOLWINDOW = 0x00000080


def get_window_title(hwnd: int) -> str:
    buf = ctypes.create_unicode_buffer(256)
    user32.GetWindowTextW(hwnd, buf, 256)
    return buf.value


def get_process_name(hwnd: int) -> str:
    try:
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value == 0:
            return ""
        hproc = kernel32.OpenProcess(0x0400 | 0x0010, False, pid.value)
        if hproc == 0:
            return ""
        name_buf = ctypes.create_unicode_buffer(260)
        size = wintypes.DWORD(260)
        if psapi.GetModuleBaseNameW(hproc, None, name_buf, size):
            return name_buf.value
        kernel32.CloseHandle(hproc)
    except Exception:
        pass
    return ""


def enumerate_visible_windows() -> list[tuple[int, str, str]]:
    windows: list[tuple[int, str, str]] = []
    seen = set()

    def callback(hwnd: int, _: int) -> bool:
        if hwnd in seen:
            return True
        if not user32.IsWindowVisible(hwnd):
            return True
        ex_style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        if ex_style & WS_EX_TOOLWINDOW:
            return True
        title = get_window_title(hwnd)
        if not title.strip():
            return True
        pname = get_process_name(hwnd)
        if not pname:
            return True
        seen.add(hwnd)
        windows.append((hwnd, title, pname))
        return True

    user32.EnumWindows(EnumWindowsProc(callback), 0)
    return windows


def minimize_window(hwnd: int) -> None:
    user32.ShowWindow(hwnd, SW_MINIMIZE)


def restore_window(hwnd: int) -> None:
    user32.ShowWindow(hwnd, SW_RESTORE)
    user32.SetForegroundWindow(hwnd)
