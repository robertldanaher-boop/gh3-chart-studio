"""Background update check. Network work runs off the GUI thread; results come
back through a queued slot, so no widget is touched from the worker thread."""
import os
import time

from PySide6.QtCore import QObject, QThread, Qt, QUrl, Signal, Slot
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QMessageBox

from .updates import check_for_update, due, RELEASES_PAGE

LAST_CHECK_KEY = 'updates/last_check'


class _CheckThread(QThread):
    done = Signal(object)

    def __init__(self, check, parent=None):
        super().__init__(parent)
        self.check = check

    def run(self):
        self.done.emit(self.check())


def default_prompt(parent, result, manual):
    """Show the result. Returns the URL the user chose to open, or ''."""
    box = QMessageBox(parent)
    box.setWindowTitle('Check for updates')
    box.setText(result.message)
    download = page = None
    if result.status == 'newer':
        box.setIcon(QMessageBox.Information)
        if result.installer_url:
            download = box.addButton('Download installer', QMessageBox.AcceptRole)
        page = box.addButton('Open release page', QMessageBox.ActionRole)
        box.addButton('Later', QMessageBox.RejectRole)
    elif result.status == 'unavailable':
        box.setIcon(QMessageBox.Warning)
        page = box.addButton('Open releases page', QMessageBox.ActionRole)
        box.addButton(QMessageBox.Close)
    else:
        box.setIcon(QMessageBox.Information)
        box.addButton(QMessageBox.Ok)
    box.exec()
    clicked = box.clickedButton()
    box.deleteLater()
    if download is not None and clicked is download:
        return result.installer_url
    if page is not None and clicked is page:
        return result.page_url or RELEASES_PAGE
    return ''


class UpdateChecker(QObject):
    """manual=True always reports; automatic checks only speak up when a newer
    version exists, and run at most once a day."""
    finished = Signal(object)

    def __init__(self, parent_widget, settings=None, check=check_for_update, prompt=default_prompt,
                 open_url=lambda url: QDesktopServices.openUrl(QUrl(url))):
        super().__init__(parent_widget)
        self.parent_widget = parent_widget
        self.settings = settings
        self.check_fn = check
        self.prompt = prompt
        self.open_url = open_url
        self.thread = None
        self.manual = False
        self.last_result = None

    def running(self):
        return self.thread is not None and self.thread.isRunning()

    def check_if_due(self):
        if os.environ.get('GH3_NO_UPDATE_CHECK'):
            return False
        last = self.settings.value(LAST_CHECK_KEY, 0) if self.settings is not None else 0
        if not due(last, time.time()):
            return False
        return self.check(manual=False)

    def check(self, manual=True):
        if self.running():
            return False
        self.manual = manual
        self.thread = _CheckThread(self.check_fn, self)
        self.thread.done.connect(self._done, Qt.QueuedConnection)
        self.thread.start()
        return True

    @Slot(object)
    def _done(self, result):
        self.last_result = result
        if self.settings is not None:
            try:
                self.settings.setValue(LAST_CHECK_KEY, time.time())
            except Exception:
                pass
        if self.manual or result.status == 'newer':
            url = self.prompt(self.parent_widget, result, self.manual)
            if url:
                self.open_url(url)
        self.finished.emit(result)

    def shutdown(self):
        if self.thread is not None:
            self.thread.wait(10000)
