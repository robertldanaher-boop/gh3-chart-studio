"""Exports carry only what Guitar Hero III guitar play uses."""
from gh3studio.gh3_profile import lean_events, lean_chart_metadata, lean_ini, omitted_sections


def test_events_keep_sections_and_end_only():
    events = [(0, 'section Intro'), (10, 'lyric Hel-'), (11, 'phrase_start'), (12, 'phrase_end'),
              (20, 'crowd_clap'), (30, '[section Verse]'), (35, 'prc_chorus_1'), (40, 'music_start'), (99, 'end')]
    kept, removed = lean_events(events)
    assert kept == [(0, 'section Intro'), (30, '[section Verse]'), (35, 'prc_chorus_1'), (99, 'end')]
    assert removed == {'crowd': 1, 'lyric': 1, 'music': 1, 'phrase': 2}


def test_chart_header_keeps_identity_and_timing():
    meta = {'Name': 'N', 'Artist': 'A', 'Charter': 'C', 'Offset': '0', 'Resolution': '192', 'PreviewStart': '5',
            'MusicStream': 'song.ogg', 'GuitarStream': 'guitar.ogg', 'DrumStream': 'drums.ogg', 'Player2': 'bass',
            'Difficulty': '0', 'MediaType': 'cd', 'Length': '200', 'SongIniDelay': '0'}
    kept, removed = lean_chart_metadata(meta)
    assert set(kept) == {'Name', 'Artist', 'Charter', 'Offset', 'Resolution', 'PreviewStart', 'MusicStream'}
    assert 'DrumStream' in removed and 'Player2' in removed


def test_song_ini_drops_other_instruments():
    values = {'name': 'N', 'artist': 'A', 'diff_guitar': '4', 'diff_drums': '5', 'diff_drums_real': '5', 'pro_drums': 'True',
              'diff_vocals': '3', 'diff_vocals_harm': '3', 'diff_keys': '2', 'diff_bass': '3', 'diff_guitarghl': '4',
              'five_lane_drums': 'False', 'video_start_time': '0', 'icon': 'rb', 'loading_phrase': 'x',
              'preview_start_time': '1000', 'delay': '0', 'song_length': '1000', 'hopo_frequency': '170', 'Charter': 'C'}
    kept, removed = lean_ini(values)
    assert set(kept) == {'name', 'artist', 'diff_guitar', 'preview_start_time', 'delay', 'song_length', 'hopo_frequency', 'Charter'}
    assert {'diff_drums', 'pro_drums', 'diff_vocals', 'diff_keys', 'diff_bass', 'diff_guitarghl', 'icon'} <= set(removed)


def test_omitted_sections_listed():
    warnings = ['Other instrument/section omitted from export: ExpertDrums',
                'Other instrument/section omitted from export: PART VOCALS', 'unrelated']
    assert omitted_sections(warnings) == ['ExpertDrums', 'PART VOCALS']


def test_full_export_is_guitar_only_and_lean(tmp_path):
    import pytest
    sf = pytest.importorskip('soundfile')
    import numpy as np
    from gh3studio.service import load
    from gh3studio.song_export import export_song_folder
    chart = tmp_path / 'src' / 'notes.chart'
    chart.parent.mkdir()
    chart.write_text('[Song]\n{\n  Name = "Song"\n  Artist = "Band"\n  Resolution = 192\n  Offset = 0\n'
                     '  Player2 = bass\n  DrumStream = "drums.ogg"\n}\n'
                     '[SyncTrack]\n{\n  0 = TS 4\n  0 = B 120000\n}\n'
                     '[Events]\n{\n  0 = E "section Intro"\n  96 = E "lyric Hey"\n  96 = E "phrase_start"\n  768 = E "end"\n}\n'
                     '[MediumSingle]\n{\n  0 = N 0 0\n  192 = N 1 0\n}\n'
                     '[ExpertDrums]\n{\n  0 = N 0 0\n}\n', encoding='utf-8')
    (chart.parent / 'song.ini').write_text('[song]\nname = Song\nartist = Band\ndiff_drums = 4\ndiff_vocals = 2\npro_drums = True\n', encoding='utf-8')
    audio = tmp_path / 'mix.wav'
    sf.write(audio, np.zeros(44100), 44100)
    song = load(chart)
    details = export_song_folder(song, {}, tmp_path / 'out', audio)
    text = (tmp_path / 'out' / 'notes.chart').read_text(encoding='utf-8')
    assert 'Drums' not in text and 'lyric' not in text and 'phrase_start' not in text and 'Player2' not in text
    assert 'section Intro' in text and '"end"' in text and '[MediumSingle]' in text
    ini = (tmp_path / 'out' / 'song.ini').read_text(encoding='utf-8')
    assert 'diff_drums' not in ini and 'pro_drums' not in ini and 'diff_vocals' not in ini and 'name = Song' in ini
    lean = details['gh3_lean']
    assert lean['instrument_sections_omitted'] == ['ExpertDrums']
    assert lean['events_removed'] == {'lyric': 1, 'phrase': 1}
    assert 'diff_drums' in lean['song_ini_keys_removed'] and 'DrumStream' in lean['chart_song_keys_removed']
