from fractions import Fraction
import copy
import pytest
from gh3studio.model import Song,Note,Phrase,ChartError
from gh3studio.editing import prepare_cleanup,shift_timing,timeline
from gh3studio.converter import convert
from gh3studio.service import export_bundle

def test_cleanup_explicit_preserves_original_and_lists_each_change(tmp_path):
    song=Song(tracks={'Expert':[Note(0,0,300),Note(0,1,220),Note(192,0,30)]},modifiers={'Expert':[(0,'N 6'),(96,'N 7')]})
    original=copy.deepcopy(song)
    preview,report=prepare_cleanup(song)
    assert report['remaining_errors'] and len(report['changes'])==2
    prepared,report=prepare_cleanup(song,True,True)
    assert song==original and not report['remaining_errors']
    assert prepared.tracks['Expert']==[Note(0,0,192),Note(0,1,192),Note(192,0,30)]
    assert len(report['changes'])==4
    result,conversion=convert(prepared);export_bundle(result,conversion,tmp_path/'export')
    assert all(n.lane<4 for n in result.tracks['Medium'])

def test_shift_across_tempo_boundary_preserves_elapsed_duration(tmp_path):
    song=Song(tempos=[(0,Fraction(500000)),(192,Fraction(1000000))],
              tracks={'Medium':[Note(96,0,96),Note(384,2,48)]},
              phrases={'Medium':[Phrase(96,2,336)]},events=[(480,'end')])
    original=copy.deepcopy(song);shifted=shift_timing(song,250)
    assert song==original and shifted.tempos==song.tempos and shifted.signatures==song.signatures
    for before,after in zip(song.tracks['Medium'],shifted.tracks['Medium']):
        assert shifted.seconds(after.tick)==pytest.approx(song.seconds(before.tick)+.25)
        assert shifted.seconds(after.tick+after.length)==pytest.approx(song.seconds(before.tick+before.length)+.25)
    assert shifted.events==[(528,'end')]
    export_bundle(shifted,{},tmp_path/'shifted')

@pytest.mark.parametrize('shift',[-1000,float('nan'),10001])
def test_invalid_shift_rejected(shift):
    with pytest.raises(ChartError):shift_timing(Song(tracks={'Medium':[Note(0,0)]}),shift)

def test_hopo_candidates_no_strum_promise_and_chords_excluded():
    song=Song(tracks={'Medium':[Note(0,3),Note(48,2),Note(96,3),Note(144,3),Note(192,0),Note(192,1),Note(240,2)]})
    assert [n[3] for n in timeline(song,'Medium')]==[False,True,True,False,False,False,False]
    assert not any(n[3] for n in timeline(song,'Medium',.1))
