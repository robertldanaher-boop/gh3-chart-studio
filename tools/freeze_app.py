"""Build the existing onedir app; no new runtime dependencies or UPX packing."""
import argparse
from pathlib import Path
import subprocess
import sys
import sysconfig


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--distpath',default='dist')
    parser.add_argument('--workpath',default='build')
    args=parser.parse_args()
    if sys.platform!='win32' or sys.version_info[:2]!=(3,11) or sysconfig.get_platform()!='win-amd64':
        parser.error('Build with Windows x64 Python 3.11')
    root=Path(__file__).resolve().parents[1]
    subprocess.run([sys.executable,str(root/'tools/collect_licenses.py')],check=True,cwd=root)
    import PyInstaller.__main__
    PyInstaller.__main__.run(['--noconfirm','--clean','--noupx','--onedir','--windowed',
        '--name','GH3ChartStudio','--distpath',str(Path(args.distpath).resolve()),
        '--workpath',str(Path(args.workpath).resolve()),'--collect-all','imageio_ffmpeg',
        *[arg for source,target in [('LICENSE','.'),('docs','docs'),('licenses','licenses'),
          ('examples','examples'),('gh3studio/assets','gh3studio/assets')]
          for arg in ['--add-data',str(root/source)+';'+target]],
        '--icon',str(root/'gh3studio/assets/app.ico'),str(root/'run_app.py')])


if __name__=='__main__':main()
