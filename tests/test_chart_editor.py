from copy import deepcopy
from fractions import Fraction
import pytest
from gh3studio.model import Song, Note, ChartError
from gh3studio.chart_editor import EditSession
from gh3studio.hopo import effective_states


def song():
    return Song(tempos=[(0,Fraction(500000)),(768,Fraction(400000))],tracks={'Expert':[Note(0,0),Note(192,1),Note(384,2)],'Medium':[Note(0,0),Note(192,1),Note(384,2)]})


def test_edits_undo_and_immutable_source():
    source=song();before=deepcopy(source);s=EditSession(source)
    s.change('Expert','move',note=Note(192,1),tick=240,lane=3)
    s.change('Expert','resize',note=Note(240,3),length=96)
    assert Note(240,3,96) in s.song.tracks['Expert']
    assert source==before and s.song.tempos==source.tempos
    assert s.song.tracks['Medium']==source.tracks['Medium']
    final=deepcopy(s.song);s.undo();s.undo();assert s.song==source
    s.redo();s.redo();assert s.song==final


def test_medium_rejects_orange_and_conflicts_transactionally():
    s=EditSession(song());before=deepcopy(s.song)
    for args in [dict(action='add',tick=96,lane=4),dict(action='add',tick=0,lane=0),dict(action='resize',note=Note(0,0),length=300),dict(action='pattern',tick=576,lanes=[0,4])]:
        with pytest.raises(ChartError):s.change('Medium',**args)
        assert s.song==before and not s.undo_stack


def test_chord_sustain_star_pattern_hopo():
    s=EditSession(song());s.change('Medium','add',tick=192,lane=3)
    s.change('Medium','resize',note=Note(192,1),length=96)
    assert {n.length for n in s.song.tracks['Medium'] if n.tick==192}=={96}
    s.change('Medium','star',tick=0,length=768)
    with pytest.raises(ChartError):s.change('Medium','star',tick=384,length=768)
    s.change('Medium','pattern',tick=768,lanes=[3,2,3],step=48)
    s.change('Medium','hopo',tick=768)
    assert effective_states(s.song,'Medium')[768]
    s.change('Medium','strum',tick=816)
    assert not effective_states(s.song,'Medium')[816]
    s.change('Medium','delete',note=Note(768,3))
    assert not any(t==768 for t,_ in s.song.modifiers['Medium'])


def test_editor_export_all_difficulties_roundtrip(tmp_path):
    import soundfile as sf
    import numpy as np
    from gh3studio.song_export import export_song_folder
    from gh3studio.chartio import read_chart
    s=EditSession(song());s.change('Expert','hopo',tick=192);s.change('Expert','star',tick=0,length=384)
    audio=tmp_path/'source.wav';sf.write(audio,np.zeros((48000,2)),48000)
    out=tmp_path/'edited';export_song_folder(s.song,{},out,audio,editor_all=True)
    read=read_chart(out/'notes.chart')
    assert read.tracks==s.song.tracks and read.phrases['Expert']==s.song.phrases['Expert']
    assert read.modifiers['Expert']==s.song.modifiers['Expert']
    assert (out/'song.ogg').exists() and (out/'song.ini').exists()
    # Expert-only editing must not invent Medium.
    s.song.tracks.pop('Medium');export_song_folder(s.song,{},tmp_path/'expert',audio,editor_all=True)
    assert 'Medium' not in read_chart(tmp_path/'expert'/'notes.chart').tracks


def test_gui_drag_and_difficulty(tmp_path):
    from PySide6.QtCore import Qt,QPoint
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication
    from gh3studio.gui import Window
    from gh3studio.editor_gui import ChartEditorDialog
    app=QApplication.instance() or QApplication([])
    w=Window();w.song=song();w.playback.set_chart(w.song,'Expert')
    dialog=ChartEditorDialog(w.playback);dialog.show();app.processEvents()
    view=dialog.view
    x,_,y=view.note_geometry((.5,.5,1,False));target,_,ty=view.note_geometry((.625,.625,3,False))
    QTest.mousePress(view,Qt.LeftButton,pos=QPoint(round(x),round(y)))
    QTest.mouseRelease(view,Qt.LeftButton,pos=QPoint(round(target),round(ty)))
    assert Note(240,3) in dialog.session.song.tracks['Expert']
    dialog.edit('resize',note=Note(240,3),length=48)
    _,tail,y=view.note_geometry((.625,.75,3,False));end,_,_=view.note_geometry((.875,.875,3,False))
    QTest.mousePress(view,Qt.LeftButton,pos=QPoint(round(tail),round(y)))
    QTest.mouseRelease(view,Qt.LeftButton,pos=QPoint(round(end),round(y)))
    assert Note(240,3,96) in dialog.session.song.tracks['Expert']
    dialog.difficulty.setCurrentText('Medium');assert view.lane_count()==4
    dialog.edit('add',tick=576,lane=4);assert 'not applied' in dialog.status.text()
    dialog.exported=True;dialog.reject();w.close();app.processEvents()
