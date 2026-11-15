import copy
import pytest
from gh3studio.model import Song,Note,ChartError
from gh3studio.hopo import prefer_hopos,effective_states
from gh3studio.song_export import prepare_medium,export_song_folder
from gh3studio.chartio import read_chart


def test_hopo_flips_only_non_natural_changing_single_runs():
    song=Song(tracks={'Expert':[Note(0,4)],'Medium':[Note(0,3),Note(48,2),Note(144,3),Note(240,3),Note(336,0),Note(336,1),Note(432,0),Note(624,2)]})
    original=copy.deepcopy(song)
    result,report=prefer_hopos(song,.5)
    assert result.modifiers['Medium']==[(144,'N 5 0')]
    assert song==original and result.tracks==original.tracks
    states=effective_states(result,'Medium')
    assert states[48] and states[144] and not states[240] and not states[336] and not states[624]
    generous,review=prefer_hopos(song,1.)
    assert (624,'N 5 0') in generous.modifiers['Medium']
    assert review['estimated_hopo_events']>report['estimated_hopo_events']


def test_900_plus_notes_keep_exact_density_and_can_have_majority_hopos():
    song=Song(tracks={'Medium':[Note(i*96,i%4,24) for i in range(1000)]})
    result,report=prefer_hopos(song,.5)
    assert result.tracks==song.tracks and report['estimated_hopo_events']==999
    assert len(result.modifiers['Medium'])==999 and report['note_events']==1000
    assert report['estimated_hopo_percent']==99.9


def test_hopo_export_reopens_and_keeps_other_difficulties(tmp_path):
    from pathlib import Path
    song=Song(tracks={'Expert':[Note(0,4)],'Hard':[Note(0,2)],'Medium':[Note(0,3),Note(96,2),Note(192,3)]})
    output,report=prefer_hopos(song)
    assert not prepare_medium(output)[1]['remaining_errors']
    export_song_folder(output,{'hopo_assistance':report},tmp_path/'out',Path(__file__).parents[1]/'examples/audio/onset-study.wav')
    reopened=read_chart(tmp_path/'out/notes.chart')
    assert reopened.modifiers['Medium']==[(96,'N 5 0'),(192,'N 5 0')]
    assert reopened.tracks==song.tracks
    assert all(n.lane<4 for n in reopened.tracks['Medium'])


def test_hopo_orphan_duplicate_and_tap_rejected():
    song=Song(tracks={'Medium':[Note(0,0)]},modifiers={'Medium':[(96,'N 5 0')]})
    assert 'no playable note' in str(prepare_medium(song)[1])
    song.modifiers={'Medium':[(0,'N 5 0'),(0,'E *')]}
    assert 'Duplicate' in str(prepare_medium(song)[1])
    for marker in ('N 6 0','E "*"'):
        song.modifiers={'Medium':[(0,marker)]}
        with pytest.raises(ChartError,match='unsupported'):prefer_hopos(song)
