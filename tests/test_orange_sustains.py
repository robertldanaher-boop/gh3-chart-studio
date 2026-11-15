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
    assert report['sustain_transfers'][0]['previous_length']==blue_length


def test_new_blue_overlap_is_reported_not_silently_trimmed():
    song=Song(tracks={'Expert':[Note(0,4,384),Note(192,3)]})
    output,_=remove_orange_to_medium(song,'Expert',strict=False,orange_sustains_to_blue=True)
    assert output.tracks['Medium']==[Note(0,3,384),Note(192,3)]
    assert prepare_medium(output)[1]['remaining_errors']


def random_copy(notes,seed=0):
    return remove_orange_to_medium(Song(tracks={'Expert':notes}),'Expert',strict=False,randomize_orange_sustains=True,sustain_seed=seed)


def test_seed_repeatable_and_uses_all_four_lanes():
    notes=[Note(i*192,4,96) for i in range(40)]
    a,report=random_copy(notes,12)
    b,_=random_copy(notes,12)
    c,_=random_copy(notes,13)
    assert a.tracks==b.tracks and a.tracks!=c.tracks
    assert {n.lane for n in a.tracks['Medium']}=={0,1,2,3}
    assert [(n.tick,n.length) for n in a.tracks['Medium']]==[(n.tick,n.length) for n in notes]
    assert report['settings']['sustain_seed']==12


def test_prefers_simultaneous_and_avoids_future_and_previous_conflicts():
    # Red already held, Green has a future note, Yellow is simultaneous and clear.
    notes=[Note(0,1,384),Note(192,0),Note(96,2),Note(96,4,192)]
    for seed in range(8):
        out,r=random_copy(notes,seed)
        assert Note(96,2,192) in out.tracks['Medium']
        assert r['sustain_transfers'][0]['lane']==2
        assert not r['sustain_lane_conflicts']


def test_uses_new_clear_lane_when_simultaneous_lane_is_blocked():
    notes=[Note(0,0),Note(96,0),Note(0,4,192)]
    out,r=random_copy(notes)
    moved=r['sustain_transfers'][0]
    assert moved['lane'] in (1,2,3) and not moved['conflict']
    assert Note(0,0) in out.tracks['Medium']
    assert Note(0,moved['lane'],192) in out.tracks['Medium']


def test_no_clear_lane_preserves_and_flags_full_sustain():
    out,r=random_copy([Note(0,4,384)]+[Note(192,lane) for lane in range(4)])
    assert r['sustain_lane_conflicts']==1
    assert any(n.tick==0 and n.length==384 for n in out.tracks['Medium'])
    assert prepare_medium(out)[1]['remaining_errors']


def test_randomized_exports_have_only_four_lanes(tmp_path):
    out,_=random_copy([Note(i*192,4,96) for i in range(16)],9)
    for name,writer,reader in [('random.chart',write_chart,read_chart),('random.mid',write_midi,read_midi)]:
        writer(out,tmp_path/name)
        assert reader(tmp_path/name).tracks['Medium']==out.tracks['Medium']
