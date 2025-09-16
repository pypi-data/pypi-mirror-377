import platform
import os
import subprocess
import math
import time
from typing import Optional, Tuple
from .logging_utils import get_logger, log_exception


# ===== Conditional Imports via Windows and macOS =====
_WINDOWS_IMPORTS_AVAILABLE = False
logger = get_logger()
logger.info("window_actions module imported")
if platform.system() == 'Windows':
    try:
        import ctypes
        from ctypes import wintypes
        import win32con
        import win32gui
        import win32api
        import win32process
        _WINDOWS_IMPORTS_AVAILABLE = True
    except Exception as e:
        # This now Indicates a *Broken Installation*, Not Something to Fix at Runtime
        log_exception("Windows backend import failure")
        raise RuntimeError(
            "Windows Backend Requested But pywin32 is Not Installed. "
            "Reinstall the Package on Windows."
        ) from e

_MACOS_IMPORTS_AVAILABLE = False
if platform.system() == 'Darwin':
    try:
        from AppKit import NSScreen, NSWorkspace
        from Quartz.CoreGraphics import (
            CGEventCreateKeyboardEvent,
            CGEventPost,
            kCGHIDEventTap,
            kCGEventFlagMaskControl,
            kCGEventFlagMaskCommand,
        )
        from ApplicationServices import (
            AXUIElementCreateApplication,
            AXUIElementCopyAttributeValue,
            AXUIElementSetAttributeValue,
            AXValueCreate,
            AXValueGetValue,
            kAXValueCGPointType,
            kAXValueCGSizeType,
            AXUIElementPerformAction
        )
        _MACOS_IMPORTS_AVAILABLE = True
    except Exception as e:
        # This now Indicates a *Broken Installation*, Not Something to Fix at Runtime
        log_exception("macOS backend import failure")
        raise RuntimeError(
            "macOS Backend Requested But PyObjC Frameworks are Missing. "
            "Reinstall This Package on macOS so the Platform Deps Resolve."
        ) from e


# ===== Windows DWM (via Visible Frame Bounds) =====
if _WINDOWS_IMPORTS_AVAILABLE:
    DWMWA_EXTENDED_FRAME_BOUNDS = 9
    _dwmapi = ctypes.windll.dwmapi

    class RECT(ctypes.Structure):
        _fields_ = [('left', ctypes.c_long),
                    ('top', ctypes.c_long),
                    ('right', ctypes.c_long),
                    ('bottom', ctypes.c_long)]


# ===== macOS Accessibility Constants =====
if _MACOS_IMPORTS_AVAILABLE:
    # String constants (portable across PyObjC variants)
    AX_FOCUSED_WINDOW = "AXFocusedWindow"
    AX_WINDOWS       = "AXWindows"
    AX_ROLE          = "AXRole"
    AX_SUBROLE       = "AXSubrole"
    AX_POSITION      = "AXPosition"
    AX_SIZE          = "AXSize"
    AX_RESIZABLE     = "AXResizable"
    AX_FULLSCREEN    = "AXFullScreen"
    AX_MINIMIZED     = "AXMinimized"
    AX_RAISE         = "AXRaise"
    AX_MINIMIZE_BTN  = "AXMinimizeButton"
    AX_PRESS         = "AXPress"


# ===== System Detection =====
def execute_os(mac_command, win_command):

    os_name = platform.system()

    if os_name == 'Darwin':
        logger.debug("execute_os -> macOS path")
        return mac_command
    elif os_name == 'Windows': 
        logger.debug("execute_os -> Windows path")
        return win_command
    else:
        logger.warning("Unsupported Operating System (Not MacOS or Windows)")
        return False
# ===== Common Exclusion Helpers =====
def _excluded_list():
    """返回需要忽略的AI软件列表"""
    raw = "AIdo,com.silicon-geek.aido,aido.exe,aido"
    return [s.strip().lower() for s in raw.split(",") if s.strip()]

def _is_excluded_name(name: Optional[str]) -> bool:
    """检查应用名称是否在忽略列表中"""
    if not name:
        return False
    name_lower = name.lower()
    excluded = _excluded_list()
    
    # 精确匹配
    if name_lower in excluded:
        return True
    
    # 部分匹配（用于处理版本号等变化）
    for excluded_name in excluded:
        if excluded_name in name_lower or name_lower in excluded_name:
            return True
    
    return False



# ===== macOS Helper Functions =====
def _focused_window_for_actions():
    logger.info("_focused_window_for_actions: locating frontmost app")
    ax_app = _frontmost_ax_app()
    if not ax_app:
        logger.warning("_focused_window_for_actions: no frontmost app")
        return None
    win = _focused_or_standard_window(ax_app)
    logger.info(f"_focused_window_for_actions: window found? {bool(win)}")
    return win

def _ax_copy(el, attr):
    res = AXUIElementCopyAttributeValue(el, attr, None)
    if isinstance(res, tuple) and len(res) == 2:  # (err, value)
        return None if res[0] else res[1]  # res[0] is error, res[1] is value
    return res

def _do_region(region: str) -> bool:
    logger.info(f"_do_region: region={region}")
    ax_app = _frontmost_ax_app()
    if not ax_app:
        logger.warning("_do_region: no frontmost app")
        return False
    win = _focused_or_standard_window(ax_app)
    if not _prep_window(win):
        logger.warning("_do_region: window not resizable or invalid")
        return False
    screen = _pick_screen_for(win)
    x, y, w, h = _target_frame_for_screen_region(screen, region)
    logger.info(f"_do_region: target frame x={x} y={y} w={w} h={h}")
    ok = _tile(win, x, y, w, h)
    logger.info(f"_do_region: tile result={ok}")
    return ok

def _send_keystroke_control_command_f():
    KEY_F = 0x03
    ev_down = CGEventCreateKeyboardEvent(None, KEY_F, True)
    ev_up   = CGEventCreateKeyboardEvent(None, KEY_F, False)
    for ev in (ev_down, ev_up):
        ev.setFlags_(kCGEventFlagMaskControl | kCGEventFlagMaskCommand)
        CGEventPost(kCGHIDEventTap, ev)

def _ax_point(x: float, y: float):
    return AXValueCreate(kAXValueCGPointType, (float(x), float(y)))

def _ax_size(w: float, h: float):
    return AXValueCreate(kAXValueCGSizeType, (float(w), float(h)))

def _ax_get_point(el, attr) -> Optional[Tuple[float, float]]:
    v = _ax_copy(el, attr)
    if v is None: return None
    out = AXValueGetValue(v, kAXValueCGPointType, None)
    if isinstance(out, tuple) and len(out) == 2:
        ok, pt = out
        return tuple(pt) if ok else None
    return tuple(out) if out is not None else None

def _ax_get_size(el, attr) -> Optional[Tuple[float, float]]:
    v = _ax_copy(el, attr)
    if v is None: return None
    out = AXValueGetValue(v, kAXValueCGSizeType, None)
    if isinstance(out, tuple) and len(out) == 2:
        ok, sz = out
        return tuple(sz) if ok else None
    return tuple(out) if out is not None else None

def _ax_bool(el, attr, default=False) -> bool:
    v = _ax_copy(el, attr)
    return bool(v) if isinstance(v, bool) else default

def _union_max_y() -> float:
    # 已弃用：这个函数导致坐标转换错误
    # Now called only when needed, not at module import
    return max((s.frame().origin.y + s.frame().size.height) for s in NSScreen.screens())

def _screen_for_point(px: float, py: float):
    # Now called only when needed, not at module import
    for s in NSScreen.screens():
        f = s.frame()
        if (px >= f.origin.x and px <= f.origin.x + f.size.width and
            py >= f.origin.y and py <= f.origin.y + f.size.height):
            return s
    return NSScreen.mainScreen()

def _frontmost_pid() -> Optional[int]:
    app = NSWorkspace.sharedWorkspace().frontmostApplication()
    return int(app.processIdentifier()) if app else None

def _frontmost_pid_applescript() -> Optional[int]:
    """
    Alternative focus detection using osascript.
    Most reliable method for macOS - gets the truly focused window.
    """
    try:
        import subprocess
        import json
        
        # AppleScript to get the focused window's app bundle ID
        script = '''
        tell application "System Events"
            set frontApp to name of first application process whose frontmost is true
            return frontApp
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True, timeout=2)
        
        if result.returncode == 0 and result.stdout.strip():
            app_name = result.stdout.strip()
            # Exclude by app name first
            if app_name and app_name.lower() in _excluded_list():
                logger.info(f"_frontmost_pid_applescript: excluded app_name={app_name}")
                return None
            
            # Get the PID for this app name
            workspace = NSWorkspace.sharedWorkspace()
            running_apps = workspace.runningApplications()
            
            for app in running_apps:
                if app.localizedName() == app_name:
                    # Exclude by bundle identifier if provided
                    try:
                        bid = app.bundleIdentifier()
                    except Exception:
                        bid = None
                    if bid and bid.lower() in _excluded_list():
                        logger.info(f"_frontmost_pid_applescript: excluded bundle={bid}")
                        return None
                    pid = int(app.processIdentifier())
                    logger.info(f"_frontmost_pid_applescript: pid={pid} name={app_name} bundle={bid}")
                    return pid
                    
    except Exception:
        pass
    
    # Fallback to original method
    pid = _frontmost_pid()
    logger.info(f"_frontmost_pid_applescript: fallback pid={pid}")
    return pid

def _frontmost_ax_app():
    # 优先返回当前前台未被排除的应用；若被排除，则自动激活下一个未排除的可见应用
    ax = _frontmost_ax_app_raw()
    if ax and not _is_excluded_current_app():
        return ax
    # 当前应用在忽略列表（如 AIdo）时，自动寻找并激活下一个未忽略的可见应用
    if _activate_next_unexcluded_app():
        # 激活后给系统一点时间切换前台，再重试获取，避免竞态
        time.sleep(0.15)
        ax = _frontmost_ax_app_raw()
        if not ax:
            for _ in range(10):
                time.sleep(0.1)
                ax = _frontmost_ax_app_raw()
                if ax:
                    logger.info("_frontmost_ax_app: acquired after retry")
                    break
        if ax and not _is_excluded_current_app():
            return ax
    return None

def _frontmost_ax_app_raw():
    pid = _frontmost_pid_applescript()
    if not pid:
        return None
    try:
        return AXUIElementCreateApplication(pid)
    except Exception:
        log_exception("AXUIElementCreateApplication failed")
        return None

def _is_excluded_current_app() -> bool:
    try:
        app = NSWorkspace.sharedWorkspace().frontmostApplication()
        if not app:
            return False
        name = app.localizedName() if hasattr(app, 'localizedName') else None
        if _is_excluded_name(name):
            return True
        try:
            bid = app.bundleIdentifier()
        except Exception:
            bid = None
        return _is_excluded_name(bid)
    except Exception:
        return False

def _activate_app_by_name(app_name: str) -> bool:
    try:
        script = f'''
        tell application "System Events"
            if exists (process "{app_name}") then
                set frontmost of process "{app_name}" to true
                return "OK"
            else
                return "NO"
            end if
        end tell
        '''
        res = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, timeout=2)
        return res.returncode == 0 and res.stdout.strip() == "OK"
    except Exception:
        return False

def _ordered_visible_app_names() -> list:
    try:
        script = '''
        tell application "System Events"
            set theProcs to every process whose visible is true
            set theNames to {}
            repeat with p in theProcs
                set end of theNames to name of p
            end repeat
            return theNames
        end tell
        '''
        res = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, timeout=2)
        if res.returncode != 0:
            return []
        out = res.stdout.strip()
        if not out:
            return []
        return [s.strip() for s in out.split(",") if s.strip()]
    except Exception:
        return []

def _activate_next_unexcluded_app() -> bool:
    names = _ordered_visible_app_names()
    if not names:
        return False
    for name in names:
        if not _is_excluded_name(name):
            if _activate_app_by_name(name):
                logger.info(f"_activate_next_unexcluded_app: activated {name}")
                return True
    return False

def _focused_or_standard_window(ax_app):
    win = _ax_copy(ax_app, AX_FOCUSED_WINDOW)
    if win:
        return win
    for w in (_ax_copy(ax_app, AX_WINDOWS) or []):
        if _ax_bool(w, AX_MINIMIZED, False):
            continue
        role = _ax_copy(w, AX_ROLE) or ""
        sub  = _ax_copy(w, AX_SUBROLE) or ""
        if role == "AXWindow" and sub in ("AXStandardWindow", "AXDocumentWindow", ""):
            return w
    ws = _ax_copy(ax_app, AX_WINDOWS) or []
    return ws[0] if ws else None

def _tile(win, x: float, y: float, w: float, h: float) -> bool:
    # raise (best effort)
    if AXUIElementPerformAction is not None:
        try:
            AXUIElementPerformAction(win, AX_RAISE)
        except Exception:
            pass
    # position → size, then reverse if needed
    try:
        AXUIElementSetAttributeValue(win, AX_POSITION, _ax_point(x, y))
        AXUIElementSetAttributeValue(win, AX_SIZE, _ax_size(w, h))
        return True
    except Exception:
        try:
            AXUIElementSetAttributeValue(win, AX_SIZE, _ax_size(w, h))
            AXUIElementSetAttributeValue(win, AX_POSITION, _ax_point(x, y))
            return True
        except Exception:
            logger.warning("_tile: failed to set AX attributes")
            return False

def _target_frame_for_screen_region(screen, region: str) -> Tuple[float, float, float, float]:
    """
    Return (x, y_topLeftAX, w, h) for a given region of the screen's visibleFrame.
    Regions: 'left', 'right', 'top', 'bottom',
             'left_third', 'middle_third', 'right_third',
             'left_two_third', 'right_two_third',
             'top_left_quarter', 'top_right_quarter',
             'bottom_left_quarter', 'bottom_right_quarter',
             'maximize'.
    """
    v = screen.visibleFrame()  # respects menu bar & Dock
    vX, vY, vW, vH = float(v.origin.x), float(v.origin.y), float(v.size.width), float(v.size.height)
    # macOS坐标系：visibleFrame已经返回正确的坐标，无需转换
    axTopLeftY = vY

    if region in ("left", "right"):
        # 使用精确的浮点计算，然后四舍五入
        halfW = round(vW / 2.0)
        if region == "left":
            return (vX, axTopLeftY, halfW, vH)
        else:
            return (vX + halfW, axTopLeftY, vW - halfW, vH)

    elif region in ("top", "bottom"):
        halfH = round(vH / 2.0)
        if region == "top":
            return (vX, axTopLeftY, vW, halfH)
        else:
            return (vX, axTopLeftY + halfH, vW, vH - halfH)

    elif region in ("left_third", "middle_third", "right_third"):
        thirdW = round(vW / 3.0)
        if region == "left_third":
            return (vX, axTopLeftY, thirdW, vH)
        elif region == "middle_third":
            return (vX + thirdW, axTopLeftY, thirdW, vH)
        else:  # right_third
            return (vX + 2*thirdW, axTopLeftY, vW - 2*thirdW, vH)
    
    elif region in ("left_two_third", "right_two_third"):
        thirdW = round(vW / 3.0)
        if region == "left_two_third":
            # start at left edge, take two-thirds
            return (vX, axTopLeftY, 2*thirdW, vH)
        else:  # right_two_third
            # start one-third in, take the rest
            return (vX + thirdW, axTopLeftY, vW - thirdW, vH)

    elif region in (
        "top_left_quarter", "top_right_quarter",
        "bottom_left_quarter", "bottom_right_quarter"
    ):
        halfW = round(vW / 2.0)
        halfH = round(vH / 2.0)

        if region == "top_left_quarter":
            return (vX, axTopLeftY, halfW, halfH)

        elif region == "top_right_quarter":
            return (vX + halfW, axTopLeftY, vW - halfW, halfH)

        elif region == "bottom_left_quarter":
            return (vX, axTopLeftY + halfH, halfW, vH - halfH)

        elif region == "bottom_right_quarter":
            return (vX + halfW, axTopLeftY + halfH, vW - halfW, vH - halfH)
            
    elif region == "maximize":
        # Fill entire visible working area (Dock + Menu bar excluded)
        return (vX, axTopLeftY, vW, vH)
    
    else:
        logger.error(f"Unknown region: {region}")
        raise ValueError(f"Unknown region: {region}")

def _prep_window(win) -> bool:
    if not win or not _ax_bool(win, AX_RESIZABLE, True):
        return False
    if _ax_bool(win, AX_FULLSCREEN, False):
        try:
            AXUIElementSetAttributeValue(win, AX_FULLSCREEN, False)
        except Exception:
            pass
    return True

def _pick_screen_for(win):
    pos = _ax_get_point(win, AX_POSITION) or (0.0, 0.0)
    size = _ax_get_size(win, AX_SIZE) or (0.0, 0.0)
    cx, cy = pos[0] + size[0]/2.0, pos[1] + size[1]/2.0
    scr = _screen_for_point(cx, cy)
    try:
        f = scr.frame()
        logger.info(f"_pick_screen_for: window center=({cx},{cy}) screen=({f.origin.x},{f.origin.y},{f.size.width},{f.size.height})")
    except Exception:
        pass
    return scr


# ===== Windows Helper Functions =====
def check_exit_fullscreen_win(hwnd):
    """Restore if Window is Maximized so it can be Resized/Moved."""
    placement = win32gui.GetWindowPlacement(hwnd)
    if placement[1] == win32con.SW_SHOWMAXIMIZED:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

def set_dpi_aware_win():
    """Ensure Coordinates Match Physical Pixels on High-DPI Displays."""
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

def get_effective_dimension_win(hwnd):
    """(L, T, R, B) for the Monitor Containing hwnd, Excluding Taskbar."""
    monitor = win32api.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
    mi = win32api.GetMonitorInfo(monitor)  # Keys: "Monitor" & "Work"
    return mi['Work']

def get_visible_frame_win(hwnd):
    """
    (L, T, R, B) of the Visible Window Frame (Excludes Drop Shadow).
    Falls back to GetWindowRect if DWM Call Fails.
    """
    rect = RECT()
    hr = _dwmapi.DwmGetWindowAttribute(
        wintypes.HWND(hwnd),
        ctypes.c_uint(DWMWA_EXTENDED_FRAME_BOUNDS),
        ctypes.byref(rect),
        ctypes.sizeof(rect),
    )
    if hr == 0:
        return rect.left, rect.top, rect.right, rect.bottom
    return win32gui.GetWindowRect(hwnd)

def apply_effective_bounds_win(hwnd, target_ltrb):
    """
    Move/Resize so the Visible Frame Aligns with the Target Rect.
    1) Set Outer Bounds Roughly, 2) Measure Insets, 3) Correct.
    """
    L, T, R, B = target_ltrb
    W = max(1, R - L)
    H = max(1, B - T)

    win32gui.SetWindowPos(
        hwnd, 0, L, T, W, H,
        win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE | win32con.SWP_SHOWWINDOW | win32con.SWP_FRAMECHANGED
    )

    visL, visT, visR, visB = get_visible_frame_win(hwnd)
    outL, outT, outR, outB = win32gui.GetWindowRect(hwnd)

    inset_left   = visL - outL
    inset_top    = visT - outT
    inset_right  = outR - visR
    inset_bottom = outB - visB

    corrL = L - inset_left
    corrT = T - inset_top
    corrW = W + inset_left + inset_right
    corrH = H + inset_top + inset_bottom

    corrL = int(round(corrL))
    corrT = int(round(corrT))
    corrW = max(1, int(round(corrW)))
    corrH = max(1, int(round(corrH)))

    win32gui.SetWindowPos(
        hwnd, 0, corrL, corrT, corrW, corrH,
        win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE | win32con.SWP_SHOWWINDOW | win32con.SWP_FRAMECHANGED
    )

def _bring_window_to_front_win(hwnd):
    """Best-effort bring-to-front for target window before moving/resizing."""
    try:
        # If minimized or maximized, restore to normal so it can be resized
        placement = win32gui.GetWindowPlacement(hwnd)
        if placement and placement[1] in (win32con.SW_SHOWMINIMIZED, win32con.SW_SHOWMAXIMIZED):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    except Exception:
        pass
    try:
        win32gui.BringWindowToTop(hwnd)
    except Exception:
        pass
    try:
        win32gui.SetForegroundWindow(hwnd)
    except Exception:
        # Foreground lock timeout may block; try activating
        try:
            win32gui.SetActiveWindow(hwnd)
        except Exception:
            pass

def apply_window_fraction_win(rx, ry, rw, rh):
    """
    Snap the Foreground Window to a Rectangle Expressed as Fractions
    of the Monitor Work Area: (rx, ry, rw, rh) in [0..1].
    """
    set_dpi_aware_win()
    hwnd = _get_top_visible_unexcluded_window()
    if not hwnd:
        raise RuntimeError("No visible unexcluded foreground window found.")

    check_exit_fullscreen_win(hwnd)

    waL, waT, waR, waB = get_effective_dimension_win(hwnd)
    waW = waR - waL
    waH = waB - waT

    # 修复Windows坐标计算，确保精确的像素对齐
    L = waL + int(round(waW * rx))
    T = waT + int(round(waH * ry))
    R = waL + int(round(waW * (rx + rw)))
    B = waT + int(round(waH * (ry + rh)))

    # 确保窗口至少有一个像素的宽度和高度
    R = max(R, L + 1)
    B = max(B, T + 1)

    apply_effective_bounds_win(hwnd, (L, T, R, B))
# Windows exclusion checker
def _is_excluded_windows(hwnd) -> bool:
    ex = _excluded_list()
    if not ex:
        return False
    try:
        title = (win32gui.GetWindowText(hwnd) or "").lower()
    except Exception:
        title = ""
    # Title substring match
    if title and any(e in title for e in ex):
        return True
    # Process executable name/path match
    try:
        pid = win32process.GetWindowThreadProcessId(hwnd)[1]
        hproc = win32api.OpenProcess(
            win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ,
            False,
            pid,
        )
        exe_path = win32process.GetModuleFileNameEx(hproc, 0) if hproc else ""
        exe_name = os.path.basename(exe_path).lower() if exe_path else ""
        if exe_name and exe_name in ex:
            return True
        if exe_path and any(e in exe_path.lower() for e in ex):
            return True
    except Exception:
        pass
    return False

def _get_top_visible_unexcluded_window():
    try:
        # Start from foreground
        hwnd = win32gui.GetForegroundWindow()
        # Iterate Z-order backwards using GetWindow with GW_HWNDPREV
        GW_HWNDPREV = 3
        visited = set()
        while hwnd and hwnd not in visited:
            visited.add(hwnd)
            if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindow(hwnd):
                if not _is_excluded_windows(hwnd):
                    return hwnd
            hwnd = win32gui.GetWindow(hwnd, GW_HWNDPREV)
    except Exception:
        pass
    return None


# ===== (Tool 01) Minimise Window =====
def minimise_window():
    run = execute_os(minimise_window_mac, minimise_window_win)
    return run()

def minimise_window_mac() -> bool:
    """
    Minimize the focused window. Uses AXMinimized; falls back to pressing the
    minimize button (AXPress) if available.
    """
    win = _focused_window_for_actions()
    if not win:
        return False
    # Prefer attribute
    try:
        AXUIElementSetAttributeValue(win, AX_MINIMIZED, True)
        return True
    except Exception:
        pass
    # Fallback: press the minimize button
    try:
        btn = _ax_copy(win, AX_MINIMIZE_BTN)
        if btn and AXUIElementPerformAction is not None:
            AXUIElementPerformAction(btn, AX_PRESS)
            return True
    except Exception:
        pass
    return False

def minimise_window_win():

    try:
        hwnd = _get_top_visible_unexcluded_window()
        if not hwnd:
            return False
        result = ctypes.windll.user32.ShowWindow(hwnd, 6)

        if result:
            return True
        else:
            print("Failed to Minimise Window")
            return False
 
    except Exception as e:
        print(f"Error Minimising Window: {e}")
        return False


# ===== (Tool 02) Maximise Window =====
def maximise_window():
    run = execute_os(maximise_window_mac, maximise_window_win)
    return run()

def maximise_window_mac() -> bool:
    return _do_region("maximize")

def maximise_window_win():
    """Put the Foreground Window into the OS 'Maximize/Bordered Fullscreen' State (Bordered, Taskbar Visible)."""
    set_dpi_aware_win()
    hwnd = _get_top_visible_unexcluded_window()
    if not hwnd:
        raise RuntimeError("No visible unexcluded foreground window found.")
    win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)


# ===== (Tool 03) Fullscreen Window =====
def fullscreen_window():
    run = execute_os(fullscreen_window_mac, fullscreen_window_win)
    return run()

def fullscreen_window_mac() -> bool:
    """
    Enter native macOS fullscreen for the focused window.
    Falls back to sending ⌃⌘F if AXFullScreen isn't available.
    """
    win = _focused_window_for_actions()
    if not win:
        return False
    # Try AX attribute first
    try:
        cur = _ax_copy(win, AX_FULLSCREEN)
        if isinstance(cur, bool) and cur is False:
            AXUIElementSetAttributeValue(win, AX_FULLSCREEN, True)
            return True
        if isinstance(cur, bool) and cur is True:
            return True  # already fullscreen
    except Exception:
        pass
    # Fallback: send the keyboard shortcut
    try:
        _send_keystroke_control_command_f()
        return True
    except Exception:
        return False

def fullscreen_window_win():
    """Put the Foreground Window into the OS 'Maximize/Bordered Fullscreen' State (Bordered, Taskbar Visible)."""
    set_dpi_aware_win()
    hwnd = _get_top_visible_unexcluded_window()
    if not hwnd:
        raise RuntimeError("No visible unexcluded foreground window found.")
    win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)


# ===== (Tool 04) Left 1/2 Screen =====
def left_half_window():
    run = execute_os(left_half_window_mac, left_half_window_win)
    return run()

def left_half_window_mac() -> bool:   
    return _do_region("left")

def left_half_window_win():
    apply_window_fraction_win(0.0, 0.0, 0.5, 1.0)


# ===== (Tool 05) Right 1/2 Screen =====
def right_half_window():
    run = execute_os(right_half_window_mac, right_half_window_win)
    return run()

def right_half_window_mac() -> bool:  
    return _do_region("right")

def right_half_window_win():
    apply_window_fraction_win(0.5, 0.0, 0.5, 1.0)


# ===== (Tool 06) Left 1/3 Screen =====
def left_third_window():
    run = execute_os(left_third_window_mac, left_third_window_win)
    return run()

def left_third_window_mac() -> bool:   
    return _do_region("left_third")

def left_third_window_win():
    apply_window_fraction_win(0.0, 0.0, 1.0/3.0, 1.0)


# ===== (Tool 07) Middle 1/3 Screen =====
def middle_third_window():
    run = execute_os(middle_third_window_mac, middle_third_window_win)
    return run()

def middle_third_window_mac() -> bool: 
    return _do_region("middle_third")

def middle_third_window_win():
    apply_window_fraction_win(1.0/3.0, 0.0, 1.0/3.0, 1.0)


# ===== (Tool 08) Right 1/3 Screen =====
def right_third_window():
    run = execute_os(right_third_window_mac, right_third_window_win)
    return run()

def right_third_window_mac() -> bool:  
    return _do_region("right_third")

def right_third_window_win():
    apply_window_fraction_win(2.0/3.0, 0.0, 1.0/3.0, 1.0)


# ===== (Tool 09) Top 1/2 Screen =====
def top_half_window():
    run = execute_os(top_half_window_mac, top_half_window_win)
    return run()

def top_half_window_mac() -> bool:    
    return _do_region("top")

def top_half_window_win():
    apply_window_fraction_win(0.0, 0.0, 1.0, 0.5)


# ===== (Tool 10) Bottom 1/2 Screen =====
def bottom_half_window():
    run = execute_os(bottom_half_window_mac, bottom_half_window_win)
    return run()

def bottom_half_window_mac() -> bool: 
    return _do_region("bottom")

def bottom_half_window_win():
    apply_window_fraction_win(0.0, 0.5, 1.0, 0.5)


# ===== (Tool 11) Top Left 1/4 Screen =====
def top_left_quadrant_window():
    run = execute_os(top_left_quadrant_window_mac, top_left_quadrant_window_win)
    return run()

def top_left_quadrant_window_mac() -> bool:
    return _do_region("top_left_quarter")  

def top_left_quadrant_window_win():
    apply_window_fraction_win(0.0, 0.0, 0.5, 0.5)


# ===== (Tool 12) Top Right 1/4 Screen =====
def top_right_quadrant_window():
    run = execute_os(top_right_quadrant_window_mac, top_right_quadrant_window_win)
    return run()

def top_right_quadrant_window_mac() -> bool:
    return _do_region("top_right_quarter")

def top_right_quadrant_window_win():
    apply_window_fraction_win(0.5, 0.0, 0.5, 0.5)


# ===== (Tool 13) Bottom Left 1/4 Screen =====
def bottom_left_quadrant_window():
    run = execute_os(bottom_left_quadrant_window_mac, bottom_left_quadrant_window_win)
    return run()

def bottom_left_quadrant_window_mac() -> bool:
    return _do_region("bottom_left_quarter")

def bottom_left_quadrant_window_win():
    apply_window_fraction_win(0.0, 0.5, 0.5, 0.5)


# ===== (Tool 14) Bottom Right 1/4 Screen =====
def bottom_right_quadrant_window():
    run = execute_os(bottom_right_quadrant_window_mac, bottom_right_quadrant_window_win)
    return run()

def bottom_right_quadrant_window_mac() -> bool:
    return _do_region("bottom_right_quarter")

def bottom_right_quadrant_window_win():
    apply_window_fraction_win(0.5, 0.5, 0.5, 0.5)


# ===== (Tool 15) Left 2/3 Screen =====
def left_two_thirds_window():
    run = execute_os(left_two_thirds_window_mac, left_two_thirds_window_win)
    return run()

def left_two_thirds_window_mac() -> bool: 
    return _do_region("left_two_third")

def left_two_thirds_window_win():
    apply_window_fraction_win(0.0, 0.0, 2.0/3.0, 1.0)


# ===== (Tool 16) Right 2/3 Screen =====
def right_two_thirds_window():
    run = execute_os(right_two_thirds_window_mac, right_two_thirds_window_win)
    return run()

def right_two_thirds_window_mac() -> bool: 
    return _do_region("right_two_third")

def right_two_thirds_window_win():
    apply_window_fraction_win(1.0/3.0, 0.0, 2.0/3.0, 1.0)
