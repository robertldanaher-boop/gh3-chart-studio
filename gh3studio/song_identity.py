"""Song identity shared by the export dialog, folder name and metadata writers."""
import re
from datetime import datetime
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


def export_folder_name(metadata,now=None):
    title=metadata.get('Name','').strip() or 'Untitled Song'
    artist=metadata.get('Artist','').strip() or 'Unknown Artist'
    stem=re.sub(r'[<>:"/\\|?*\x00-\x1f]','_',f'{artist} - {title}').strip(' .')[:100].rstrip(' .')
    return f'{stem} [Medium] - {(now or datetime.now()).strftime("%Y%m%d_%H%M%S_%f")}'
