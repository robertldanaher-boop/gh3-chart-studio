"""Check GitHub for a newer release. No Qt here so it can be tested offline.

The check reads the repository's latest published release. If the repository is
private (GitHub answers 404 without a token) or the PC is offline, the result is
'unavailable' with a plain explanation, never an error dialog or a crash.
Nothing is downloaded or installed automatically: the user is offered the
release page or installer link and decides.
"""
import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass

from . import __version__

REPOSITORY = 'robertldanaher-boop/gh3-chart-studio'
RELEASES_PAGE = f'https://github.com/{REPOSITORY}/releases'
LATEST_API = f'https://api.github.com/repos/{REPOSITORY}/releases/latest'
CHECK_INTERVAL_SECONDS = 24 * 60 * 60


def parse_version(text):
    """'v0.14.0' / '0.14.0' / 'GH3 Chart Studio 0.14.0' -> (0, 14, 0); None if absent."""
    match = re.search(r'(\d+)\.(\d+)(?:\.(\d+))?', str(text or ''))
    if not match:
        return None
    return tuple(int(part or 0) for part in match.groups())


@dataclass
class UpdateResult:
    status: str            # 'newer', 'current' or 'unavailable'
    current: str
    latest: str = ''
    page_url: str = RELEASES_PAGE
    installer_url: str = ''
    message: str = ''
    source_zip_url: str = ''  # GitHub's automatic "Source code (zip)" for the release tag


def _fetch(url, timeout=8):
    request = urllib.request.Request(url, headers={
        'Accept': 'application/vnd.github+json',
        'User-Agent': f'GH3ChartStudio/{__version__}'})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode('utf-8'))


def interpret(release, current=__version__):
    """Turn a GitHub release JSON object into an UpdateResult."""
    if not isinstance(release, dict) or release.get('draft'):
        return UpdateResult('unavailable', current, message='No published release was found.')
    tag = release.get('tag_name') or release.get('name') or ''
    latest, mine = parse_version(tag), parse_version(current)
    if latest is None or mine is None:
        return UpdateResult('unavailable', current, tag, message=f'Could not read the release version "{tag}".')
    installer = attached_zip = ''
    for asset in release.get('assets') or []:
        name = str(asset.get('name', '')).lower()
        if name.endswith('.exe') and not installer:
            installer = asset.get('browser_download_url', '')
        # A release ZIP Bob attaches (GH3_Chart_Studio_vX_Y_Z.zip) is preferred over
        # GitHub's automatic source ZIP: it is exactly the package he was given.
        if name.endswith('.zip') and 'gh3' in name and not attached_zip:
            attached_zip = asset.get('browser_download_url', '')
    page = release.get('html_url') or RELEASES_PAGE
    label = '.'.join(map(str, latest))
    zipball = attached_zip or release.get('zipball_url') or ''
    if latest > mine:
        return UpdateResult('newer', current, label, page, installer,
                            f'Version {label} is available (you have {current}).', zipball)
    return UpdateResult('current', current, label, page, installer,
                        f'You have the latest version ({current}).', zipball)


def check_for_update(fetch=_fetch, current=__version__):
    try:
        return interpret(fetch(LATEST_API), current)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            message = ('No public release was found. The GitHub repository may be private '
                       'or have no published release yet. You can open the releases page instead.')
        else:
            message = f'GitHub answered with error {exc.code}. Try again later.'
        return UpdateResult('unavailable', current, message=message)
    except (urllib.error.URLError, TimeoutError, OSError):
        return UpdateResult('unavailable', current, message='Could not reach GitHub. Check the internet connection and try again.')
    except ValueError:
        return UpdateResult('unavailable', current, message='GitHub returned an unreadable answer. Try again later.')


def due(last_checked, now, interval=CHECK_INTERVAL_SECONDS):
    try:
        return now - float(last_checked) >= interval
    except (TypeError, ValueError):
        return True


# ---- Download and install -------------------------------------------------
# The update is the release's source ZIP, installed with the same
# "Install GH3 Chart Studio.cmd" Bob uses by hand: it copies the program, runs
# setup and the tests once, and keeps the Start menu entries.

INSTALLER_CMD = 'Install GH3 Chart Studio.cmd'
MAX_DOWNLOAD_BYTES = 200 * 1024 * 1024


def _download(url, destination, progress=lambda done, total: None, cancel=lambda: False, timeout=30):
    request = urllib.request.Request(url, headers={'User-Agent': f'GH3ChartStudio/{__version__}',
                                                   'Accept': 'application/vnd.github+json'})
    with urllib.request.urlopen(request, timeout=timeout) as response, open(destination, 'wb') as out:
        total = int(response.headers.get('Content-Length') or 0)
        done = 0
        while True:
            if cancel():
                raise RuntimeError('Download cancelled')
            block = response.read(256 * 1024)
            if not block:
                break
            done += len(block)
            if done > MAX_DOWNLOAD_BYTES:
                raise RuntimeError('Download is unexpectedly large; stopped')
            out.write(block)
            progress(done, total)
    return destination


def extract_update(zip_path, folder, expected_version):
    """Safely extract the release ZIP and return the folder holding the installer.
    Refuses paths that escape the folder and a version that does not match."""
    import zipfile
    from pathlib import Path
    folder = Path(folder).resolve()
    with zipfile.ZipFile(zip_path) as archive:
        bad = archive.testzip()
        if bad:
            raise RuntimeError(f'Downloaded update is damaged ({bad})')
        for member in archive.infolist():
            target = (folder / member.filename).resolve()
            if not target.is_relative_to(folder):
                raise RuntimeError('Downloaded update contains an unsafe path; not installed')
        archive.extractall(folder)
    roots = [p.parent for p in folder.rglob(INSTALLER_CMD) if (p.parent / 'gh3studio' / '__init__.py').is_file()]
    if len(roots) != 1:
        raise RuntimeError('Downloaded update does not contain the installer; open the release page instead')
    root = roots[0]
    found = parse_version((root / 'gh3studio' / '__init__.py').read_text(encoding='utf-8'))
    if found != parse_version(expected_version):
        raise RuntimeError(f'Downloaded update is version {".".join(map(str, found or ()))}, expected {expected_version}')
    return root


def download_update(result, workdir, progress=lambda done, total: None, cancel=lambda: False, fetch=_download):
    """Download and unpack the release; returns the folder to install from."""
    from pathlib import Path
    if not result.source_zip_url:
        raise RuntimeError('This release has no downloadable source package; open the release page instead')
    workdir = Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    archive = workdir / f'GH3_Chart_Studio_{result.latest}.zip'
    fetch(result.source_zip_url, archive, progress, cancel)
    return extract_update(archive, workdir / 'extracted', result.latest)


def launch_installer(root, popen=None):
    """Start the installer detached so it keeps running after the studio closes."""
    import subprocess
    import sys
    from pathlib import Path
    popen = popen or subprocess.Popen
    flags = 0
    if sys.platform == 'win32':
        flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
    return popen(['cmd.exe', '/c', str(Path(root) / INSTALLER_CMD)], cwd=str(root), creationflags=flags,
                 close_fds=True)
