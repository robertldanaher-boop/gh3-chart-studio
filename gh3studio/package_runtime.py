"""Package identity separates Windows-managed MSIX updates from source installers."""
import ctypes
import sys
from pathlib import Path


def is_msix():
    if sys.platform != 'win32':
        return False
    # Also marks an unpacked engineering build: never let it self-replace with Win32 setup.
    if getattr(sys, 'frozen', False) and (Path(sys.executable).parent/'GH3_MSIX_PACKAGE').is_file():
        return True
    try:
        size = ctypes.c_uint32(0)
        api = ctypes.windll.kernel32.GetCurrentPackageFullName
        api.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.c_wchar_p]
        api.restype = ctypes.c_long
        return api(ctypes.byref(size), None) == 122 and size.value > 0
    except (AttributeError, OSError):
        return False


def configure_working_directory():
    if not is_msix():
        return
    import os
    from PySide6.QtCore import QStandardPaths
    root = Path(QStandardPaths.writableLocation(QStandardPaths.AppLocalDataLocation))
    root.mkdir(parents=True, exist_ok=True)
    os.chdir(root)
