from pathlib import Path
import pytest
from PySide6.QtCore import QTimer,Qt,QUrl
from PySide6.QtWidgets import QWidget,QDialog
from gh3studio.gui import Window
from gh3studio.sync_gui import SynchronizationDialog
from gh3studio.cleaner import inspect_chart
from test_gui import app,wait,dispose_closed_windows_on_gui_thread
from test_cleaner import fixture
from test_synchronization import anchored


def test_dialog_presets_preview_confirmation_and_cancel(tmp_path,app):
    path=fixture(tmp_path/'source',{'Name':'Study','Artist':'Artist','Offset':'0.2'})
    (path.parent/'song.ini').write_text('[song]\ndelay=75\n',encoding='utf-8')
    row=inspect_chart(path);dialog=SynchronizationDialog(row)
    dialog.show();app.processEvents()
    assert not dialog.apply.isEnabled() and dialog.review is None
    assert Path(dialog.player.source().toLocalFile())==Path(row['audio'])
    dialog.mode.setCurrentIndex(1);assert dialog.shift.value()==75
    dialog.mode.setCurrentIndex(2);assert dialog.shift.value()==200
    dialog.mode.setCurrentIndex(3);assert dialog.shift.value()==-200
    assert dialog.highway.shift==-.2
    dialog.confirm.setChecked(True);assert dialog.apply.isEnabled()
    dialog.mode.setCurrentIndex(4);dialog.shift.setValue(125)
    assert not dialog.confirm.isChecked() and not dialog.apply.isEnabled()
    dialog.difficulty.setCurrentText('Hard');assert len(dialog.highway.notes)==1
    dialog.position_changed(1000);assert dialog.highway.position==1
    dialog.reject();assert dialog.review is None and dialog.player.source().isEmpty()
    dialog.deleteLater()


def test_cleaner_review_button_rechecks_then_exports_without_mutating_converter(tmp_path,app):
    path=fixture(tmp_path/'source',{'Name':'Study','Artist':'Artist','Offset':'0.2'})
    w=Window();w.cleaner.scan(path.parent);wait(w);w.show();panel=w.cleaner
    assert not panel.rows[0]['errors'];assert panel.sync_button.isEnabled()
    assert 'automatic — song.ini delay only' in panel.details.toPlainText()
    def accept_dialog():
        dialog=panel.findChild(SynchronizationDialog)
        assert dialog is not None
        dialog.mode.setCurrentIndex(2);dialog.confirm.setChecked(True);dialog.apply.click()
    QTimer.singleShot(0,accept_dialog);panel.sync_button.click();wait(w)
    assert not panel.rows[0]['errors'] and panel.rows[0]['sync_review']['shift_ms']==200
    assert 'reviewed for this source' in panel.details.toPlainText()
    assert w.song is None and w.converted is None
    original=panel.rows[0]['song'].tracks
    panel.recheck(0,metadata={'Name':'Renamed','Artist':'Artist'});wait(w)
    assert panel.rows[0]['song'].tracks==original
    panel.set_checked(True);panel.approve.setChecked(True);panel.export_to(tmp_path/'export');wait(w)
    assert panel.last_output==tmp_path/'export'
    assert list((tmp_path/'export').glob('*/song.ogg'))
    w.close()


@pytest.mark.parametrize('large',[False,True])
def test_sync_dialog_and_footer_fit_with_wide_text(tmp_path,app,large):
    path=fixture(tmp_path/'source',{'Name':'Study','Artist':'Artist','Offset':'0.2'})
    w=Window();dialog=SynchronizationDialog(inspect_chart(path),w)
    if large:dialog.setStyleSheet(dialog.styleSheet()+'\nQWidget {font-size:18px;}')
    for widget in [dialog,*dialog.findChildren(QWidget)]:
        font=widget.font();font.setStretch(160);widget.setFont(font)
    dialog.resize(1024,700);dialog.show();app.processEvents()
    assert dialog.width()<=1024 and dialog.height()<=700
    assert dialog.apply.visibleRegion().boundingRect()==dialog.apply.rect()
    dialog.reject();dialog.deleteLater();w.close()


def test_conflicting_anchor_requires_separate_acknowledgement(tmp_path,app):
    path=anchored(fixture(tmp_path/'source'),750000)
    dialog=SynchronizationDialog(inspect_chart(path));dialog.show()
    dialog.mode.setCurrentIndex(4);dialog.confirm.setChecked(True)
    assert not dialog.apply.isEnabled()
    dialog.anchor_confirm.setChecked(True);assert dialog.apply.isEnabled()
    dialog.apply.click();assert dialog.result()==QDialog.Accepted and dialog.review['accept_anchor_map']
    dialog.deleteLater()


def test_gui_automatic_delay_exports_without_sync_dialog(tmp_path,app):
    path=fixture(tmp_path/'source',{'Name':'Automatic','Artist':'Artist','Offset':'0.2'})
    (path.parent/'song.ini').write_text('[song]\ndelay=75\n',encoding='utf-8')
    w=Window();panel=w.cleaner;panel.scan(path.parent);wait(w)
    assert not panel.rows[0]['errors'] and 'sync_review' not in panel.rows[0]
    assert panel.rows[0]['synchronization']['reviewed_shift_ms']==75
    assert panel.findChild(SynchronizationDialog) is None
    panel.set_checked(True);panel.approve.setChecked(True);panel.export_to(tmp_path/'export');wait(w)
    assert list((tmp_path/'export').glob('*/song.ogg'))
    assert panel.findChild(SynchronizationDialog) is None
    assert w.song is None and w.converted is None
    w.close()
