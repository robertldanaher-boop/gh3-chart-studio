"""Single-song view mixes separate tracks once and previews/exports the mix."""
import shutil
from pathlib import Path
import numpy as np
import soundfile as sf
from test_gui import app, wait, FIXTURE
from gh3studio.gui import Window


def test_opening_song_with_separate_tracks_previews_the_mix(tmp_path, app):
    folder = tmp_path / 'Artist - Song'
    folder.mkdir()
    chart = folder / 'notes.chart'
    shutil.copyfile(FIXTURE, chart)
    sf.write(folder / 'song.wav', np.full((22050, 2), .2), 44100)
    sf.write(folder / 'guitar.wav', np.full(22050, .3), 44100)
    sf.write(folder / 'preview.wav', np.zeros(100), 44100)
    w = Window()
    w.open_path(chart)
    wait(w)
    assert w.song is not None and w.audio_mix is not None
    mixed, report = w.audio_mix
    assert Path(w.playback.player.source().toLocalFile()).resolve() == Path(mixed).resolve()
    assert [s['file'] for s in report['stems']] == ['song.wav', 'guitar.wav']
    data, rate = sf.read(mixed, always_2d=True)
    assert rate == 44100 and data.shape == (22050, 2) and abs(data[1000, 0] - .5) < .01
    assert 'Mixed 2 audio tracks' in w.log.toPlainText()
    w.close()
