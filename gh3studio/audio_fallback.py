"""Strict local FFmpeg-to-PCM fallback. No discarded-error or timing repair flags."""
from pathlib import Path
import subprocess
import soundfile as sf
from .model import ChartError


def decode_to_pcm(source,destination,expected=None):
    import imageio_ffmpeg
    try:
        executable=imageio_ffmpeg.get_ffmpeg_exe()
        command=[executable,'-nostdin','-hide_banner','-v','error','-xerror',
                 '-err_detect','explode','-protocol_whitelist','file,pipe',
                 '-i',str(Path(source).resolve()),'-map','0:a:0','-vn','-sn','-dn',
                 '-map_metadata','0','-c:a','pcm_f32le','-f','wav','-y',str(destination)]
        result=subprocess.run(command,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,
                              stderr=subprocess.PIPE,text=True,errors='replace',timeout=180,
                              creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        if result.returncode:raise ChartError(result.stderr.strip()[-4000:] or f'FFmpeg exit {result.returncode}')
        info=sf.info(destination)
        actual=(info.frames,info.samplerate,info.channels)
        if info.frames<=0 or info.channels not in (1,2):raise ChartError('Recovery did not produce nonempty mono/stereo audio')
        if expected and tuple(expected)!=actual:
            raise ChartError(f'Recovered frames/rate/channels {actual} do not match source header {tuple(expected)}; refusing possible truncation or timing change')
        return {'decoder':'FFmpeg','provider':'imageio-ffmpeg '+imageio_ffmpeg.__version__,
                'decoded_frames':info.frames,'sample_rate':info.samplerate,'channels':info.channels,
                'source_header_matched':bool(expected),'resampled':False,'trimmed_frames':0}
    except Exception as exc:
        raise ChartError(f'Alternate audio decoder failed for "{source}": {exc}') from exc
