import time
from functools import wraps
import functools
import sys
import logging
logger = logging.getLogger(__name__)
logger.debug(f"initializing {__name__}")


def timeit_decorator(func):
    def timeit_wrapper(func, *args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.timer(
            f"{elapsed_time:.2f} : {func.__name__}  ")
        return result

    """Decorator to time a function."""
    def wrapper(*args, **kwargs):
        return timeit_wrapper(func, *args, **kwargs)
    return wrapper


def logging_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.trace(
            f"{func.__name__} args: {args} and kwargs: {kwargs}")
        return func(*args, **kwargs)
    return wrapper


def human_readable_time(timestamp):
    import datetime  # pylint: disable=import-outside-toplevel

    now = datetime.datetime.now()
    dt_object = datetime.datetime.fromtimestamp(timestamp)
    diff = now - dt_object
    if diff.days > 0:
        return f"{diff.days} days ago"
    elif diff.seconds < 60:
        return f"{diff.seconds} seconds ago"
    elif diff.seconds < 3600:
        return f"{diff.seconds // 60} minutes ago"
    else:
        return f"{diff.seconds // 3600} hours ago"


def timestamp_to_human_readable(timestamp):
    import datetime  # pylint: disable=import-outside-toplevel

    try:
        dt_object = datetime.datetime.fromtimestamp(timestamp)
        return dt_object.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return ""


def get_active_app_name_osx():
    from AppKit import NSWorkspace  # pylint: disable=import-outside-toplevel

    try:
        active_app = NSWorkspace.sharedWorkspace().activeApplication()
        return active_app["NSApplicationName"]
    except:
        return ""


def get_active_window_title_osx():
    # pylint: disable=import-outside-toplevel
    from Quartz import (
        CGWindowListCopyWindowInfo,
        kCGNullWindowID,
        kCGWindowListOptionOnScreenOnly,
    )

    try:
        app_name = get_active_app_name_osx()
        windows = CGWindowListCopyWindowInfo(
            kCGWindowListOptionOnScreenOnly, kCGNullWindowID
        )
        for window in windows:
            if window["kCGWindowOwnerName"] == app_name:
                return window.get("kCGWindowName", "Unknown")
    except:
        return ""
    return ""


def get_active_app_name_windows():
    import psutil  # pylint: disable=import-outside-toplevel
    import win32gui  # pylint: disable=import-outside-toplevel
    import win32process  # pylint: disable=import-outside-toplevel

    try:
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        exe = psutil.Process(pid).name()
        return exe
    except:
        return ""


def get_active_window_title_windows():
    import win32gui  # pylint: disable=import-outside-toplevel

    try:
        hwnd = win32gui.GetForegroundWindow()
        return win32gui.GetWindowText(hwnd)
    except:
        return ""


def get_active_app_name_linux():
    return ''


def get_active_window_title_linux():
    return ''


def get_active_app_name():
    if sys.platform == "win32":
        return get_active_app_name_windows()
    elif sys.platform == "darwin":
        return get_active_app_name_osx()
    elif sys.platform.startswith("linux"):
        return get_active_app_name_linux()
    else:
        raise NotImplementedError("This platform is not supported")


def get_active_window_title():
    if sys.platform == "win32":
        return get_active_window_title_windows()
    elif sys.platform == "darwin":
        return get_active_window_title_osx()
    elif sys.platform.startswith("linux"):
        return get_active_window_title_linux()
    else:
        raise NotImplementedError("This platform is not supported")


def is_user_active_osx():
    import subprocess

    try:
        # Run the 'ioreg' command to get idle time information
        output = subprocess.check_output(
            ["ioreg", "-c", "IOHIDSystem"]).decode()

        # Find the line containing "HIDIdleTime"
        for line in output.split('\n'):
            if "HIDIdleTime" in line:
                # Extract the idle time value
                idle_time = int(line.split('=')[-1].strip())

                # Convert idle time from nanoseconds to seconds
                idle_seconds = idle_time / 1000000000

                # If idle time is less than 5 seconds, consider the user not idle
                return idle_seconds < 5

        # If "HIDIdleTime" is not found, assume the user is not idle
        return True

    except subprocess.CalledProcessError:
        # If there's an error running the command, assume the user is not idle
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        # If there's any other error, assume the user is not idle
        return True


def is_user_active():
    if sys.platform == "win32":
        return True
    elif sys.platform == "darwin":
        return is_user_active_osx()
    elif sys.platform.startswith("linux"):
        return True
    else:
        raise NotImplementedError("This platform is not supported")


def read_file_to_string(file_path):
    with open(file_path, 'r') as file:
        return file.read()
