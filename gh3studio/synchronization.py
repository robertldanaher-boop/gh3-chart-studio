"""Reviewed zero-offset export using exact chart translation and audio padding."""
import copy
import math
from fractions import Fraction
from .model import ChartError, Note, Phrase


def timing_values(song):
    try:
        offset=float(song.metadata.get('Offset','0'))
        delay=float(song.metadata.get('SongIniDelay','0'))
    except (ValueError,TypeError):
        raise ChartError('Offset and song.ini delay must be finite numbers')
    if not math.isfinite(offset) or not math.isfinite(delay):
        raise ChartError('Offset and song.ini delay must be finite numbers')
    return offset,delay


def normalize(song, shift_ms, sample_rate):
    """Positive shift means notes later relative to the original recording.

    Translate every chart object by whole initial bars, including tempo changes.
    Pad audio to achieve the requested relative shift without discarding samples.
    Only padding is sample-rounded; musical tick lengths remain exactly intact.
    """
    offset,delay=timing_values(song)
    if not math.isfinite(shift_ms) or abs(shift_ms)>60000:
        raise ChartError('Reviewed shift must be within ±60,000 ms')
    if not isinstance(sample_rate,int) or sample_rate<=0:raise ChartError('Invalid sample rate')
    if not song.tempos or song.tempos[0][0]!=0 or song.tempos[0][1]<=0:
        raise ChartError('An initial tempo at tick zero is required')
    if not song.signatures or song.signatures[0][0]!=0 or any(d!=4 for _,_,d in song.signatures):
        raise ChartError('Synchronization normalization requires reviewed /4 meter')
    delta=Fraction(str(shift_ms))/1000
    bar_ticks=song.resolution*song.signatures[0][1]
    bar_seconds=bar_ticks*song.tempos[0][1]/song.resolution/1000000
    bars=max(0,math.ceil(delta/bar_seconds))
    ticks=bars*bar_ticks
    lead=bars*bar_seconds
    pad_frames=round((lead-delta)*sample_rate)
    if pad_frames<0 or pad_frames>120*sample_rate:
        raise ChartError('This tempo/shift requires over two minutes of padding; review externally')
    result=copy.deepcopy(song)
    result.tracks={d:[Note(n.tick+ticks,n.lane,n.length) for n in notes] for d,notes in song.tracks.items()}
    result.phrases={d:[Phrase(p.tick+ticks,p.kind,p.length) for p in phrases] for d,phrases in song.phrases.items()}
    result.modifiers={d:[(t+ticks,m) for t,m in markers] for d,markers in song.modifiers.items()}
    result.events=[(t+ticks,e) for t,e in song.events]
    result.tempos=[song.tempos[0]]+[(t+ticks,v) for t,v in song.tempos[1:]]
    result.signatures=[song.signatures[0]]+[(t+ticks,n,d) for t,n,d in song.signatures[1:]]
    result.metadata['Offset']='0';result.metadata['SongIniDelay']='0'
    result.ini_metadata['delay']='0'
    result.warnings=[w for w in result.warnings if not w.startswith('song.ini delay found:')]
    result.warnings.append('Synchronization was explicitly normalized; use zero importer delay for this export.')
    # Preview timestamps refer to the recording; keep them pointing at the same music.
    for key in ('preview_start_time','preview_end_time'):
        try:
            value=float(result.ini_metadata[key])
            if math.isfinite(value) and value>=0:result.ini_metadata[key]=str(round(value+pad_frames/sample_rate*1000))
        except (KeyError,ValueError):pass
    for key in ('PreviewStart','PreviewEnd'):
        try:
            value=float(result.metadata[key])
            if math.isfinite(value) and value>=0:result.metadata[key]=str(value+pad_frames/sample_rate)
        except (KeyError,ValueError):pass
    effective=float(lead)-pad_frames/sample_rate
    report={'action':'normalize reviewed synchronization','source_offset_seconds':offset,
            'source_ini_delay_ms':delay,'reviewed_shift_ms':float(shift_ms),
            'chart_lead_ticks':ticks,'chart_lead_seconds':float(lead),
            'audio_padding_frames':pad_frames,'sample_rate':sample_rate,
            'audio_padding_seconds':pad_frames/sample_rate,'effective_shift_ms':effective*1000,
            'rounding_error_ms':(effective-float(delta))*1000,
            'audio_trimmed':False,'note_lengths_changed':False,
            'tempo_policy':'Tempo/meter values retained; changes translated with all chart objects'}
    return result,report


def inspect_anchors(song):
    """Compare editor anchor timestamps to the existing BPM map; do not retime it."""
    return [{'action':'remove editor tempo anchor; keep BPM map','tick':tick,
             'anchor_microseconds':stamp,'bpm_map_seconds':song.seconds(tick),
             'difference_ms':(stamp/1000000-song.seconds(tick))*1000,
             'needs_review':abs(stamp/1000000-song.seconds(tick))>.001}
            for tick,stamp in song.anchors]
