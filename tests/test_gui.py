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


def test_guided_audio_review_excludes_attack_and_stays_in_workspace(tmp_path,app):
    w=Window();w.show();audio=w.audio;w.tabs.setCurrentWidget(audio)
    audio.open_path(FIXTURE.parent/'audio'/'onset-study.wav');wait(w)
    assert w.tabs.currentWidget() is audio and audio.pages.currentWidget() is audio.analysis_page
    assert audio.onsets.rowCount()==15 and 'Step 2' in audio.next_step.text()
    excluded=audio.analysis.onsets[0]['time']
    audio.onsets.setData(audio.onsets.index(0,0),Qt.Unchecked,Qt.CheckStateRole)
    audio.create_draft();wait(w)
    assert w.tabs.currentWidget() is audio and audio.pages.currentWidget() is w.playback
    assert len(w.converted.tracks['Medium'])==14 and audio.export_button.isEnabled()
    assert w.report['attack_review']['excluded_times_seconds']==[excluded]
    assert all(abs(w.converted.seconds(n.tick)-excluded)>.001 for n in w.converted.tracks['Medium'])
    w.export_to(tmp_path/'reviewed');wait(w)
    assert (tmp_path/'reviewed'/'notes.mid').exists()
    audio.show_analysis();audio.onsets.select_all(False)
    assert not audio.draft_button.isEnabled() and w.converted is None and not audio.export_button.isEnabled()
    w.close()


def test_external_stem_analyzed_original_mix_retained(tmp_path,app):
    import shutil
    original=FIXTURE.parent/'audio'/'onset-study.wav';stem=tmp_path/'guitar.wav';shutil.copyfile(original,stem)
    w=Window();w.audio.open_path(original);wait(w)
    w.audio.open_stem(stem);wait(w)
    assert w.audio.analysis.source_path==str(stem.resolve())
    # Qt returns forward slashes on Windows; compare filesystem paths, not text.
    assert Path(w.playback.player.source().toLocalFile()).resolve()==original.resolve()
    w.audio.create_draft();wait(w)
    assert w.report['audio']['external_stem'] is True
    assert w.report['audio']['listening_path']==str(original)
    w.audio.restore_mix();wait(w)
    assert w.audio.path==original and not w.audio.mix_button.isEnabled()
    w.close()


def test_horizontal_preview_time_and_lane_geometry(app):
    w=Window();view=w.playback.highway;view.resize(900,300)
    view.notes=[(1,2,0,False),(1,1,3,True),(2,2,0,False)]
    x,end,y=view.note_geometry(view.notes[0]);x2,_,y2=view.note_geometry(view.notes[1])
    assert x==x2 and y<y2 and end>x
    assert view.note_geometry(view.notes[2])[0]>x
    view.position=1
    assert view.note_geometry(view.notes[0])[0]==90
    view.shift=.1
    assert view.note_geometry(view.notes[0])[0]>90
    w.close()


def test_guided_footer_visible_at_small_window(app):
    w=Window();w.resize(1024,700);w.show();w.tabs.setCurrentWidget(w.audio);QApplication.processEvents()
    assert w.audio.draft_button.isVisible()
    assert w.audio.draft_button.visibleRegion().boundingRect().height()>0
    assert not w.audio.advanced.isVisible()
    w.audio.advanced_toggle.setChecked(True);QApplication.processEvents()
    assert w.audio.template.isVisible() and w.audio.learned.isVisible()
    assert w.audio.draft_button.visibleRegion().boundingRect().height()>0
    w.close()


def test_new_audio_analysis_cannot_export_previous_chart(app):
    w=Window();w.open_path(FIXTURE);wait(w);w.start_convert();wait(w)
    source=w.song;assert w.converted is not None
    w.audio.open_path(FIXTURE.parent/'audio'/'onset-study.wav');wait(w)
    assert w.song is source  # Still available as an optional tempo-map template.
    assert w.converted is None and not w.audio.export_button.isEnabled()
    w.close()


def test_library_scan_populates_table_without_browse(tmp_path,app):
    import shutil
    root=tmp_path/'charts';root.mkdir();shutil.copyfile(FIXTURE,root/'study.chart')
    w=Window();w.library.db_path.setText(str(tmp_path/'library.sqlite3'))
    w.library.filter.setCurrentIndex(1);w.library.scan(root);wait(w)
    assert w.library.last_scan['imported']==1
    assert w.library.filter.currentIndex()==0 and w.library.table.rowCount()>0
    assert w.library.table.item(0,1).text()
    assert 'newest pattern rows' in w.library.summary.text()
    w.close()


def test_audio_difficulty_selection_orange_only_medium_export(tmp_path,app):
    from gh3studio.chartio import write_chart,read_chart
    from gh3studio.model import Song,Note
    source=Song(tracks={'Expert':[Note(0,0,48),Note(0,4,48),Note(96,4),Note(192,3)],
                       'Hard':[Note(0,1),Note(192,4)],'Easy':[Note(0,0)]})
    path=tmp_path/'source.chart';write_chart(source,path)
    w=Window();w.open_path(path);wait(w);w.audio.show_listen()
    panel=w.playback;panel.difficulty.setCurrentText('Hard')
    assert panel.current[1]=='Hard' and len(panel.highway.notes)==2
    panel.difficulty.setCurrentText('Expert');panel.remove_orange();wait(w)
    assert w.converted.tracks['Medium']==[Note(0,0,48),Note(192,3)]
    assert w.converted.tracks['Expert']==source.tracks['Expert'] and w.song.tracks==source.tracks
    assert panel.difficulty.currentText()=='Medium' and w.audio.export_button.isEnabled()
    panel.difficulty.setCurrentText('Expert');assert len(panel.highway.notes)==4
    w.export_to(tmp_path/'out');wait(w)
    result=read_chart(tmp_path/'out'/'notes.chart')
    assert result.tracks['Hard']==source.tracks['Hard'] and result.tracks['Expert']==source.tracks['Expert']
    assert read_chart(path).tracks==source.tracks
    w.close()


def test_marked_display_copy_replaces_old_medium_and_folder_export(tmp_path,app):
    from gh3studio.chartio import write_chart,read_chart
    from gh3studio.model import Song,Note
    from gh3studio.song_export_gui import SongExportDialog
    from PySide6.QtWidgets import QDialogButtonBox
    song=Song(tracks={'Expert':[Note(0,1),Note(96,4),Note(192,3)],'Hard':[Note(0,2)],'Medium':[Note(0,0)]},modifiers={'Expert':[(0,'N 6 0')]})
    path=tmp_path/'source.chart';write_chart(song,path)
    w=Window();w.open_path(path);wait(w);w.playback.remove_orange();wait(w)
    assert w.converted.tracks['Medium']==[Note(0,1),Note(192,3)]
    assert 'OUTPUT copied from Expert' in w.playback.provenance.text()
    w.playback.difficulty.setCurrentText('Expert');w.playback.difficulty.setCurrentText('Medium')
    assert [n[2] for n in w.playback.highway.notes]==[1,3]
    audio=FIXTURE.parent/'audio'/'onset-study.wav'
    dialog=SongExportDialog(w.converted,str(audio),w)
    assert not dialog.buttons.button(QDialogButtonBox.Save).isEnabled()
    dialog.markers.setChecked(True)
    assert dialog.buttons.button(QDialogButtonBox.Save).isEnabled()
    w.export_song_to(tmp_path/'out',audio,dialog.prepared,dict(w.report,medium_export_cleanup=dialog.review));wait(w)
    assert read_chart(tmp_path/'out'/'notes.chart').tracks['Expert']==song.tracks['Expert']
    assert (tmp_path/'out'/'song.wav').is_file()
    dialog.close();w.close()


def test_failed_orange_copy_disables_stale_export(app):
    from gh3studio.model import Song,Note
    w=Window();w.song=Song(tracks={'Expert':[Note(0,4)],'Medium':[Note(0,1)]})
    w.converted=w.song;w.report={'source_difficulty':'Hard'};w.refresh_preview()
    w.playback.difficulty.setCurrentText('Expert');w.playback.remove_orange();wait(w)
    assert w.converted is None and not w.audio.export_button.isEnabled()
    assert 'empty' in w.playback.status.text()
    assert 'OUTPUT' not in w.playback.provenance.text()
    w.close()
