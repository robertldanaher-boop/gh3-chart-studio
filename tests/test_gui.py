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
    assert audio.onsets.rowCount()==15 and 'step 2' in audio.next_step.text().lower()
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


@pytest.mark.parametrize('large_text',[False,True])
def test_guided_footer_visible_at_small_window(app,large_text):
    w=Window()
    if large_text:w.setStyleSheet(w.styleSheet()+'\nQWidget {font-size:18px;}')
    w.resize(1024,700);w.show();w.tabs.setCurrentWidget(w.audio);QApplication.processEvents()
    assert w.width()<=1024 and w.height()<=700, w.layout_report()
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
    dialog=SongExportDialog(w.converted,str(audio),w,conversion_report=w.report)
    assert dialog.markers.isHidden()
    # 0.18.5: the source tap becomes TheGHOST forced-note flips; nothing else survives.
    assert all(m=='N 5 0' for markers in w.converted.modifiers.values() for _,m in markers)
    assert w.song.modifiers.get('Expert')
    assert dialog.buttons.button(QDialogButtonBox.Save).isEnabled()
    w.export_song_to(tmp_path/'out',audio,dialog.prepared,dict(w.report,medium_export_cleanup=dialog.review));wait(w)
    assert read_chart(tmp_path/'out'/'notes.chart').tracks['Expert']==song.tracks['Expert']
    assert (tmp_path/'out'/'song.ogg').is_file()
    assert Path(w.playback.player.source().toLocalFile()).resolve()==audio.resolve()
    dialog.close();w.close()


def test_failed_orange_copy_disables_stale_export(app):
    from gh3studio.model import Song,Note
    w=Window();w.song=Song(tracks={'Expert':[],'Medium':[Note(0,1)]})
    w.converted=w.song;w.report={'source_difficulty':'Hard'};w.refresh_preview()
    w.playback.remove_orange(source=(w.song,'Expert'));wait(w)
    assert w.converted is None and not w.audio.export_button.isEnabled()
    assert 'empty' in w.playback.status.text()
    assert 'OUTPUT' not in w.playback.provenance.text()
    w.close()


def test_preview_play_without_audio_prompts_and_starts(app,monkeypatch):
    from PySide6.QtWidgets import QFileDialog
    from PySide6.QtMultimedia import QMediaPlayer
    path=FIXTURE.parent/'audio'/'onset-study.wav'
    monkeypatch.setattr(QFileDialog,'getOpenFileName',lambda *a,**k:(str(path),''))
    w=Window();w.playback.toggle()
    for _ in range(200):
        QApplication.processEvents();QTest.qWait(10)
        if w.playback.player.position()>100:break
    assert Path(w.playback.player.source().toLocalFile()).resolve()==path.resolve()
    assert w.playback.player.position()>100
    assert w.playback.player.playbackState()==QMediaPlayer.PlayingState
    assert w.playback.play_button.text()=='Pause preview audio'
    w.close()


def test_chart_autoloads_recording_and_missing_audio_clears_source(tmp_path,app):
    import shutil
    from gh3studio.chartio import write_chart
    from gh3studio.model import Song,Note
    folder=tmp_path/'song';folder.mkdir();chart=folder/'notes.chart'
    write_chart(Song(tracks={'Expert':[Note(0,0)]}),chart)
    shutil.copyfile(FIXTURE.parent/'audio'/'onset-study.wav',folder/'song.wav')
    w=Window();w.open_path(chart);wait(w)
    assert Path(w.playback.player.source().toLocalFile()).resolve()==(folder/'song.wav').resolve()
    assert w.playback.devices.count()>=1
    assert not w.playback.open_audio(folder/'missing.wav')
    assert w.playback.player.source().isEmpty() and 'not found' in w.playback.label.text()
    w.close()


def test_cancel_preview_file_picker_does_not_play(app,monkeypatch):
    from PySide6.QtWidgets import QFileDialog
    from PySide6.QtMultimedia import QMediaPlayer
    monkeypatch.setattr(QFileDialog,'getOpenFileName',lambda *a,**k:('',''))
    w=Window();w.playback.toggle()
    assert w.playback.player.source().isEmpty()
    assert w.playback.player.playbackState()==QMediaPlayer.StoppedState
    w.close()


def test_export_audio_path_changes_do_not_repeat_chart_cleanup(app,monkeypatch):
    from gh3studio.model import Song,Note
    import gh3studio.song_export_gui as module
    from PySide6.QtWidgets import QDialogButtonBox
    original=module.prepare_medium;calls=[]
    def tracked(*args,**kwargs):
        calls.append(1);return original(*args,**kwargs)
    monkeypatch.setattr(module,'prepare_medium',tracked)
    dialog=module.SongExportDialog(Song(tracks={'Medium':[Note(0,0)]}))
    assert len(calls)==1
    dialog.audio.setText(str(FIXTURE.parent/'audio'/'onset-study.wav'))
    assert len(calls)==1 and dialog.buttons.button(QDialogButtonBox.Save).isEnabled()
    dialog.audio.setText('')
    assert len(calls)==1 and not dialog.buttons.button(QDialogButtonBox.Save).isEnabled()
    dialog.close()


def test_export_identity_and_hopo_review_preserve_original(app,tmp_path):
    from gh3studio.model import Song,Note
    from gh3studio.song_export_gui import SongExportDialog
    from PySide6.QtWidgets import QDialogButtonBox
    song=Song(metadata={'Name':'Original','Artist':'Artist'},tracks={'Medium':[Note(0,0),Note(96,1)]})
    dialog=SongExportDialog(song,str(FIXTURE.parent/'audio'/'onset-study.wav'))
    dialog.identity_fields['Name'].setText('Reviewed title')
    dialog.hopo.setChecked(True)
    assert dialog.prepared.metadata['Name']=='Reviewed title' and song.metadata['Name']=='Original'
    assert dialog.prepared.modifiers['Medium']==[(96,'N 5 0')]
    assert dialog.review['hopo_assistance']['estimated_hopo_events']==1
    assert dialog.buttons.button(QDialogButtonBox.Save).isEnabled()
    dialog.show();QApplication.processEvents()
    assert dialog.buttons.isVisible() and dialog.buttons.visibleRegion().boundingRect().height()>0
    dialog.close()


def test_guided_start_cancel_keeps_current_song(app,monkeypatch):
    from PySide6.QtWidgets import QFileDialog
    w=Window();assert w.tabs.currentWidget() is w.welcome
    w.open_path(FIXTURE);wait(w);original=w.song
    monkeypatch.setattr(QFileDialog,'getOpenFileName',lambda *a,**k:('',''))
    assert not w.start_guided('audio')
    assert w.song is original and w.goal is None
    w.close()


def test_guided_orange_hard_path_and_next_step(tmp_path,app):
    from gh3studio.model import Song,Note
    from gh3studio.chartio import write_chart
    song=Song(tracks={'Expert':[Note(0,0),Note(96,4)],'Hard':[Note(0,2),Note(192,4),Note(384,3)],'Medium':[Note(0,1)]})
    chart=tmp_path/'notes.chart';write_chart(song,chart)
    w=Window();assert w.start_guided('orange',chart);wait(w)
    assert w.tabs.currentWidget() is w.adapt
    assert 'Choose Expert or Hard' in w.adapt.next_step.text()
    w.adapt.source.setCurrentText('Hard');w.adapt.create_button.click();wait(w)
    assert w.converted.tracks['Medium']==[Note(0,2),Note(384,3)]
    assert 'Compare tracks' in w.adapt.next_step.text()
    assert w.converted.tracks['Expert']==song.tracks['Expert']
    w.close()


def test_guided_audio_starts_without_old_chart_template(app):
    w=Window();w.open_path(FIXTURE);wait(w);w.audio.template.setChecked(True)
    assert w.start_guided('audio',FIXTURE.parent/'audio'/'onset-study.wav');wait(w)
    assert w.song is None and w.original_song is None and not w.audio.template.isChecked()
    assert w.tabs.currentWidget() is w.audio and w.audio.pages.currentWidget() is w.audio.analysis_page
    w.audio.create_draft();wait(w)
    assert w.converted is not None and w.audio.pages.currentWidget() is w.playback
    w.close()


def test_guided_refinement_and_export_completion(tmp_path,app):
    w=Window();w.start_guided('refine',FIXTURE);wait(w)
    assert w.tabs.currentWidget() is w.converter
    w.start_convert();wait(w)
    w.export_song_to(tmp_path/'out',FIXTURE.parent/'audio'/'onset-study.wav');wait(w)
    assert w.last_export_path==tmp_path/'out'
    assert 'EXPORT COMPLETE' in w.audio.next_step.text() and not w.audio.open_export_button.isHidden()
    w.invalidate()
    assert w.last_export_path is None and w.audio.open_export_button.isHidden()
    w.close()


def test_orange_sustain_transfer_checkbox(tmp_path,app):
    from gh3studio.model import Song,Note
    from gh3studio.chartio import write_chart
    path=tmp_path/'notes.chart'
    write_chart(Song(tracks={'Expert':[Note(0,4,96),Note(192,0)],'Hard':[Note(0,1)]}),path)
    w=Window();w.open_path(path);wait(w)
    w.playback.difficulty.setCurrentText('Expert')
    w.playback.orange_sustains.setChecked(True)
    w.playback.remove_orange();wait(w)
    assert w.converted.tracks['Medium']==[Note(0,3,96),Note(192,0)]
    assert 'sustains → four frets' in w.playback.provenance.text()
    w.playback.regenerate_sustains.click();wait(w)
    assert w.report['transferred_orange_sustains']==1
    assert w.report['source_difficulty']=='Expert'
    assert w.report['sustain_seed']==1
    assert len(w.converted.tracks['Medium'])==2
    assert w.converted.tracks['Expert']==w.song.tracks['Expert']
    w.close()


def test_clean_goal_reviews_and_exports_folder(tmp_path,app):
    from test_cleaner import fixture
    source=tmp_path/'songs';fixture(source/'one')
    w=Window();assert w.start_guided('clean',str(source));wait(w)
    assert w.tabs.currentWidget() is w.cleaner
    assert len(w.cleaner.rows)==1 and not w.cleaner.rows[0]['errors']
    assert w.cleaner.table.item(0,0).checkState()==Qt.Checked
    output=tmp_path/'cleaned'
    w.cleaner.export_to(output);assert not output.exists()
    w.cleaner.approve.setChecked(True);w.cleaner.export_to(output);wait(w)
    assert (output/'cleanup_summary.json').exists()
    assert w.cleaner.last_output==output
    assert not w.cleaner.approve.isChecked()
    w.close()


def test_folder_drop_in_clean_only_routes_to_cleaner(tmp_path,app):
    from test_cleaner import fixture
    source=tmp_path/'songs';fixture(source/'one')
    w=Window();w.show();w.enter_workspace('clean');mime=QMimeData();mime.setUrls([QUrl.fromLocalFile(str(source))])
    event=QDropEvent(QPointF(10,10),Qt.CopyAction,mime,Qt.LeftButton,Qt.NoModifier)
    w.dropEvent(event);wait(w)
    assert w.tabs.currentWidget() is w.cleaner
    assert len(w.cleaner.rows)==1
    w.resize(1024,700);app.processEvents()
    assert w.cleaner.export_button.visibleRegion().boundingRect().height()>0
    w.close()


def test_wide_hidden_library_controls_scroll_instead_of_widening_window(app):
    from PySide6.QtWidgets import QScrollArea
    w=Window()
    w.library.similar_button.setText('Find matches with unusually wide Windows font metrics ' * 5)
    w.resize(1024,700);w.show();w.tabs.setCurrentWidget(w.audio);app.processEvents()
    assert w.width()<=1024, w.layout_report()
    w.tabs.setCurrentWidget(w.library);app.processEvents()
    scroll=w.library.findChild(QScrollArea)
    assert scroll.horizontalScrollBar().maximum()>0
    assert w.width()<=1024, w.layout_report()
    w.close()


def test_cleaner_metadata_dialog_retains_edits_on_invalid_chart(tmp_path,app,monkeypatch):
    from test_cleaner import fixture
    from PySide6.QtWidgets import QDialog,QLineEdit
    source=tmp_path/'songs';path=fixture(source/'one')
    path.write_text('invalid chart syntax',encoding='utf-8')
    w=Window();w.start_guided('clean',str(source));wait(w)
    assert w.cleaner.rows[0]['errors']
    def edit(dialog):
        fields=dialog.findChildren(QLineEdit)
        fields[0].setText('Corrected † title');fields[1].setText('Correct artist');fields[2].setText('Album')
        return QDialog.Accepted
    monkeypatch.setattr(QDialog,'exec',edit)
    w.cleaner.edit_metadata();wait(w)
    assert w.cleaner.table.item(0,1).text()=='Corrected † title'
    assert 'Name: Corrected † title' in w.cleaner.details.toPlainText()
    assert 'still needs correction' in w.cleaner.status.text()
    def reopen(dialog):
        fields=dialog.findChildren(QLineEdit)
        assert [e.text() for e in fields[:3]]==['Corrected † title','Correct artist','Album']
        return QDialog.Rejected
    monkeypatch.setattr(QDialog,'exec',reopen)
    w.cleaner.edit_metadata()
    assert path.read_text(encoding='utf-8')=='invalid chart syntax'
    w.close()


def test_cleaner_bulk_selection_and_visible_start(tmp_path,app,monkeypatch):
    from test_cleaner import fixture
    from PySide6.QtWidgets import QFileDialog
    source=tmp_path/'songs';fixture(source/'one');fixture(source/'two')
    bad=fixture(source/'bad');bad.write_text('broken',encoding='utf-8')
    w=Window();w.resize(1024,700);w.show();w.start_guided('clean',str(source));wait(w)
    panel=w.cleaner
    panel.select_none.click()
    assert all(panel.table.item(i,0).checkState()==Qt.Unchecked for i in range(3))
    panel.select_ready.click()
    assert sum(panel.table.item(i,0).checkState()==Qt.Checked for i in range(3))==2
    assert '2 checked' in panel.selection_summary.text()
    assert panel.export_button.visibleRegion().boundingRect().height()>0
    assert not panel.open_output.isEnabled()
    panel.approve.setChecked(True)
    def unexpected_picker(*args,**kwargs):raise AssertionError('Start must not open a folder picker')
    monkeypatch.setattr(QFileDialog,'getExistingDirectory',unexpected_picker)
    panel.export_button.click();wait(w)
    assert panel.last_output is not None and panel.open_output.isEnabled()
    w.close()


def test_cleaner_select_all_reports_blocked_and_exports_valid(tmp_path,app,monkeypatch):
    from test_cleaner import fixture
    import json
    source=tmp_path/'songs';fixture(source/'good')
    bad=fixture(source/'bad');bad.write_text('broken',encoding='utf-8')
    w=Window();w.cleaner.scan(source);wait(w);panel=w.cleaner
    panel.select_all.click()
    assert all(panel.table.item(i,0).checkState()==Qt.Checked for i in range(2))
    assert '2 checked of 2' in panel.selection_summary.text()
    assert '1 blocked' in panel.selection_summary.text()
    assert any('BLOCKED:' in panel.table.item(i,3).text() for i in range(2))
    panel.approve.setChecked(True);panel.output_path.setText(str(source))
    panel.export_button.click()
    assert not w.busy() and 'Cannot start' in panel.status.text()
    panel.output_path.setText(str(tmp_path/'output'));panel.export_button.click();wait(w)
    results=json.loads((panel.last_output/'cleanup_summary.json').read_text(encoding='utf-8'))['results']
    assert sorted(r['status'] for r in results)==['exported','failed']
    assert next(r['error'] for r in results if r['status']=='failed')=='; '.join(next(r['errors'] for r in panel.rows if r['errors']))
    assert '1 exported, 1 failed' in panel.status.text()
    log=(panel.last_output/'cleanup.log').read_text(encoding='utf-8')
    assert 'START |' in log and 'EXPORTED |' in log and 'FAILED |' in log and 'FINISHED |' in log
    from PySide6.QtWidgets import QFileDialog
    report=tmp_path/'scan.txt'
    monkeypatch.setattr(QFileDialog,'getSaveFileName',lambda *a,**kw:(str(report),'Text (*.txt)'))
    panel.save_report.click()
    assert 'ERROR:' in report.read_text(encoding='utf-8') and 'READY' in report.read_text(encoding='utf-8')
    w.close()
