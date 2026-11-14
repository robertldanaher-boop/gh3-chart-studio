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

def test_pattern_library_scan_browse_rate_generate_export(tmp_path,app):
    import shutil
    root=tmp_path/'charts';root.mkdir();shutil.copyfile(FIXTURE,root/'study.chart')
    w=Window();w.library.db_path.setText(str(tmp_path/'library.sqlite3'))
    w.library.scan(root);wait(w)
    assert w.library.last_scan['state']=='completed'
    w.library.refresh();wait(w)
    assert w.library.table.rowCount()>0
    w.library.table.selectRow(0);w.library.rating.setValue(5);w.library.save_rating();wait(w)
    assert w.library.store().summary()['ratings']==1
    w.open_path(FIXTURE);wait(w);w.start_variations();wait(w)
    assert len(w.variants)==3 and w.export_button.isEnabled()
    w.variant_choice.setCurrentIndex(2)
    assert w.report['variant']=='Melodic Technical'
    w.export_to(tmp_path/'variant');wait(w)
    assert (tmp_path/'variant'/'notes.mid').exists()
    w.close()

def test_audio_gui_analyze_draft_compare_export(tmp_path,app):
    import numpy as np
    import soundfile as sf
    sr=22050;samples=np.zeros(sr*5,dtype=np.float32)
    for start in np.arange(.5,4,.5):
        t=np.arange(2205)/sr;samples[int(start*sr):int(start*sr)+len(t)]=.6*np.sin(2*np.pi*440*t)*np.exp(-t*30)
    path=tmp_path/'study.wav';sf.write(path,samples,sr)
    w=Window();w.audio.open_path(path);wait(w)
    assert len(w.audio.analysis.onsets)==7 and w.audio.draft_button.isEnabled()
    assert len(w.audio.wave.scene().items())>100
    w.audio.create_draft();wait(w)
    assert w.report['audio']['sha256'] and w.export_button.isEnabled()
    w.audio.compare();wait(w)
    assert w.audio.last_diagnostics['median_abs_error_ms']<1
    w.export_to(tmp_path/'audio-result');wait(w)
    assert (tmp_path/'audio-result'/'notes.mid').exists()
    w.audio.sensitivity.setValue(5)
    assert w.audio.analysis is None and not w.audio.draft_button.isEnabled()
    w.close()

def test_audio_settings_restore(tmp_path,app,monkeypatch):
    import json
    from PySide6.QtWidgets import QFileDialog
    config={'audio_analysis':{'sensitivity':5,'min_interval_ms':90,'manual_bpm':137.5},'shift_ms':125,'use_authored_tempo_map':False,'use_learned_patterns':True,'seed':77}
    path=tmp_path/'audio-settings.json';path.write_text(json.dumps(config))
    monkeypatch.setattr(QFileDialog,'getOpenFileName',lambda *args,**kwargs:(str(path),'JSON'))
    w=Window();w.load_config()
    assert w.audio.sensitivity.value()==5 and w.audio.spacing.value()==90 and w.audio.bpm.value()==137.5
    assert w.audio.shift.value()==125 and not w.audio.template.isChecked() and w.audio.learned.isChecked() and w.seed.value()==77
    w.report={'audio':{},'settings':config}
    destination=tmp_path/'saved.json';monkeypatch.setattr(QFileDialog,'getSaveFileName',lambda *args,**kwargs:(str(destination),'JSON'))
    w.save_config();assert json.loads(destination.read_text())==config
    w.close()


@pytest.fixture(autouse=True)
def dispose_closed_windows_on_gui_thread(app):
    # Closing alone need not dispose native Qt objects. Flush deferred deletion
    # before another test starts an allocation-heavy worker.
    yield
    import gc
    from PySide6.QtCore import QCoreApplication,QEvent
    for widget in QApplication.topLevelWidgets():
        if isinstance(widget,Window) and widget.busy(): wait(widget)
        widget.close();widget.deleteLater()
    QCoreApplication.sendPostedEvents(None,QEvent.DeferredDelete)
    app.processEvents();gc.collect()
    QCoreApplication.sendPostedEvents(None,QEvent.DeferredDelete)


def test_cleanup_dialog_review_cancel_and_apply(tmp_path,app):
    from gh3studio.cleanup_gui import CleanupDialog
    from gh3studio.model import Song,Note
    song=Song(tracks={'Expert':[Note(0,0,300),Note(192,0)]},modifiers={'Expert':[(0,'N 6')]})
    dialog=CleanupDialog(song)
    assert not dialog.apply_button.isEnabled()
    dialog.trim.setChecked(True)
    assert dialog.apply_button.isEnabled() and len(dialog.report['changes'])==2
    assert song.modifiers and song.tracks['Expert'][0].length==300
    dialog.reject();dialog.close()


def test_playback_shift_preview_apply_undo_redo_export(tmp_path,app):
    w=Window();w.open_path(FIXTURE);wait(w);w.start_convert();wait(w)
    original=w.converted;notes=list(original.tracks['Medium'])
    panel=w.playback;panel.shift.setValue(100)
    assert w.converted is original and panel.highway.shift==.1
    panel.apply_shift()
    assert w.converted is not original and w.converted.tracks['Medium']!=notes
    assert w.report['timing_edits_ms']==[100] and panel.undo_button.isEnabled()
    changed=w.converted
    panel.undo();assert w.converted is original and w.converted.tracks['Medium']==notes
    panel.redo();assert w.converted is changed
    w.export_to(tmp_path/'timing-output');wait(w)
    assert (tmp_path/'timing-output'/'notes.mid').exists()
    w.close()


def test_audio_only_variations_without_authored_chart(tmp_path,app):
    w=Window();w.library.db_path.setText(str(tmp_path/'corpus.sqlite3'))
    w.library.scan(FIXTURE.parent);wait(w)
    path=FIXTURE.parent/'audio'/'onset-study.wav'
    w.audio.open_path(path);wait(w)
    assert w.song is None and not w.audio.template.isChecked()
    w.audio.create_draft();wait(w)
    assert w.converted and w.report['audio']
    w.start_variations();wait(w)
    assert len(w.variants)==3
    w.close()


def test_real_media_playback_pause_and_seek(app):
    from PySide6.QtMultimedia import QMediaPlayer
    w=Window();panel=w.playback;panel.output.setMuted(True)
    panel.open_audio(FIXTURE.parent/'audio'/'onset-study.wav')
    for _ in range(200):
        QApplication.processEvents();QTest.qWait(10)
        if panel.player.duration():break
    assert panel.player.duration()==9000 and panel.player.hasAudio()
    panel.toggle()
    for _ in range(200):
        QApplication.processEvents();QTest.qWait(10)
        if panel.player.position()>100:break
    assert panel.player.position()>100 and panel.player.error()==QMediaPlayer.NoError
    panel.toggle();assert panel.player.playbackState()==QMediaPlayer.PausedState
    panel.player.setPosition(2500);QApplication.processEvents()
    assert panel.player.position()==2500
    panel.stop();assert panel.player.position()==0 and panel.player.playbackState()==QMediaPlayer.PausedState
    panel.player.setPosition(2500);w.close()
