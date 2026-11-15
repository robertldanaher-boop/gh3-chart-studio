import copy
from pathlib import Path
import numpy as np
import pytest
import soundfile as sf
from gh3studio.model import Song,Note,ChartError
from gh3studio.editing import remove_orange_to_medium
from gh3studio.song_export import prepare_medium,export_song_folder
from gh3studio.chartio import read_chart,write_chart

@pytest.mark.parametrize('difficulty',['Expert','Hard','Medium','Easy'])
def test_displayed_difficulty_exact_copy(difficulty):
    song=Song(tracks={d:[Note(i*192,0,300),Note(i*192,4,300),Note(i*192+96,0)] for i,d in enumerate(('Expert','Hard','Medium','Easy'))},modifiers={difficulty:[(0,'N 6 0')]})
    original=copy.deepcopy(song)
    output,report=remove_orange_to_medium(song,difficulty,strict=False)
    assert output.tracks['Medium']==[n for n in song.tracks[difficulty] if n.lane!=4]
    assert song==original and report['retained_notes_exact']
    for d in ('Expert','Hard','Easy'):assert output.tracks[d]==song.tracks[d]
    assert output.modifiers['Medium']==song.modifiers[difficulty]
    assert report['compatibility_errors']


def test_song_folder_and_medium_only_review(tmp_path):
    song=Song(metadata={'Name':'A song','Artist':'An artist'},tracks={'Expert':[Note(0,0,300),Note(0,4,300),Note(96,0)],'Hard':[Note(0,3,500)],'Medium':[Note(0,2)]},modifiers={'Expert':[(0,'N 6 0'),(100,'N 7 40')],'Hard':[(0,'N 5 0')]})
    output,report=remove_orange_to_medium(song,'Expert',strict=False)
    _,review=prepare_medium(output)
    assert review['remaining_errors'] and not review['changes']
    prepared,review=prepare_medium(output,True,True)
    assert not review['remaining_errors'] and review['changes']
    assert prepared.tracks['Expert']==song.tracks['Expert']
    assert prepared.modifiers['Expert']==song.modifiers['Expert']
    assert prepared.tracks['Hard']==song.tracks['Hard']
    audio=tmp_path/'mix.wav';sf.write(audio,np.zeros((4410,2)),44100)
    dest=tmp_path/'song';details=export_song_folder(prepared,dict(report,medium_export_cleanup=review),dest,audio)
    assert {'notes.chart','song.wav','song.ini','validation.json','settings.json','IMPORT_README.txt'}=={p.name for p in dest.iterdir()}
    reopened=read_chart(dest/'notes.chart')
    assert reopened.tracks==prepared.tracks
    for diff in prepared.tracks:assert reopened.modifiers.get(diff,[])==prepared.modifiers.get(diff,[])
    assert sf.info(dest/'song.wav').frames==4410
    assert details['folder_checks']['medium_orange_gems']==0
    assert 'name = A song' in (dest/'song.ini').read_text()
    with pytest.raises(ChartError,match='already exists'):export_song_folder(prepared,report,dest,audio)


def test_failed_audio_export_rolls_back(tmp_path):
    song=Song(tracks={'Medium':[Note(0,0)]});audio=tmp_path/'bad.wav';audio.write_bytes(b'invalid')
    with pytest.raises(Exception):export_song_folder(song,{},tmp_path/'out',audio)
    assert not (tmp_path/'out').exists() and not list(tmp_path.glob('.gh3-song-*'))


def test_offset_blocks_folder_export():
    song=Song(metadata={'SongIniDelay':'25'},tracks={'Medium':[Note(0,0)]})
    assert 'delay' in prepare_medium(song)[1]['remaining_errors'][0]
