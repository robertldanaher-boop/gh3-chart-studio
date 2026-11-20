"""Keep top-level windows inside the visible desktop area.

The studio used to open at a fixed 1180x840. On a smaller or scaled display
(for example 1366x768, or 1920x1080 at 150%) that is taller than the usable
screen, so Windows placed the title bar above the top edge and the resize
corner below the taskbar: the window could neither be moved nor shrunk.

fit_geometry() is pure arithmetic so it can be tested without Qt. The Qt
helpers only read the screen's available area (which excludes the taskbar)
and apply the result. Windows stay normal resizable windows; nothing here
fixes their size.
"""

# Allowance for title bar and borders before the window has been shown and
# its real frame margins are known. Generous on purpose: a slightly smaller
# window is harmless, a hidden title bar is not.
DEFAULT_FRAME_EXTRA = (16, 48)

PREFERRED_MAIN_SIZE = (1180, 840)


def fit_geometry(preferred, minimum, available, frame_extra=DEFAULT_FRAME_EXTRA):
    """Return (x, y, width, height) for a window.

    preferred/minimum: (width, height) of the client area.
    available: (x, y, width, height) usable desktop area.
    frame_extra: (horizontal, vertical) pixels added by borders/title bar.
    x/y are the frame's top-left corner; width/height the client size.

    The client shrinks from preferred to fit the available area, but never
    below minimum (layouts cannot be compressed further).
    The frame is centred, but its top-left corner is always kept inside the
    available area so the title bar stays reachable even when the minimum
    size does not fit.
    """
    pw, ph = (max(1, int(v)) for v in preferred)
    mw, mh = (max(0, int(v)) for v in minimum)
    ax, ay, aw, ah = (int(v) for v in available)
    ew, eh = (max(0, int(v)) for v in frame_extra)
    width = max(min(pw, aw - ew), mw, 1)
    height = max(min(ph, ah - eh), mh, 1)
    x = ax + max(0, (aw - (width + ew)) // 2)
    y = ay + max(0, (ah - (height + eh)) // 2)
    return x, y, width, height


def _available(widget):
    from PySide6.QtGui import QGuiApplication
    screen = widget.screen() if hasattr(widget, 'screen') else None
    if screen is None:
        screen = QGuiApplication.primaryScreen()
    if screen is None:
        return None
    rect = screen.availableGeometry()
    return rect.x(), rect.y(), rect.width(), rect.height()


def _frame_extra(widget):
    if widget.isVisible():
        frame, inner = widget.frameGeometry(), widget.geometry()
        extra = (frame.width() - inner.width(), frame.height() - inner.height())
        if extra[0] > 0 or extra[1] > 0:
            return extra
    return DEFAULT_FRAME_EXTRA


def _minimum(widget):
    hint, explicit = widget.minimumSizeHint(), widget.minimumSize()
    return max(hint.width(), explicit.width(), 0), max(hint.height(), explicit.height(), 0)


def place_on_screen(widget, preferred=PREFERRED_MAIN_SIZE):
    """Size a top-level window to fit the screen and centre it there."""
    available = _available(widget)
    if available is None:
        widget.resize(*preferred)
        return
    x, y, width, height = fit_geometry(preferred, _minimum(widget), available, _frame_extra(widget))
    widget.resize(width, height)
    widget.move(x, y)


def fit_size(widget, width, height):
    """Resize a dialog to (width, height), shrunk to fit the screen if needed.

    Position is left to Qt, which centres dialogs over their parent.
    """
    available = _available(widget)
    if available is None:
        widget.resize(width, height)
        return
    _, _, w, h = fit_geometry((width, height), (0, 0), available)
    widget.resize(w, h)
