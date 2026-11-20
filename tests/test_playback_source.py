"""Re-opening the recording that is already loaded must not rebuild the media backend."""
from pathlib import Path
from test_gui import app, FIXTURE
from gh3studio.gui import Window


def test_same_recording_is_not_reloaded(app):
    recording = FIXTURE.parent / 'audio' / 'onset-study.wav'
    w = Window()
    calls = []
    original = w.playback.player.setSource
    w.playback.player.setSource = lambda url: (calls.append(url), original(url))
    assert w.playback.open_audio(recording)
    assert w.playback.open_audio(recording)
    assert w.playback.open_audio(str(recording).replace('\\', '/'))
    assert len(calls) == 1
    assert Path(w.playback.player.source().toLocalFile()).resolve() == recording.resolve()
    w.playback.clear_audio()
    assert w.playback.open_audio(recording) and len(calls) == 3  # cleared (empty URL) then loaded again
    w.close()


def test_failed_recording_can_be_retried(app, tmp_path):
    from PySide6.QtMultimedia import QMediaPlayer
    bad = tmp_path / 'broken.wav'
    bad.write_bytes(b'not audio')
    w = Window()
    calls = []
    original = w.playback.player.setSource
    w.playback.player.setSource = lambda url: (calls.append(url), original(url))
    w.playback.player.mediaStatus = lambda: QMediaPlayer.InvalidMedia  # simulate a failed load
    assert w.playback.open_audio(bad) and w.playback.open_audio(bad)
    assert len(calls) == 2  # a recording that failed to load is loaded again
    w.close()
