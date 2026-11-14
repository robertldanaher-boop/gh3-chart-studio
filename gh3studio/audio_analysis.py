"""CPU audio analysis with explicit uncertainty; no instrument transcription."""
import hashlib
import math
from dataclasses import asdict,dataclass
from pathlib import Path
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly,find_peaks,correlate
from scipy.ndimage import median_filter
from .model import ChartError

RATE=22050
HOP=128
FRAME=1024
ALGORITHM='spectral-energy-v1'

@dataclass(frozen=True)
class AudioSettings:
    sensitivity:int=4
    min_interval_ms:int=70
    manual_bpm:float=0
    def validate(self):
        if not 1<=self.sensitivity<=6:raise ChartError('Sensitivity must be 1–6')
        if not 30<=self.min_interval_ms<=1000:raise ChartError('Minimum onset spacing must be 30–1000 ms')
        if not math.isfinite(self.manual_bpm) or (self.manual_bpm!=0 and not 30<=self.manual_bpm<=300):raise ChartError('Manual BPM must be 30–300, or zero for automatic')

@dataclass
class AudioAnalysis:
    source_path:str
    source_hash:str
    duration:float
    original_rate:int
    original_channels:int
    settings:dict
    onsets:list
    bpm:float|None
    tempo_candidates:list
    beat_times:list
    beat_fit:float
    quiet_spans:list
    sections:list
    waveform:list
    warnings:list
    algorithm:str=ALGORITHM
    def report(self):return asdict(self)

def check_cancel(cancelled):
    if cancelled():raise ChartError('Cancelled; audio operation stopped')

def decode(path,cancelled=lambda:False,progress=lambda d,t,p:None):
    path=Path(path)
    if path.suffix.lower() not in ('.wav','.flac','.ogg','.mp3'):raise ChartError('Choose WAV, FLAC, OGG or MP3 audio')
    if path.stat().st_size>512*1024*1024:raise ChartError('Audio input exceeds the 512 MiB safety limit')
    digest=hashlib.sha256()
    with path.open('rb') as f:
        while data:=f.read(1024*1024):
            check_cancel(cancelled);digest.update(data)
    warnings=[];chunks=[];fallback=False
    try:
        with sf.SoundFile(path) as audio:
            sr=audio.samplerate;channels=audio.channels;frames=len(audio)
            if not 8000<=sr<=192000 or not 1<=channels<=8:raise ChartError('Supported audio: 8–192 kHz, 1–8 channels')
            if frames==0:raise ChartError('Audio file is empty')
            if frames/sr>1200 or frames*4>128*1024*1024:raise ChartError('Audio exceeds 20 minutes or the 128 MiB mono analysis limit; analyze a shorter/lower-rate copy')
            done=0
            for block in audio.blocks(blocksize=65536,dtype='float32',always_2d=True):
                check_cancel(cancelled)
                if not np.all(np.isfinite(block)):raise ChartError('Audio contains non-finite sample values')
                mono=block.mean(axis=1)
                energy=np.mean(block.astype(np.float64)**2,axis=0)
                # Avoid falsely interpreting opposite-polarity stereo as silence.
                if channels>1 and np.mean(mono.astype(np.float64)**2)<.01*max(energy):
                    mono=block[:,int(np.argmax(energy))];fallback=True
                chunks.append(mono);done+=len(block);progress(done,frames,'Decoding audio')
    except (RuntimeError,sf.LibsndfileError) as exc:
        raise ChartError(f'Audio decoder failed: {exc}. Try a WAV/FLAC copy if this codec is unavailable.') from exc
    if fallback:warnings.append('Stereo cancellation detected; the strongest channel was used in affected blocks.')
    samples=np.concatenate(chunks);del chunks
    if np.max(np.abs(samples))>=.999:warnings.append('Near-full-scale samples detected; clipping may affect attack estimates.')
    check_cancel(cancelled)
    if sr!=RATE:
        factor=math.gcd(sr,RATE);samples=resample_poly(samples,RATE//factor,sr//factor).astype(np.float32)
    return samples,sr,channels,frames/sr,digest.hexdigest(),warnings

def spectral_features(samples,cancelled=lambda:False,progress=lambda d,t,p:None):
    padded=np.pad(samples,(FRAME//2,FRAME//2))
    frames=np.lib.stride_tricks.sliding_window_view(padded,FRAME)[::HOP]
    window=np.hanning(FRAME);freq=np.fft.rfftfreq(FRAME,1/RATE)
    flux=[];energy=[];centroids=[];previous=np.zeros(FRAME//2+1)
    for start in range(0,len(frames),1024):
        check_cancel(cancelled);part=frames[start:start+1024]
        spectrum=np.abs(np.fft.rfft(part*window,axis=1))
        differences=np.maximum(0,np.diff(spectrum,axis=0,prepend=previous[None,:]))
        flux.extend(np.sqrt(np.sum(differences*differences,axis=1)))
        energy.extend(np.sqrt(np.mean(part.astype(np.float64)**2,axis=1)))
        centroids.extend(np.sum(spectrum*freq,axis=1)/np.maximum(np.sum(spectrum,axis=1),1e-12))
        previous=spectrum[-1];progress(min(start+len(part),len(frames)),len(frames),'Analyzing attacks')
    return np.asarray(flux),np.asarray(energy),np.asarray(centroids)

def estimate_tempo(novelty,onsets,manual_bpm):
    if len(onsets)<3:return (float(manual_bpm) if manual_bpm else None),[],([0.0] if manual_bpm else []),0.0
    strength=novelty.astype(np.float64);strength=np.maximum(0,strength-np.median(strength))
    ac=correlate(strength,strength,mode='full',method='fft')[len(strength)-1:]
    lo=max(1,round(60/200*RATE/HOP));hi=min(len(ac)-1,round(60/60*RATE/HOP))
    candidates=[]
    if hi>lo and ac[0]>1e-12:
        indexes,_=find_peaks(ac[lo:hi+1])
        for idx in indexes:
            lag=idx+lo
            # Parabolic refinement avoids coarse integer-hop tempo quantization.
            correction=0.0
            if 0<lag<len(ac)-1:
                denominator=ac[lag-1]-2*ac[lag]+ac[lag+1]
                if abs(denominator)>1e-12:correction=float(np.clip(.5*(ac[lag-1]-ac[lag+1])/denominator,-.5,.5))
            bpm=60*RATE/(HOP*(lag+correction))
            candidates.append({'bpm':round(float(bpm),3),'relative_score':round(float(max(0,ac[lag]/ac[0])),4)})
    candidates=sorted(candidates,key=lambda x:(-x['relative_score'],abs(x['bpm']-120)))[:5]
    bpm=float(manual_bpm) if manual_bpm else candidates[0]['bpm'] if candidates else None
    if bpm is None:return None,candidates,[],0.0
    period=60/bpm;times=np.array([x['time'] for x in onsets])
    possible=times[:min(128,len(times))]%period
    def fit(phase):
        distance=np.abs((times-phase+period/2)%period-period/2)
        return float(np.mean(distance<.05))
    phase=max(possible,key=fit);score=fit(phase)
    return bpm,candidates,[float(phase)],score

def analyze_audio(path,settings=AudioSettings(),cancelled=lambda:False,progress=lambda d,t,p:None):
    settings.validate();samples,sr,channels,duration,digest,warnings=decode(path,cancelled,progress)
    flux,energy,centroids=spectral_features(samples,cancelled,progress)
    times=np.arange(len(energy))*HOP/RATE
    rise=np.maximum(0,np.diff(energy,prepend=0))
    novelty=.6*flux/max(float(flux.max()),1e-12)+.4*rise/max(float(rise.max()),1e-12)
    local=median_filter(novelty,size=51,mode='nearest');novelty=np.maximum(0,novelty-local)
    threshold=max(.015,float(novelty.max())*(.28-.035*settings.sensitivity))
    indices,_=find_peaks(np.pad(novelty,(1,1)),height=threshold,
                        prominence=max(.005,.07-.009*settings.sensitivity),
                        distance=max(1,round(settings.min_interval_ms/1000*RATE/HOP)))
    indices=indices-1;indices=indices[(indices>=0)&(indices<len(novelty))]
    onsets=[]
    gate=max(1e-5,float(energy.max())*.008)
    for index in indices:
        check_cancel(cancelled)
        if energy[index]<gate:continue
        center=int(times[index]*RATE);left=max(0,center-int(.035*RATE));right=min(len(samples),center+int(.035*RATE))
        if right<=left:continue
        absolute=np.abs(samples[left:right]);smooth=np.convolve(absolute,np.ones(22)/22,mode='same')
        floor=float(np.percentile(smooth,10));level=floor+.2*(float(smooth.max())-floor)
        above=np.flatnonzero(smooth>max(level,1e-6))
        refined=(left+int(above[0]))/RATE if len(above) else float(times[index])
        if refined>=duration:continue
        candidate={'time':round(refined,6),'strength':round(float(novelty[index]/max(novelty.max(),1e-12)),5),
                   'centroid_hz':round(float(centroids[index]),2)}
        if onsets and candidate['time']-onsets[-1]['time']<settings.min_interval_ms/1000:
            if candidate['strength']>onsets[-1]['strength']:onsets[-1]=candidate
        else:onsets.append(candidate)
    bpm,candidates,phase,fit=estimate_tempo(novelty,onsets,settings.manual_bpm)
    beat_times=[] if bpm is None or not phase else np.arange(phase[0],duration,60/bpm).round(6).tolist()
    quiet=[];start=None
    for i,is_quiet in enumerate(energy<max(1e-5,float(energy.max())*.02)):
        if is_quiet and start is None:start=float(times[i])
        elif not is_quiet and start is not None:
            if times[i]-start>=.3:quiet.append([round(start,4),round(float(times[i]),4)])
            start=None
    if start is not None and duration-start>=.3:quiet.append([round(start,4),round(duration,4)])
    # Coarse energy changes, intentionally labeled review points rather than phrases.
    sections=[{'time':0.0,'reason':'Start'}]
    energies=[]
    for second in range(0,math.ceil(duration),2):
        part=energy[(times>=second)&(times<second+2)];energies.append(float(np.mean(part)) if len(part) else 0)
    for i in range(1,len(energies)):
        ratio=(energies[i]+1e-6)/(energies[i-1]+1e-6)
        if (ratio>2.5 or ratio<.4) and i*2-sections[-1]['time']>=4:
            sections.append({'time':float(i*2),'reason':'Energy change — review'})
    stride=max(1,math.ceil(len(samples)/4000));wave=[]
    for i in range(0,len(samples),stride):
        part=samples[i:i+stride];wave.append([round(i/RATE,6),float(part.min()),float(part.max())])
    warnings.extend(['Onsets are mixed-audio attack candidates, not isolated guitar notes.',
        'Tempo/beat grid is a constant-tempo estimate; half/double-time ambiguity and drift are possible.',
        'Energy-change markers are review points, not verified musical phrase boundaries.'])
    if not onsets:warnings.append('No reliable attacks detected. Silence or sustained audio cannot produce a useful onset draft.')
    if bpm is None:warnings.append('Insufficient rhythmic evidence for a tempo estimate; enter a manual BPM.')
    elif fit<.5:warnings.append('Low beat-grid fit: verify tempo manually before relying on the grid.')
    if settings.manual_bpm:warnings.append('Manual BPM overrides the automatic estimate.')
    check_cancel(cancelled)
    return AudioAnalysis(str(Path(path).resolve()),digest,duration,sr,channels,asdict(settings),onsets,bpm,candidates,beat_times,fit,quiet,sections,wave,warnings)
