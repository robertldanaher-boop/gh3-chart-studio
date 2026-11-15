import configparser
import hashlib
import json
import shutil
import tempfile
from pathlib import Path
from .chartio import read_chart, write_chart
from .midiio import read_midi, write_midi
from .validation import ensure_valid
from .model import ChartError, Note
from . import __version__

def load(path, phrase_mode='modern', *, learning_only=False):
    path=Path(path)
    if path.stat().st_size>32*1024*1024: raise ChartError('Input exceeds the 32 MiB safety limit')
    if path.suffix.lower()=='.chart': song=read_chart(path)
    elif path.suffix.lower() in ('.mid','.midi'): song=read_midi(path,phrase_mode)
    else: raise ChartError('Choose a .chart or .mid file')
    ini=path.parent/'song.ini'
    if ini.exists():
        parser=configparser.ConfigParser(interpolation=None,strict=False)
        parser.read(ini,encoding='utf-8-sig')
        if parser.has_section('song'):
            for src,dst in {'name':'Name','artist':'Artist','album':'Album','year':'Year','genre':'Genre','charter':'Charter'}.items():
                if parser.has_option('song',src): song.metadata[dst]=parser.get('song',src)
            if parser.has_option('song','delay'):
                song.metadata['SongIniDelay']=parser.get('song','delay')
                song.warnings.append('song.ini delay found: set the same delay in TheGHOST; no automatic offset is applied')
    checks=ensure_valid(song,learning_only=learning_only)
    if learning_only:
        song.warnings=checks["warnings"]
    return song

def export_bundle(song, report, destination, source_path=None):
    """Stage, reopen, verify, then rename a new directory; never overwrite."""
    destination=Path(destination)
    if destination.exists(): raise ChartError('Output folder already exists. Choose a new folder name.')
    ensure_valid(song,True)
    if float(song.metadata.get('Offset','0'))!=0:
        raise ChartError('Nonzero chart Offset cannot be applied equivalently by TheGHOST MIDI. Set Offset to zero in a copy and apply the original offset explicitly in TheGHOST.')
    destination.parent.mkdir(parents=True,exist_ok=True)
    staging=Path(tempfile.mkdtemp(prefix='.gh3-stage-',dir=destination.parent))
    try:
        write_chart(song,staging/'notes.chart'); write_midi(song,staging/'notes.mid')
        checks={}
        for name,reader in [('notes.chart',read_chart),('notes.mid',lambda p:read_midi(p,'legacy'))]:
            reopened=reader(staging/name); ensure_valid(reopened,True)
            expected = song.tracks if name.endswith('.chart') else {d:[Note(n.tick,n.lane,max(1,n.length)) for n in ns] for d,ns in song.tracks.items()}
            if reopened.tracks != expected: raise ChartError(f'{name}: note read-back mismatch')
            if reopened.signatures != song.signatures or reopened.events != song.events: raise ChartError(f'{name}: timing/event read-back mismatch')
            for diff in song.tracks:
                if reopened.phrases.get(diff,[]) != song.phrases.get(diff,[]): raise ChartError(f'{name}: phrase read-back mismatch')
            if [t for t,_ in reopened.tempos]!=[t for t,_ in song.tempos]: raise ChartError('Tempo position mismatch')
            end=max(n.tick+n.length for ns in song.tracks.values() for n in ns)
            probes={end}|{t for t,_ in song.tempos}
            drift=max(abs(reopened.seconds(t)-song.seconds(t)) for t in probes)
            if drift>0.001: raise ChartError(f'{name}: tempo representation drift exceeds 1 ms ({drift*1000:.3f} ms)')
            checks[name]={'reopened':True,'medium_orange_gems':0,'max_tempo_boundary_drift_ms':drift*1000,
                          'sha256':hashlib.sha256((staging/name).read_bytes()).hexdigest()}
        parser=configparser.ConfigParser(interpolation=None)
        parser['song']={k.lower():str(v) for k,v in song.metadata.items() if k in ('Name','Artist','Album','Year','Genre','Charter')}
        with (staging/'song.ini').open('w',encoding='utf-8') as f: parser.write(f)
        details=dict(report,exports=checks,version=__version__,midi_profile='TheGHOST legacy per-difficulty phrases; Medium star power = 79')
        details['warnings']=list(details.get('warnings',[]))+[
            'MIDI zero-length chart gems use 1 tick note duration; MIDI imports preserve their actual duration, including 1-tick notes.',
            'TheGHOST legacy MIDI parser discards sustains shorter than 160 ticks. Prefer notes.chart for short sustains.',
            'TheGHOST may alter sustain lengths, especially across tempo changes. In-game verification is pending.',
            'Audio files are not copied. Import the original audio in TheGHOST. Choose either notes.chart OR notes.mid.']
        if song.metadata.get('Name','').encode('latin-1',errors='replace').decode('latin-1')!=song.metadata.get('Name',''):
            details['warnings'].append('MIDI track title uses Latin-1 replacement characters; the complete Unicode title is retained in song.ini and application MIDI metadata.')
        if source_path:
            digest=hashlib.sha256()
            with Path(source_path).open('rb') as source:
                while chunk:=source.read(1024*1024): digest.update(chunk)
            details['source_sha256']=digest.hexdigest()
        (staging/'validation.json').write_text(json.dumps(details,indent=2),encoding='utf-8')
        (staging/'settings.json').write_text(json.dumps(report.get('settings',{}),indent=2),encoding='utf-8')
        staging.rename(destination)
    except Exception:
        shutil.rmtree(staging,ignore_errors=True); raise
    return details
