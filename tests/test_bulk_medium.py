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
    from gh3studio.bulk_gui import BulkDialog
    app=QApplication.instance() or QApplication([])
    root=tmp_path/'collection';fixture(root/'artist'/'song',tracks={'Expert':[Note(0,0),Note(192,4,96)]})
    w=Window();d=BulkDialog(w);d.show();d.panel.scan(root);wait(w);app.processEvents()
    assert len(d.panel.rows)==1 and not d.panel.rows[0]['errors']
    d.panel.set_checked(True);d.panel.approve.setChecked(True);d.panel.export_to(tmp_path/'out');wait(w)
    assert list((tmp_path/'out').glob('*/notes.chart'))
    assert w.song is None and w.converted is None
    d.reject();w.close();app.processEvents()
