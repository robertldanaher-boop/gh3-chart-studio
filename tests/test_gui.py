import os
import pytest
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from pathlib import Path
from PySide6.QtCore import QMimeData,QUrl,QPointF,Qt
from PySide6.QtGui import QDropEvent
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from gh3studio.gui import Window
FIXTURE=Path(__file__).parents[1]/'examples'/'technical-study.chart'
def wait(window):
    for _ in range(1000):
        QApplication.processEvents()
        if not window.busy(): return
        QTest.qWait(10)
    raise AssertionError('GUI worker timeout')
@pytest.fixture(scope='module')
def app():
    application=QApplication.instance() or QApplication([])
    yield application
    application.processEvents()

def test_gui_workflow(tmp_path,app):
    window=Window(); window.show()
    mime=QMimeData(); mime.setUrls([QUrl.fromLocalFile(str(FIXTURE))])
    window.dropEvent(QDropEvent(QPointF(50,50),Qt.CopyAction,mime,Qt.LeftButton,Qt.NoModifier)); wait(window)
    assert window.song is not None
    QTest.mouseClick(window.convert_button,Qt.LeftButton); wait(window)
    assert window.converted and window.export_button.isEnabled()
    assert len(window.preview.scene().items())>20
    window.export_to(tmp_path/'gui-output'); wait(window)
    assert (tmp_path/'gui-output'/'notes.mid').exists() and 'Export verified' in window.log.toPlainText()
    window.sliders['Density'].setValue(1)
    assert window.converted is None and not window.export_button.isEnabled()
    window.close()
def test_gui_error(tmp_path,app):
    path=tmp_path/'bad.chart'; path.write_text('bad')
    window=Window(); window.open_path(path); wait(window)
    assert window.song is None and not window.convert_button.isEnabled() and 'ERROR' in window.log.toPlainText()
    window.close()

def test_worker_results_delivered_on_main_thread(app):
    from PySide6.QtCore import QThread
    window=Window(); seen=[]
    for i in range(12):
        window.run_job('Thread regression',lambda cancel:42,lambda value:seen.append((value,QThread.currentThread()==app.thread())))
        wait(window)
    assert seen==[(42,True)]*12
    window.close()
