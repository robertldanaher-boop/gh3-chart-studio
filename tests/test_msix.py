import importlib.util
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import pytest
from gh3studio import package_runtime
from test_gui import app

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('gh3_msix_manifest',ROOT/'packaging/msix_manifest.py')
manifest=importlib.util.module_from_spec(spec);spec.loader.exec_module(manifest)


def test_msix_manifest_preserves_exact_publisher_and_has_full_trust_identity(tmp_path):
    (tmp_path/'GH3ChartStudio.exe').write_bytes(b'fixture')
    publisher='CN=Bob & Studio, O=Example'
    path=manifest.write_manifest(tmp_path,'0.20.0',publisher)
    doc=ET.parse(path);ns={'f':manifest.FOUNDATION,'uap':manifest.UAP,'r':manifest.RESCAP}
    identity=doc.find('f:Identity',ns)
    assert identity.attrib['Publisher']==publisher and identity.attrib['Version']=='0.20.0.0'
    assert identity.attrib['ProcessorArchitecture']=='x64'
    app=doc.find('f:Applications/f:Application',ns)
    assert app.attrib['Executable']=='GH3ChartStudio.exe' and app.attrib['EntryPoint']=='Windows.FullTrustApplication'
    assert doc.find('f:Capabilities/r:Capability',ns).attrib['Name']=='runFullTrust'
    assert (tmp_path/'GH3_MSIX_PACKAGE').exists()


@pytest.mark.parametrize('version,publisher',[('0.20','CN=Test'),('70000.0.0','CN=Test'),('0.20.0','')])
def test_manifest_rejects_invalid_identity_input(tmp_path,version,publisher):
    (tmp_path/'GH3ChartStudio.exe').write_bytes(b'fixture')
    with pytest.raises(ValueError):manifest.write_manifest(tmp_path,version,publisher)


def test_manifest_icons_have_required_sizes(tmp_path):
    from PySide6.QtGui import QImage
    manifest.write_icons(tmp_path)
    for name,size in [('Square44x44Logo',44),('Square150x150Logo',150),('StoreLogo',50)]:
        image=QImage(str(tmp_path/'Assets'/(name+'.png')))
        assert image.width()==image.height()==size


def test_marker_makes_frozen_engineering_build_use_msix_policy(tmp_path,monkeypatch):
    monkeypatch.setattr(sys,'platform','win32');monkeypatch.setattr(sys,'frozen',True,raising=False)
    monkeypatch.setattr(sys,'executable',str(tmp_path/'GH3ChartStudio.exe'))
    (tmp_path/'GH3_MSIX_PACKAGE').write_text('managed')
    assert package_runtime.is_msix()


def test_msix_cannot_launch_source_updater(app,monkeypatch):
    from PySide6.QtWidgets import QWidget
    from gh3studio.updates_gui import UpdateChecker
    monkeypatch.setattr(package_runtime,'is_msix',lambda:True)
    notifications=[];calls=[];parent=QWidget()
    checker=UpdateChecker(parent,check=lambda:calls.append('network'),download=lambda *a:calls.append('download'),notify=notifications.append)
    assert not checker.check_on_startup()
    assert not checker.check(manual=True)
    assert not checker.start_install(object())
    assert not calls and len(notifications)==2
    parent.close()


def test_packaged_working_directory_is_user_data(app,tmp_path,monkeypatch):
    from PySide6.QtCore import QStandardPaths
    old=Path.cwd()
    monkeypatch.setattr(package_runtime,'is_msix',lambda:True)
    monkeypatch.setattr(QStandardPaths,'writableLocation',lambda *a:str(tmp_path/'user-data'))
    try:
        package_runtime.configure_working_directory()
        assert Path.cwd()==tmp_path/'user-data'
    finally:
        import os
        os.chdir(old)
