"""Reproduce import/cleanup/paired-export QA on user-supplied charts, unchanged."""
import hashlib,json,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from gh3studio.patterns import PatternStore,scan_folder
from gh3studio.service import load,export_bundle
from gh3studio.editing import prepare_cleanup
from gh3studio.converter import Settings,convert
from gh3studio.variations import generate_variations
import shutil
results=[]
with tempfile.TemporaryDirectory() as td:
 root=Path(td);store=PatternStore(root/'patterns.sqlite3')
 for i,arg in enumerate(sys.argv[1:]):
  source=Path(arg);before=hashlib.sha256(source.read_bytes()).hexdigest()
  folder=root/str(i);folder.mkdir();shutil.copyfile(source,folder/'notes.chart')
  scan=scan_folder(folder,store);assert scan['failed']==0 and scan['imported']==1
  assert scan_folder(folder,store)['duplicates']==1
  song=load(source,learning_only=True);clean,review=prepare_cleanup(song,True,True)
  converted,report=convert(clean);export_bundle(converted,report,root/f'converted-{i}')
  variants=generate_variations(clean,Settings(),store,42)
  for name,(result,report) in variants.items():export_bundle(result,report,root/f'{i}-{name}')
  assert hashlib.sha256(source.read_bytes()).hexdigest()==before
  results.append(dict(file=source.name,title=song.metadata.get('Name'),sha256=before,
    patterns_added=scan['patterns_added'],cleanup_changes=len(review['changes']),
    medium_gems=len(converted.tracks['Medium']),paired_exports=4,original_unchanged=True))
print(json.dumps(results,indent=2,ensure_ascii=False))
