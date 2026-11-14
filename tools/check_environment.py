"""Report actual capability; never imply missing-dependency tests passed."""
import importlib
import platform
import sys
print('Python:',sys.version.replace('\n',' '),'Platform:',platform.platform())
missing=[]
for name in ('PySide6','soundfile','mido','numpy','scipy','pytest'):
    try:
        module=importlib.import_module(name)
        print(name, 'OK',getattr(module,'__version__','version unavailable'))
    except Exception as exc:
        missing.append(name);print(name,'UNAVAILABLE',str(exc))
if missing:
    print('Full suite blocked. With pytest installed, run only: python -m pytest tests/test_minimal.py -q')
    print('That subset does NOT verify MIDI, audio analysis, GUI, playback, or Windows.')
    sys.exit(1)
print('Dependencies import. Full-suite command: python -m pytest -q')
print('Windows and actual audio/gameplay acceptance remain separate.')
