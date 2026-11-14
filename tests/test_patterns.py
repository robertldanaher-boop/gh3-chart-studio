import json
import shutil
import sqlite3
from pathlib import Path
from fractions import Fraction
import pytest
from gh3studio.model import Song,Note,ChartError
from gh3studio.patterns import PatternStore,scan_folder,extract
from gh3studio.variations import generate_variations,VARIANTS
from gh3studio.converter import Settings
from gh3studio.service import load,export_bundle

FIXTURE=Path(__file__).parents[1]/'examples'/'technical-study.chart'
@pytest.fixture
def corpus(tmp_path):
    root=tmp_path/'songs';root.mkdir();shutil.copyfile(FIXTURE,root/'study.chart')
    store=PatternStore(tmp_path/'patterns.sqlite3')
    report=scan_folder(root,store)
    assert report['state']=='completed'
    return root,store

def test_recursive_duplicate_failure_resume_and_originals(tmp_path):
    root=tmp_path/'songs';(root/'nested').mkdir(parents=True)
    for p in [root/'one.chart',root/'nested'/'copy.chart']:shutil.copyfile(FIXTURE,p)
    (root/'bad.chart').write_text('not a chart')
    store=PatternStore(tmp_path/'db.sqlite3');report=scan_folder(root,store)
    assert report['state']=='completed_with_errors'
    assert (report['imported'],report['duplicates'],report['failed'])==(1,1,1)
    count=store.summary()['patterns'];assert count>0
    second=scan_folder(root,store)
    assert second['duplicates']==2 and second['failed']==1 and second['patterns_added']==0
    assert store.summary()['patterns']==count
    assert (root/'one.chart').read_bytes()==FIXTURE.read_bytes()
    with sqlite3.connect(store.path) as db:
        assert db.execute('SELECT count(*) FROM runs').fetchone()[0]==2
        assert db.execute("SELECT status FROM paths WHERE path LIKE '%bad.chart'").fetchone()[0]=='failed'

def test_cancel_resume(tmp_path):
    root=tmp_path/'songs';root.mkdir()
    for i in range(4): (root/f'{i}.chart').write_text(FIXTURE.read_text().replace('Four-Fret Technical Study',str(i)))
    store=PatternStore(tmp_path/'db.sqlite3');state={'cancel':False}
    def progress(done,total,path):
        if done==1:state['cancel']=True
    report=scan_folder(root,store,cancelled=lambda:state['cancel'],progress=progress)
    assert report['state']=='cancelled' and report['imported']==1
    again=scan_folder(root,store)
    assert again['state']=='completed' and again['imported']==3 and again['duplicates']==1

def test_cancel_during_extraction_rolls_back(tmp_path,monkeypatch):
    from gh3studio import patterns
    root=tmp_path/'songs';root.mkdir();shutil.copyfile(FIXTURE,root/'s.chart')
    store=PatternStore(tmp_path/'db.sqlite3');flag={'value':False};original=patterns.extract
    def stop(*args):
        result=original(*args);flag['value']=True;return result
    monkeypatch.setattr(patterns,'extract',stop)
    report=scan_folder(root,store,cancelled=lambda:flag['value'])
    assert report['state']=='cancelled' and store.summary()['sources']==0

def test_tempo_aware_features_and_exact_fractions():
    song=Song(resolution=192,tempos=[(0,Fraction(500000)),(768,Fraction(1000000))],
              tracks={'Expert':[Note(0,0),Note(64,1),Note(128,2,192),Note(768,3,384)]})
    p=extract(song,'Expert')[0]
    assert p['tokens'][1]['beat']=='1/3'
    assert p['tokens'][2]['lengths']==['1']
    assert p['features']['window_seconds']==6
    assert p['features']['events_per_second']==pytest.approx(4/6)
    assert p['features']['events']==4 and p['features']['gems']==4

def test_rating_ranking_persistence(corpus):
    root,store=corpus;items=store.browse();query=json.loads(items[0]['payload'])['features']
    before={p['id']:p['distance'] for p in store.similar(query,limit=100)}
    identifier=items[0]['id'];fingerprint=store.fingerprint();store.rate(identifier,5)
    reopened=PatternStore(store.path)
    after={p['id']:p['distance'] for p in reopened.similar(query,limit=100)}
    assert after[identifier]==pytest.approx(before[identifier]-.3)
    assert reopened.fingerprint()!=fingerprint and reopened.summary()['ratings']==1
    with pytest.raises(ChartError):store.rate(identifier,6)
    with pytest.raises(ChartError):store.rate(100000,3)

def test_category_filter(corpus):
    _,store=corpus;category=store.browse()[0]['category']
    assert all(row['category']==category for row in store.browse(category))
    assert store.browse('nonexistent')==[]

def test_changed_content_is_versioned(corpus):
    root,store=corpus;path=root/'study.chart'
    path.write_text(path.read_text().replace('Four-Fret Technical Study','New title'))
    report=scan_folder(root,store)
    assert report['imported']==1 and store.summary()['sources']==2

def test_metadata_change_reindexes(corpus):
    root,store=corpus;(root/'song.ini').write_text('[song]\nname = New metadata\n')
    report=scan_folder(root,store)
    assert report['imported']==1 and any(row['title']=='New metadata' for row in store.browse())

def test_schema_rejects_future_version(tmp_path):
    path=tmp_path/'db.sqlite3'
    with sqlite3.connect(path) as db:db.execute('PRAGMA user_version=99')
    with pytest.raises(ChartError):PatternStore(path).connect()
    with sqlite3.connect(path) as db:assert db.execute('PRAGMA user_version').fetchone()[0]==99

def test_unrelated_database_untouched(tmp_path):
    path=tmp_path/'db.sqlite3'
    with sqlite3.connect(path) as db:db.execute('CREATE TABLE important(value TEXT)');db.execute("INSERT INTO important VALUES('keep')")
    with pytest.raises(ChartError):PatternStore(path).connect()
    with sqlite3.connect(path) as db:assert db.execute('SELECT value FROM important').fetchone()[0]=='keep'

def test_symlinks_not_followed(tmp_path):
    root=tmp_path/'songs';root.mkdir()
    try:(root/'linked.chart').symlink_to(FIXTURE)
    except OSError:pytest.skip('Symlink permission unavailable')
    report=scan_folder(root,PatternStore(tmp_path/'db.sqlite3'))
    assert report['found']==0

@pytest.mark.parametrize('seed',[0,42,2147483647])
def test_variants_reproducible_four_frets_and_export(corpus,tmp_path,seed):
    _,store=corpus;song=load(FIXTURE);settings=Settings(chords=6)
    variants=generate_variations(song,settings,store,seed)
    repeat=generate_variations(song,settings,store,seed)
    assert variants==repeat and tuple(variants)==VARIANTS
    source_ticks={n.tick for n in song.tracks['Expert']}
    source_durations={n.tick:n.length for n in song.tracks['Expert']}
    for name,(result,report) in variants.items():
        assert {n.tick for n in result.tracks['Medium']}==source_ticks
        assert all(0<=n.lane<=3 and n.length==source_durations[n.tick] for n in result.tracks['Medium'])
        assert result.tracks['Expert']==song.tracks['Expert'] and result.tempos==song.tempos
        assert report['pattern_matches'] and report['corpus_fingerprint']==store.fingerprint()
        export_bundle(result,report,tmp_path/name)
    melody=variants['Melodic Technical'][0].tracks['Medium']
    assert len(melody)==len({n.tick for n in melody})

def test_variant_cancellation(corpus):
    _,store=corpus
    with pytest.raises(ChartError,match='Cancelled'):generate_variations(load(FIXTURE),Settings(),store,cancelled=lambda:True)

def test_empty_corpus_cannot_claim_learning(tmp_path):
    with pytest.raises(ChartError,match='Scan'):generate_variations(load(FIXTURE),Settings(),PatternStore(tmp_path/'db.sqlite3'))

def test_corpus_influences_frets(tmp_path):
    from gh3studio.chartio import write_chart
    results=[]
    for lane in (0,4):
        root=tmp_path/str(lane);root.mkdir()
        donor=Song(tracks={'Expert':[Note(i*192,lane) for i in range(8)]})
        write_chart(donor,root/'notes.chart');store=PatternStore(tmp_path/f'{lane}.sqlite3');scan_folder(root,store)
        source=Song(tracks={'Expert':[Note(i*192,2) for i in range(8)]})
        results.append(generate_variations(source,Settings(),store,0)['Melodic Technical'][0].tracks['Medium'])
    assert {n.lane for n in results[0]}=={0}
    assert {n.lane for n in results[1]}=={3}

def test_repeated_ngram_extraction():
    s=Song(tracks={'Expert':[Note(i*96,lane) for i,lane in enumerate([0,1,2,0,1,2,0,1,2])]})
    p=extract(s,'Expert')[0]
    assert any(m['count']==3 and len(m['sequence'])==3 for m in p['repeated_motifs'])

def test_no_schema_collision_with_other_app(tmp_path):
    path=tmp_path/'other.sqlite3'
    with sqlite3.connect(path) as db:
        db.execute('PRAGMA user_version=1');db.execute('CREATE TABLE keep(x)')
    with pytest.raises(ChartError,match='not a GH3'):PatternStore(path).connect()

def test_modifier_track_skipped_not_marked_learned(tmp_path):
    root=tmp_path/'charts';root.mkdir()
    text=FIXTURE.read_text().replace('[ExpertSingle]\n{','[ExpertSingle]\n{\n  0 = N 7 0')
    (root/'modified.chart').write_text(text)
    store=PatternStore(tmp_path/'patterns.sqlite3');report=scan_folder(root,store)
    assert report['imported']==1
    assert {r['difficulty'] for r in store.browse()}=={'Hard'}
    assert 'skipped Expert' in report['files'][0]['detail']

@pytest.mark.parametrize('marker',['N 5','N 6','E solo','E soloend','E "solo"'])
def test_shape_markers_are_retained_without_discarding_difficulty(tmp_path,marker):
    from gh3studio.chartio import write_chart
    song=Song(tracks={'Expert':[Note(0,0),Note(192,1)]},modifiers={'Expert':[(0,marker)]})
    root=tmp_path/'charts';root.mkdir();path=root/'notes.chart';write_chart(song,path)
    if marker.startswith('N '):
        path.write_text(path.read_text().replace('= '+marker+'\n','= '+marker+' 0\n'))
    original=path.read_bytes();store=PatternStore(tmp_path/'db.sqlite3')
    report=scan_folder(root,store)
    assert report['imported']==1 and report['failed']==0
    payload=json.loads(store.browse()[0]['payload'])
    assert payload['source_markers']==[[0,marker]]
    assert 'shape-only' in report['files'][0]['detail']
    assert path.read_bytes()==original


def test_learning_accepts_overlap_but_load_and_export_stay_strict(tmp_path):
    from gh3studio.chartio import write_chart
    from gh3studio.validation import validate
    song=Song(tracks={'Expert':[Note(0,0,384),Note(192,0,96)],'Medium':[Note(0,1)]})
    root=tmp_path/'charts';root.mkdir();path=root/'notes.chart';write_chart(song,path)
    store=PatternStore(tmp_path/'db.sqlite3');report=scan_folder(root,store)
    assert report['imported']==1 and 'Same-lane sustain overlap' in report['files'][0]['detail']
    payload=next(json.loads(r['payload']) for r in store.browse() if r['difficulty']=='Expert')
    assert payload['tokens'][0]['lengths']==['2']
    with pytest.raises(ChartError,match='overlap'):load(path)
    with pytest.raises(ChartError,match='overlap'):export_bundle(song,{},tmp_path/'out')
    with pytest.raises(ValueError):validate(song,True,learning_only=True)


def test_learning_does_not_accept_invalid_notes(tmp_path):
    from gh3studio.chartio import write_chart
    root=tmp_path/'charts';root.mkdir()
    write_chart(Song(tracks={'Expert':[Note(0,0,-1)]}),root/'bad.chart')
    report=scan_folder(root,PatternStore(tmp_path/'db.sqlite3'))
    assert report['failed']==1 and report['patterns_added']==0


def test_variation_style_filter(corpus):
    _,store=corpus;category=store.browse()[0]['category']
    result=generate_variations(load(FIXTURE),Settings(),store,category=category)
    rows={row['id']:row for row in store.browse(limit=10000)}
    for song,report in result.values():
        assert report['pattern_style']==category
        assert all(rows[m['pattern_id']]['category']==category for m in report['pattern_matches'])
    with pytest.raises(ChartError,match='Unknown pattern style'):
        generate_variations(load(FIXTURE),Settings(),store,category='invented')
