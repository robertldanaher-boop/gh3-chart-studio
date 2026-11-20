"""Song identity shared by the export dialog, folder name and metadata writers."""
import re
from pathlib import Path
import soundfile as sf

FIELDS={'Name':'name','Artist':'artist','Album':'album','Year':'year','Genre':'genre','Charter':'charter','TrackNumber':'track','AlbumArtist':'album_artist','Copyright':'copyright'}
AUDIO_FIELDS={'Name':'title','Artist':'artist','Album':'album','Year':'date','Genre':'genre','TrackNumber':'tracknumber','Copyright':'copyright'}


def fill_from_audio(metadata,audio_path):
    result=dict(metadata)
    if audio_path and Path(audio_path).is_file():
        try:
            with sf.SoundFile(audio_path) as source:tags=source.copy_metadata()
            for field,tag in AUDIO_FIELDS.items():
                if not result.get(field,'').strip() or result.get(field,'').strip().lower() in ('unknown','unknown artist'):
                    if tags.get(tag):result[field]=tags[tag]
        except (OSError,RuntimeError):pass  # Audio validation reports errors during export.
    return result


# "1. ", "03.", "12. " added by renaming tools to mark a track position. Only digits
# followed by a dot that is NOT followed by another digit, so "2.0", "10.000
# Maniacs" style names and plain numbers ("3 Doors Down", "311", "The 1975") stay.
TRACK_PREFIX=re.compile(r'^\s*\d{1,3}\s*\.(?!\d)\s*')
TRACK_PREFIX_FIELDS=('Artist','Name')


def strip_track_number(value):
    """Return value without a leading track-number prefix like "1. " or "03."."""
    text=str(value or '')
    match=TRACK_PREFIX.match(text)
    if not match:return text
    rest=text[match.end():].strip()
    return rest or text


def clean_track_numbers(metadata):
    """Remove track-number prefixes from Artist and Name. Returns (metadata, changes)."""
    result=dict(metadata);changes=[]
    for field in TRACK_PREFIX_FIELDS:
        before=result.get(field,'')
        after=strip_track_number(before)
        if after!=before:
            result[field]=after
            changes.append({'action':'remove track-number prefix','field':'Title' if field=='Name' else field,'from':before,'to':after})
    return result,changes


def export_folder_name(metadata,now=None):
    """Windows-safe identity; metadata itself is never sanitized or truncated."""
    def part(value,fallback):
        value=re.sub(r'[<>:"/\\|?*\x00-\x1f]','_',value.strip())
        return value[:48].rstrip(' .') or fallback
    return part(metadata.get('Artist',''),'Unknown Artist')+' - '+part(metadata.get('Name',''),'Untitled Song')


def export_folder_path(parent,metadata,source_path=None):
    """Choose a nonexisting name, treating case-only collisions like Windows."""
    parent=Path(parent);stem=export_folder_name(metadata)
    occupied={p.name.casefold():p for p in parent.iterdir()} if parent.exists() else {}
    name=stem;number=2
    while name.casefold() in occupied:
        if source_path:
            import json
            existing=occupied[name.casefold()]
            try:
                details=json.loads((existing/'validation.json').read_text(encoding='utf-8'))
                source=str(Path(source_path).resolve())
                if details.get('source_chart_path')==source or source in details.get('source_hashes',{}):return existing
            except (OSError,ValueError):pass
        name=f'{stem} ({number})';number+=1
    return parent/name
