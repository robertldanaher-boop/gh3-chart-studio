# Dependencies and license review

Original implementation; no third-party chart engine source was copied.

- PySide6 / Shiboken 6.8.3: Qt for Python, LGPLv3/GPLv3 or commercial terms.
  Uses standard QtCore, QtGui and QtWidgets APIs, Python 3.11 compatible wheels.
  https://doc.qt.io/qtforpython-6/licenses.html
  https://github.com/pyside/pyside-setup
  Qt license texts are in licenses/Qt. Python source launch keeps Qt replaceable.
- Mido 1.3.3: MIT; Python >=3.7; read/write standard MIDI without a hardware backend.
  https://github.com/mido/mido ; license notice included in licenses/mido.
- pytest 8.3.5: MIT; test-only.
- PyInstaller 6.12.0: GPL with bootloader exception; build-only.
  A Windows executable must be built/tested on Windows. One-directory mode is used.
- Transitive installed distribution notices are collected in licenses. The Windows
  build collects notices again in its own installed environment.

Independent QA used parsehero 0.0.2 (GPL-3.0) in a separate Node process. It is NOT
bundled, linked into, or required by the application. Its dependency midi-file is
MIT. tools/independent_check.mjs is our own test harness; install the external parser
separately to repeat the check. https://github.com/awphi/parsehero

TheGHOST source was inspected for interoperability only; none is redistributed.
The chart-format documentation was consulted as a reference. See COMPATIBILITY.md.

Before distributing compiled Qt binaries, include their applicable notices and
source/relinking availability as required by the chosen Qt license. This source
package does not include Qt binaries or claim commercial-license authorization.

## Audio stack added in 0.3.0

- NumPy 2.2.4 and SciPy 1.15.2: BSD-3-Clause; Python 3.11 wheels verified in local QA.
  https://numpy.org/doc/stable/license.html ; https://scipy.org/faq/
- SoundFile 0.13.1: BSD-3-Clause; its bundled libsndfile uses LGPL-2.1 terms.
  https://python-soundfile.readthedocs.io/en/latest/
  Library notice is copied from the installed wheel's _soundfile_data/COPYING.
- CFFI and pycparser: transitive decoder dependencies; installed notices collected.
- No FFmpeg binary, model weights, dataset or source-separation code is bundled.

PyInstaller's installed SoundFile hook was inspected: it collects the libsndfile
shared library and COPYING notice. That source inspection does not prove a Windows
binary build. Review the bundled dependency notices for binary redistribution.

## Playback added in 0.4.0

QtMultimedia QMediaPlayer/QAudioOutput are now used for playback. The installed
PySide6 6.8.3 Linux wheel reports FFmpeg 7.1 under LGPL-2.1-or-later at runtime.
Qt's own license and its FFmpeg third-party obligations both apply to binary builds:
https://doc.qt.io/qt-6.8/licenses-used-in-qt.html
https://doc.qt.io/qt-6.8/qtmultimedia-index.html#licenses-and-attributions
No Qt/FFmpeg binaries are included in this source ZIP. A compiled distribution
requires an audit of the actual platform backend, matching notices and corresponding
source availability; the existing distribution-notice collector alone does not
complete that audit. Do not describe a Windows binary as distribution-ready based
only on a successful PyInstaller build. We use Qt APIs; no FFmpeg source was copied.

## Audio recovery dependency (0.7.3)

imageio-ffmpeg 0.6.0 (BSD-2-Clause wrapper) supplies a separate FFmpeg executable.
The binary has its own GPL license; the wrapper's BSD license does not cover it.
See docs/FFMPEG_DEPENDENCY.md. This source ZIP does not redistribute that executable;
START_WINDOWS installs the hash-pinned upstream Windows wheel. Build collection now
captures the actual executable's license/build notices as well as wrapper notices.
