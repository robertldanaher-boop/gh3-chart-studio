"""Atomic chart-and-audio folders; only Medium is subject to export cleanup."""
import copy
import configparser
import hashlib
import json
import shutil
import tempfile
from itertools import groupby
from pathlib import Path
from .audio_export import export_ogg
from .song_identity import FIELDS
from .hopo import is_flip
from .chartio import read_chart, write_chart
from .editing import prepare_cleanup
from .validation import validate
from .model import ChartError


def prepare_medium(song, strip_markers=False, trim_sustains=False):
    isolated=copy.deepcopy(song)
    isolated.tracks={'Medium':copy.deepcopy(song.tracks.get('Medium',[]))}
    isolated.phrases={'Medium':copy.deepcopy(song.phrases.get('Medium',[]))}
    isolated.modifiers={'Medium':copy.deepcopy(song.modifiers.get('Medium',[]))}
    isolated,review=prepare_cleanup(isolated,strip_markers,trim_sustains)
    markers=isolated.modifiers.get('Medium',[])
    isolated.modifiers['Medium']=[(t,m) for t,m in markers if not is_flip(m)]
    errors=validate(isolated,True)['errors']
    isolated.modifiers['Medium']=markers
    note_ticks={n.tick for n in isolated.tracks['Medium']}
    flip_ticks=[t for t,m in markers if is_flip(m)]
    if any(t not in note_ticks for t in flip_ticks):errors.append('Medium HOPO marker has no playable note')
    if len(flip_ticks)!=len(set(flip_ticks)):errors.append('Duplicate Medium HOPO flip markers')
    previous_end=0
    for tick,group in groupby(sorted(isolated.tracks['Medium']),key=lambda n:n.tick):
        notes=list(group)
        if len({n.length for n in notes})>1 or tick<previous_end:
            errors.append(f'Medium chord/extended sustain at tick {tick}; review sustain cleanup')
        previous_end=max(n.tick+n.length for n in notes)
    if float(song.metadata.get('Offset','0')) or float(song.metadata.get('SongIniDelay','0')):
        errors.append('Nonzero chart Offset/song.ini delay: resolve synchronization explicitly before folder export')
    result=copy.deepcopy(song)
    result.tracks['Medium']=isolated.tracks['Medium']
    result.phrases['Medium']=isolated.phrases['Medium']
    result.modifiers['Medium']=isolated.modifiers.get('Medium',[])
    review['remaining_errors']=list(dict.fromkeys(errors))
    return result,review


def automatic_export_timing(song,audio_path):
    from .synchronization import timing_values,normalize
    offset,delay=timing_values(song)
    if not (offset or delay):return song,{}
    import soundfile as sf
    song,plan=normalize(song,delay,sf.info(audio_path).samplerate)
    plan.update(automatic=True,policy='song.ini delay only; chart Offset ignored; missing delay = 0')
    return song,plan


def export_song_folder(song, report, destination, audio_path, source_path=None, *, clean_all=False, audio_padding_frames=0, editor_all=False, overwrite=False):
    destination=Path(destination);audio_path=Path(audio_path)
    combined=bool(report.get("all_difficulty_cleanup") or report.get("conversion",{}).get("all_difficulty_cleanup"))
    if combined:
        song,plan=automatic_export_timing(song,audio_path)
        if plan:report=dict(report,synchronization=plan);audio_padding_frames=plan['audio_padding_frames']
        else:audio_padding_frames=report.get('synchronization',{}).get('audio_padding_frames',audio_padding_frames)
        if not editor_all:clean_all=True
    if report.get('difficulty_completion') or report.get('conversion',{}).get('difficulty_completion'):
        from .difficulty_set import check_complete_conversion
        check_complete_conversion(song)
    if editor_all:
        from .chart_editor import check_editor_song
        check_editor_song(song)
        if not any(song.tracks.values()):raise ChartError('No playable notes')
        if float(song.metadata.get('Offset','0')) or float(song.metadata.get('SongIniDelay','0')):raise ChartError('Resolve synchronization in Clean songs before editor export')
        checks={'remaining_errors':[]}
    elif clean_all:
        checked,review=prepare_cleanup(song,True,True)
        errors=validate(song)['errors']
        if checked.tracks!=song.tracks or any(song.modifiers.values()):errors.append('All difficulties must be cleaned before export')
        if any(n.lane==4 for n in song.tracks.get('Medium',[])):errors.append('ORANGE IS PROHIBITED IN MEDIUM')
        if float(song.metadata.get('Offset','0')) or float(song.metadata.get('SongIniDelay','0')):errors.append('Nonzero audio offset/delay requires review')
        if any(d!=4 for _,_,d in song.signatures):errors.append('Non-/4 meter requires review')
        if not any(song.tracks.values()):errors.append('No playable notes')
        checks={'remaining_errors':errors}
    else:_,checks=prepare_medium(song)
    if checks['remaining_errors']:raise ChartError('\n'.join(checks['remaining_errors']))
    if destination.exists() and not overwrite:raise ChartError('Output folder already exists; choose a new folder')
    if overwrite and any(Path(p).resolve().is_relative_to(destination.resolve()) for p in (audio_path,source_path) if p):raise ChartError('Choose an output folder separate from the input song')
    if not audio_path.is_file():raise ChartError('Select the matching full-mix audio file')
    destination.parent.mkdir(parents=True,exist_ok=True)
    stage=Path(tempfile.mkdtemp(prefix='.gh3-song-',dir=destination.parent))
    try:
        audio_details=export_ogg(audio_path,stage/'song.ogg',song.metadata,reconcile_metadata=clean_all or editor_all,padding_frames=audio_padding_frames)
        frames,rate,channels=(audio_details[k] for k in ('frames','sample_rate','channels'))
        output=copy.deepcopy(song)
        for key in ('GuitarStream','BassStream','RhythmStream'):output.metadata.pop(key,None)
        output.metadata['MusicStream']='song.ogg'
        if 'Length' in output.metadata:output.metadata['Length']=str(frames/rate)
        write_chart(output,stage/'notes.chart');reopened=read_chart(stage/'notes.chart')
        if reopened.tracks!=song.tracks or reopened.events!=song.events or reopened.signatures!=song.signatures:
            raise ChartError('Chart note/timing read-back mismatch')
        for diff in song.tracks:
            if reopened.phrases.get(diff,[])!=song.phrases.get(diff,[]):raise ChartError('Phrase read-back mismatch')
            canonical=lambda items:[(t,m+' 0' if m.startswith('N ') and len(m.split())==2 else m) for t,m in items]
            if reopened.modifiers.get(diff,[])!=canonical(song.modifiers.get(diff,[])):raise ChartError('Marker read-back mismatch')
        end=max(n.tick+n.length for notes in song.tracks.values() for n in notes)
        probes={end}|{t for t,_ in song.tempos}
        drift=max(abs(reopened.seconds(t)-song.seconds(t)) for t in probes)
        if [t for t,_ in reopened.tempos]!=[t for t,_ in song.tempos] or drift>.001:raise ChartError('Tempo read-back mismatch')
        ini=configparser.ConfigParser(interpolation=None)
        ini['song']=dict(song.ini_metadata)
        ini['song'].update({key:str(song.metadata[field]) for field,key in FIELDS.items() if field in song.metadata})
        ini['song'].update({'song_length':str(round(frames/rate*1000)),'delay':'0'})
        with (stage/'song.ini').open('w',encoding='utf-8') as f:ini.write(f)
        warnings=['Medium structural checks passed; Windows/TheGHOST/Wii runtime acceptance remains untested.',
                  'Expert, Hard and Easy are retained as authored, including their markers and any source sustain issues.',
                  'Audio is the selected full mix as Ogg Vorbis. Existing Vorbis is copied unchanged; other formats undergo lossy encoding without resampling or timing shifts.',
                  'Import notes.chart and song.ogg in TheGHOST. Do not substitute a MIDI file from another export.']
        if clean_all:
            warnings[0]='All exported guitar difficulties passed structural cleanup checks; runtime acceptance remains untested.'
            warnings[1]='Source files are unchanged. Exported difficulties include the reviewed marker removals and sustain repairs.'
            warnings[2]='Audio is Ogg Vorbis with reviewed metadata. Existing Vorbis is reused only when tags agree; conflicting tags require lossy re-encoding.'
        if editor_all:
            warnings[0]='Edited difficulties passed structural checks; manually verify timing, sustains and HOPOs in game.'
            warnings[1]='All difficulties reflect the editor working copy. Source files are unchanged.'
        if audio_padding_frames:warnings[2]='Audio has reviewed leading silence; no source samples were trimmed. Vorbis was re-encoded. See synchronization and audio_export details.'
        details=dict(report,source_chart_path=str(Path(source_path).resolve()) if source_path else None,song_identity={field:song.metadata.get(field,'') for field in FIELDS},source_ini_metadata=report.get('source_ini_metadata',dict(song.ini_metadata)),audio_export=audio_details,folder_checks={'medium_orange_gems':0,'chart_reopened':True,'audio_frames':frames,'audio_sample_rate':rate,'audio_channels':channels,'tempo_drift_ms':drift*1000},warnings=list(report.get('warnings',[]))+warnings)
        def digest(path):
            h=hashlib.sha256()
            with Path(path).open('rb') as f:
                for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
            return h.hexdigest()
        for field in FIELDS:
            if field in song.metadata and reopened.metadata.get(field)!=song.metadata[field]:raise ChartError('Chart metadata read-back mismatch: '+field)
        ini_check=configparser.ConfigParser(interpolation=None);ini_check.read(stage/'song.ini',encoding='utf-8')
        if dict(ini_check['song'])!=dict(ini['song']):raise ChartError('song.ini metadata read-back mismatch')
        details['warnings']+=audio_details['metadata_warnings']
        details['files_sha256']={p.name:digest(p) for p in stage.iterdir() if p.is_file()}
        details['audio_source_sha256']=digest(audio_path)
        if source_path:details['source_sha256']=digest(source_path)
        (stage/'validation.json').write_text(json.dumps(details,indent=2),encoding='utf-8')
        (stage/'IMPORT_README.txt').write_text('GH3 Chart Studio song import\n\nSelect notes.chart as the chart and song.ogg as the full-mix audio in TheGHOST.\nUse the Medium difficulty for the four-fret output. Expert/Hard remain authored source tracks.\nsong.ini carries the title, artist and duration; verify these in the importer.\nThis is an import folder, not a Wii game-ready archive. TheGHOST builds game assets.\nNo album artwork is supplied. No separate guitar/bass stems are fabricated.\nCheck timing, HOPO behavior and sustain lengths in TheGHOST and the game.\nIf HOPO assistance was enabled, set TheGHOST HOPO measure to 2.95.\nHOPO flips depend on this setting; HOPOs still require a starting/recovery strum.\nSee validation.json for reviewed cleanup and automated checks.\n',encoding='utf-8')
        if clean_all:
            readme=stage/'IMPORT_README.txt'
            readme.write_text(readme.read_text(encoding='utf-8').replace('Use the Medium difficulty for the four-fret output. Expert/Hard remain authored source tracks.','All included guitar difficulties were cleaned; see validation.json for repairs and any generated difficulty slots.'),encoding='utf-8')
        if editor_all:
            readme=stage/'IMPORT_README.txt'
            readme.write_text(readme.read_text(encoding='utf-8').replace('Use the Medium difficulty for the four-fret output. Expert/Hard remain authored source tracks.','All included difficulties reflect the editor working copy; see validation.json for edit history.'),encoding='utf-8')
        from .output_replace import publish
        publish(stage,destination,overwrite)
        return details
    except Exception:
        shutil.rmtree(stage,ignore_errors=True)
        raise
