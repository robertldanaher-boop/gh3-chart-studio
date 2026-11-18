# Alternate decoder dependency and packaging

Pinned provider: imageio-ffmpeg 0.6.0. Its wrapper is BSD-2-Clause; the FFmpeg
executable is separately licensed. The installed Linux executable reports GPL
version 3 or later. The checked Windows executable contains GPL version 3 or later
library-license strings and --enable-gpl. GPL-3 text and the wrapper's notice are
included under licenses/FFmpeg and licenses/imageio-ffmpeg respectively.

The upstream Windows wheel is imageio_ffmpeg-0.6.0-py3-none-win_amd64.whl, SHA-256:
02fa47c83703c37df6bfe4896aab339013f62bf02c5ebf2dce6da56af04ffc0a
It contains imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe. The Linux wheel
used in testing contains FFmpeg 7.0.2. Both are supplied by the pinned provider;
we tested the Linux executable, not the Windows executable.

This release ZIP contains our source and notices, not an FFmpeg binary. Startup
installs the hash-pinned upstream wheel along with the other dependencies. The
application invokes the executable as a separate local process, without a shell,
for strict decoding only. No new upstream implementation code is copied into the
application, and no user music is bundled. Existing Nanook/TeamGHOST credits remain.

build_windows.cmd now collects imageio_ffmpeg package data, including its executable.
tools/collect_licenses.py records the actual executable's -L and -version outputs
as BINARY_LICENSE.txt and BINARY_BUILD.txt for that build. This collection supplements,
and does not replace, the full license obligations. A compiled redistributable is
not provided or declared distribution-ready here. Before redistributing a compiled
build, arrange the corresponding-source/license materials required by its actual
FFmpeg build and bundled components; a version string or website link alone is not
a complete corresponding-source package. The same care applies to existing Qt/native
libraries. No Windows executable, signing or reputation guarantee is claimed.

References checked:
https://pypi.org/project/imageio-ffmpeg/0.6.0/
https://github.com/imageio/imageio-ffmpeg
https://github.com/imageio/imageio-ffmpeg/blob/v0.6.0/LICENSE
https://ffmpeg.org/legal.html
https://ffmpeg.org/download.html

Reproducible source installation remains START_WINDOWS.cmd using
requirements-windows.lock with --require-hashes and --only-binary=:all:.
The provider lookup may honor IMAGEIO_FFMPEG_EXE if deliberately set by the user;
otherwise it locates the packaged executable. No PATH edit or elevation is required.
