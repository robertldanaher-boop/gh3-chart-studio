from gh3studio.preview_audio import matching_audio


def test_matching_recording_uses_metadata_and_safe_song_default(tmp_path):
    chart=tmp_path/'notes.chart';chart.touch()
    (tmp_path/'song.ogg').touch()
    assert matching_audio(chart,{})==tmp_path/'song.ogg'
    (tmp_path/'song.wav').touch()
    assert matching_audio(chart,{}) is None
    assert matching_audio(chart,{'MusicStream':'song.wav'})==tmp_path/'song.wav'


def test_matching_recording_never_guesses_stems_or_outside_files(tmp_path):
    folder=tmp_path/'song';folder.mkdir();chart=folder/'notes.chart';chart.touch()
    (folder/'guitar.ogg').touch();(tmp_path/'outside.wav').touch()
    assert matching_audio(chart,{}) is None
    assert matching_audio(chart,{'MusicStream':'../outside.wav'}) is None
