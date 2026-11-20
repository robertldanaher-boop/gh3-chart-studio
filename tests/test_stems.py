"""Multi-track songs: find the stems and mix them into one full mix."""
import numpy as np
import pytest
from gh3studio.stems import find_song_audio, mix_stems, describe, HEADROOM
from gh3studio.model import ChartError


def folder_with(tmp_path, *names):
    (tmp_path / 'notes.chart').write_text('[Song]\n{\n}\n', encoding='utf-8')
    for name in names:
        (tmp_path / name).write_bytes(b'x')
    return tmp_path / 'notes.chart'


def test_stems_detected_with_backing_first_and_extras_left_out(tmp_path):
    chart = folder_with(tmp_path, 'song.ogg', 'guitar.ogg', 'rhythm.ogg', 'drums_1.ogg', 'vocals.ogg',
                        'preview.ogg', 'crowd.ogg', 'commentary.ogg')
    plan = find_song_audio(chart, {})
    assert plan['kind'] == 'stems'
    assert [p.name for p in plan['paths']] == ['song.ogg', 'guitar.ogg', 'rhythm.ogg', 'drums_1.ogg', 'vocals.ogg']
    left = {item['file'] for item in plan['left_out']}
    assert left == {'preview.ogg', 'crowd.ogg', 'commentary.ogg'}


def test_song_only_is_single_full_mix(tmp_path):
    chart = folder_with(tmp_path, 'song.ogg', 'preview.ogg')
    plan = find_song_audio(chart, {})
    assert plan['kind'] == 'single' and [p.name for p in plan['paths']] == ['song.ogg']


def test_only_unconventional_file_is_used_with_warning(tmp_path):
    chart = folder_with(tmp_path, 'Artist - Title.mp3', 'preview.ogg')
    plan = find_song_audio(chart, {})
    assert plan['kind'] == 'single' and plan['paths'][0].name == 'Artist - Title.mp3'
    assert 'Verify' in plan['notes'][0]


def test_ambiguous_unconventional_files_are_none(tmp_path):
    chart = folder_with(tmp_path, 'a.ogg', 'b.ogg')
    assert find_song_audio(chart, {})['kind'] == 'none'


def test_duplicate_formats_prefer_ogg_and_note_it(tmp_path):
    chart = folder_with(tmp_path, 'song.mp3', 'song.ogg', 'guitar.wav')
    plan = find_song_audio(chart, {})
    assert [p.name for p in plan['paths']] == ['song.ogg', 'guitar.wav']
    assert any('song.mp3' in note for note in plan['notes'])


def test_chart_stream_entries_name_stems(tmp_path):
    chart = folder_with(tmp_path, 'backing.ogg', 'lead.ogg')
    plan = find_song_audio(chart, {'MusicStream': 'backing.ogg', 'GuitarStream': 'lead.ogg'})
    assert plan['kind'] == 'stems' and [p.name for p in plan['paths']] == ['backing.ogg', 'lead.ogg']


def test_instruments_without_backing_still_mix(tmp_path):
    chart = folder_with(tmp_path, 'guitar.ogg', 'bass.ogg')
    plan = find_song_audio(chart, {})
    assert plan['kind'] == 'stems' and len(plan['paths']) == 2
    assert any('No song/backing' in n for n in plan['notes'])


class Fake:
    def __init__(self, data, rate):
        self.data = np.asarray(data, np.float32)
        if self.data.ndim == 1:
            self.data = self.data[:, None]
        self.samplerate, self.channels, self.frames, self.pos = rate, self.data.shape[1], self.data.shape[0], 0

    def read(self, n, dtype='float32', always_2d=True):
        block = self.data[self.pos:self.pos + n]
        self.pos += len(block)
        return block

    def seek(self, frame):
        self.pos = frame

    def close(self):
        pass


class Sink:
    def __init__(self):
        self.blocks = []
        self.closed = False

    def write(self, block):
        self.blocks.append(np.array(block))

    def close(self):
        self.closed = True

    def data(self):
        return np.concatenate(self.blocks)


def run(sources, tmp_path):
    files = {}
    for name in sources:
        files[str(tmp_path / name)] = sources[name]
    sink = Sink()
    report = mix_stems(list(files), tmp_path / 'mix.wav', opener=lambda p: Fake(*files[str(p)]),
                       writer=lambda path, rate, ch: (setattr(sink, 'format', (rate, ch)), sink)[1])
    return report, sink


def test_mix_sums_pads_and_upmixes_mono(tmp_path):
    song = np.stack([np.full(100, .1), np.full(100, .2)], axis=1)
    guitar = np.full(60, .3)  # mono, shorter
    report, sink = run({'song.ogg': (song, 44100), 'guitar.ogg': (guitar, 44100)}, tmp_path)
    out = sink.data()
    assert sink.format == (44100, 2) and out.shape == (100, 2) and sink.closed
    assert np.allclose(out[:60], [[.4, .5]]) and np.allclose(out[60:], [[.1, .2]])
    assert report['turned_down'] is False and report['gain'] == 1.0
    assert report['stems'][1]['padded_frames'] == 40
    assert 'Mixed 2 audio tracks' in describe(report)


def test_mix_turns_down_evenly_only_when_it_would_clip(tmp_path):
    loud = np.full((50, 2), .8)
    report, sink = run({'song.ogg': (loud, 48000), 'guitar.ogg': (loud, 48000)}, tmp_path)
    out = sink.data()
    assert report['turned_down'] and report['peak_before'] == pytest.approx(1.6, abs=1e-3)
    assert np.abs(out).max() == pytest.approx(HEADROOM, abs=1e-5)
    assert np.allclose(out, out[0])  # same gain everywhere, no limiting artifacts
    assert 'turned down' in describe(report)


def test_mix_resamples_to_main_rate(tmp_path):
    pytest.importorskip('scipy')
    song = np.zeros((44100, 2))
    guitar = np.full((48000, 1), .25)
    report, sink = run({'song.ogg': (song, 44100), 'guitar.ogg': (guitar, 48000)}, tmp_path)
    assert sink.format[0] == 44100 and report['stems'][1]['resampled_from'] == 48000
    assert abs(sink.data().shape[0] - 44100) <= 2
    assert sink.data()[20000, 0] == pytest.approx(.25, abs=.01)


def test_unreadable_or_bad_stem_is_a_clear_error(tmp_path):
    def opener(path):
        if path.name == 'guitar.ogg':
            raise RuntimeError('corrupt header')
        return Fake(np.zeros((10, 2)), 44100)
    with pytest.raises(ChartError, match='guitar.ogg'):
        mix_stems([tmp_path / 'song.ogg', tmp_path / 'guitar.ogg'], tmp_path / 'm.wav', opener=opener, writer=lambda *a: Sink())
    with pytest.raises(ChartError, match='at least two'):
        mix_stems([tmp_path / 'song.ogg'], tmp_path / 'm.wav')


def test_real_files_mix_and_encode_round_trip(tmp_path):
    sf = pytest.importorskip('soundfile')
    rate = 44100
    t = np.arange(rate) / rate
    sf.write(tmp_path / 'song.ogg', np.stack([np.sin(2 * np.pi * 220 * t) * .3] * 2, axis=1), rate, format='OGG', subtype='VORBIS')
    sf.write(tmp_path / 'guitar.ogg', (np.sin(2 * np.pi * 330 * t) * .3)[:rate // 2], rate, format='OGG', subtype='VORBIS')
    sf.write(tmp_path / 'preview.ogg', np.zeros(rate // 10), rate, format='OGG', subtype='VORBIS')
    chart = tmp_path / 'notes.chart'
    chart.write_text('[Song]\n{\n}\n', encoding='utf-8')
    plan = find_song_audio(chart, {})
    assert plan['kind'] == 'stems' and len(plan['paths']) == 2
    report = mix_stems(plan['paths'], tmp_path / 'mix.wav', roles=plan['roles'])
    info = sf.info(tmp_path / 'mix.wav')
    assert (info.samplerate, info.channels) == (rate, 2) and abs(info.frames - rate) < 2048
    assert all(len(s['sha256']) == 64 for s in report['stems'])
    assert report['stems'][1]['role'] == 'guitar'


def test_explicit_stream_beats_conventional_duplicate(tmp_path):
    chart = folder_with(tmp_path, 'song.ogg', 'backing.mp3', 'guitar.ogg')
    plan = find_song_audio(chart, {'MusicStream': 'backing.mp3'})
    assert [p.name for p in plan['paths']] == ['backing.mp3', 'guitar.ogg']
    assert any('song.ogg' in note for note in plan['notes'])


def test_cache_prune_keeps_newest_and_current(tmp_path):
    import os, time
    from gh3studio.stems import prune_cache
    for i in range(9):
        wav = tmp_path / f'm{i}.wav'
        wav.write_bytes(b'x')
        (tmp_path / f'm{i}.json').write_text('{}')
        os.utime(wav, (time.time() - 100 + i, time.time() - 100 + i))
    (tmp_path / 'x.partial.wav').write_bytes(b'x')
    prune_cache(tmp_path, keep={'m0.wav'}, newest=3)
    left = sorted(p.name for p in tmp_path.glob('*.wav'))
    assert left == ['m0.wav', 'm6.wav', 'm7.wav', 'm8.wav', 'x.partial.wav']
    assert not (tmp_path / 'm3.json').exists() and (tmp_path / 'm8.json').exists()
