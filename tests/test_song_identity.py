import configparser
import copy
from datetime import datetime
import numpy as np
import soundfile as sf
from gh3studio.model import Song,Note
from gh3studio.song_identity import export_folder_name,fill_from_audio
from gh3studio.chartio import write_chart,read_chart
from gh3studio.service import load
from gh3studio.song_export import export_song_folder


def test_windows_folder_uses_unicode_identity_with_safe_characters():
    name=export_folder_name({'Artist':'Björk / Artist','Name':'Song: "Title"?'},datetime(2026,11,15,6,0))
    assert name=='Björk _ Artist - Song_ _Title__'
    assert len(export_folder_name({'Artist':'a'*300,'Name':'b'*300}))<150


def test_chart_ini_audio_metadata_round_trip(tmp_path):
    song=Song(metadata={'Name':'† Song / title','Artist':'Björk','Album':'Álbum','Year':'2026','Genre':'Rock','Charter':'Bob','TrackNumber':'7','Copyright':'Owner'},tracks={'Medium':[Note(0,0)]})
    chart=tmp_path/'notes.chart';write_chart(song,chart)
    (tmp_path/'song.ini').write_text('[song]\nname = † Song / title\nartist = Björk\ncharter = Bob\ncustom_tag = preserve me\npreview_start_time = 12000\n',encoding='utf-8')
    source=load(chart);original=copy.deepcopy(source)
    audio=tmp_path/'mix.wav';sf.write(audio,np.zeros(4410),44100)
    dest=tmp_path/'out';report=export_song_folder(source,{},dest,audio)
    assert source==original
    reread=load(dest/'notes.chart')
    for key,value in source.metadata.items():
        if key!='Resolution':assert reread.metadata[key]==value
    assert reread.ini_metadata['custom_tag']=='preserve me'
    assert reread.ini_metadata['preview_start_time']=='12000'
    with sf.SoundFile(dest/'song.ogg') as sound:
        assert sound.title=='† Song / title' and sound.artist=='Björk' and sound.album=='Álbum' and sound.tracknumber=='7'
    assert report['song_identity']['Charter']=='Bob'


def test_audio_tags_fill_missing_fields_without_overwriting_chart(tmp_path):
    audio=tmp_path/'mix.ogg'
    with sf.SoundFile(audio,'w',format='OGG',subtype='VORBIS',samplerate=44100,channels=1) as sound:
        sound.title='Tagged title';sound.artist='Tagged artist';sound.album='Tagged album';sound.write(np.zeros(4410))
    assert fill_from_audio({},audio)['Name']=='Tagged title'
    assert fill_from_audio({'Name':'Authored title','Artist':'Unknown'},audio)['Name']=='Authored title'
    assert fill_from_audio({'Artist':'Unknown'},audio)['Artist']=='Tagged artist'
    source_bytes=audio.read_bytes()
    song=Song(metadata={'Name':'Authored title','Artist':'Authored artist'},tracks={'Medium':[Note(0,0)]})
    report=export_song_folder(song,{},tmp_path/'out',audio)
    assert (tmp_path/'out/song.ogg').read_bytes()==source_bytes
    assert report['audio_export']['metadata_warnings']
    assert read_chart(tmp_path/'out/notes.chart').metadata['Artist']=='Authored artist'


def test_folder_collisions_keep_existing_files(tmp_path):
    from gh3studio.song_identity import export_folder_path
    metadata={'Artist':'Artist','Name':'Song'}
    assert export_folder_path(tmp_path,metadata).name=='Artist - Song'
    (tmp_path/'artist - song').mkdir()
    (tmp_path/'Artist - Song (2)').write_text('leave alone')
    assert export_folder_path(tmp_path,metadata).name=='Artist - Song (3)'
    assert (tmp_path/'Artist - Song (2)').read_text()=='leave alone'
