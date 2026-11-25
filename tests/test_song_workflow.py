"""Acceptance for preservation, explicit adaptation and the shared song workspace."""
import copy
import json
from pathlib import Path
import numpy as np
import pytest
import soundfile as sf
from PySide6.QtCore import Qt
from gh3studio.chartio import write_chart,read_chart
from gh3studio.model import Song,Note,ChartError
from gh3studio.cleaner import inspect_chart,export_cleaned
from gh3studio.gui import Window
from gh3studio.review_gui import SongReviewDialog
from test_gui import app,wait


def song_folder(tmp_path,tracks=None):
    folder=tmp_path/'source';folder.mkdir()
    song=Song(metadata={'Name':'A song','Artist':'An artist'},tracks=tracks or {
        'Expert':[Note(0,0),Note(96,4),Note(192,2,48),Note(384,3)],
        'Hard':[Note(0,1),Note(192,2)],'Easy':[Note(48,0,48)],'Medium':[Note(48,1)]})
    write_chart(song,folder/'notes.chart')
    sf.write(folder/'song.wav',np.zeros(22050),44100)
    return folder/'notes.chart',song


def options(**overrides):
    return dict(medium_source='Expert',preserve_sustains=False,create_easy=False,
        fill_missing=False,repair_others=False,repair_sustains=False,
        repair_medium_orange=False,allow_empty_fallback=False,**overrides)


def test_adapt_preserves_authored_easy_and_hard_and_exports_summary(tmp_path):
    path,original=song_folder(tmp_path)
    row=inspect_chart(path,**options())
    assert not row['errors'],row['errors']
    for diff in ('Easy','Hard','Expert'):
        assert row['song'].tracks[diff]==original.tracks[diff]
    assert row['song'].tracks['Medium']==[n for n in original.tracks['Expert'] if n.lane<4]
    assert 'Easy: unchanged (1 → 1 gems)' in row['summary']
    output=export_cleaned([row],tmp_path/'out',path.parent)
    assert output[0]['status']=='exported',output
    folder=Path(output[0]['folder']);reopened=read_chart(folder/'notes.chart')
    assert all(n.lane<4 for n in reopened.tracks['Medium'])
    assert reopened.tracks['Easy']==original.tracks['Easy']
    assert json.loads((folder/'validation.json').read_text())['difficulty_summary']==row['summary']
    assert read_chart(path).tracks==original.tracks


def test_missing_tracks_stay_missing_unless_explicitly_requested(tmp_path):
    path,original=song_folder(tmp_path,{'Expert':[Note(0,0),Note(192,2)]})
    row=inspect_chart(path,**options())
    assert not row['errors']
    assert set(row['song'].tracks)=={'Expert','Medium'}
    opts=options();opts.update(create_easy=True,fill_missing=True)
    full=inspect_chart(path,**opts)
    assert not full['errors']
    assert all(full['song'].tracks[d] for d in ('Easy','Medium','Hard','Expert'))
    assert all(n.lane<3 for n in full['song'].tracks['Easy'])


def test_unapproved_sustain_repairs_block_instead_of_changing_source_tracks(tmp_path):
    path,_=song_folder(tmp_path,{'Expert':[Note(0,0,300),Note(96,1)]})
    row=inspect_chart(path,repair_sustains=False)
    assert row['errors'] and row['song'] is None
    approved=inspect_chart(path,repair_sustains=True)
    assert not approved['errors']
    assert approved['song'].tracks['Expert'][0].length==96
    assert read_chart(path).tracks['Expert'][0].length==300


def test_remove_orange_only_does_not_invent_notes_when_medium_would_be_empty(tmp_path):
    path,_=song_folder(tmp_path,{'Expert':[Note(0,4),Note(192,4)]})
    row=inspect_chart(path,**options())
    assert any('leave Medium empty' in e for e in row['errors'])
    assert row['song'] is None


def test_existing_medium_orange_requires_explicit_repair(tmp_path):
    path,_=song_folder(tmp_path,{'Medium':[Note(0,0),Note(96,4,48)]})
    row=inspect_chart(path,repair_medium_orange=False)
    assert any('Medium contains Orange' in e for e in row['errors'])
    approved=inspect_chart(path,repair_medium_orange=True,preserve_sustains=False)
    assert not approved['errors']
    assert approved['song'].tracks['Medium']==[Note(0,0)]


def test_both_goals_share_queue_and_check_only_cannot_export(tmp_path,app):
    path,_=song_folder(tmp_path)
    w=Window();w.show();w.welcome.actions['orange'].click()
    assert w.tabs.currentWidget() is w.cleaner
    panel=w.cleaner
    assert not any(c.isChecked() for c in (panel.create_easy,panel.fill_missing,panel.repair_others,panel.repair_sustains,panel.bulk_sustains))
    panel.scan(path);wait(w)
    assert len(panel.rows)==1 and not panel.rows[0]['errors']
    assert panel.rows[0]['conversion']['source_difficulty']=='Expert'
    panel.approve.setChecked(True)
    w.welcome.actions['clean'].click();wait(w)
    assert w.tabs.currentWidget() is panel and not panel.approve.isChecked()
    assert 'conversion' not in panel.rows[0]
    panel.goal_choice.setCurrentIndex(0);wait(w)
    assert not panel.export_button.isEnabled()
    panel.approve.setChecked(True);panel.export_to(tmp_path/'forbidden')
    assert not (tmp_path/'forbidden').exists()
    w.close()


def test_preview_edit_returns_to_same_queue_without_separate_export(tmp_path,app):
    path,_=song_folder(tmp_path)
    w=Window();w.cleaner.set_goal('orange');w.cleaner.scan(path);wait(w)
    row=w.cleaner.rows[0];before=copy.deepcopy(row['song'])
    dialog=SongReviewDialog(w.cleaner,row)
    assert dialog.panel.current[0] is row['song']
    assert w.converted is None and w.song is None  # independent of reserved converter
    edited=copy.deepcopy(row['song']);edited.tracks['Medium'].append(Note(576,1))
    w.cleaner.approve.setChecked(True)
    dialog.apply_edits(edited,[{'action':'add','tick':576}])
    assert row['song'].tracks['Medium'][-1]==Note(576,1)
    assert not w.cleaner.approve.isChecked()
    assert before.tracks['Medium']!=row['song'].tracks['Medium']
    forbidden=copy.deepcopy(edited);forbidden.tracks['Medium'].append(Note(768,4))
    with pytest.raises(ChartError,match='Orange'):dialog.apply_edits(forbidden,[])
    assert all(n.lane<4 for n in row['song'].tracks['Medium'])
    dialog.dispose();dialog.deleteLater();w.close()


@pytest.mark.parametrize('large_text',[False,True])
def test_shared_queue_footer_fits_small_window(app,large_text):
    w=Window()
    if large_text:w.setStyleSheet(w.styleSheet()+'\nQWidget {font-size:18px;}')
    w.resize(1024,700);w.show()
    for goal in ('clean','orange'):
        w.enter_workspace(goal);app.processEvents()
        assert w.width()<=1024 and w.height()<=700,w.layout_report()
        assert w.cleaner.export_button.visibleRegion().boundingRect()==w.cleaner.export_button.rect()
    w.close()


def test_prepared_preview_compensates_export_padding(tmp_path,app):
    path,_=song_folder(tmp_path)
    (path.parent/'song.ini').write_text('[song]\ndelay = -100\n')
    w=Window();w.cleaner.scan(path);wait(w)
    row=w.cleaner.rows[0]
    assert not row['errors']
    dialog=SongReviewDialog(w.cleaner,row)
    assert dialog.panel.highway.shift==-row['synchronization']['audio_padding_seconds']
    dialog.view.setCurrentIndex(0)
    assert dialog.panel.highway.shift==-.1
    dialog.dispose();dialog.deleteLater();w.close()


def test_optional_difficulty_filling_does_not_override_empty_medium_gate(tmp_path,app):
    path,_=song_folder(tmp_path,{'Expert':[Note(0,4),Note(192,4)]})
    w=Window();panel=w.cleaner;panel.set_goal('orange')
    panel.create_easy.setChecked(True);panel.fill_missing.setChecked(True)
    panel.scan(path);wait(w)
    assert any('leave Medium empty' in e for e in panel.rows[0]['errors'])
    assert panel.rows[0]['song'] is None
    w.close()


def test_scan_brings_song_review_into_view_at_small_size(tmp_path,app):
    path,_=song_folder(tmp_path)
    w=Window();w.resize(1024,700);w.show();w.enter_workspace('orange')
    w.cleaner.scan(path);wait(w)
    from PySide6.QtTest import QTest
    QTest.qWait(25);app.processEvents()
    assert w.cleaner.table.visibleRegion().boundingRect().height()>=125
    assert w.cleaner.export_button.visibleRegion().boundingRect()==w.cleaner.export_button.rect()
    w.close()


def test_repair_does_not_inherit_hidden_sustain_transfer_choice(tmp_path,app):
    path,_=song_folder(tmp_path,{'Expert':[Note(0,0),Note(192,2)],'Medium':[Note(0,0),Note(96,4,48)]})
    w=Window();panel=w.cleaner;panel.set_goal('orange');panel.bulk_sustains.setChecked(True)
    panel.set_goal('clean');panel.repair_orange.setChecked(True);panel.scan(path);wait(w)
    assert not panel.rows[0]['errors']
    assert panel.rows[0]['song'].tracks['Medium']==[Note(0,0)]
    w.close()
