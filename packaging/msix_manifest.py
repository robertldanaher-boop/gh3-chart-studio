"""Generate the desktop MSIX manifest and size-correct icons from existing app art."""
import argparse
from pathlib import Path
import re
import xml.etree.ElementTree as ET

FOUNDATION='http://schemas.microsoft.com/appx/manifest/foundation/windows10'
UAP='http://schemas.microsoft.com/appx/manifest/uap/windows10'
RESCAP='http://schemas.microsoft.com/appx/manifest/foundation/windows10/restrictedcapabilities'


def write_manifest(app_root,version,publisher,identity='BobDanaher.GH3ChartStudio'):
    root=Path(app_root)
    if not (root/'GH3ChartStudio.exe').is_file():raise ValueError('Frozen app executable is missing')
    if not re.fullmatch(r'\d+\.\d+\.\d+',version):raise ValueError('Expected major.minor.patch version')
    if any(int(part)>65535 for part in version.split('.')):raise ValueError('MSIX version component exceeds 65535')
    if not publisher.strip() or not publisher.startswith('CN='):raise ValueError('Use the exact certificate subject, beginning CN=')
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9.-]{2,49}',identity):raise ValueError('Invalid MSIX package identity')
    ET.register_namespace('',FOUNDATION);ET.register_namespace('uap',UAP);ET.register_namespace('rescap',RESCAP)
    package=ET.Element(f'{{{FOUNDATION}}}Package',{'IgnorableNamespaces':'uap rescap'})
    def element(parent,name,**attributes):return ET.SubElement(parent,f'{{{FOUNDATION}}}{name}',attributes)
    element(package,'Identity',Name=identity,Publisher=publisher,Version=version+'.0',ProcessorArchitecture='x64')
    props=element(package,'Properties')
    for key,value in [('DisplayName','GH3 Chart Studio'),('PublisherDisplayName','Bob Danaher'),('Logo',r'Assets\StoreLogo.png')]:element(props,key).text=value
    resources=element(package,'Resources');element(resources,'Resource',Language='en-us')
    deps=element(package,'Dependencies');element(deps,'TargetDeviceFamily',Name='Windows.Desktop',MinVersion='10.0.17763.0',MaxVersionTested='10.0.26100.0')
    apps=element(package,'Applications');app=element(apps,'Application',Id='Studio',Executable='GH3ChartStudio.exe',EntryPoint='Windows.FullTrustApplication')
    ET.SubElement(app,f'{{{UAP}}}VisualElements',{'DisplayName':'GH3 Chart Studio','Description':'Guitar chart repair and four-fret Medium workshop',
        'BackgroundColor':'transparent','Square150x150Logo':r'Assets\Square150x150Logo.png','Square44x44Logo':r'Assets\Square44x44Logo.png'})
    capabilities=element(package,'Capabilities');ET.SubElement(capabilities,f'{{{RESCAP}}}Capability',{'Name':'runFullTrust'})
    ET.indent(package)
    ET.ElementTree(package).write(root/'AppxManifest.xml',encoding='utf-8',xml_declaration=True)
    (root/'GH3_MSIX_PACKAGE').write_text('Windows-managed package. Do not run the source/Win32 updater.\n',encoding='utf-8')
    return root/'AppxManifest.xml'


def write_icons(app_root):
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QImage
    source=Path(__file__).resolve().parents[1]/'gh3studio/assets/app_icon.png'
    image=QImage(str(source))
    if image.isNull():raise ValueError('App icon could not be loaded')
    assets=Path(app_root)/'Assets';assets.mkdir(exist_ok=True)
    for name,size in [('Square44x44Logo',44),('Square150x150Logo',150),('StoreLogo',50)]:
        if not image.scaled(size,size,Qt.IgnoreAspectRatio,Qt.SmoothTransformation).save(str(assets/(name+'.png'))):raise ValueError('Could not create MSIX icon')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--app-root',required=True);parser.add_argument('--version',required=True)
    parser.add_argument('--publisher',required=True);args=parser.parse_args()
    write_manifest(args.app_root,args.version,args.publisher);write_icons(args.app_root)
