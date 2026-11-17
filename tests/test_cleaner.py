import copy
import json
from fractions import Fraction
from pathlib import Path
import numpy as np
import pytest
import soundfile as sf
from gh3studio.model import Song,Note,ChartError
from gh3studio.chartio import write_chart,read_chart
from gh3studio.cleaner import inspect_chart,scan_charts,export_cleaned,fingerprint


def fixture(folder,metadata=None,tracks=None):
    folder.mkdir(parents=True)
    song=Song(metadata=metadata or {'Name':'Song †','Artist':'Artist'},tracks=tracks or {'Expert':[Note(0,0,300),Note(96,1),Note(192,4)],'Hard':[Note(0,2)]},modifiers={'Expert':[(0,'N 6 0'),(192,'N 7 0')]})
    song.tempos=[(0,Fraction(500000)),(192,Fraction(400000))]
    write_chart(song,folder/'notes.chart');sf.write(folder/'song.wav',np.zeros((4410,2)),44100)
    return folder/'notes.chart'


def test_recursive_export_all_difficulties_without_inventing_medium(tmp_path):
    source=tmp_path/'sources';path=fixture(source/'one');fixture(source/'sub'/'two')
    before={str(p):fingerprint(p) for p in source.rglob('*') if p.is_file()}
    rows=scan_charts(source);assert len(rows)==2 and all(not r['errors'] for r in rows)
    assert all(r['changes'] for r in rows)
    results=export_cleaned(rows,tmp_path/'cleaned',source)
    assert all(r['status']=='exported' for r in results)
    for result in results:
        folder=Path(result['folder']);song=read_chart(folder/'notes.chart')
        assert set(song.tracks)=={'Expert','Hard'}
        assert song.tracks['Expert'][0].length==96
        assert song.tracks['Expert'][-1].lane==4
        assert not any(song.modifiers.values())
        assert song.tempos==read_chart(path).tempos
        assert sf.info(folder/'song.ogg').subtype=='VORBIS'
        assert 'name = Song †' in (folder/'song.ini').read_text(encoding='utf-8')
    assert before=={str(p):fingerprint(p) for p in source.rglob('*') if p.is_file()}


def test_missing_metadata_and_audio_block_until_corrected(tmp_path):
    path=fixture(tmp_path/'source',{'Name':'unknown','Artist':'unknown'})
    (path.parent/'song.wav').rename(path.parent/'guitar.wav')
    row=inspect_chart(path);assert len(row['errors'])==3
    fixed=inspect_chart(path,path.parent/'guitar.wav',{'Name':'Verified title','Artist':'Verified artist'})
    assert not fixed['errors'] and fixed['song'].metadata['Name']=='Verified title'


def test_medium_orange_sustain_preserved_and_unsupported_phrase_removed(tmp_path):
    path=fixture(tmp_path/'source',tracks={'Medium':[Note(0,4,96),Note(192,0)]})
    text=path.read_text(encoding='utf-8').replace('[MediumSingle]\n{','[MediumSingle]\n{\n  0 = S 99 48')
    path.write_text(text,encoding='utf-8')
    with pytest.raises(ChartError):read_chart(path)
    row=inspect_chart(path);assert not row['errors']
    assert len(row['song'].tracks['Medium'])==2
    assert row['song'].tracks['Medium'][0].length==96
    assert all(n.lane<4 for n in row['song'].tracks['Medium'])
    assert any(c.get('marker')=='S 99 48' for c in row['changes'])


def test_source_change_and_per_song_failure_do_not_overwrite(tmp_path):
    source=tmp_path/'source';one=fixture(source/'one');fixture(source/'two')
    rows=scan_charts(source);one.write_text(one.read_text(encoding='utf-8')+'\n',encoding='utf-8')
    dest=tmp_path/'output';results=export_cleaned(rows,dest,source)
    assert [r['status'] for r in results]==['failed','exported']
    assert 'changed' in results[0]['error']
    with pytest.raises(ChartError):export_cleaned(rows,dest,source)
    with pytest.raises(ChartError):export_cleaned(rows,source/'out',source)


def test_ambiguous_chart_and_cancel(tmp_path):
    path=fixture(tmp_path/'source');path.rename(path.parent/'a.chart')
    (path.parent/'b.chart').write_text((path.parent/'a.chart').read_text(encoding='utf-8'),encoding='utf-8')
    assert 'Multiple' in scan_charts(path.parent)[0]['errors'][0]
    assert scan_charts(path.parent,lambda:True)==[]
    results=export_cleaned([],tmp_path/'out',path.parent,lambda:True)
    assert results==[] and json.loads((tmp_path/'out'/'cleanup_summary.json').read_text(encoding='utf-8'))['cancelled']


def test_offset_and_nonstandard_meter_block(tmp_path):
    path=fixture(tmp_path/'source',{'Name':'Song','Artist':'Artist','Offset':'0.1'})
    assert 'Offset' in inspect_chart(path)['errors'][0]
    song=read_chart(path);song.metadata['Offset']='0';song.signatures=[(0,6,8)];write_chart(song,path)
    assert 'Non-/4' in inspect_chart(path)['errors'][0]


def test_ogg_tags_reconciled_in_clean_export(tmp_path):
    path=fixture(tmp_path/'source');(path.parent/'song.wav').unlink()
    with sf.SoundFile(path.parent/'song.ogg','w',samplerate=44100,channels=1,format='OGG',subtype='VORBIS') as stream:
        stream.title='Wrong';stream.artist='Wrong';stream.write(np.zeros(4410))
    row=inspect_chart(path);assert not row['errors']
    results=export_cleaned([row],tmp_path/'out',path.parent)
    with sf.SoundFile(Path(results[0]['folder'])/'song.ogg') as stream:
        assert stream.copy_metadata()['title']=='Song †'
        assert stream.copy_metadata()['artist']=='Artist'


@pytest.mark.parametrize('broken',[False,True])
def test_metadata_edits_survive_chart_errors(tmp_path,broken):
    path=fixture(tmp_path/'source',{'Name':'Old title','Artist':'Old artist','Offset':'0.1'})
    if broken:path.write_text('invalid chart syntax',encoding='utf-8')
    edits={'Name':'Corrected † title','Artist':'Correct artist','Album':'Album','Year':'1999','Charter':''}
    row=inspect_chart(path,path.parent/'song.wav',edits)
    assert row['errors'] and row['song'] is None
    assert all(row['metadata'][k]==v for k,v in edits.items())
    assert row['audio']==str(path.parent/'song.wav')
    again=inspect_chart(path,row['audio'],row['metadata'])
    assert all(again['metadata'][k]==v for k,v in edits.items())


def test_metadata_recheck_does_not_restore_stale_timing_fields(tmp_path):
    path=fixture(tmp_path/'source',{'Name':'Song','Artist':'Artist','Offset':'0.1'})
    old=inspect_chart(path)
    song=read_chart(path);song.metadata['Offset']='0';write_chart(song,path)
    fixed=inspect_chart(path,metadata=dict(old['metadata'],Name='Corrected'))
    assert not fixed['errors']
    assert fixed['song'].metadata['Offset']=='0'
    assert fixed['metadata']['Name']=='Corrected'
