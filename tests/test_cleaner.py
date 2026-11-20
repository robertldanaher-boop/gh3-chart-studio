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
    assert {Path(r['folder']).name for r in results}=={'Artist - Song †','Artist - Song † (2)'}
    for result in results:
        folder=Path(result['folder']);song=read_chart(folder/'notes.chart')
        assert set(song.tracks)=={'Expert','Hard'}
        assert song.tracks['Expert'][0].length==96
        assert song.tracks['Expert'][-1].lane==4
        # 0.18.5: only TheGHOST forced-note flips remain; the source tap at 0 plays as a HOPO, the open note is gone.
        assert song.modifiers.get('Expert')==[(0,'N 5 0')] and not song.modifiers.get('Hard')
        from gh3studio.hopo import effective_states
        assert effective_states(song,'Expert')[0] is True
        assert song.tempos==read_chart(path).tempos
        assert sf.info(folder/'song.ogg').subtype=='VORBIS'
        assert 'name = Song †' in (folder/'song.ini').read_text(encoding='utf-8')
    assert before=={str(p):fingerprint(p) for p in source.rglob('*') if p.is_file()}


def test_missing_metadata_and_audio_block_until_corrected(tmp_path):
    path=fixture(tmp_path/'source',{'Name':'unknown','Artist':'unknown'})
    (path.parent/'song.wav').rename(path.parent/'preview.wav')
    row=inspect_chart(path);assert len(row['errors'])==3
    fixed=inspect_chart(path,path.parent/'preview.wav',{'Name':'Verified title','Artist':'Verified artist'})
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
    repeated=export_cleaned(rows,dest,source)
    assert [r['status'] for r in repeated]==['failed','exported']
    assert repeated[1]['folder']==results[1]['folder']
    with pytest.raises(ChartError):export_cleaned(rows,source/'out',source)


def test_ambiguous_chart_and_cancel(tmp_path):
    path=fixture(tmp_path/'source');path.rename(path.parent/'a.chart')
    (path.parent/'b.chart').write_text((path.parent/'a.chart').read_text(encoding='utf-8'),encoding='utf-8')
    assert 'Multiple' in scan_charts(path.parent)[0]['errors'][0]
    assert scan_charts(path.parent,lambda:True)==[]
    results=export_cleaned([],tmp_path/'out',path.parent,lambda:True)
    assert results==[] and json.loads((tmp_path/'out'/'cleanup_summary.json').read_text(encoding='utf-8'))['cancelled']


def test_offset_auto_resolved_but_nonstandard_meter_blocks(tmp_path):
    path=fixture(tmp_path/'source',{'Name':'Song','Artist':'Artist','Offset':'0.1'})
    row=inspect_chart(path);assert not row['errors']
    assert row['synchronization']['automatic'] and row['synchronization']['reviewed_shift_ms']==0
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
    else:
        song=read_chart(path);song.signatures=[(0,6,8)];write_chart(song,path)
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


def test_single_packaged_audio_named_guitar_auto_matches(tmp_path):
    path=fixture(tmp_path/'artist'/'album'/'song')
    (path.parent/'song.wav').rename(path.parent/'guitar.wav')
    sf.write(path.parent/'preview.wav',np.zeros(100),44100)
    rows=scan_charts(tmp_path)
    assert len(rows)==1 and not rows[0]['errors']
    assert Path(rows[0]['audio']).name=='guitar.wav'


def test_separate_instrument_tracks_are_mixed_not_blocked(tmp_path):
    # 0.15.0 policy (Bob): separate downloaded tracks are mixed into one song.ogg.
    path=fixture(tmp_path/'song')
    (path.parent/'song.wav').rename(path.parent/'guitar.wav')
    sf.write(path.parent/'bass.wav',np.zeros(100),44100)
    row=inspect_chart(path)
    assert [Path(p).name for p in row['audio_stems']]==['guitar.wav','bass.wav']
    assert not [e for e in row['errors'] if 'audio' in e.lower()]
    assert set(row['hashes'])>={str(path.parent/'guitar.wav'),str(path.parent/'bass.wav')}
    assert any(c.get('action')=='mix separate audio tracks into song.ogg' for c in row['changes'])


def test_unreadable_stem_blocks_with_its_name(tmp_path):
    path=fixture(tmp_path/'song')
    (path.parent/'guitar.wav').write_bytes(b'not audio')
    row=inspect_chart(path)
    assert any('guitar.wav' in e for e in row['errors'])


def test_separate_tracks_export_one_mixed_song_ogg(tmp_path):
    source=tmp_path/'sources';path=fixture(source/'stems')
    folder=path.parent
    tone=lambda n,amp:amp*np.sin(2*np.pi*440*np.arange(n)/44100)
    sf.write(folder/'song.wav',np.stack([tone(4410,.25)]*2,axis=1),44100)
    sf.write(folder/'guitar.ogg',tone(8820,.25),44100,format='OGG',subtype='VORBIS')  # mono, longer
    sf.write(folder/'rhythm.wav',np.stack([tone(4410,.6)]*2,axis=1),44100)  # in phase: peaks sum to ~1.1
    sf.write(folder/'preview.ogg',np.zeros(441),44100,format='OGG',subtype='VORBIS')
    before={str(p):fingerprint(p) for p in folder.iterdir()}
    rows=scan_charts(source)
    assert not rows[0]['errors'] and [Path(p).name for p in rows[0]['audio_stems']]==['song.wav','guitar.ogg','rhythm.wav']
    result=export_cleaned(rows,tmp_path/'out',source)[0]
    assert result['status']=='exported' and 'Mixed 3 audio tracks' in result['audio_mixed']
    out=Path(result['folder'])
    data,rate=sf.read(out/'song.ogg',always_2d=True)
    assert rate==44100 and data.shape[1]==2 and abs(len(data)-8820)<1100
    assert np.abs(data).max()<1.0  # decoded Ogg must not clip after the anti-clip turn-down
    details=json.loads((out/'validation.json').read_text(encoding='utf-8'))
    mix=details['audio_stems']
    # guitar.ogg is the longest track; the shorter song/rhythm tracks are padded with silence.
    assert mix['turned_down'] and 'padded_frames' not in mix['stems'][1]
    assert mix['stems'][0]['padded_frames']==mix['stems'][2]['padded_frames']==mix['frames']-4410>0
    assert {s['file'] for s in mix['stems']}=={'song.wav','guitar.ogg','rhythm.wav'}
    assert before=={str(p):fingerprint(p) for p in folder.iterdir()}
    assert not (out/'guitar.ogg').exists() and not (out/'preview.ogg').exists()


def test_scan_removes_track_number_prefix_but_manual_edit_wins(tmp_path):
    path=fixture(tmp_path/'song',metadata={'Name':'3. Song Title','Artist':'1. The Band'})
    row=inspect_chart(path)
    assert row['metadata']['Name']=='Song Title' and row['metadata']['Artist']=='The Band'
    assert row['song'].metadata['Name']=='Song Title'
    assert any(c.get('action')=='remove track-number prefix' for c in row['changes'])
    assert any('track-number prefix' in w for w in row['warnings'])
    edited=inspect_chart(path,metadata={'Name':'3. Song Title','Artist':'1. The Band'})
    assert edited['metadata']['Name']=='3. Song Title'  # a deliberate manual entry is kept
