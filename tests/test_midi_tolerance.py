"""Downloaded MIDI charts: same-fret overlaps and track-name variants are handled, not blocked."""
import mido
import pytest
from gh3studio.midiio import read_midi
from gh3studio.model import ChartError


def write(path, tracks, resolution=192):
    mid = mido.MidiFile(type=1, ticks_per_beat=resolution)
    tempo = mido.MidiTrack([mido.MetaMessage('track_name', name='TEMPO', time=0), mido.MetaMessage('set_tempo', tempo=500000, time=0)])
    mid.tracks.append(tempo)
    for name, messages in tracks:
        track = mido.MidiTrack([mido.MetaMessage('track_name', name=name, time=0)])
        track.extend(messages)
        mid.tracks.append(track)
    mid.save(path)
    return path


def on(note, time=0):
    return mido.Message('note_on', note=note, velocity=100, time=time)


def off(note, time=0):
    return mido.Message('note_off', note=note, velocity=0, time=time)


def test_same_fret_restart_ends_earlier_note(tmp_path):
    # Bob: "Overlapping MIDI pitch 84 at 166464" blocked songs. 84 is Hard green.
    path = write(tmp_path / 'notes.mid', [('PART GUITAR', [on(84), on(84, 192), off(84, 0), off(84, 96), on(96, 0), off(96, 96)])])
    song = read_midi(path)
    assert [(n.tick, n.lane, n.length) for n in song.tracks['Hard']] == [(0, 0, 192), (192, 0, 96)]
    assert any('overlapping MIDI notes' in w for w in song.warnings)


def test_restart_before_late_note_off_is_kept(tmp_path):
    path = write(tmp_path / 'notes.mid', [('PART GUITAR', [on(84), on(84, 192), off(84, 108), off(84, 100)])])
    notes = read_midi(path).tracks['Hard']
    assert [n.tick for n in notes] == [0, 192] and notes[0].length == 192


@pytest.mark.parametrize('name', ['Part Guitar', 'PART_GUITAR', 'part guitar', 'T1 GEMS'])
def test_guitar_track_name_variants(tmp_path, name):
    path = write(tmp_path / 'notes.mid', [(name, [on(96), off(96, 96)])])
    assert read_midi(path).tracks['Expert']


def test_rhythm_or_coop_used_only_without_lead_guitar(tmp_path):
    path = write(tmp_path / 'a.mid', [('PART DRUMS', []), ('PART RHYTHM', [on(97), off(97, 96)])])
    song = read_midi(path)
    assert song.tracks['Expert'][0].lane == 1 and any('PART RHYTHM' in w for w in song.warnings)
    path = write(tmp_path / 'b.mid', [('PART GUITAR COOP', [on(98), off(98, 96)]), ('PART GUITAR', [on(96), off(96, 96)])])
    assert read_midi(path).tracks['Expert'][0].lane == 0


def test_no_guitar_part_names_the_tracks_found(tmp_path):
    path = write(tmp_path / 'notes.mid', [('PART DRUMS', [on(96), off(96, 96)]), ('PART VOCALS', [])])
    with pytest.raises(ChartError, match='found tracks: TEMPO, PART DRUMS, PART VOCALS'):
        read_midi(path)


def test_note_without_note_off_ends_at_track_end(tmp_path):
    path = write(tmp_path / 'notes.mid', [('PART GUITAR', [on(96), on(97, 96), off(97, 96)])])
    song = read_midi(path)
    assert [(n.tick, n.lane, n.length) for n in song.tracks['Expert']] == [(0, 0, 192), (96, 1, 96)]
    assert any('no note-off' in w for w in song.warnings)


def test_late_original_release_does_not_shorten_restart(tmp_path):
    path=write(tmp_path/'fifo.mid',[('PART GUITAR',[on(84),on(84,192),off(84,108),off(84,100)])])
    assert [(n.tick,n.length) for n in read_midi(path).tracks['Hard']]==[(0,192),(192,208)]


def test_multiple_restarts_pair_releases_in_fifo_order(tmp_path):
    path=write(tmp_path/'many.mid',[('PART GUITAR',[on(96),on(96,96),on(96,96),off(96,48),off(96,48),off(96,96)])])
    assert [(n.tick,n.length) for n in read_midi(path).tracks['Expert']]==[(0,96),(96,96),(192,192)]


def test_same_tick_duplicate_does_not_swallow_real_release(tmp_path):
    path=write(tmp_path/'duplicate.mid',[('PART GUITAR',[on(96),on(96),off(96,96),on(97,96),off(97,96)])])
    assert [(n.tick,n.lane,n.length) for n in read_midi(path).tracks['Expert']]==[(0,0,96),(192,1,96)]
