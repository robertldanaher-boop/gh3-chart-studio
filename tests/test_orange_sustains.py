import copy
import pytest
from gh3studio.model import Song, Note
from gh3studio.editing import remove_orange_to_medium
from gh3studio.song_export import prepare_medium
from gh3studio.chartio import write_chart,read_chart
from gh3studio.midiio import write_midi,read_midi


def test_transfer_preserves_timing_and_source_and_exports(tmp_path):
    song=Song(tracks={'Expert':[Note(0,4,96),Note(192,4,0),Note(384,1,96),Note(384,4,96)],'Hard':[Note(0,0)],'Medium':[Note(0,2)]})
    before=copy.deepcopy(song)
    output,report=remove_orange_to_medium(song,'Expert',strict=False,orange_sustains_to_blue=True)
    assert output.tracks['Medium']==[Note(0,3,96),Note(384,1,96),Note(384,3,96)]
    assert song==before and output.tracks['Expert']==before.tracks['Expert'] and output.tracks['Hard']==before.tracks['Hard']
    assert report['transferred_orange_sustains']==2
    for name,writer,reader in [('notes.chart',write_chart,read_chart),('notes.mid',write_midi,read_midi)]:
        writer(output,tmp_path/name)
        assert reader(tmp_path/name).tracks['Medium']==output.tracks['Medium']


@pytest.mark.parametrize('blue_length,orange_length,expected',[(0,96,96),(48,96,96),(192,96,192)])
def test_simultaneous_blue_merges_without_duplicate(blue_length,orange_length,expected):
    song=Song(tracks={'Hard':[Note(0,3,blue_length),Note(0,4,orange_length)]})
    output,report=remove_orange_to_medium(song,'Hard',strict=False,orange_sustains_to_blue=True)
    assert output.tracks['Medium']==[Note(0,3,expected)]
    assert report['sustain_transfers'][0]['blue_length_before']==blue_length


def test_new_blue_overlap_is_reported_not_silently_trimmed():
    song=Song(tracks={'Expert':[Note(0,4,384),Note(192,3)]})
    output,_=remove_orange_to_medium(song,'Expert',strict=False,orange_sustains_to_blue=True)
    assert output.tracks['Medium']==[Note(0,3,384),Note(192,3)]
    assert prepare_medium(output)[1]['remaining_errors']
