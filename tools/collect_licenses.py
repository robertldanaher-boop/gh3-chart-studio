"""Collect installed distribution notices for a build; run with the build environment."""
from importlib.metadata import distributions
from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[1]/'licenses'
for dist in distributions():
    name=dist.metadata['Name']
    for entry in dist.files or []:
        if any(word in entry.name.lower() for word in ('license','copying','notice')) and str(entry).find('dist-info')>=0:
            src=Path(dist.locate_file(entry))
            if src.is_file():
                dest=root/name/entry.name; dest.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(src,dest)
print('Collected installed distribution license notices.')

# SoundFile wheels carry libsndfile's LGPL notice outside dist-info.
try:
    import _soundfile_data
    notice=Path(_soundfile_data.__file__).parent/'COPYING'
    if notice.is_file():
        dest=root/'libsndfile'/'COPYING';dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(notice,dest)
except ImportError:
    pass

# FFmpeg is a separate executable with its own license, not the wrapper's BSD license.
import subprocess
import imageio_ffmpeg
executable=imageio_ffmpeg.get_ffmpeg_exe()
dest=root/'FFmpeg';dest.mkdir(parents=True,exist_ok=True)
for flag,name in [('-L','BINARY_LICENSE.txt'),('-version','BINARY_BUILD.txt')]:
    result=subprocess.run([executable,flag],capture_output=True,text=True,check=True,
                          creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    (dest/name).write_text(result.stdout+result.stderr,encoding='utf-8')
