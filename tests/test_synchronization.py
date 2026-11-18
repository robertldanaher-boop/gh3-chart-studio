import copy
import json
from fractions import Fraction
from pathlib import Path
import numpy as np
import pytest
import soundfile as sf
from gh3studio.model import Song,Note,Phrase,ChartError
from gh3studio.chartio import read_chart,write_chart
from gh3studio.cleaner import inspect_chart,export_cleaned,fingerprint
from gh3studio.synchronization import normalize
from gh3studio.audio_export import export_ogg
from test_cleaner import fixture


def review(row,shift=125,accept_anchors=False):
    return {'shift_ms':shift,'source_hashes':copy.deepcopy(row['hashes']),
            'chart_path':row['path'],'audio_path':row['audio'],'accept_anchor_map':accept_anchors}


@pytest.mark.parametrize('shift',[-500,0,500,123.456,-123.456,60000,-60000])
def test_normalize_preserves_music_across_tempo_and_meter_changes(shift):
    song=Song(metadata={'Offset':'0.2','SongIniDelay':'100'},
              tracks={'Expert':[Note(0,0,500),Note(768,4,192)],'Medium':[Note(192,1,192)]},
              tempos=[(0,Fraction(500000)),(192,Fraction(400000)),(576,Fraction(600000))],
              signatures=[(0,4,4),(576,3,4)],events=[(0,'section Intro'),(1200,'end')],
              phrases={'Expert':[Phrase(0,2,768)]},modifiers={'Expert':[(768,'N 5 0')]})
    original=copy.deepcopy(song);out,plan=normalize(song,shift,44100)
    assert song==original
    ticks=plan['chart_lead_ticks'];pad=plan['audio_padding_frames']/44100
    assert ticks%768==0
    assert out.tempos==[song.tempos[0]]+[(t+ticks,v) for t,v in song.tempos[1:]]
    assert out.signatures==[song.signatures[0]]+[(t+ticks,n,d) for t,n,d in song.signatures[1:]]
    for difficulty,notes in song.tracks.items():
        for before,after in zip(notes,out.tracks[difficulty]):
            assert after.lane==before.lane and after.length==before.length
            for old_tick,new_tick in [(before.tick,after.tick),(before.tick+before.length,after.tick+after.length)]:
                assert out.seconds(new_tick)-pad==pytest.approx(song.seconds(old_tick)+shift/1000,abs=.5/44100+1e-12)
    assert out.events==[(t+ticks,e) for t,e in song.events]
    assert out.phrases['Expert']==[Phrase(ticks,2,768)]
    assert out.modifiers['Expert']==[(768+ticks,'N 5 0')]
    assert out.metadata['Offset']==out.metadata['SongIniDelay']==out.ini_metadata['delay']=='0'


@pytest.mark.parametrize('value',[float('nan'),float('inf'),60001,-60001])
def test_bad_shifts_are_rejected(value):
    with pytest.raises(ChartError):normalize(Song(),value,44100)


def test_audio_padding_retains_recording_and_frame_count(tmp_path):
    sr=22050;data=np.zeros((sr,2),dtype='float32');data[4000,0]=.7;data[12000,1]=.7
    source=tmp_path/'original.wav';target=tmp_path/'song.ogg';sf.write(source,data,sr,subtype='FLOAT')
    digest=fingerprint(source);report=export_ogg(source,target,{'Name':'Sync study'},padding_frames=12345)
    decoded,rate=sf.read(target,always_2d=True)
    assert rate==sr and decoded.shape==(sr+12345,2)
    for lane,peak in enumerate([4000,12000]):assert abs(np.argmax(abs(decoded[:,lane]))-(12345+peak))<=1
    assert np.max(abs(decoded[:10000]))<.001
    assert report['padding_frames']==12345 and report['trimmed_frames']==0 and report['timing_shift_applied']
    assert fingerprint(source)==digest


@pytest.mark.parametrize('shift',[-150,0,250])
def test_review_resolves_blocker_and_exports_logged_zero_offset_copy(tmp_path,shift):
    path=fixture(tmp_path/'source',{'Name':'Sync study','Artist':'Artist','Offset':'0.25'})
    (path.parent/'song.ini').write_text('[song]\ndelay = 100\npreview_start_time = 20\n',encoding='utf-8')
    before={str(p):fingerprint(p) for p in path.parent.iterdir()}
    row=inspect_chart(path);assert any('Offset' in e for e in row['errors'])
    fixed=inspect_chart(path,sync_review=review(row,shift));assert not fixed['errors']
    assert not any('set the same delay' in w for w in fixed['warnings'])
    result=export_cleaned([fixed],tmp_path/'output',path.parent)[0];assert result['status']=='exported'
    folder=Path(result['folder']);out=read_chart(folder/'notes.chart')
    details=json.loads((folder/'validation.json').read_text(encoding='utf-8'))
    assert out.metadata['Offset']=='0' and 'delay = 0' in (folder/'song.ini').read_text(encoding='utf-8')
    assert details['synchronization']['reviewed_shift_ms']==shift
    assert details['source_ini_metadata']['delay']=='100'
    assert sf.info(folder/'song.ogg').frames==4410+fixed['synchronization']['audio_padding_frames']
    assert 'SYNCHRONIZATION' in (tmp_path/'output'/'cleanup.log').read_text(encoding='utf-8')
    assert before=={str(p):fingerprint(p) for p in path.parent.iterdir()}


@pytest.mark.parametrize('changed',['chart','ini','audio','audio_path'])
def test_changed_sources_expire_review(tmp_path,changed):
    path=fixture(tmp_path/'source',{'Name':'Song','Artist':'Artist','Offset':'0.2'})
    ini=path.parent/'song.ini';ini.write_text('[song]\ndelay=100\n',encoding='utf-8')
    row=inspect_chart(path);accepted=review(row)
    if changed=='chart':path.write_text(path.read_text(encoding='utf-8')+'\n',encoding='utf-8')
    if changed=='ini':ini.write_text('[song]\ndelay=200\n',encoding='utf-8')
    if changed=='audio':sf.write(path.parent/'song.wav',np.zeros(2205),44100)
    audio=None
    if changed=='audio_path':
        import shutil
        audio=path.parent/'different.wav';shutil.copyfile(path.parent/'song.wav',audio)
    checked=inspect_chart(path,audio=audio,sync_review=accepted)
    assert any('expired' in e for e in checked['errors']) and 'synchronization' not in checked


def test_metadata_recheck_retains_timing_without_double_shift(tmp_path):
    path=fixture(tmp_path/'source',{'Name':'Song','Artist':'Artist','Offset':'0.2'})
    row=inspect_chart(path);accepted=review(row,333)
    once=inspect_chart(path,sync_review=accepted)
    twice=inspect_chart(path,metadata={'Name':'Correct title'},sync_review=once['sync_review'])
    assert not twice['errors'] and twice['song'].tracks==once['song'].tracks
    assert twice['song'].metadata['Name']=='Correct title'


def anchored(path,stamp=500000,tick=192):
    text=path.read_text(encoding='utf-8').replace('[SyncTrack]\n{',f'[SyncTrack]\n{{\n  {tick} = A {stamp}')
    path.write_text(text,encoding='utf-8');return path


def test_matching_editor_anchor_removed_without_changing_tempo_or_notes(tmp_path):
    path=fixture(tmp_path/'source',tracks={'Expert':[Note(192,0,96)]})
    expected=read_chart(path);anchored(path)
    with pytest.raises(ChartError,match='anchors'):read_chart(path)
    row=inspect_chart(path);assert not row['errors']
    assert row['song'].tempos==expected.tempos and row['song'].tracks==expected.tracks
    assert not row['song'].anchors
    result=export_cleaned([row],tmp_path/'out',path.parent)[0];assert result['status']=='exported'
    assert '= A ' not in (Path(result['folder'])/'notes.chart').read_text(encoding='utf-8')
    assert row['anchor_checks'][0]['difference_ms']==0


def test_conflicting_anchor_requires_explicit_existing_bpm_choice(tmp_path):
    path=anchored(fixture(tmp_path/'source'),stamp=750000)
    row=inspect_chart(path);assert any('anchor timestamps' in e for e in row['errors'])
    assert inspect_chart(path,sync_review=review(row,0))['errors']
    fixed=inspect_chart(path,sync_review=review(row,0,True));assert not fixed['errors']
    assert fixed['song'].tempos==row['sync_source'].tempos
    assert fixed['anchor_checks'][0]['difference_ms']==250


@pytest.mark.parametrize('tick,stamp',[(96,250000),(192,-1)])
def test_unpaired_or_invalid_anchors_stay_blocked(tmp_path,tick,stamp):
    path=anchored(fixture(tmp_path/'source'),stamp,tick)
    assert inspect_chart(path)['errors']


def test_unreviewed_anchors_cannot_be_silently_written(tmp_path):
    song=Song(anchors=[(0,0)])
    with pytest.raises(ChartError,match='anchors'):write_chart(song,tmp_path/'out.chart')


def test_preview_times_follow_the_padded_recording():
    song=Song(metadata={'PreviewStart':'10','PreviewEnd':'20'},
              ini_metadata={'preview_start_time':'10000','preview_end_time':'-1'})
    out,plan=normalize(song,-250,44100)
    assert float(out.metadata['PreviewStart'])==10.25
    assert float(out.metadata['PreviewEnd'])==20.25
    assert out.ini_metadata['preview_start_time']=='10250'
    assert out.ini_metadata['preview_end_time']=='-1'


def test_duplicate_editor_anchors_are_not_silently_resolved(tmp_path):
    path=anchored(anchored(fixture(tmp_path/'source')))
    assert any('Duplicate tempo anchors' in e for e in inspect_chart(path)['errors'])
