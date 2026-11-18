"""Acceptance for the focused UI, including real exported chart/audio artifacts."""
from pathlib import Path
import pytest
from PySide6.QtCore import Qt,QPoint
from PySide6.QtWidgets import QFileDialog,QDialogButtonBox
from gh3studio.gui import Window
from gh3studio.chartio import read_chart,write_chart
from gh3studio.model import Song,Note
from test_gui import app,wait,dispose_closed_windows_on_gui_thread,FIXTURE
from test_cleaner import fixture


def test_home_only_offers_essential_goals_and_reserve_is_reversible(app):
    w=Window();w.show();app.processEvents()
    assert set(w.welcome.actions)=={'clean','orange'}
    assert [w.tabs.tabText(i) for i in range(w.tabs.count()) if w.tabs.isTabVisible(i)]==['Home','Clean songs','Four-fret Medium']
    w.welcome.actions['clean'].click();assert w.tabs.currentWidget() is w.cleaner
    w.open_reserved(w.library);assert w.tabs.currentWidget() is w.library and w.tabs.isTabVisible(w.tabs.indexOf(w.library))
    w.hide_reserved();assert w.tabs.currentWidget() is w.welcome
    assert all(not w.tabs.isTabVisible(w.tabs.indexOf(p)) for p in w.reserved)
    w.close()


@pytest.mark.parametrize('large_text',[False,True])
def test_essential_actions_visible_at_1024_by_700(app,large_text):
    w=Window()
    if large_text:w.setStyleSheet(w.styleSheet()+'\nQWidget {font-size:18px;}')
    w.resize(1024,700);w.show()
    for goal,panel in [('clean',w.cleaner),('orange',w.adapt)]:
        w.enter_workspace(goal);app.processEvents()
        assert w.width()<=1024 and w.height()<=700
        assert panel.export_button.visibleRegion().boundingRect().height()>=panel.export_button.height()-2
        assert panel.steps.isVisible()
    w.close()


def test_guided_medium_preserves_sustain_and_compares_exact_source(tmp_path,app):
    source=Song(metadata={'Name':'Study','Artist':'Fixture'},tracks={
        'Expert':[Note(0,0),Note(96,4,96),Note(288,2)],
        'Hard':[Note(0,1),Note(96,4,96),Note(288,3)],'Medium':[Note(0,2)]})
    chart=tmp_path/'source.chart';write_chart(source,chart)
    w=Window();w.show();w.start_guided('orange',chart);wait(w)
    assert w.adapt.preserve.isChecked()
    w.adapt.source.setCurrentText('Hard');w.adapt.create_button.click();wait(w)
    assert w.report['source_difficulty']=='Hard' and w.report['transferred_orange_sustains']==1
    assert w.playback.current==(w.converted,'Medium')
    medium=list(w.converted.tracks['Medium']);assert any(n.tick==96 and n.length==96 for n in medium)
    assert all(n.lane<4 for n in medium)
    w.adapt.restore_button.click();assert w.playback.current==(w.song,'Hard')
    w.playback.difficulty.setCurrentText('Medium');assert w.playback.current[0].tracks['Medium']==source.tracks['Medium']
    w.adapt.output_preview.click();assert w.playback.current==(w.converted,'Medium')
    assert w.converted.tracks['Medium']==medium
    w.export_song_to(tmp_path/'output',FIXTURE.parent/'audio'/'onset-study.wav');wait(w)
    exported=read_chart(tmp_path/'output'/'notes.chart')
    assert exported.tracks['Hard']==source.tracks['Hard'] and exported.tracks['Expert']==source.tracks['Expert']
    assert exported.tracks['Medium']==medium and (tmp_path/'output'/'song.ogg').is_file()
    assert w.adapt.open_output.isEnabled() and 'Export complete' in w.adapt.next_step.text()
    w.close()


def test_cleaner_filter_full_queue_selection_and_failed_log_access(tmp_path,app):
    good=fixture(tmp_path/'songs'/'good');bad=fixture(tmp_path/'songs'/'bad');bad.write_text('broken',encoding='utf-8')
    w=Window();w.start_guided('clean',tmp_path/'songs');wait(w);panel=w.cleaner
    panel.filter.setCurrentText('Needs help');app.processEvents()
    for i,row in enumerate(panel.rows):assert panel.table.isRowHidden(i)==(not row['errors'])
    panel.select_all.click();assert all(panel.table.item(i,0).checkState()==Qt.Checked for i in range(2))
    panel.select_none.click()
    bad_index=next(i for i,row in enumerate(panel.rows) if row['errors'])
    panel.table.item(bad_index,0).setCheckState(Qt.Checked);panel.approve.setChecked(True)
    panel.export_to(tmp_path/'failed-output');wait(w)
    assert panel.open_output.isEnabled()  # Logs remain reachable even when every selected song failed.
    assert panel.detail_tabs.currentWidget() is panel.results
    assert 'NEEDS HELP:' in panel.results.toPlainText() and 'Invalid chart syntax' in panel.results.toPlainText()
    assert (tmp_path/'failed-output'/'cleanup.log').is_file()
    w.close()


def test_reserved_preview_returns_to_focused_workspace(app):
    w=Window();w.start_guided('orange',FIXTURE);wait(w)
    w.open_reserved(w.audio);w.audio.show_listen();app.processEvents()
    assert w.audio.pages.currentWidget() is w.playback
    w.enter_workspace('orange');app.processEvents()
    assert w.adapt.isAncestorOf(w.playback) and not w.playback.legacy_conversion.isVisible()
    assert w.adapt.source.count()>0
    w.close()


def test_failed_import_visible_in_active_workflow(tmp_path,app):
    chart=tmp_path/'broken.chart';chart.write_text('broken',encoding='utf-8')
    w=Window();w.start_guided('orange',chart);wait(w)
    assert 'Needs attention:' in w.adapt.next_step.text()
    assert 'Could not complete:' in w.operation_label.text()
    assert not w.adapt.export_button.isEnabled()
    w.close()


def test_export_review_explains_missing_recording(app):
    from gh3studio.song_export_gui import SongExportDialog
    dialog=SongExportDialog(Song(tracks={'Medium':[Note(0,0)]}))
    assert not dialog.buttons.button(QDialogButtonBox.Save).isEnabled()
    assert 'recording' in dialog.readiness.text()
    assert 'Structural checks passed' in dialog.details.toPlainText()
    dialog.close()
