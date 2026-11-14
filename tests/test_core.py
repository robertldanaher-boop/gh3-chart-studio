import copy
import random
from fractions import Fraction
from pathlib import Path
import mido
import pytest
from gh3studio.model import Song,Note,Phrase,ChartError
from gh3studio.converter import Settings,convert
from gh3studio.chartio import read_chart,write_chart
from gh3studio.midiio import read_midi,write_midi
from gh3studio.service import load,export_bundle
from gh3studio.validation import ensure_valid
FIXTURE=Path(__file__).parents[1]/'examples'/'technical-study.chart'
@pytest.fixture
def song(): return load(FIXTURE)
def test_fixture(song):
    assert song.metadata['Name']=='Four-Fret Technical Study'
    assert song.tempos==[(0,Fraction(500000)),(1536,Fraction(400000)),(3072,Fraction(600000))]
    assert song.seconds(3072)==pytest.approx(7.2)
@pytest.mark.parametrize('source',['Expert','Hard'])
def test_timing_immutable(song,source):
    original=copy.deepcopy(song); result,report=convert(song,Settings(source=source,chords=6))
    assert song==original and result.tracks[source]==song.tracks[source]
    assert {n.tick for n in result.tracks['Medium']}=={n.tick for n in song.tracks[source]}
    assert {n.lane for n in result.tracks['Medium']}<=set(range(4))
    lengths={n.tick:n.length for n in song.tracks[source]}
    assert all(n.length==lengths[n.tick] for n in result.tracks['Medium'])
    assert result.tempos==song.tempos and report['removed_events']==0
@pytest.mark.parametrize('density',range(1,7))
def test_density(song,density):
    result,report=convert(song,Settings(density=density))
    assert {n.tick for n in result.tracks['Medium']}<={n.tick for n in song.tracks['Expert']}
    assert report['medium_events']<=report['source_events']
def test_controls(song):
    dense,_=convert(song,Settings(density=6,chords=6)); sparse,_=convert(song,Settings(density=1,chords=1))
    assert len(sparse.tracks['Medium'])<len(dense.tracks['Medium'])
    assert len({n.tick for n in sparse.tracks['Medium']})==len(sparse.tracks['Medium'])
    s=Song(tracks={'Expert':[Note(i*192,l) for i,l in enumerate([0,4,0,4,1,4,2,0])]})
    low,_=convert(s,Settings(movement=1)); high,_=convert(s,Settings(movement=6))
    assert low.tracks['Medium']!=high.tracks['Medium']
def test_reproducible(song): assert convert(song)==convert(song)
@pytest.mark.parametrize('seed',range(12))
def test_random_roundtrip(seed,tmp_path):
    rng=random.Random(seed); notes=[]
    for i in range(120):
        length=rng.choice([0,0,48,96])
        for lane in sorted(rng.sample(range(5),rng.randint(1,5))): notes.append(Note(i*192,lane,length))
    result,report=convert(Song(tracks={'Expert':notes}),Settings(chords=6))
    export_bundle(result,report,tmp_path/'out')
    assert all(n.lane<4 for n in read_chart(tmp_path/'out'/'notes.chart').tracks['Medium'])
def test_midi_wire_and_phrases(song,tmp_path):
    original=FIXTURE.read_bytes(); result,report=convert(song)
    details=export_bundle(result,report,tmp_path/'out',FIXTURE)
    assert FIXTURE.read_bytes()==original
    mid=mido.MidiFile(tmp_path/'out'/'notes.mid'); guitar=next(t for t in mid.tracks if t.name=='PART GUITAR')
    active=set(); seen=set(); absolute=0; onsets=[]
    for m in guitar:
        absolute+=m.time
        if m.type=='note_on' and m.velocity:
            assert m.note not in active; active.add(m.note); seen.add(m.note)
            if 72<=m.note<=76: onsets.append(absolute)
        elif m.type=='note_off':
            assert m.note in active; active.remove(m.note)
    assert not active and 76 not in seen and 79 in seen and 116 not in seen
    assert set(onsets)=={n.tick for n in result.tracks['Medium']}
    assert details['exports']['notes.mid']['reopened']
    reopened=read_midi(tmp_path/'out'/'notes.mid','legacy')
    assert reopened.metadata==result.metadata and reopened.phrases['Medium']==result.phrases['Medium']
@pytest.mark.parametrize('fmt',['chart','mid'])
def test_reimport(song,tmp_path,fmt):
    path=tmp_path/('source.'+fmt); (write_chart if fmt=='chart' else write_midi)(song,path)
    result,_=convert(load(path,'legacy'),Settings(source='Hard'))
    assert result.tracks['Medium']
def test_overwrite(song,tmp_path):
    result,report=convert(song); target=tmp_path/'out'; target.mkdir(); (target/'keep').write_text('safe')
    with pytest.raises(ChartError,match='already exists'): export_bundle(result,report,target)
    assert (target/'keep').read_text()=='safe'
def test_failure_atomic(song,tmp_path,monkeypatch):
    from gh3studio import service
    result,report=convert(song)
    def broken(*args): raise OSError('disk failure')
    monkeypatch.setattr(service,'write_midi',broken)
    with pytest.raises(OSError): export_bundle(result,report,tmp_path/'out')
    assert list(tmp_path.iterdir())==[]
@pytest.mark.parametrize('bad',[Note(-1,0),Note(0,5),Note(0,0,-1)])
def test_invalid(bad):
    with pytest.raises(ChartError): ensure_valid(Song(tracks={'Expert':[bad]}))
def test_orange_block(song,tmp_path):
    song.tracks['Medium']=[Note(0,4)]
    with pytest.raises(ChartError,match='ORANGE'): export_bundle(song,{},tmp_path/'out')
@pytest.mark.parametrize('notes',[[Note(0,0,192),Note(96,1)],[Note(0,0,192),Note(0,1,96)],[Note(0,0),Note(0,0)],[Note(0,0,192),Note(96,0)]])
def test_invalid_shapes(notes):
    with pytest.raises(ChartError): convert(Song(tracks={'Expert':notes}))
def test_modifiers_missing_cancel(song):
    with pytest.raises(ChartError,match='Cancelled'): convert(song,cancelled=lambda:True)
    song.modifiers['Expert']=[(0,'N 5')]
    with pytest.raises(ChartError,match='forced'): convert(song)
    with pytest.raises(ChartError,match='No Expert'): convert(Song())
def test_offset(song,tmp_path):
    song.metadata['Offset']='0.12'; result,report=convert(song)
    with pytest.raises(ChartError,match='Offset'): export_bundle(result,report,tmp_path/'out')
def test_unpaired(tmp_path):
    mid=mido.MidiFile(); tr=mido.MidiTrack(); mid.tracks.append(tr)
    tr.extend([mido.MetaMessage('track_name',name='PART GUITAR'),mido.Message('note_on',note=96,velocity=100)])
    mid.save(tmp_path/'bad.mid')
    with pytest.raises(ChartError,match='Unterminated'): read_midi(tmp_path/'bad.mid')
def test_modern_sp(tmp_path):
    mid=mido.MidiFile(); tr=mido.MidiTrack(); mid.tracks.append(tr)
    tr.extend([mido.MetaMessage('track_name',name='PART GUITAR'),mido.Message('note_on',note=116,velocity=100),mido.Message('note_on',note=96,velocity=100),mido.Message('note_on',note=96,velocity=0,time=192),mido.Message('note_off',note=116,time=192)])
    mid.save(tmp_path/'modern.mid'); result,_=convert(read_midi(tmp_path/'modern.mid'))
    assert result.phrases['Medium']==[Phrase(0,2,384)]
def test_comments_bom(tmp_path):
    text=FIXTURE.read_text().replace('0 = B 120000','0 = B 120000 // tempo')
    path=tmp_path/'test.chart'; path.write_bytes(('\ufeff'+text.replace('\n','\r\n')).encode())
    assert read_chart(path).tempos[0]==(0,Fraction(500000))
@pytest.mark.parametrize('text',['[Song]\n{\nResolution = 192\n','[Song]\n{\n}\n','[Song]\n{\nResolution = 192\n}\n[SyncTrack]\n{\n0 = B 0\n}\n'])
def test_malformed(text,tmp_path):
    path=tmp_path/'bad.chart'; path.write_text(text)
    with pytest.raises(ChartError): read_chart(path)
def test_faceoff(song,tmp_path):
    song.phrases['Expert'] += [Phrase(0,0,384),Phrase(384,1,384)]
    song.phrases['Expert'].sort(key=lambda p:(p.tick,p.kind))
    result,report=convert(song); export_bundle(result,report,tmp_path/'out')
def test_ini(song,tmp_path):
    write_chart(song,tmp_path/'notes.chart'); (tmp_path/'song.ini').write_text('[song]\nname = Preferred title\nartist = 100% original\ndelay = 120\n')
    s=load(tmp_path/'notes.chart')
    assert s.metadata['Name']=='Preferred title' and s.metadata['Artist']=='100% original'
    assert any('delay' in w for w in s.warnings)

def test_fractional_bpm_and_cross_tempo_sustain(tmp_path):
    song=Song(tempos=[(0,Fraction(60000000000,123456)),(240,Fraction(60000000000,98765))],tracks={'Expert':[Note(0,4,384),Note(480,1,192)]})
    result,report=convert(song)
    assert result.tracks['Medium'][0].length==384
    details=export_bundle(result,report,tmp_path/'out')
    assert details['exports']['notes.mid']['max_tempo_boundary_drift_ms']<1
    assert read_chart(tmp_path/'out'/'notes.chart').tempos==song.tempos

def test_high_tick_rejected():
    with pytest.raises(ChartError): ensure_valid(Song(tracks={'Expert':[Note(0x10000000,1)]}))

def test_original_medium_replaced_without_mutation(song):
    song.tracks['Medium']=[Note(1,4)]
    result,_=convert(song)
    assert song.tracks['Medium']==[Note(1,4)]
    assert all(n.lane<4 for n in result.tracks['Medium'])

def test_failed_readback_not_published(song,tmp_path,monkeypatch):
    from gh3studio import service
    result,report=convert(song)
    def invalid(path):
        bad=copy.deepcopy(result);bad.tracks['Medium']=[Note(0,4)];return bad
    monkeypatch.setattr(service,'read_chart',invalid)
    with pytest.raises(ChartError): export_bundle(result,report,tmp_path/'out')
    assert not list(tmp_path.iterdir())
