"""Frozen-binary smoke checks, deliberately separate from game acceptance."""
import json
import os
from pathlib import Path
import tempfile


def run(destination):
    os.environ['QT_QPA_PLATFORM']='offscreen'
    os.environ['GH3_NO_UPDATE_CHECK']='1'
    from PySide6.QtCore import QCoreApplication,QEvent
    from PySide6.QtWidgets import QApplication
    from .gui import Window
    from .model import Song,Note
    from .converter import convert
    from .service import export_bundle
    from .audio_export import export_ogg
    from .branding import ICON_PNG
    from .welcome import legal_notice_text
    import numpy as np
    import soundfile as sf
    result={}
    with tempfile.TemporaryDirectory(prefix='gh3-frozen-check-') as folder:
        root=Path(folder)
        song=Song(tracks={'Expert':[Note(i*192,i%5,48) for i in range(1000)]})
        converted,report=convert(song)
        export_bundle(converted,report,root/'song')
        if any(n.lane>=4 for n in converted.tracks['Medium']):raise RuntimeError('Medium contains Orange')
        result['chart_and_midi_readback']=True
        wav=root/'source.wav';sf.write(wav,np.zeros(4410),44100)
        export_ogg(wav,root/'song.ogg');info=sf.info(root/'song.ogg')
        if info.frames!=4410 or info.subtype!='VORBIS':raise RuntimeError('Ogg codec check failed')
        result['ogg_encode_decode']=True
        import subprocess,imageio_ffmpeg
        subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-version'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        result['bundled_ffmpeg_runs']=True
        app=QApplication.instance() or QApplication([])
        window=Window();window.show();app.processEvents()
        if not ICON_PNG.is_file() or not legal_notice_text():raise RuntimeError('Package assets/notices missing')
        result['qt_window_and_assets']=True
        window.close();QCoreApplication.sendPostedEvents(None,QEvent.DeferredDelete);app.processEvents()
    Path(destination).write_text(json.dumps(result,indent=2),encoding='utf-8')
