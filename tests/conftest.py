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
