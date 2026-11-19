from pathlib import Path
import pytest
from gh3studio.output_replace import publish
from gh3studio.cleaner import scan_charts,export_cleaned
from test_cleaner import fixture


def test_batch_repeat_updates_same_folders_and_preserves_extras(tmp_path):
    root=tmp_path/'source';fixture(root/'a');fixture(root/'b')
    rows=scan_charts(root);dest=tmp_path/'output'
    first=export_cleaned(rows,dest,root)
    folders=[Path(r['folder']) for r in first]
    (folders[0]/'cover.jpg').write_bytes(b'keep art')
    (folders[0]/'notes.mid').write_bytes(b'stale chart')
    second=export_cleaned(list(reversed(rows)),dest,root)
    assert {r['source']:r['folder'] for r in first}=={r['source']:r['folder'] for r in second}
    assert len([p for p in dest.iterdir() if p.is_dir()])==2
    assert (folders[0]/'cover.jpg').read_bytes()==b'keep art'
    assert not (folders[0]/'notes.mid').exists()
    assert (dest/'cleanup.log').read_text().count('START |')==2


def test_publish_rolls_back_if_install_fails(tmp_path,monkeypatch):
    old=tmp_path/'song';old.mkdir();(old/'notes.chart').write_text('old')
    stage=tmp_path/'stage';stage.mkdir();(stage/'notes.chart').write_text('new')
    real=Path.rename
    def fail(self,target):
        if self==stage:raise OSError('simulated lock')
        return real(self,target)
    monkeypatch.setattr(Path,'rename',fail)
    with pytest.raises(OSError):publish(stage,old,True)
    assert (old/'notes.chart').read_text()=='old'
    assert not list(tmp_path.glob('.gh3-backup-*'))


def test_failed_audio_update_keeps_previous_export(tmp_path,monkeypatch):
    root=tmp_path/'source';fixture(root/'song')
    rows=scan_charts(root);dest=tmp_path/'output';first=export_cleaned(rows,dest,root)
    folder=Path(first[0]['folder']);before={p.name:p.read_bytes() for p in folder.iterdir()}
    def fail(*a,**k):raise OSError('cannot decode')
    monkeypatch.setattr('gh3studio.song_export.export_ogg',fail)
    assert export_cleaned(rows,dest,root)[0]['status']=='failed'
    assert before=={p.name:p.read_bytes() for p in folder.iterdir()}
