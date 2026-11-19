"""Publish a validated folder with rollback if replacement fails."""
from pathlib import Path
import shutil
import uuid
from .model import ChartError


def publish(stage,destination,overwrite=False):
    stage=Path(stage);destination=Path(destination)
    if not destination.exists():stage.rename(destination);return
    if not overwrite:raise ChartError('Output folder already exists')
    if destination.is_symlink() or not destination.is_dir():raise ChartError('Output must be a regular directory')
    # Preserve unrelated artwork/user files. Managed outputs are replaced as a set.
    managed={'notes.chart','notes.mid','song.ogg','song.ini','validation.json','import_readme.txt'}
    for item in destination.iterdir():
        if item.name.casefold() in managed:continue
        if item.is_symlink():raise ChartError('Cannot replace output containing symbolic links')
        target=stage/item.name
        if item.is_dir():shutil.copytree(item,target,symlinks=True)
        else:shutil.copy2(item,target)
    backup=destination.with_name('.gh3-backup-'+uuid.uuid4().hex)
    destination.rename(backup)
    try:stage.rename(destination)
    except Exception:
        backup.rename(destination)
        raise
    # A locked unrelated file may leave a backup; never report the new export as lost.
    shutil.rmtree(backup,ignore_errors=True)
