import hashlib
import json
import numpy as np
import pytest
import soundfile as sf
from gh3studio.audio_export import export_ogg
from gh3studio.song_export import export_song_folder
from gh3studio.model import Song,Note,ChartError
from gh3studio.chartio import read_chart

@pytest.mark.parametrize('channels',[1,2])
@pytest.mark.parametrize('rate',[22050,44100,48000])
def test_encode_vorbis_preserves_frame_rate_channels_and_timing(tmp_path,channels,rate):
    samples=np.zeros((rate,channels),dtype='float32')
    rng=np.random.default_rng(42);samples[rate//3:rate//3+1024]=rng.uniform(-.5,.5,(1024,channels))
    source=tmp_path/'mix.wav';sf.write(source,samples,rate,subtype='FLOAT')
    before=source.read_bytes();target=tmp_path/'song.ogg';report=export_ogg(source,target)
    decoded,actual_rate=sf.read(target,always_2d=True)
    assert actual_rate==rate and decoded.shape==samples.shape
    assert sf.info(target).format=='OGG' and sf.info(target).subtype=='VORBIS'
    # Lossy encoding changes samples, but does not translate the authored audio.
    from scipy.signal import correlate,correlation_lags
    correlation=correlate(decoded[:,0],samples[:,0],method='fft')
    assert correlation_lags(len(decoded),len(samples))[np.argmax(correlation)]==0
    assert report['operation']=='encoded_to_vorbis' and report['fully_decoded']
    assert source.read_bytes()==before


def test_existing_vorbis_reused_byte_for_byte_and_folder_has_no_duplicates(tmp_path):
    source=tmp_path/'recording.ogg';sf.write(source,np.zeros(6000),48000,format='OGG',subtype='VORBIS')
    song=Song(metadata={'MusicStream':'old.wav'},tracks={'Medium':[Note(0,0)]})
    folder=tmp_path/'export';report=export_song_folder(song,{'settings':{'source':'Expert'}},folder,source)
    assert (folder/'song.ogg').read_bytes()==source.read_bytes()
    assert report['audio_export']['operation']=='copied_without_reencoding'
    assert read_chart(folder/'notes.chart').metadata['MusicStream']=='song.ogg'
    assert sorted(p.name for p in folder.iterdir())==sorted(['notes.chart','song.ogg','song.ini','validation.json','IMPORT_README.txt'])
    assert json.loads((folder/'validation.json').read_text())['settings']=={'source':'Expert'}
    assert report['files_sha256']['song.ogg']==hashlib.sha256(source.read_bytes()).hexdigest()


def test_codec_checked_not_just_extension(tmp_path):
    source=tmp_path/'fake.ogg';sf.write(source,np.zeros(2000),44100,format='WAV')
    target=tmp_path/'out.ogg';report=export_ogg(source,target)
    assert report['operation']=='encoded_to_vorbis' and sf.info(target).subtype=='VORBIS'


def test_invalid_channels_roll_back_song_folder(tmp_path):
    source=tmp_path/'surround.wav';sf.write(source,np.zeros((2000,6)),44100)
    with pytest.raises(ChartError,match='mono or stereo'):
        export_song_folder(Song(tracks={'Medium':[Note(0,0)]}),{},tmp_path/'out',source)
    assert not (tmp_path/'out').exists() and not list(tmp_path.glob('.gh3-song-*'))
