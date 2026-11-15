import pytest
from PySide6.QtWidgets import QApplication

@pytest.fixture(scope='module')
def app():
    application = QApplication.instance() or QApplication([])
    yield application
    application.processEvents()

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QDialog
from gh3studio.first_run import FirstRunDialog, has_accepted


def settings_at(path):
    return QSettings(str(path), QSettings.Format.IniFormat)


def test_acceptance_persists_without_reprompt(tmp_path, app):
    path = tmp_path / 'preferences.ini'
    settings = settings_at(path)
    assert not has_accepted(settings)
    dialog = FirstRunDialog(settings)
    assert 'open-source chart-based' in dialog.notice.toPlainText()
    dialog.agree.click()
    assert dialog.result() == QDialog.DialogCode.Accepted
    assert has_accepted(settings_at(path))


def test_decline_and_close_do_not_record_acceptance(tmp_path, app):
    settings = settings_at(tmp_path / 'preferences.ini')
    for action in ('decline', 'close'):
        dialog = FirstRunDialog(settings)
        dialog.show()
        app.processEvents()
        if action == 'decline':
            dialog.decline.click()
        else:
            dialog.close()
        assert dialog.result() == QDialog.DialogCode.Rejected
        assert not has_accepted(settings)


def test_missing_notice_cannot_be_accepted(tmp_path, app, monkeypatch):
    def missing():
        raise FileNotFoundError()
    monkeypatch.setattr('gh3studio.first_run.legal_notice_text', missing)
    dialog = FirstRunDialog(settings_at(tmp_path / 'preferences.ini'))
    assert not dialog.agree.isEnabled()


def test_settings_write_failure_keeps_dialog_open(tmp_path, app, monkeypatch):
    class Unwritable:
        def setValue(self, *args): pass
        def sync(self): pass
        def status(self): return QSettings.Status.AccessError
    messages = []
    monkeypatch.setattr('gh3studio.first_run.QMessageBox.warning', lambda *args: messages.append(args))
    dialog = FirstRunDialog(Unwritable())
    dialog.show()
    dialog.agree.click()
    assert messages
    assert dialog.isVisible()
    assert dialog.result() != QDialog.DialogCode.Accepted
    dialog.close()


@pytest.mark.parametrize('accept', [True, False])
def test_main_gate_controls_studio_launch(tmp_path, app, monkeypatch, accept):
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QWidget
    import gh3studio.gui as gui
    settings = settings_at(tmp_path / 'main.ini')
    monkeypatch.setattr('PySide6.QtCore.QSettings', lambda *args: settings)
    opened = []
    class Studio(QWidget):
        def __init__(self):
            super().__init__()
            opened.append(True)
            QTimer.singleShot(0, app.quit)
    monkeypatch.setattr(gui, 'Window', Studio)
    monkeypatch.setattr(gui, 'QApplication', lambda *args: app)
    def choose():
        gate = next(w for w in app.topLevelWidgets() if isinstance(w, FirstRunDialog) and w.isVisible())
        (gate.agree if accept else gate.decline).click()
    QTimer.singleShot(0, choose)
    QTimer.singleShot(1000, app.quit)
    with pytest.raises(SystemExit):
        gui.main()
    assert bool(opened) == accept
    assert has_accepted(settings) == accept
    for widget in app.topLevelWidgets():
        widget.close()
