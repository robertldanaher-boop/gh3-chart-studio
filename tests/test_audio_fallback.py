from pathlib import Path
import subprocess
import numpy as np
import pytest
import soundfile as sf
import imageio_ffmpeg
from gh3studio.audio_export import export_ogg,AudioExportError
from gh3studio.audio_fallback import decode_to_pcm
from gh3studio.song_export import export_song_folder
from gh3studio.model import Song,Note,ChartError


@pytest.mark.parametrize('channels,padding',[(1,0),(2,1234)])
def test_native_decode_failure_retries_real_ffmpeg_and_replaces_partial_output(tmp_path,monkeypatch,channels,padding):
    samples=np.zeros((96000,channels),dtype='float32');samples[12000:24000]=.2
    wav=tmp_path/'source.wav';src=tmp_path/'source.opus';sf.write(wav,samples,48000)
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-i',str(wav),'-c:a','libopus',str(src)],check=True)
    before=src.read_bytes();original=sf.SoundFile.read
    def fail_after_block(self,*args,**kwargs):
        if str(self.name)==str(src) and self.tell()>=65536:raise sf.LibsndfileError(3)
        return original(self,*args,**kwargs)
    monkeypatch.setattr(sf.SoundFile,'read',fail_after_block)
    dest=tmp_path/'song.ogg';report=export_ogg(src,dest,{'Name':'Synthetic recovery','Artist':'Fixture'},padding_frames=padding)
    decoded,rate=sf.read(dest,always_2d=True)
    assert decoded.shape==(96000+padding,channels) and rate==48000
    assert report['fallback']['source_header_matched'] and report['fallback']['decoded_frames']==96000
    assert 'decode source' in report['fallback']['original_error']
    assert report['fully_decoded'] and report['padding_frames']==padding
    assert sf.info(dest).subtype=='VORBIS' and src.read_bytes()==before
    assert report['embedded_tags']['title']=='Synthetic recovery'


def test_write_failure_reports_stage_and_does_not_retry_decoder(tmp_path,monkeypatch):
    src=tmp_path/'source.wav';sf.write(src,np.zeros(4800),48000)
    import gh3studio.audio_fallback as fallback
    monkeypatch.setattr(fallback,'decode_to_pcm',lambda *a,**k:pytest.fail('Write failures must not retry decoding'))
    original=sf.SoundFile.write
    def broken(self,*args,**kwargs):
        if str(self.name)==str(tmp_path/'out.ogg'):raise sf.LibsndfileError(3)
        return original(self,*args,**kwargs)
    monkeypatch.setattr(sf.SoundFile,'write',broken)
    with pytest.raises(AudioExportError,match='write Ogg.*out.ogg'):export_ogg(src,tmp_path/'out.ogg')


def test_both_decoders_fail_and_atomic_folder_is_removed(tmp_path):
    src=tmp_path/'broken.opus';src.write_bytes(b'not an audio stream')
    song=Song(tracks={'Medium':[Note(0,0)]})
    with pytest.raises(ChartError,match='Automatic recovery could not complete') as error:
        export_song_folder(song,{},tmp_path/'output',src)
    assert 'broken.opus' in str(error.value) and not (tmp_path/'output').exists()
    assert not list(tmp_path.glob('.gh3-song-*'))


def test_recovery_rejects_duration_mismatch(tmp_path):
    src=tmp_path/'source.wav';sf.write(src,np.zeros(4800),48000)
    with pytest.raises(ChartError,match='do not match source header'):
        decode_to_pcm(src,tmp_path/'decoded.wav',(5000,48000,1))


def test_decoder_timeout_is_actionable(tmp_path,monkeypatch):
    def timeout(*args,**kwargs):raise subprocess.TimeoutExpired('ffmpeg',180)
    monkeypatch.setattr(subprocess,'run',timeout)
    with pytest.raises(ChartError,match='Alternate audio decoder failed.*source.opus'):
        decode_to_pcm(tmp_path/'source.opus',tmp_path/'decoded.wav')
