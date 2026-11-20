"""Windows open fully reachable: title bar on screen, size fitted to the desktop."""
import os
import pytest
from gh3studio.window_fit import fit_geometry, PREFERRED_MAIN_SIZE, DEFAULT_FRAME_EXTRA

MAIN_MIN = (1024, 700)  # the layout limit the GUI tests already enforce


def inside(result, available, extra=DEFAULT_FRAME_EXTRA):
    x, y, w, h = result
    ax, ay, aw, ah = available
    return ax <= x and ay <= y and x + w + extra[0] <= ax + aw and y + h + extra[1] <= ay + ah


def test_large_display_keeps_preferred_size_and_centres():
    available = (0, 0, 2560, 1400)
    x, y, w, h = fit_geometry(PREFERRED_MAIN_SIZE, MAIN_MIN, available)
    assert (w, h) == PREFERRED_MAIN_SIZE
    assert inside((x, y, w, h), available)
    assert abs((x + (w + DEFAULT_FRAME_EXTRA[0]) / 2) - 1280) <= 1


@pytest.mark.parametrize('available', [
    (0, 0, 1920, 1040),     # 1080p, 100%, taskbar
    (0, 0, 1536, 824),      # 1080p at 125%
    (0, 0, 1366, 728),      # common laptop
])
def test_shorter_displays_shrink_window_so_title_bar_and_corner_are_visible(available):
    result = fit_geometry(PREFERRED_MAIN_SIZE, (800, 500), available)
    assert inside(result, available)
    assert result[2] <= PREFERRED_MAIN_SIZE[0] and result[3] <= PREFERRED_MAIN_SIZE[1]


@pytest.mark.parametrize('available', [(0, 0, 1280, 672), (0, 0, 1024, 600), (-1920, 30, 1280, 650)])
def test_title_bar_stays_on_screen_even_when_minimum_does_not_fit(available):
    x, y, w, h = fit_geometry(PREFERRED_MAIN_SIZE, MAIN_MIN, available)
    assert (x, y) >= (available[0], available[1]) and y >= available[1] and x >= available[0]
    assert w >= MAIN_MIN[0] and h >= MAIN_MIN[1]


def test_never_larger_than_preferred_and_never_below_minimum():
    x, y, w, h = fit_geometry((800, 600), (300, 200), (0, 0, 3000, 2000))
    assert (w, h) == (800, 600)
    x, y, w, h = fit_geometry((800, 600), (900, 650), (0, 0, 3000, 2000))
    assert (w, h) == (900, 650)


def test_real_window_opens_with_title_bar_inside_available_area():
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    pytest.importorskip('PySide6')
    from PySide6.QtWidgets import QApplication, QDialog
    from gh3studio.gui import Window
    from gh3studio.window_fit import place_on_screen, fit_size
    app = QApplication.instance() or QApplication([])
    w = Window()
    place_on_screen(w)
    w.show()
    app.processEvents()
    place_on_screen(w)
    app.processEvents()
    available = w.screen().availableGeometry()
    frame = w.frameGeometry()
    assert frame.left() >= available.left() and frame.top() >= available.top(), (frame, available)
    floor = (max(w.minimumSizeHint().width(), w.minimumSize().width()),
             max(w.minimumSizeHint().height(), w.minimumSize().height()))
    assert w.width() <= max(PREFERRED_MAIN_SIZE[0], floor[0])
    assert w.height() <= max(PREFERRED_MAIN_SIZE[1], floor[1])
    w.close()
    dialog = QDialog()
    fit_size(dialog, 20000, 20000)
    assert dialog.width() <= available.width() and dialog.height() <= available.height()
    dialog.deleteLater()
    app.processEvents()
