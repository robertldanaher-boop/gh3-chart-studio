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
    installer = ''
    for asset in release.get('assets') or []:
        name = str(asset.get('name', ''))
        if name.lower().endswith('.exe'):
            installer = asset.get('browser_download_url', '')
            break
    page = release.get('html_url') or RELEASES_PAGE
    label = '.'.join(map(str, latest))
    if latest > mine:
        return UpdateResult('newer', current, label, page, installer,
                            f'Version {label} is available (you have {current}).')
    return UpdateResult('current', current, label, page, installer,
                        f'You have the latest version ({current}).')


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
