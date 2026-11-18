"""One full-mix Ogg Vorbis asset per song, without redundant transcoding."""
from pathlib import Path
import shutil
import tempfile
import numpy as np
import soundfile as sf
from .model import ChartError
from .song_identity import AUDIO_FIELDS


class AudioExportError(ChartError):
    def __init__(self,stage,path,cause,state):
        super().__init__(f'Audio {stage} failed for "{path}": {cause}')
        self.stage=stage;self.state=state;self.cause=cause


def export_ogg(source_path,destination,metadata=None, *, reconcile_metadata=False, padding_frames=0):
    try:
        return _export_checked(source_path,destination,metadata,reconcile_metadata=reconcile_metadata,padding_frames=padding_frames)
    except AudioExportError as first:
        if first.stage not in ('open source','read source metadata','decode source') or not isinstance(first.cause,sf.LibsndfileError):
            raise
        from .audio_fallback import decode_to_pcm
        try:
            with tempfile.TemporaryDirectory(prefix='gh3-audio-recovery-') as folder:
                decoded=Path(folder)/'decoded.wav'
                recovery=decode_to_pcm(source_path,decoded,first.state.get('source_info'))
                result=_export_checked(decoded,destination,metadata,reconcile_metadata=reconcile_metadata,
                                       padding_frames=padding_frames,source_tags=first.state.get('tags'))
                recovery['original_error']=str(first)
                result['fallback']=recovery
                result['metadata_warnings'].append('Source audio recovered automatically with FFmpeg; original recording unchanged. See audio_export.fallback.')
                return result
        except Exception as second:
            raise ChartError(f'{first}\nAutomatic recovery could not complete: {second}') from second


def _export_checked(source_path,destination,metadata=None, *, reconcile_metadata=False,padding_frames=0,source_tags=None):
    state={'stage':'open source','path':str(source_path)}
    try:
        return _export_soundfile(source_path,destination,metadata,reconcile_metadata=reconcile_metadata,
                                 padding_frames=padding_frames,source_tags=source_tags,state=state)
    except Exception as exc:
        raise AudioExportError(state['stage'],state['path'],exc,state) from exc


def _export_soundfile(source_path,destination,metadata=None, *, reconcile_metadata=False,padding_frames=0,source_tags=None,state):
    if not isinstance(padding_frames,int) or padding_frames<0:raise ChartError("Invalid audio padding")
    source_path=Path(source_path);destination=Path(destination)
    with sf.SoundFile(source_path) as source:
        if source.channels not in (1,2) or source.frames<=0:
            raise ChartError('Audio must be nonempty mono or stereo')
        if padding_frames>120*source.samplerate:raise ChartError("Audio padding exceeds two minutes")
        expected=(source.frames+padding_frames,source.samplerate,source.channels)
        state['source_info']=(source.frames,source.samplerate,source.channels)
        state['stage']='read source metadata'
        original_tags=source.copy_metadata() if source_tags is None else source_tags
        state['tags']=original_tags
        desired_tags=dict(original_tags)
        desired_tags.update({tag:str(metadata[field]) for field,tag in AUDIO_FIELDS.items() if metadata and metadata.get(field)})
        reuse=source.format=='OGG' and source.subtype=='VORBIS' and padding_frames==0
        if reconcile_metadata and any(original_tags.get(k)!=v for k,v in desired_tags.items() if k!='software'):reuse=False
        if not reuse:
            state.update(stage='create Ogg',path=str(destination))
            with sf.SoundFile(destination,'w',format='OGG',subtype='VORBIS',samplerate=source.samplerate,channels=source.channels) as target:
                state['stage']='write Ogg metadata'
                for tag,value in desired_tags.items():setattr(target,tag,value)
                state['stage']='write audio padding'
                remaining=padding_frames
                while remaining:
                    count=min(remaining,65536)
                    target.write(np.zeros((count,source.channels),dtype='float32'));remaining-=count
                while True:
                    state.update(stage='decode source',path=str(source_path))
                    block=source.read(65536,dtype='float32',always_2d=True)
                    if not len(block):break
                    if not np.isfinite(block).all():raise ChartError('Audio contains nonfinite samples')
                    state.update(stage='write Ogg',path=str(destination))
                    target.write(block)
                state.update(stage='finalize Ogg',path=str(destination))
    state.update(stage='copy Ogg',path=str(destination))
    if reuse:shutil.copyfile(source_path,destination)
    # Decode the entire exported asset, not just its header. A corrupt copied Ogg
    # must not be accepted merely because its container metadata is readable.
    state.update(stage='validate exported Ogg',path=str(destination))
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
            'fully_decoded':True,'resampled':False,'timing_shift_applied':bool(padding_frames),'padding_frames':padding_frames,'trimmed_frames':0}
