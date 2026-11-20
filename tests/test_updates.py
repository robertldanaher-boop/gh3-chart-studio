"""Update checks never touch the network in tests and never crash on failure."""
import os
import urllib.error
import pytest
from gh3studio.updates import parse_version, interpret, check_for_update, due, RELEASES_PAGE


def release(tag, exe=True, draft=False):
    assets = [{'name': 'notes.txt', 'browser_download_url': 'https://x/notes.txt'}]
    if exe:
        assets.append({'name': f'GH3ChartStudio-Setup-{tag}.exe', 'browser_download_url': f'https://x/{tag}.exe'})
    return {'tag_name': tag, 'html_url': f'https://x/releases/{tag}', 'assets': assets, 'draft': draft}


def test_parse_version_forms():
    assert parse_version('v0.14.0') == (0, 14, 0)
    assert parse_version('GH3 Chart Studio 0.13.1') == (0, 13, 1)
    assert parse_version('1.2') == (1, 2, 0)
    assert parse_version('latest') is None
    assert parse_version('v0.13.10') > parse_version('v0.13.9')


def test_newer_release_offers_installer():
    result = interpret(release('v0.15.0'), current='0.14.0')
    assert result.status == 'newer' and result.latest == '0.15.0'
    assert result.installer_url == 'https://x/v0.15.0.exe'


def test_same_or_older_release_is_current():
    assert interpret(release('v0.14.0'), current='0.14.0').status == 'current'
    assert interpret(release('v0.11.5'), current='0.14.0').status == 'current'


def test_release_without_installer_still_links_page():
    result = interpret(release('v0.15.0', exe=False), current='0.14.0')
    assert result.status == 'newer' and result.installer_url == '' and result.page_url.endswith('v0.15.0')


def test_draft_or_garbage_is_unavailable():
    assert interpret(release('v9.0.0', draft=True), current='0.14.0').status == 'unavailable'
    assert interpret({'tag_name': 'nightly'}, current='0.14.0').status == 'unavailable'
    assert interpret(None, current='0.14.0').status == 'unavailable'


def test_private_repo_offline_and_bad_json_are_unavailable_not_errors():
    def private(url):
        raise urllib.error.HTTPError(url, 404, 'Not Found', None, None)

    def offline(url):
        raise urllib.error.URLError('no network')

    def garbage(url):
        raise ValueError('bad json')

    for fetch, words in [(private, 'private'), (offline, 'internet'), (garbage, 'unreadable')]:
        result = check_for_update(fetch=fetch, current='0.14.0')
        assert result.status == 'unavailable' and words in result.message
        assert result.page_url == RELEASES_PAGE


def test_daily_interval():
    assert due(0, 100000)
    assert not due(100000, 100000 + 60)
    assert due('not-a-number', 5)


def test_checker_reports_only_newer_when_automatic(tmp_path):
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    pytest.importorskip('PySide6')
    from PySide6.QtCore import QSettings
    from PySide6.QtWidgets import QApplication, QWidget
    from gh3studio.updates import UpdateResult
    from gh3studio.updates_gui import UpdateChecker, LAST_CHECK_KEY
    app = QApplication.instance() or QApplication([])
    parent = QWidget()
    settings = QSettings(str(tmp_path / 'settings.ini'), QSettings.IniFormat)
    prompts, opened = [], []

    def run(result, manual):
        checker = UpdateChecker(parent, settings, check=lambda: result,
                                prompt=lambda w, r, m: (prompts.append((r.status, m)), 'https://x/page')[1],
                                open_url=opened.append)
        assert checker.check(manual=manual)
        checker.thread.wait(5000)
        for _ in range(50):
            app.processEvents()
            if checker.last_result is not None:
                break
        assert checker.last_result is result
        checker.shutdown()

    run(UpdateResult('current', '0.14.0', '0.14.0', message='ok'), manual=False)
    run(UpdateResult('unavailable', '0.14.0', message='offline'), manual=False)
    assert prompts == [] and opened == []
    run(UpdateResult('newer', '0.14.0', '0.15.0', message='new'), manual=False)
    assert prompts == [('newer', False)] and opened == ['https://x/page']
    run(UpdateResult('unavailable', '0.14.0', message='offline'), manual=True)
    assert prompts[-1] == ('unavailable', True)
    assert float(settings.value(LAST_CHECK_KEY)) > 0
    os.environ['GH3_NO_UPDATE_CHECK'] = '1'
    try:
        assert UpdateChecker(parent, settings, check=lambda: None).check_if_due() is False
    finally:
        del os.environ['GH3_NO_UPDATE_CHECK']
    parent.deleteLater()
    app.processEvents()


def test_icon_assets_present_and_loadable():
    from gh3studio.branding import ICON_ICO, ICON_PNG, LOGO_PNG
    for path in (ICON_ICO, ICON_PNG, LOGO_PNG):
        assert path.exists() and path.stat().st_size > 1000, path
    assert ICON_ICO.read_bytes()[:4] == b'\x00\x00\x01\x00'  # ICO header
    assert ICON_PNG.read_bytes()[:8] == b'\x89PNG\r\n\x1a\n'
