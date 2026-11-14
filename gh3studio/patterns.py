"""Local statistical pattern extraction and transactional SQLite corpus storage."""
import hashlib
import json
import os
import sqlite3
from collections import Counter
from contextlib import closing
from fractions import Fraction
from itertools import groupby
from pathlib import Path
from .model import ChartError
from .service import load

SCHEMA_VERSION = 1
APPLICATION_ID = 0x47483343
WINDOW_BEATS = 8
CATEGORIES = ('Steady rhythm','Fast rhythm','Repeating riff','Technical run','Alternating chord pattern','Sustained passage','Mixed passage')

def groups(notes):
    return [(tick,list(ns)) for tick,ns in groupby(sorted(notes),key=lambda n:n.tick)]

def extract(song,difficulty,cancelled=lambda:False):
    """Eight-quarter-note windows, not inferred musical phrases or bar boundaries."""
    windows={}
    for tick,ns in groups(song.tracks.get(difficulty,[])):
        windows.setdefault(tick//(song.resolution*WINDOW_BEATS),[]).append((tick,ns))
    output=[]
    for window,events in sorted(windows.items()):
        if cancelled(): raise ChartError('Cancelled')
        start=window*song.resolution*WINDOW_BEATS
        end=start+song.resolution*WINDOW_BEATS
        tokens=[{'beat':str(Fraction(t-start,song.resolution)),
                 'lanes':[n.lane for n in ns],
                 'lengths':[str(Fraction(n.length,song.resolution)) for n in ns]} for t,ns in events]
        count=len(events); gems=sum(len(ns) for _,ns in events)
        chord_ratio=sum(len(ns)>1 for _,ns in events)/count
        sustain_ratio=sum(n.length>song.resolution/12 for _,ns in events for n in ns)/gems
        centers=[sum(n.lane for n in ns)/len(ns) for _,ns in events]
        movement=sum(abs(a-b) for a,b in zip(centers,centers[1:]))/max(1,count-1)
        rhythm=[str(Fraction(events[i][0]-events[i-1][0],song.resolution)) for i in range(1,count)]
        repeats=Counter(tuple(token['lanes']) for token in tokens)
        repeat_ratio=max(repeats.values())/count
        hopo=sum(len(events[i][1])==1 and centers[i]!=centers[i-1] and 0<events[i][0]-events[i-1][0]<=song.resolution/3 for i in range(1,count))/max(1,count-1)
        seconds=song.seconds(end)-song.seconds(start)
        rate=count/WINDOW_BEATS
        category=('Sustained passage' if sustain_ratio>=0.6 else
                  'Alternating chord pattern' if chord_ratio>=0.5 else
                  'Technical run' if movement>=1 and rate>=2 else
                  'Repeating riff' if repeat_ratio>=0.5 and count>=4 else
                  'Fast rhythm' if rate>=2 else 'Steady rhythm' if len(set(rhythm))<=1 else 'Mixed passage')
        features=dict(events=count,gems=gems,events_per_beat=rate,events_per_second=count/seconds,
                      chord_ratio=chord_ratio,sustain_ratio=sustain_ratio,movement=movement,
                      repetition=repeat_ratio,hopo_opportunities=hopo,window_seconds=seconds,
                      average_bpm=60*WINDOW_BEATS/seconds,category=category)
        motifs=Counter()
        for size in (2,3,4):
            for i in range(max(0,count-size+1)):
                key=json.dumps([[tokens[j]['lanes'],str(Fraction(events[j][0]-events[i][0],song.resolution))] for j in range(i,i+size)],separators=(',',':'))
                motifs[key]+=1
        payload=dict(tokens=tokens,rhythm=rhythm,features=features,start_tick=start,
                     repeated_motifs=[{'sequence':json.loads(key),'count':n} for key,n in sorted(motifs.items()) if n>1],
                     tempo_changes=[(t,str(us)) for t,us in song.tempos if start<=t<end])
        output.append(payload)
    return output

class PatternStore:
    def __init__(self,path):
        self.path=Path(path)
    def connect(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        db=sqlite3.connect(self.path,timeout=20)
        db.row_factory=sqlite3.Row
        try:
            db.execute('PRAGMA foreign_keys=ON')
            version=db.execute('PRAGMA user_version').fetchone()[0]
            if version==SCHEMA_VERSION and db.execute('PRAGMA application_id').fetchone()[0]!=APPLICATION_ID:
                raise ChartError('Selected database is not a GH3 pattern database')
            if version not in (0,SCHEMA_VERSION): raise ChartError(f'Unsupported database schema {version}; do not downgrade it')
            tables={r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if version==0 and tables: raise ChartError('Selected database is not a GH3 pattern database')
            if version==0:
                db.executescript('''
                BEGIN;
                CREATE TABLE sources(id TEXT PRIMARY KEY, title TEXT NOT NULL, metadata TEXT NOT NULL);
                CREATE TABLE paths(path TEXT PRIMARY KEY, source_id TEXT REFERENCES sources(id), status TEXT NOT NULL, detail TEXT NOT NULL);
                CREATE TABLE patterns(id INTEGER PRIMARY KEY, source_id TEXT NOT NULL REFERENCES sources(id), difficulty TEXT NOT NULL,
                    start_tick INTEGER NOT NULL, category TEXT NOT NULL, rate REAL NOT NULL, payload TEXT NOT NULL,
                    UNIQUE(source_id,difficulty,start_tick));
                CREATE INDEX pattern_rate ON patterns(rate);
                CREATE INDEX pattern_category ON patterns(category);
                CREATE TABLE ratings(pattern_id INTEGER PRIMARY KEY REFERENCES patterns(id), score INTEGER NOT NULL CHECK(score BETWEEN 1 AND 5));
                CREATE TABLE runs(id INTEGER PRIMARY KEY, root TEXT NOT NULL, state TEXT NOT NULL, report TEXT NOT NULL);
                PRAGMA application_id=1195914051;
                PRAGMA user_version=1;
                COMMIT;
                ''')
            return db
        except Exception:
            db.close(); raise
    def summary(self):
        with closing(self.connect()) as db:
            return {'sources':db.execute('SELECT count(*) FROM sources').fetchone()[0],
                    'patterns':db.execute('SELECT count(*) FROM patterns').fetchone()[0],
                    'ratings':db.execute('SELECT count(*) FROM ratings').fetchone()[0]}
    def browse(self,category='',limit=200):
        with closing(self.connect()) as db:
            rows=db.execute('''SELECT p.*,s.title,coalesce(r.score,3) AS rating FROM patterns p
                JOIN sources s ON s.id=p.source_id LEFT JOIN ratings r ON r.pattern_id=p.id
                WHERE (?='' OR p.category=?) ORDER BY p.id LIMIT ?''',(category,category,limit)).fetchall()
            return [dict(r) for r in rows]
    def similar(self,features,category='',limit=8):
        with closing(self.connect()) as db:
            # Indexed range search bounds the candidate pool for large corpora.
            rate=features['events_per_beat']
            rows=db.execute('''SELECT p.*,coalesce(r.score,3) AS rating FROM patterns p
                LEFT JOIN ratings r ON r.pattern_id=p.id
                WHERE p.rate BETWEEN ? AND ? AND (?='' OR p.category=?)
                ORDER BY p.id LIMIT 512''',(max(0,rate-1),rate+1,category,category)).fetchall()
            if not rows:
                rows=db.execute('''SELECT p.*,coalesce(r.score,3) AS rating FROM patterns p
                    LEFT JOIN ratings r ON r.pattern_id=p.id WHERE (?='' OR p.category=?) ORDER BY p.id LIMIT 512''',(category,category)).fetchall()
            candidates=[]
            for row in rows:
                item=dict(row); payload=json.loads(item['payload']); f=payload['features']
                distance=(abs(f['events_per_beat']-rate)+2*abs(f['chord_ratio']-features['chord_ratio'])+
                          abs(f['movement']-features['movement'])/4+abs(f['sustain_ratio']-features['sustain_ratio']))
                item['distance']=distance-(item['rating']-3)*0.15
                item['data']=payload; candidates.append(item)
            return sorted(candidates,key=lambda p:(p['distance'],p['id']))[:limit]
    def rate(self,pattern_id,score):
        if not isinstance(score,int) or not 1<=score<=5: raise ChartError('Rating must be 1–5')
        with closing(self.connect()) as db,db:
            if not db.execute('SELECT 1 FROM patterns WHERE id=?',(pattern_id,)).fetchone(): raise ChartError('Pattern no longer exists')
            db.execute('INSERT INTO ratings VALUES(?,?) ON CONFLICT(pattern_id) DO UPDATE SET score=excluded.score',(pattern_id,score))
    def fingerprint(self,cancelled=lambda:False):
        with closing(self.connect()) as db:
            h=hashlib.sha256()
            for row in db.execute('SELECT id,source_id,difficulty,start_tick,payload FROM patterns ORDER BY id'):
                if cancelled(): raise ChartError('Cancelled')
                h.update(json.dumps(tuple(row)).encode())
            for row in db.execute('SELECT pattern_id,score FROM ratings ORDER BY pattern_id'): h.update(json.dumps(tuple(row)).encode())
            return h.hexdigest()

def scan_folder(root,store,phrase_mode='modern',cancelled=lambda:False,progress=lambda done,total,path:None):
    root=Path(root).resolve()
    if not root.is_dir(): raise ChartError('Select an existing chart folder')
    report={'root':str(root),'state':'running','found':0,'imported':0,'duplicates':0,'failed':0,'patterns_added':0,'files':[]}
    with closing(store.connect()) as db:
        with db:
            run=db.execute('INSERT INTO runs(root,state,report) VALUES(?,?,?)',(str(root),'running','{}')).lastrowid
        try:
            files=[]
            def walk_error(error):
                report['failed']+=1;report['files'].append({'path':str(error.filename),'status':'failed','detail':str(error)})
            for directory,dirs,names in os.walk(root,followlinks=False,onerror=walk_error):
                dirs[:]=sorted(d for d in dirs if not d.startswith('.') and not (Path(directory)/d).is_symlink())
                if cancelled(): break
                for name in sorted(names):
                    path=Path(directory)/name
                    if path.suffix.lower() in ('.chart','.mid','.midi') and not path.is_symlink(): files.append(path)
                progress(0,0,f'Discovering: {len(files)} charts')
            report['found']=len(files)
            for index,path in enumerate(files):
                if cancelled(): break
                progress(index,len(files),str(path))
                try:
                    if path.stat().st_size>32*1024*1024: raise ChartError('Input exceeds 32 MiB')
                    raw=path.read_bytes();ini=path.parent/'song.ini'
                    if ini.exists() and ini.stat().st_size>1024*1024: raise ChartError('song.ini exceeds 1 MiB')
                    identity=hashlib.sha256(raw+b'\0'+(ini.read_bytes() if ini.exists() else b'')+b'\0'+phrase_mode.encode()+path.suffix.lower().encode()).hexdigest()
                    with db:
                        known=db.execute('SELECT 1 FROM sources WHERE id=?',(identity,)).fetchone()
                        if known:
                            status='duplicate';detail='Content already indexed; source record reused';new_count=0
                        else:
                            song=load(path,phrase_mode);patterns=[];skipped=[]
                            for diff in ('Easy','Medium','Hard','Expert'):
                                if song.modifiers.get(diff): skipped.append(diff);continue
                                patterns.extend((diff,p) for p in extract(song,diff,cancelled))
                            if not patterns: raise ChartError('No supported playable guitar patterns')
                            db.execute('INSERT INTO sources VALUES(?,?,?)',(identity,song.metadata.get('Name',path.stem),json.dumps(song.metadata)))
                            for diff,p in patterns:
                                db.execute('INSERT INTO patterns(source_id,difficulty,start_tick,category,rate,payload) VALUES(?,?,?,?,?,?)',
                                    (identity,diff,p['start_tick'],p['features']['category'],p['features']['events_per_beat'],json.dumps(p,sort_keys=True)))
                            status='imported';new_count=len(patterns)
                            detail=f'{new_count} windows added'+(f'; unsupported modifiers: skipped {", ".join(skipped)}' if skipped else '')
                            if song.warnings: detail+='; '+'; '.join(song.warnings)
                        if cancelled(): raise ChartError('Cancelled')
                        db.execute('INSERT INTO paths VALUES(?,?,?,?) ON CONFLICT(path) DO UPDATE SET source_id=excluded.source_id,status=excluded.status,detail=excluded.detail',
                                   (str(path),identity,status,detail))
                    report['duplicates' if status=='duplicate' else 'imported']+=1
                    report['patterns_added']+=new_count
                except (OSError,ValueError,EOFError,KeyError) as exc:
                    if cancelled(): break
                    status='failed';detail=f'{type(exc).__name__}: {exc}';report['failed']+=1
                    with db:
                        db.execute('INSERT INTO paths VALUES(?,NULL,?,?) ON CONFLICT(path) DO UPDATE SET source_id=NULL,status=excluded.status,detail=excluded.detail',(str(path),status,detail))
                report['files'].append({'path':str(path),'status':status,'detail':detail})
                progress(index+1,len(files),str(path))
            report['state']='cancelled' if cancelled() else 'completed_with_errors' if report['failed'] else 'completed'
        except Exception:
            report['state']='failed';raise
        finally:
            with db: db.execute('UPDATE runs SET state=?,report=? WHERE id=?',(report['state'],json.dumps(report),run))
    report['summary']=store.summary()
    return report
