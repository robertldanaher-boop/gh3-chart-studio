import json
from types import SimpleNamespace
import queue
import threading
import time
from pathlib import Path
from unittest.mock import patch
import pytest
from tools.startup_windows import Startup,progress,load_history,duration,cache_key


def test_progress_never_claims_completion_from_time():
    assert progress(0,999,[1,1,1])[0]<34
    assert progress(2,999,[1,1,1])[0]<100
    assert progress(1,0,[90,30,10],50)[0]==50
    assert duration(125)=='02:05'


def test_history_valid_and_corrupt(tmp_path):
    path=tmp_path/'timings.json'
    assert load_history(path)[1] is False
    path.write_text(json.dumps({'seconds':[2,25,1]}));assert load_history(path)==([2,25,1],True)
    path.write_text('{invalid');assert load_history(path)[1] is False
    path.write_text(json.dumps({'seconds':[0,-1,1]}));assert load_history(path)[1] is False


def test_lock_change_invalidates_cache(tmp_path):
    lock=tmp_path/'requirements-windows.lock';lock.write_text('first')
    before=cache_key(tmp_path,'python');lock.write_text('second')
    assert cache_key(tmp_path,'python')!=before


def worker(tmp_path):
    root=tmp_path;(root/'.venv'/'Scripts').mkdir(parents=True)
    (root/'.venv'/'Scripts'/'python.exe').touch();(root/'requirements-windows.lock').write_text('test')
    obj=Startup.__new__(Startup);obj.root=root;obj.cancelled=threading.Event();obj.process=None
    obj.events=queue.Queue();obj.durations=[];obj.log_path=root/'start_windows.log';obj.log=obj.log_path.open('w');obj.started=time.monotonic()
    obj.lines=[];obj.write=obj.lines.append;obj.commands=[]
    obj.command=lambda args,env=None:obj.commands.append((args,env))
    return obj


@pytest.mark.parametrize('cached',[False,True])
@pytest.mark.parametrize('pip_present',[False,True])
def test_worker_setup_tests_and_ready_handshake(tmp_path,cached,pip_present):
    obj=worker(tmp_path);python=tmp_path/'.venv'/'Scripts'/'python.exe'
    if cached:(python.parent.parent/'startup_dependencies.json').write_text(json.dumps({'key':cache_key(tmp_path,python),'packages':'packages'}))
    class Process:
        def __init__(self,args,**kw):
            assert 'QT_QPA_PLATFORM' not in kw['env']
            Path(kw['env']['GH3_STARTUP_READY']).write_text('ready')
        def poll(self):return None
    with patch('tools.startup_windows.subprocess.run',return_value=SimpleNamespace(returncode=0 if pip_present else 1)),patch('tools.startup_windows.subprocess.check_output',return_value='packages'),patch('tools.startup_windows.subprocess.Popen',Process):obj.work()
    commands=[args for args,_ in obj.commands]
    assert any('ensurepip' in args for args in commands)==(not pip_present)
    assert any('pytest' in args for args in commands)
    assert any('install' in args for args in commands)==(not cached)
    test_env=next(env for args,env in obj.commands if 'pytest' in args)
    assert test_env['QT_QPA_PLATFORM']=='offscreen'
    assert (tmp_path/'startup_timings.json').exists()
    assert ('ready',None) in list(obj.events.queue)
    assert not list(tmp_path.glob('.startup-ready-*'))
    obj.log.close()


def test_failed_tests_never_launch(tmp_path):
    obj=worker(tmp_path)
    def command(args,env=None):
        if 'pytest' in args:raise RuntimeError('test failed')
    obj.command=command
    with patch('tools.startup_windows.subprocess.run',return_value=SimpleNamespace(returncode=0)),patch('tools.startup_windows.subprocess.check_output',return_value='packages'),patch('tools.startup_windows.subprocess.Popen') as popen:obj.work()
    popen.assert_not_called()
    assert ('failed',None) in list(obj.events.queue)
    assert not (tmp_path/'startup_timings.json').exists()
    obj.log.close()


def test_real_app_reports_ready_after_event_loop_starts(tmp_path):
    import os
    import subprocess
    import sys
    ready=tmp_path/'ready';env=dict(os.environ,QT_QPA_PLATFORM='offscreen',GH3_STARTUP_READY=str(ready))
    with (tmp_path/'app.log').open('w') as output:
        process=subprocess.Popen([sys.executable,'run_app.py'],env=env,stdout=output,stderr=subprocess.STDOUT)
        try:
            deadline=time.monotonic()+15
            while not ready.exists() and time.monotonic()<deadline and process.poll() is None:time.sleep(.05)
            assert ready.exists(),(tmp_path/'app.log').read_text()
            assert ready.read_text()=='ready' and process.poll() is None
        finally:
            process.terminate();process.wait(timeout=10)
