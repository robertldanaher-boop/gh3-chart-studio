"""Application icon/logo and Windows taskbar identity."""
import sys
from pathlib import Path

ASSETS = Path(__file__).resolve().parent / 'assets'
ICON_ICO = ASSETS / 'app.ico'
ICON_PNG = ASSETS / 'app_icon.png'
LOGO_PNG = ASSETS / 'logo.png'
APP_USER_MODEL_ID = 'GH3ChartStudio.Studio'


def app_icon():
    from PySide6.QtGui import QIcon
    for path in (ICON_ICO, ICON_PNG):
        if path.exists():
            return QIcon(str(path))
    return QIcon()


def apply_identity(app):
    """Window/taskbar icon. On Windows also group the taskbar button under the
    studio's own identity instead of python.exe (matches the shortcut's ID)."""
    if sys.platform == 'win32':
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_USER_MODEL_ID)
        except Exception:
            pass
    icon = app_icon()
    if not icon.isNull():
        app.setWindowIcon(icon)
