"""Reviewable multi-folder guitar-chart cleanup; never edits source folders."""
import copy
import hashlib
import json
import traceback
from datetime import datetime
from pathlib import Path
import re
import soundfile as sf
from .service import load
from .editing import prepare_cleanup, remove_orange_to_medium
from .preview_audio import matching_audio
from .song_identity import fill_from_audio, FIELDS
from .song_export import export_song_folder
from .validation import validate
from .model import ChartError


def fingerprint(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def inspect_chart(path,audio=None,metadata=None,sync_review=None):
    path=Path(path).resolve()
    row={'path':str(path),'errors':[],'warnings':[],'changes':[],'metadata':{k:v for k,v in (metadata or {}).items() if k in FIELDS},'audio':str(audio) if audio else '','song':None,'hashes':{}}
    try:
        song=load(path,learning_only=True,cleanup=True)
        chosen=Path(audio).resolve() if audio else matching_audio(path,song.metadata)
        if chosen is None:
            choices=[p for p in path.parent.iterdir() if p.is_file() and p.suffix.lower() in ('.wav','.flac','.ogg','.mp3','.opus') and p.stem.lower() not in ('preview','song_preview')]
            if len(choices)==1:
                chosen=choices[0]
                row['warnings'].append('Automatically matched the only non-preview audio in this song folder: '+chosen.name+'. Verify it contains the full song, not an isolated instrument.')
        row['metadata']=fill_from_audio(song.metadata,chosen)
        if metadata is not None:row['metadata'].update({k:v for k,v in metadata.items() if k in FIELDS})
        song.metadata.update(row['metadata'])
        for field in ('Name','Artist'):
            if song.metadata.get(field,'').strip().lower() in ('','unknown','unknown artist','untitled','untitled song'):
                row['errors'].append(f'Missing {field}: enter and verify metadata')
        missing=[f for f in ('Album','Year','Genre','Charter') if not song.metadata.get(f,'').strip()]
        if missing:row['warnings'].append('Optional metadata missing: '+', '.join(missing))
        if chosen is None:row['errors'].append('No unambiguous full-mix audio: select the matching recording')
        else:
            row['audio']=str(chosen)
            try:
                with sf.SoundFile(chosen) as f:
                    if f.channels not in (1,2) or f.frames<=0:raise ChartError('Audio must be nonempty mono/stereo')
                    row['audio_format']=f.format+'/'+f.subtype
                row['hashes'][str(chosen)]=fingerprint(chosen)
            except Exception as exc:row['errors'].append('Audio: '+str(exc))
        if not any(song.tracks.values()):raise ChartError('No supported playable guitar notes')
        if any(d!=4 for _,_,d in song.signatures):raise ChartError('Non-/4 time signature needs manual review for TheGHOST; tempo/meter will not be guessed')
        from .synchronization import timing_values,normalize,inspect_anchors
        offset,delay=timing_values(song)
        for p in (path,path.parent/'song.ini'):
            if p.exists():row['hashes'][str(p)]=fingerprint(p)
        row['sync_source']=copy.deepcopy(song)
        row['sync_values']={'offset_seconds':offset,'delay_ms':delay}
        review_current=bool(sync_review is not None and sync_review.get('source_hashes')==row['hashes'] and
                            sync_review.get('chart_path')==str(path) and sync_review.get('audio_path')==row['audio'])
        row['anchor_checks']=inspect_anchors(song)
        conflicts=[a for a in row['anchor_checks'] if a['needs_review']]
        if conflicts and not (review_current and sync_review.get('accept_anchor_map')):
            row['errors'].append('Tempo anchor timestamps differ from the BPM map. Review synchronization to keep the existing BPM map, or correct the tempo map externally.')
        row['changes']+=row['anchor_checks']
        song.anchors=[]
        if sync_review is not None:
            if not review_current:
                row['errors'].append('Synchronization review expired: chart/audio/song.ini changed. Review synchronization again.')
            elif row.get('audio_format'):
                rate=sf.info(row['audio']).samplerate
                song,plan=normalize(song,float(sync_review['shift_ms']),rate)
                row['sync_review']=copy.deepcopy(sync_review);row['synchronization']=plan
                row['changes'].append(plan)
        if (offset or delay) and 'synchronization' not in row:
            row['errors'].append('Nonzero Offset or song.ini delay needs manual synchronization review')
        # Medium must never export Orange; preserve its sustains using seeded four-fret placement.
        if any(n.lane==4 for n in song.tracks.get('Medium',[])):
            song,transfer=remove_orange_to_medium(song,'Medium',strict=False,randomize_orange_sustains=True,sustain_seed=0)
            row['changes'].append({'action':'remove Medium Orange; transfer sustained Orange to four frets','removed':transfer['removed_orange_gems'],'transfers':transfer['sustain_transfers']})
        clean,review=prepare_cleanup(song,strip_markers=True,trim_sustains=True)
        row['changes']+=review['changes']
        row['errors']+=review['remaining_errors']
        if not any(clean.tracks.values()):row['errors'].append('Cleanup would leave no playable guitar notes')
        row['warnings']+=song.warnings
        row['warnings']+=['All guitar difficulties are cleaned. Forced/tap markers are removed; natural HOPO behavior may change.','Other instrument sections, stems and artwork are not included.','Metadata values require your verification; structural checks cannot prove factual correctness.']
        row['song']=clean if not row['errors'] else None
    except Exception as exc:row['errors'].append(str(exc))
    return row


def scan_charts(root,cancel=lambda:False,progress=lambda done,total,name:None):
    root=Path(root).resolve()
    if not root.is_dir():raise ChartError('Choose a song folder or parent directory')
    groups={}
    for p in root.rglob('*'):
        if cancel():break
        if p.is_file() and not p.is_symlink() and p.suffix.lower() in ('.chart','.mid','.midi'):
            if not p.resolve().is_relative_to(root):continue
            groups.setdefault(p.parent,[]).append(p)
            if len(groups)>2000:raise ChartError('Over 2,000 song folders; select a smaller directory')
    rows=[]
    for index,(folder,paths) in enumerate(sorted(groups.items()),1):
        if cancel():break
        progress(index-1,len(groups),str(folder))
        charts=[p for p in paths if p.suffix.lower()=='.chart']
        preferred=[p for p in charts if p.name.lower()=='notes.chart']
        choices=preferred or charts or [p for p in paths if p.name.lower() in ('notes.mid','notes.midi')] or paths
        if len(choices)!=1:
            rows.append({'path':str(folder),'errors':['Multiple chart candidates; select a chart file for this row'],'warnings':[],'changes':[],'metadata':{},'audio':'','song':None,'hashes':{}})
            continue
        row=inspect_chart(choices[0])
        if len(paths)>1:row['warnings'].append('Selected '+choices[0].name+'; other chart/MIDI alternatives in this folder were not exported.')
        rows.append(row)
    return rows


def export_cleaned(rows,destination,source_root,cancel=lambda:False,progress=lambda done,total,name:None):
    root=Path(source_root).resolve();dest=Path(destination).resolve()
    if dest==root or dest.is_relative_to(root):raise ChartError('Choose an output directory outside the scanned source tree')
    if dest.exists():raise ChartError('Choose a new output folder; existing folders are never overwritten')
    dest.mkdir(parents=True)
    log_path=dest/'cleanup.log'
    def log(message):
        with log_path.open('a',encoding='utf-8') as stream:
            stream.write(datetime.now().astimezone().isoformat(timespec='seconds')+' '+message+'\n')
    log(f'START | source={root} | output={dest} | requested={len(rows)}')
    results=[]
    for index,row in enumerate(rows,1):
        if cancel():break
        log(f'SONG {index}/{len(rows)} | '+row['path'])
        progress(index-1,len(rows),row['path'])
        result={'source':row['path']}
        try:
            if row['errors'] or row['song'] is None:raise ChartError('; '.join(row['errors']) or 'No parsed chart is available')
            if any(fingerprint(p)!=digest for p,digest in row['hashes'].items()):raise ChartError('Source changed after scan; rescan before export')
            song=copy.deepcopy(row['song'])
            name=re.sub(r'[<>:"/\\|?*\x00-\x1f]','_',song.metadata['Artist']+' - '+song.metadata['Name']).strip(' .')[:100]
            folder=dest/f'{index:04d} - {name}'
            report={'operation':'clean-all-guitar-difficulties','cleanup_changes':row['changes'],'warnings':row['warnings'],'source_hashes':row['hashes']}
            if row.get('sync_source'):report['source_ini_metadata']=dict(row['sync_source'].ini_metadata)
            sync=row.get('synchronization',{})
            if sync:
                report['synchronization']=sync
                log('SYNCHRONIZATION | '+json.dumps(sync,ensure_ascii=True))
            export_song_folder(song,report,folder,row['audio'],row['path'],clean_all=True,audio_padding_frames=sync.get('audio_padding_frames',0))
            result.update(status='exported',folder=str(folder))
        except Exception as exc:
            result.update(status='failed',error=str(exc));log('FAILED | '+str(exc)+'\n'+traceback.format_exc())
        else:log('EXPORTED | '+str(folder))
        results.append(result)
        (dest/'cleanup_summary.json').write_text(json.dumps({'results':results,'requested':len(rows),'processed':len(results)},indent=2),encoding='utf-8')
    (dest/'cleanup_summary.json').write_text(json.dumps({'results':results,'requested':len(rows),'processed':len(results),'cancelled':bool(cancel())},indent=2),encoding='utf-8')
    log(f'FINISHED | exported={sum(r["status"]=="exported" for r in results)} | failed={sum(r["status"]=="failed" for r in results)} | unprocessed={len(rows)-len(results)} | cancelled={bool(cancel())}')
    return results
