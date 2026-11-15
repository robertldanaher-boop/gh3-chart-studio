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

def test_hopo_candidates_follow_importer_chord_and_lane_overlap_rules():
    song=Song(tracks={'Medium':[Note(0,3),Note(48,2),Note(96,3),Note(144,3),Note(192,0),Note(192,1),Note(240,2)]})
    assert [n[3] for n in timeline(song,'Medium')]==[False,True,True,False,False,False,True]
    assert not any(n[3] for n in timeline(song,'Medium',.1))


@pytest.mark.parametrize('difficulty',['Expert','Hard'])
def test_orange_only_copy_preserves_tracks_timing_and_exports(tmp_path,difficulty):
    from gh3studio.editing import remove_orange_to_medium
    from gh3studio.chartio import read_chart
    from gh3studio.midiio import read_midi
    song=Song(tracks={'Expert':[Note(0,0,48),Note(0,4,48),Note(96,4),Note(192,3,48)],
                      'Hard':[Note(0,1,48),Note(96,4),Note(192,2,48)],'Medium':[Note(0,4)]},
              phrases={difficulty:[Phrase(0,2,384)]},events=[(480,'end')])
    original=copy.deepcopy(song)
    result,report=remove_orange_to_medium(song,difficulty)
    expected=[n for n in original.tracks[difficulty] if n.lane!=4]
    assert song==original and result.tracks['Medium']==expected
    assert result.tracks['Expert']==original.tracks['Expert'] and result.tracks['Hard']==original.tracks['Hard']
    assert result.phrases['Medium']==original.phrases[difficulty]
    assert result.tempos==original.tempos and result.events==original.events
    export_bundle(result,report,tmp_path/'out')
    chart=read_chart(tmp_path/'out'/'notes.chart');midi=read_midi(tmp_path/'out'/'notes.mid','legacy')
    assert chart.tracks['Medium']==expected
    assert all(n.lane<4 for n in midi.tracks['Medium'])
    assert chart.tracks['Expert']==original.tracks['Expert']


def test_orange_only_does_not_silently_repair_or_empty_source():
    from gh3studio.editing import remove_orange_to_medium
    song=Song(tracks={'Expert':[Note(0,4)]})
    with pytest.raises(ChartError,match='empty'):remove_orange_to_medium(song,'Expert')
    song.tracks['Expert']=[Note(0,0),Note(96,4)];song.modifiers={'Expert':[(0,'N 6')]}
    with pytest.raises(ChartError,match='unsupported gameplay'):remove_orange_to_medium(song,'Expert')
    with pytest.raises(ChartError,match='available source'):remove_orange_to_medium(song,'Invalid')
    song.modifiers={'Hard':[(0,'N 6')]}
    with pytest.raises(ChartError,match='retained difficulty'):remove_orange_to_medium(song,'Expert')
