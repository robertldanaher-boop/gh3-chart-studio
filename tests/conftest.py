"""Safety net for install-time test runs.

pytest's faulthandler_timeout (60 s) only prints a traceback; a hung test would
otherwise keep the installer waiting until the user cancels. If one test runs for
150 s, dump every thread's stack to the log and end the run with exit code 3, so
setup reports a clear failure instead of freezing.
"""
import faulthandler
import os
import sys
import threading

import pytest

HANG_LIMIT_SECONDS = float(os.environ.get("GH3_TEST_HANG_LIMIT", "150"))


@pytest.fixture(autouse=True)
def _fail_fast_if_hung(request):
    capture = request.config.pluginmanager.getplugin('capturemanager')

    def give_up():
        try:
            capture.suspend_global_capture(in_=False)  # write to the real log, not pytest's buffer
        except Exception:
            pass
        sys.stderr.write(f'\n\nTEST HUNG for {HANG_LIMIT_SECONDS} s: {request.node.nodeid}\n'
                         'Stopping the test run so setup does not freeze. Thread stacks:\n')
        faulthandler.dump_traceback(file=sys.stderr, all_threads=True)
        sys.stderr.flush()
        sys.stdout.flush()
        os._exit(3)

    timer = threading.Timer(HANG_LIMIT_SECONDS, give_up)
    timer.daemon = True
    timer.start()
    yield
    timer.cancel()


@pytest.fixture(autouse=True)
def _dispose_closed_qt_windows():
    """Applies to EVERY test module (previously only modules that imported
    test_gui.dispose_closed_windows_on_gui_thread). Closed windows own media
    players; if their deferred deletion runs inside the NEXT test's wait loop
    while a worker thread is busy, Qt's FFmpeg backend teardown can deadlock with
    Python (seen in 0.16.5/0.16.6 install runs in tests/test_stems_gui.py, a new
    module that did not import the fixture). Flush deletion here, between tests.
    """
    yield
    if 'PySide6.QtWidgets' not in sys.modules:
        return
    import gc
    import time
    from PySide6.QtCore import QCoreApplication, QEvent
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance()
    if app is None:
        return
    for widget in QApplication.topLevelWidgets():
        busy = getattr(widget, 'busy', None)
        if callable(busy):
            deadline = time.monotonic() + 30
            while busy() and time.monotonic() < deadline:
                app.processEvents()
                time.sleep(0.01)
        widget.close()
        widget.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
    app.processEvents()
    gc.collect()
    QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
