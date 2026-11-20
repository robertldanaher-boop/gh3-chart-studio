from pathlib import Path
import pytest
from gh3studio.model import Note
from gh3studio.cleaner import scan_charts,export_cleaned,fingerprint
from gh3studio.chartio import read_chart
from test_cleaner import fixture


def test_recursive_bulk_fallback_preserves_other_tracks_and_exports(tmp_path):
    root=tmp_path/'collection'
    a=fixture(root/'artist'/'album'/'one',tracks={'Expert':[Note(0,0),Note(192,4,96),Note(384,2)],'Hard':[Note(0,1)],'Medium':[Note(0,2)]})
    b=fixture(root/'two',tracks={'Hard':[Note(0,3),Note(192,4,96)]})
    fixture(root/'three',tracks={'Easy':[Note(0,0)]})
    before={str(p):fingerprint(p) for p in root.rglob('*') if p.is_file()}
    rows=scan_charts(root,inspect_options={'medium_source':'Expert then Hard'})
    assert len(rows)==3
    good=[r for r in rows if not r['errors']];assert len(good)==2
    for row in good:
        original=read_chart(row['path']);out=row['song']
        for d in ('Expert','Hard'):
            if original.tracks.get(d):assert out.tracks[d]==original.tracks[d]
        assert not any(out.modifiers.values())
        if any(original.modifiers.values()):assert row['conversion']['all_difficulty_cleanup']['changes']
        assert all(out.tracks.get(d) for d in ('Easy','Medium','Hard','Expert'))
        assert all(n.lane<3 for n in out.tracks['Easy'])
        assert all(n.lane<4 for n in out.tracks['Medium'])
        assert any(n.length==96 for n in out.tracks['Medium'])
    results=export_cleaned(rows,tmp_path/'out',root)
    assert sum(r['status']=='exported' for r in results)==2
    assert sum(r['status']=='failed' for r in results)==1
    for result in results:
        if result['status']=='exported':
            folder=Path(result['folder']);assert (folder/'song.ogg').is_file() and (folder/'song.ini').is_file()
            assert all(n.lane<4 for n in read_chart(folder/'notes.chart').tracks['Medium'])
    assert before=={str(p):fingerprint(p) for p in root.rglob('*') if p.is_file()}


def test_bulk_explicit_source_and_cancel(tmp_path):
    root=tmp_path/'source';fixture(root/'one',tracks={'Hard':[Note(0,0)]})
    assert scan_charts(root,inspect_options={'medium_source':'Expert'})[0]['errors']
    rows=scan_charts(root,inspect_options={'medium_source':'Hard'})
    assert not rows[0]['errors']
    assert export_cleaned(rows,tmp_path/'out',root,cancel=lambda:True)==[]
    with pytest.raises(ValueError):export_cleaned(rows,root/'output',root)


def test_bulk_gui_scan_and_export(tmp_path):
    from test_gui import wait
    from PySide6.QtWidgets import QApplication
    from gh3studio.gui import Window
    app=QApplication.instance() or QApplication([])
    root=tmp_path/'collection';fixture(root/'artist'/'song',tracks={'Expert':[Note(0,0),Note(192,4,96)]})
    w=Window();w.show();w.adapt.open_bulk();panel=w.adapt.bulk;panel.scan(root);wait(w);app.processEvents()
    assert len(panel.rows)==1 and not panel.rows[0]['errors']
    panel.set_checked(True);panel.approve.setChecked(True);panel.export_to(tmp_path/'out');wait(w)
    assert list((tmp_path/'out').glob('*/notes.chart'))
    assert w.song is None and w.converted is None
    assert w.adapt.pages.currentWidget() is panel
    w.close();app.processEvents()


@pytest.mark.parametrize('route',['folder_button','drop','home_drop','guided_path'])
def test_medium_collection_entry_routes_scan_nested_songs(tmp_path,monkeypatch,route):
    from test_gui import wait
    from PySide6.QtWidgets import QApplication,QFileDialog
    from PySide6.QtCore import QMimeData,QUrl,QPointF,Qt
    from PySide6.QtGui import QDropEvent
    from gh3studio.gui import Window
    app=QApplication.instance() or QApplication([])
    root=tmp_path/'collection'
    fixture(root/'artist'/'album'/'one',tracks={'Expert':[Note(0,0),Note(192,4,96)]})
    fixture(root/'two',tracks={'Hard':[Note(0,1),Note(192,3)]})
    w=Window();w.show();w.welcome.actions['orange'].click();app.processEvents()
    if route=='folder_button':
        monkeypatch.setattr(QFileDialog,'getExistingDirectory',lambda *args,**kwargs:str(root))
        assert w.adapt.folder_button.isVisible()
        w.adapt.folder_button.click()
    elif route in ('drop','home_drop'):
        if route=='home_drop':w.tabs.setCurrentWidget(w.welcome)
        mime=QMimeData();mime.setUrls([QUrl.fromLocalFile(str(root))])
        event=QDropEvent(QPointF(50,50),Qt.CopyAction,mime,Qt.LeftButton,Qt.NoModifier)
        w.dropEvent(event);assert event.isAccepted()
    else:assert w.start_guided('orange',root)
    wait(w);app.processEvents()
    assert w.goal=='orange' and w.tabs.currentWidget() is w.adapt
    assert w.adapt.pages.currentWidget() is w.adapt.bulk
    assert len(w.adapt.bulk.rows)==2 and not w.cleaner.rows
    for row in w.adapt.bulk.rows:
        assert not row['errors']
        assert row['song'].tracks['Medium'] and all(n.lane<4 for n in row['song'].tracks['Medium'])
        assert row['song'].tracks['Easy'] and all(n.lane<3 for n in row['song'].tracks['Easy'])
    w.close();app.processEvents()


def test_second_batch_after_export_scans_and_shows_all_songs(tmp_path):
    """Bob: after exporting one folder, dropping the next folder showed no songs."""
    from test_gui import wait
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QMimeData,QUrl,QPointF,Qt
    from PySide6.QtGui import QDropEvent
    from gh3studio.gui import Window
    app=QApplication.instance() or QApplication([])
    first=tmp_path/'batch one';fixture(first/'a',tracks={'Expert':[Note(0,0),Note(192,4,96)]})
    second=tmp_path/'batch two'
    fixture(second/'b',tracks={'Expert':[Note(0,1),Note(192,2)]});fixture(second/'c',tracks={'Hard':[Note(0,0),Note(96,3)]})
    w=Window();w.show();w.welcome.actions['orange'].click();app.processEvents()
    def drop(folder):
        mime=QMimeData();mime.setUrls([QUrl.fromLocalFile(str(folder))])
        event=QDropEvent(QPointF(50,50),Qt.CopyAction,mime,Qt.LeftButton,Qt.NoModifier)
        w.dropEvent(event);assert event.isAccepted();wait(w);app.processEvents()
    bulk=w.adapt.bulk
    drop(first);assert len(bulk.rows)==1
    bulk.approve.setChecked(True);bulk.output_path.setText(str(tmp_path/'out'))
    bulk.export_button.click();wait(w);app.processEvents()
    assert (tmp_path/'out'/'cleanup_summary.json').exists()
    assert w.goal=='orange' and w.tabs.currentWidget() is w.adapt  # export keeps the Prepare workflow
    bulk.search.setText('nothing matches this');bulk.filter.setCurrentIndex(1)  # leftovers from batch one
    drop(second)
    assert w.tabs.currentWidget() is w.adapt and w.adapt.pages.currentWidget() is bulk
    assert sorted(Path(r['path']).parent.name for r in bulk.rows)==['b','c']
    assert bulk.search.text()=='' and bulk.filter.currentIndex()==0
    assert not any(bulk.table.isRowHidden(i) for i in range(len(bulk.rows)))
    assert not bulk.search.acceptDrops() and not bulk.output_path.acceptDrops()
    w.close();app.processEvents()
