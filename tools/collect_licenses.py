"""Collect installed distribution notices for a build; run with the build environment."""
from importlib.metadata import distributions
from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[1]/'licenses'
for dist in distributions():
    name=dist.metadata['Name']
    for entry in dist.files or []:
        if any(word in entry.name.lower() for word in ('license','copying','notice')) and str(entry).find('dist-info')>=0:
            src=Path(dist.locate_file(entry))
            if src.is_file():
                dest=root/name/entry.name; dest.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(src,dest)
print('Collected installed distribution license notices.')
