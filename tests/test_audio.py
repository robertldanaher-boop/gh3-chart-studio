import hashlib,json
from pathlib import Path
from fractions import Fraction
import numpy as np
import pytest
import soundfile as sf
from gh3studio.audio_analysis import analyze_audio,AudioSettings
from gh3studio.audio_chart import make_draft,alignment_report,TempoClock
from gh3studio.model import Song,Note,ChartError
from gh3studio.service import export_bundle

RATE=22050

def tones(starts,duration=9,rate=RATE):
    samples=np.zeros(round(duration*rate),dtype=np.float32)
    for i,start in enumerate(starts):
        t=np.arange(round(rate*.12))/rate;burst=.7*np.sin(2*np.pi*(220+i%4*110)*t)*np.exp(-t*30)
        pos=round(start*rate);samples[pos:pos+len(t)]+=burst[:max(0,min(len(t),len(samples)-pos))]
    return samples

@pytest.fixture
def recording(tmp_path):
    starts=np.arange(.5,8,.5);path=tmp_path/'study.wav';sf.write(path,tones(starts),RATE)
    return path,starts

def test_known_attacks_and_tempo(recording):
    path,starts=recording;original=path.read_bytes();analysis=analyze_audio(path)
    assert len(analysis.onsets)==len(starts)
    assert np.max(np.abs(np.array([o['time'] for o in analysis.onsets])-starts))<.01
    assert analysis.bpm==pytest.approx(120,abs=1) and analysis.beat_fit>.9
    assert analysis.quiet_spans and analysis.waveform and analysis.sections
    assert analysis.source_hash==hashlib.sha256(original).hexdigest() and path.read_bytes()==original
    json.dumps(analysis.report())

@pytest.mark.parametrize('extension,format,subtype',[('wav','WAV','PCM_16'),('flac','FLAC','PCM_16'),('ogg','OGG','VORBIS'),('mp3','MP3','MPEG_LAYER_III')])
def test_real_codec_decode(tmp_path,extension,format,subtype):
    path=tmp_path/f'codec.{extension}';starts=np.arange(.5,4,.5)
    sf.write(path,tones(starts,5),RATE,format=format,subtype=subtype)
    analysis=analyze_audio(path)
    assert len(analysis.onsets)==len(starts)
    assert np.max(np.abs(np.array([o['time'] for o in analysis.onsets])-starts))<.04
    assert analysis.bpm==pytest.approx(120,abs=2)

def test_silence_never_invents_chart(tmp_path):
    path=tmp_path/'silence.wav';sf.write(path,np.zeros(RATE*3),RATE)
    analysis=analyze_audio(path)
    assert analysis.onsets==[] and analysis.bpm is None
    with pytest.raises(ChartError,match='No detected'):make_draft(analysis)

def test_manual_bpm(recording):
    analysis=analyze_audio(recording[0],AudioSettings(manual_bpm=137.5))
    assert analysis.bpm==137.5 and analysis.beat_times

@pytest.mark.parametrize('rate',[8000,44100,48000])
def test_resampling_preserves_attack_times(tmp_path,rate):
    starts=np.arange(.5,4,.5);path=tmp_path/'resample.wav';sf.write(path,tones(starts,5,rate),rate)
    analysis=analyze_audio(path)
    assert analysis.original_rate==rate
    assert len(analysis.onsets)==len(starts)
    assert np.max(np.abs(np.array([o['time'] for o in analysis.onsets])-starts))<.015

def test_antiphase_stereo(tmp_path):
    x=tones(np.arange(.5,4,.5),5);path=tmp_path/'stereo.wav';sf.write(path,np.column_stack((x,-x)),RATE)
    a=analyze_audio(path)
    assert len(a.onsets)==7 and a.original_channels==2
    assert any('cancellation' in w for w in a.warnings)

def test_cancellation(recording):
    with pytest.raises(ChartError,match='Cancelled'):analyze_audio(recording[0],cancelled=lambda:True)

def test_malformed_audio(tmp_path):
    path=tmp_path/'broken.mp3';path.write_bytes(b'not an audio recording')
    with pytest.raises(ChartError,match='decoder'):analyze_audio(path)

def test_nonfinite_audio_rejected(tmp_path):
    path=tmp_path/'nan.wav';sf.write(path,np.full(1000,np.nan),RATE,subtype='FLOAT')
    with pytest.raises(ChartError,match='non-finite'):analyze_audio(path)

@pytest.mark.parametrize('settings',[AudioSettings(sensitivity=0),AudioSettings(min_interval_ms=1),AudioSettings(manual_bpm=float('nan')),AudioSettings(manual_bpm=10)])
def test_settings_validation(settings):
    with pytest.raises(ChartError):settings.validate()

def test_draft_roundtrip_and_no_orange(recording,tmp_path):
    analysis=analyze_audio(recording[0],AudioSettings(manual_bpm=120))
    song,report=make_draft(analysis)
    assert len(song.tracks['Medium'])==len(analysis.onsets)
    assert {n.lane for n in song.tracks['Medium']}<=set(range(4))
    assert all(n.length==0 for n in song.tracks['Medium']) and song.phrases['Medium']==[]
    assert report['max_tick_rounding_error_ms']<1
    export_bundle(song,report,tmp_path/'audio-export',recording[0])
    assert (tmp_path/'audio-export'/'notes.mid').is_file()

def test_preserves_authored_tempo_map_and_source(recording):
    import copy
    analysis=analyze_audio(recording[0])
    original=Song(resolution=480,tempos=[(0,Fraction(500000)),(1920,Fraction(666667))],tracks={'Expert':[Note(0,4,480)]})
    unchanged=copy.deepcopy(original);draft,report=make_draft(analysis,template=original)
    assert original==unchanged and draft.tempos==original.tempos and draft.tracks['Expert']==original.tracks['Expert']
    assert max(abs(draft.seconds(n.tick)-o['time']) for n,o in zip(draft.tracks['Medium'],analysis.onsets))<.001

def test_clock_exact_cross_tempos():
    song=Song(resolution=480,tempos=[(0,Fraction(500000)),(1920,Fraction(1000000))]);clock=TempoClock(song)
    assert clock.tick(1)==960 and clock.tick(2)==1920 and clock.tick(3)==2400

def test_offset_and_global_diagnostics(recording):
    a=analyze_audio(recording[0],AudioSettings(manual_bpm=120));song,_=make_draft(a)
    shifted,_=make_draft(a,shift_ms=120)
    assert all(shifted.seconds(n.tick)-song.seconds(o.tick)==pytest.approx(.12,abs=.001) for n,o in zip(shifted.tracks['Medium'],song.tracks['Medium']))
    report=alignment_report(shifted,'Medium',a)
    assert report['suggested_additional_shift_ms']==pytest.approx(-120,abs=1)
    assert report['interpretation']=='Possible global offset'
    corrected=alignment_report(shifted,'Medium',a,-120)
    assert corrected['median_abs_error_ms']<1

def test_tempo_drift_diagnostics(recording):
    a=analyze_audio(recording[0],AudioSettings(manual_bpm=120));song,_=make_draft(a)
    song.tempos=[(0,Fraction(510000))]
    report=alignment_report(song,'Medium',a)
    assert abs(report['drift_ms_per_minute'])>20 and 'tempo drift' in report['interpretation']

def test_negative_shift_and_cancel_draft(recording):
    a=analyze_audio(recording[0])
    with pytest.raises(ChartError,match='before tick zero'):make_draft(a,shift_ms=-1000)
    with pytest.raises(ChartError,match='Cancelled'):make_draft(a,cancelled=lambda:True)

def test_offbeat_attacks_not_quantized(tmp_path):
    starts=[.5,.83,1.16,1.73,2.21,2.67,3.15,3.8];path=tmp_path/'offbeat.wav';sf.write(path,tones(starts,5),RATE)
    a=analyze_audio(path,AudioSettings(manual_bpm=120));song,_=make_draft(a)
    assert len(song.tracks['Medium'])==len(starts)
    assert max(abs(song.seconds(n.tick)-t) for n,t in zip(song.tracks['Medium'],starts))<.012
    assert any(n.tick%(song.resolution//4)!=0 for n in song.tracks['Medium'])

def test_audio_draft_uses_learned_patterns(recording,tmp_path):
    from gh3studio.patterns import PatternStore,scan_folder
    from gh3studio.chartio import write_chart
    root=tmp_path/'corpus';root.mkdir();write_chart(Song(tracks={'Expert':[Note(i*192,4) for i in range(8)]}),root/'donor.chart')
    store=PatternStore(tmp_path/'library.sqlite3');scan_folder(root,store)
    a=analyze_audio(recording[0]);song,report=make_draft(a,store=store,seed=42)
    assert {n.lane for n in song.tracks['Medium']}=={3}
    assert report['pattern_transfer']['pattern_matches']

def test_preserve_existing_end_and_full_unicode_title(recording,tmp_path):
    a=analyze_audio(recording[0]);template=Song(metadata={'Name':'曲 — Demo'},tracks={'Expert':[Note(0,4)]},events=[(10000,'end')])
    song,report=make_draft(a,template=template)
    assert (10000,'end') in song.events
    details=export_bundle(song,report,tmp_path/'unicode')
    assert any('Unicode' in w for w in details['warnings'])
    from gh3studio.midiio import read_midi
    assert read_midi(tmp_path/'unicode'/'notes.mid','legacy').metadata['Name']=='曲 — Demo'
