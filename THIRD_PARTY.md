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
