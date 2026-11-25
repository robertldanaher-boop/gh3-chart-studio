"""Background update check. Network work runs off the GUI thread; results come
back through a queued slot, so no widget is touched from the worker thread."""
import os
import time

from PySide6.QtCore import QObject, QThread, Qt, QUrl, Signal, Slot
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QMessageBox

from .updates import check_for_update, due, RELEASES_PAGE, download_update, launch_installer

INSTALL = 'install'  # prompt result: download and install now

LAST_CHECK_KEY = 'updates/last_check'


class _DownloadThread(QThread):
    done = Signal(object)
    failed = Signal(str)
    progress = Signal(int, int)

    def __init__(self, result, download, parent=None):
        super().__init__(parent)
        self.result, self.download = result, download

    def run(self):
        import tempfile
        try:
            workdir = tempfile.mkdtemp(prefix='gh3-update-')
            root = self.download(self.result, workdir, lambda d, t: self.progress.emit(d, t),
                                 self.isInterruptionRequested)
            self.done.emit(str(root))
        except Exception as exc:
            self.failed.emit(str(exc))


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
    install = None
    if result.status == 'newer':
        box.setIcon(QMessageBox.Information)
        if result.source_zip_url:
            box.setInformativeText('Download and install closes GH3 Chart Studio, installs the new version '
                                   '(setup and tests run once, a few minutes) and keeps your Start menu entries.')
            install = box.addButton('Download and install', QMessageBox.AcceptRole)
        elif result.installer_url:
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
    if install is not None and clicked is install:
        return INSTALL
    if download is not None and clicked is download:
        return result.installer_url
    if page is not None and clicked is page:
        return result.page_url or RELEASES_PAGE
    return ''


class UpdateChecker(QObject):
    """manual=True always reports; automatic checks (every launch) only speak up
    when a newer version exists."""
    finished = Signal(object)

    def __init__(self, parent_widget, settings=None, check=check_for_update, prompt=default_prompt,
                 open_url=lambda url: QDesktopServices.openUrl(QUrl(url)), download=download_update,
                 launch=launch_installer, quit_app=None, notify=None):
        super().__init__(parent_widget)
        self.parent_widget = parent_widget
        self.settings = settings
        self.check_fn = check
        self.prompt = prompt
        self.open_url = open_url
        self.download = download
        self.launch = launch
        self.quit_app = quit_app or self._quit_app
        self.notify = notify or self._notify
        self.download_thread = None
        self.progress_dialog = None
        self.installing = False
        self.thread = None
        self.manual = False
        self.last_result = None

    def running(self):
        return self.thread is not None and self.thread.isRunning()

    def check_on_startup(self):
        """Every launch: look for a newer release; prompt only when one exists
        (no message when up to date, offline or the releases are not visible)."""
        from .package_runtime import is_msix
        if os.environ.get('GH3_NO_UPDATE_CHECK') or is_msix():
            return False
        return self.check(manual=False)

    def check_if_due(self):
        if os.environ.get('GH3_NO_UPDATE_CHECK'):
            return False
        last = self.settings.value(LAST_CHECK_KEY, 0) if self.settings is not None else 0
        if not due(last, time.time()):
            return False
        return self.check(manual=False)

    def check(self, manual=True):
        from .package_runtime import is_msix
        if is_msix():
            if manual:self.notify('This MSIX installation is managed by Windows. Install a newer signed MSIX bundle with the same publisher, or update through the Microsoft Store when available. The source/Win32 updater is disabled.')
            return False
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
            if url == INSTALL:
                self.start_install(result)
            elif url:
                self.open_url(url)
        self.finished.emit(result)

    def _owner_busy(self):
        window = self.parent_widget
        while window is not None and not callable(getattr(window, 'busy', None)):
            window = window.parent() if hasattr(window, 'parent') else None
        return bool(window is not None and window.busy())

    def start_install(self, result):
        from .package_runtime import is_msix
        if is_msix():
            self.notify('MSIX updates must be installed through Windows; source/Win32 setup cannot update this package.')
            return False
        if self.installing:
            return False
        if self._owner_busy():
            self.notify('Finish or cancel the current job first, then choose Check for updates again.')
            return False
        self.installing = True
        from PySide6.QtWidgets import QProgressDialog
        self.progress_dialog = QProgressDialog(f'Downloading version {result.latest}…', 'Cancel', 0, 0, self.parent_widget)
        self.progress_dialog.setWindowTitle('Updating GH3 Chart Studio')
        self.progress_dialog.setWindowModality(Qt.ApplicationModal)
        self.progress_dialog.setMinimumDuration(0)
        self.download_thread = _DownloadThread(result, self.download, self)
        self.progress_dialog.canceled.connect(self.download_thread.requestInterruption)
        self.download_thread.progress.connect(self._progress, Qt.QueuedConnection)
        self.download_thread.done.connect(self._downloaded, Qt.QueuedConnection)
        self.download_thread.failed.connect(self._download_failed, Qt.QueuedConnection)
        self.download_thread.start()
        return True

    @Slot(int, int)
    def _progress(self, done, total):
        if self.progress_dialog is not None and total:
            self.progress_dialog.setMaximum(total)
            self.progress_dialog.setValue(min(done, total))

    def _close_progress(self):
        if self.progress_dialog is not None:
            self.progress_dialog.close()
            self.progress_dialog.deleteLater()
            self.progress_dialog = None

    @Slot(str)
    def _download_failed(self, message):
        self._close_progress()
        self.installing = False
        self.notify('The update could not be downloaded: ' + message + '\n\nYou can try again later or open the releases page.')

    @Slot(str)
    def _downloaded(self, root):
        # A job or cancellation can arrive after the initial check, while the
        # network worker is finishing. Never terminate that work to update.
        cancelled = (self.download_thread is not None and
                     self.download_thread.isInterruptionRequested())
        self._close_progress()
        if cancelled:
            self.installing = False
            return
        if self._owner_busy():
            self.installing = False
            self.notify('The update is ready, but a chart job is running. Finish or cancel it, '
                        'then choose Check for updates again. Your work has not been interrupted.')
            return
        try:
            self.launch(root)
        except Exception as exc:
            self.installing = False
            self.notify('The installer could not be started: ' + str(exc))
            return
        self.quit_app()

    def _notify(self, text):
        QMessageBox.warning(self.parent_widget, 'Update', text)

    @staticmethod
    def _quit_app():
        from PySide6.QtWidgets import QApplication
        for widget in QApplication.topLevelWidgets():
            if not widget.close():
                return
        QApplication.quit()

    def shutdown(self):
        if self.download_thread is not None and self.download_thread.isRunning():
            self.download_thread.requestInterruption()
            self.download_thread.wait(10000)
        if self.thread is not None:
            self.thread.wait(10000)
