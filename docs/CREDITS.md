# Credits and acknowledgements

GH3 Chart Studio is developed for Robert (Bob) Danaher. Its original code is MIT licensed; see LICENSE. Source song, artist and chart-author metadata are preserved separately by the export workflow.

## Compatibility references — not incorporated implementations

**Nanook and TeamGHOST — TheGHOST.** Thank you to Nanook, SciFi, Humour4Fun, UnsteadyCarrot and GameZelda. TheGHOST's importer, HOPO viewer behavior and documentation inform our Wii import profile. No TheGHOST implementation code is copied into or redistributed with GH3 Chart Studio. These credits do not imply affiliation, endorsement or verified game compatibility.

https://github.com/Nanook/TheGHOST

**TheNathannator and contributors — GuitarGame_ChartFormats.** Reference documentation for chart, MIDI and song.ini formats; not an included parsing implementation.

https://github.com/TheNathannator/GuitarGame_ChartFormats

## Application dependencies

- Python and the Python Software Foundation: runtime and standard library, including Tkinter. Installed separately; the source package does not bundle Python.
- The Qt Company and Qt/PySide6/Shiboken contributors: interface, media playback and bindings. Applicable LGPL/GPL notices are included under licenses/Qt; consult the actual terms for distribution.
- Mido: MIDI I/O, MIT.
- NumPy and SciPy communities: numerical processing/audio analysis, BSD licensing.
- SoundFile contributors: audio I/O and metadata, BSD.
- libsndfile contributors: native audio format support, LGPL.
- CFFI and pycparser: bindings/parser dependencies, MIT/BSD.

## Test/build tooling and supporting packages

pytest, PyInstaller (including its bootloader exception), pyinstaller-hooks-contrib, setuptools, packaging, altgraph, pluggy, iniconfig and Windows-specific dependencies have their own notices. Applicable copied license files live under licenses/. tools/collect_licenses.py collects installed dependency licenses for Windows builds. This credits page summarizes roles and does not replace those licenses or claim to enumerate every transitive component.

The startup screen provides a short acknowledgement; About / credits provides project links and more detail. No new third-party library, borrowed artwork, copied UI template or upstream source implementation was introduced for the visual refresh. No Claude handoff/execution is claimed by these credits.
