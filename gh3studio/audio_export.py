"""One full-mix Ogg Vorbis asset per song, without redundant transcoding."""
from pathlib import Path
import shutil
import numpy as np
import soundfile as sf
from .model import ChartError
from .song_identity import AUDIO_FIELDS


def export_ogg(source_path,destination,metadata=None):
    source_path=Path(source_path);destination=Path(destination)
    with sf.SoundFile(source_path) as source:
        if source.channels not in (1,2) or source.frames<=0:
            raise ChartError('Audio must be nonempty mono or stereo')
        expected=(source.frames,source.samplerate,source.channels)
        original_tags=source.copy_metadata()
        desired_tags=dict(original_tags)
        desired_tags.update({tag:str(metadata[field]) for field,tag in AUDIO_FIELDS.items() if metadata and metadata.get(field)})
        reuse=source.format=='OGG' and source.subtype=='VORBIS'
        if not reuse:
            with sf.SoundFile(destination,'w',format='OGG',subtype='VORBIS',samplerate=source.samplerate,channels=source.channels) as target:
                for tag,value in desired_tags.items():setattr(target,tag,value)
                for block in source.blocks(blocksize=65536,dtype='float32',always_2d=True):
                    if not np.isfinite(block).all():raise ChartError('Audio contains nonfinite samples')
                    target.write(block)
    if reuse:shutil.copyfile(source_path,destination)
    # Decode the entire exported asset, not just its header. A corrupt copied Ogg
    # must not be accepted merely because its container metadata is readable.
    with sf.SoundFile(destination) as output:
        actual=(output.frames,output.samplerate,output.channels)
        if actual!=expected or output.format!='OGG' or output.subtype!='VORBIS':
            raise ChartError('Ogg Vorbis audio read-back mismatch')
        exported_tags=output.copy_metadata()
        expected_tags=original_tags if reuse else desired_tags
        if any(exported_tags.get(k)!=v for k,v in expected_tags.items() if k!='software'):
            raise ChartError('Ogg metadata read-back mismatch')
        decoded=0
        for block in output.blocks(blocksize=65536,dtype='float32',always_2d=True):
            if not np.isfinite(block).all():raise ChartError('Exported Ogg contains nonfinite samples')
            decoded+=len(block)
        if decoded!=expected[0]:raise ChartError('Exported Ogg decoded frame count mismatch')
    metadata_warnings=[]
    if reuse and any(exported_tags.get(k)!=v for k,v in desired_tags.items() if k!='software'):
        metadata_warnings.append('Existing Ogg copied without re-encoding: its embedded tags differ from chart/song.ini metadata. Chart and song.ini contain the reviewed song identity; original Ogg tags are preserved.')
    return {'embedded_tags':exported_tags,'metadata_warnings':metadata_warnings,'file':'song.ogg','format':'OGG','codec':'VORBIS',
            'operation':'copied_without_reencoding' if reuse else 'encoded_to_vorbis',
            'frames':expected[0],'sample_rate':expected[1],'channels':expected[2],
            'fully_decoded':True,'resampled':False,'timing_shift_applied':False}
