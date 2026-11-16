"""Standard-library startup UI: available before PySide6 is installed."""
import hashlib
import json
import math
import os
from pathlib import Path
import queue
import random
import re
import subprocess
import sys
import threading
import time
import traceback
import uuid

MESSAGES=("Tuning the strings and warming up the stage…", "Giving the Orange notes a night off…", "Checking the setlist. Your encore is coming!", "Warming up the amps—no sound check required yet.", "A few backstage checks before the music starts…")
STEPS=('1 / 3 — Set up and verify dependencies','2 / 3 — Run automated tests','3 / 3 — Open GH3 Chart Studio')
DEFAULT_SECONDS=(90.,30.,10.)


def duration(value):
    value=max(0,int(value));return f'{value//60:02d}:{value%60:02d}'


def progress(step,elapsed,estimates,test_percent=None):
    # Time-based estimates never complete a step. Only real completion advances it.
    fraction=min(.95,elapsed/max(1,estimates[step]))
    if step==1 and test_percent is not None:fraction=min(.99,test_percent/100)
    percent=min(99,int(100*(step+fraction)/3))
    remaining=max(0,estimates[step]-elapsed)+sum(estimates[step+1:])
    return percent,remaining


def load_history(path):
    try:
        values=json.loads(path.read_text())['seconds']
        if len(values)==3 and all(isinstance(v,(int,float)) and 0<v<86400 for v in values):return values,True
    except (OSError,ValueError,KeyError,TypeError):pass
    return list(DEFAULT_SECONDS),False


def cache_key(root,python):
    return hashlib.sha256((root/'requirements-windows.lock').read_bytes()+str(python).encode()).hexdigest()


class Startup:
    def __init__(self,root):
        import tkinter as tk
        from tkinter import ttk
        self.root=root;self.events=queue.Queue();self.cancelled=threading.Event();self.process=None
        self.started=self.step_started=time.monotonic();self.step=0;self.test_percent=None;self.last_output=self.started
        self.estimates,self.historical=load_history(root/'startup_timings.json');self.durations=[];self.done=False;self.last_percent=0
        self.ui=tk.Tk();self.ui.title('GH3 Chart Studio — getting ready');self.ui.geometry('860x700');self.ui.minsize(690,560);self.ui.configure(bg='#101722')
        style=ttk.Style(self.ui);style.theme_use('clam')
        style.configure('.',background='#101722',foreground='#e5edf7',font=('Segoe UI',10))
        style.configure('TButton',background='#263b51',foreground='#e5edf7',padding=(12,7),borderwidth=0)
        style.map('TButton',background=[('active','#385976'),('disabled','#172535')])
        style.configure('Horizontal.TProgressbar',background='#65dfb5',troughcolor='#203247',borderwidth=0,lightcolor='#65dfb5',darkcolor='#65dfb5')
        frame=ttk.Frame(self.ui,padding=18);frame.pack(fill='both',expand=True)
        ttk.Label(frame,text='GH3  /  CHART STUDIO',font=('Segoe UI',21,'bold')).pack(anchor='w')
        ttk.Label(frame,text='SETTING THE STAGE',foreground='#72dfbf',font=('Segoe UI',9,'bold')).pack(anchor='w',pady=(4,0))
        self.motion=True;self.animation_started=time.monotonic()
        self.visual=tk.Canvas(frame,height=78,bg='#101722',highlightthickness=0);self.visual.pack(fill='x',pady=(4,0))
        ttk.Label(frame,text=random.choice(MESSAGES),wraplength=730).pack(anchor='w',pady=(6,16))
        self.stage=ttk.Label(frame,text=STEPS[0],font=('Segoe UI',12,'bold'));self.stage.pack(anchor='w')
        self.detail=ttk.Label(frame,text='Checking Python 3.11 x64…',wraplength=730);self.detail.pack(anchor='w',pady=7)
        self.bar=ttk.Progressbar(frame,maximum=100);self.bar.pack(fill='x')
        self.clock=ttk.Label(frame);self.clock.pack(anchor='w',pady=8)
        self.activity=ttk.Label(frame,wraplength=730);self.activity.pack(anchor='w')
        ttk.Label(frame,text='BACKSTAGE / LIVE DIAGNOSTICS',foreground='#a4b9d0',font=('Segoe UI',9,'bold')).pack(anchor='w',pady=(10,0))
        log_frame=ttk.Frame(frame);log_frame.pack(fill='both',expand=True,pady=8)
        self.text=tk.Text(log_frame,height=13,wrap='word',state='disabled',bg='#0b121c',fg='#c4d6e9',insertbackground='#e5edf7',relief='flat',font=('Consolas',9),padx=10,pady=8)
        scrollbar=ttk.Scrollbar(log_frame,command=self.text.yview);scrollbar.pack(side='right',fill='y');self.text.configure(yscrollcommand=scrollbar.set);self.text.pack(fill='both',expand=True)
        ttk.Label(frame,text='With thanks to open-source contributors • Nanook & TeamGHOST: compatibility references',foreground='#9fb1c6',wraplength=790,font=('Segoe UI',9)).pack(anchor='w',pady=(0,8))
        row=ttk.Frame(frame);row.pack(fill='x')
        ttk.Button(row,text='Open troubleshooting log',command=self.open_log).pack(side='left')
        self.motion_button=ttk.Button(row,text='Pause animation',command=self.toggle_animation);self.motion_button.pack(side='left',padx=8)
        ttk.Button(row,text='Credits',command=self.show_credits).pack(side='left')
        self.close_button=ttk.Button(row,text='Cancel startup',command=self.close);self.close_button.pack(side='right')
        self.ui.protocol('WM_DELETE_WINDOW',self.close)
        self.log_path=root/'start_windows.log'
        if self.log_path.exists():self.log_path.replace(root/'start_windows.previous.log')
        self.log_path.write_text('',encoding='utf-8')
        self.log=self.log_path.open('a',encoding='utf-8',buffering=1)
        self.write(f'Startup {time.strftime("%Y-%m-%d %H:%M:%S")} | Python {sys.version} | folder {root}')
        threading.Thread(target=self.work,daemon=True).start();self.ui.after(100,self.poll);self.ui.after(80,self.animate)
    def toggle_animation(self):
        self.motion=not self.motion;self.motion_button.configure(text='Pause animation' if self.motion else 'Resume animation')
    def animate(self):
        if self.motion:
            self.visual.delete('all');width=max(100,self.visual.winfo_width());phase=time.monotonic()-self.animation_started
            colors=('#69e2ac','#ff7b88','#f0d779','#75b9ff')
            for i in range(40):
                height=9+42*(.5+.5*math.sin(phase*3+i*.57))*(.65+.35*math.sin(phase+i*.24)**2)
                x=8+i*(width-16)/40
                self.visual.create_rectangle(x,65-height,x+max(3,(width-16)/40-5),65,fill=colors[(i//10)%4],outline='')
            self.visual.create_line(8,70,width-8,70,fill='#31465b')
        if not self.done:self.ui.after(80,self.animate)
    def show_credits(self):
        from tkinter import messagebox
        messagebox.showinfo('Open-source credits',
            'With thanks to Nanook and TeamGHOST (TheGHOST), and TheNathannator and contributors (GuitarGame_ChartFormats). Their work informs our compatibility profile; their implementations are not bundled.\n\nBuilt using Python/Tkinter, PySide6/Qt, Mido, NumPy, SciPy, SoundFile/libsndfile and supporting libraries. Tests/builds use pytest and PyInstaller.\n\nFull credits, project links and license information are available under About & credits in the studio and the included licenses folder.',parent=self.ui)
    def write(self,line):
        self.log.write(f'[{duration(time.monotonic()-self.started)}] {line}\n');self.log.flush();self.events.put(('log',line))
    def command(self,args,env=None):
        if self.cancelled.is_set():raise RuntimeError('Startup cancelled')
        self.write('Running: '+subprocess.list2cmdline([str(a) for a in args]))
        self.process=subprocess.Popen(args,cwd=self.root,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace',env=env,bufsize=1,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        for line in self.process.stdout:
            self.write(line.rstrip())
        code=self.process.wait();self.process=None
        if code:raise RuntimeError(f'Command failed (exit {code}); see the log above')
        if self.cancelled.is_set():raise RuntimeError('Startup cancelled')
    def stage_change(self,step,detail):self.events.put(('stage',(step,detail)))
    def work(self):
        ready=self.root/('.startup-ready-'+uuid.uuid4().hex)
        try:
            if sys.version_info[:2]!=(3,11) or sys.maxsize<=2**32:raise RuntimeError('Python 3.11 x64 is required; run py -0p to inspect installed versions')
            python=self.root/'.venv'/'Scripts'/'python.exe';start=time.monotonic()
            if not python.exists():self.command([sys.executable,'-u','-m','venv',str(self.root/'.venv')])
            self.command([str(python),'-c',"import sys,struct; assert sys.version_info[:2]==(3,11) and struct.calcsize('P')==8, 'Existing environment must use Python 3.11 x64'"])
            # A copied or partly installed environment may have lost pip.
            pip_check=subprocess.run([str(python),'-m','pip','--version'],cwd=self.root,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            if pip_check.returncode:self.command([str(python),'-m','ensurepip','--upgrade'])
            # Exact installed-version probe avoids pip/network work on unchanged installations.
            probe="import importlib.metadata as m,json; print(json.dumps(sorted((d.metadata['Name'].lower().replace('_','-'),d.version) for d in m.distributions())))"
            snapshot=subprocess.check_output([str(python),'-c',probe],cwd=self.root,text=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0)).strip()
            stamp=self.root/'.venv'/'startup_dependencies.json';key=cache_key(self.root,python)
            try:cached=json.loads(stamp.read_text())
            except (OSError,ValueError):cached={}
            if cached!={'key':key,'packages':snapshot}:
                self.command([str(python),'-u','-m','pip','install','--disable-pip-version-check','--require-hashes','--only-binary=:all:','-r','requirements-windows.lock'])
                snapshot=subprocess.check_output([str(python),'-c',probe],cwd=self.root,text=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0)).strip()
                self.command([str(python),'-m','pip','check'])
                stamp.write_text(json.dumps({'key':key,'packages':snapshot}))
            else:self.write('Dependency lock and installed versions unchanged: reusing verified setup (no package download).')
            self.durations.append(time.monotonic()-start);start=time.monotonic()
            self.stage_change(1,'Each completed test appears below. The full test suite still runs every startup.')
            env=dict(os.environ,QT_QPA_PLATFORM='offscreen',PYTHONUNBUFFERED='1')
            self.command([str(python),'-u','-m','pytest','-v','--tb=short','-o','faulthandler_timeout=60'],env)
            self.durations.append(time.monotonic()-start);start=time.monotonic()
            self.stage_change(2,'Tests passed. Waiting for the application window to report ready…')
            env=dict(os.environ,GH3_STARTUP_READY=str(ready),PYTHONUNBUFFERED='1');env.pop('QT_QPA_PLATFORM',None)
            self.log.flush()
            with self.log_path.open('a',encoding='utf-8') as output:
                self.process=subprocess.Popen([str(python),'-u','run_app.py'],cwd=self.root,stdout=output,stderr=subprocess.STDOUT,env=env,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            while not ready.exists():
                if self.cancelled.is_set():raise RuntimeError('Startup cancelled')
                if self.process.poll() is not None:raise RuntimeError(f'Application exited before reporting ready (exit {self.process.returncode})')
                if time.monotonic()-start>120:raise RuntimeError('Application did not report ready within 120 seconds; inspect start_windows.log')
                self.cancelled.wait(.1)
            self.durations.append(time.monotonic()-start)
            (self.root/'startup_timings.json').write_text(json.dumps({'seconds':self.durations}))
            self.write('Application window ready. Step durations: '+', '.join(f'{v:.1f}s' for v in self.durations))
            self.events.put(('ready',None))
        except Exception:
            if self.process and self.process.poll() is None:
                subprocess.run(['taskkill','/PID',str(self.process.pid),'/T','/F'],capture_output=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            self.write(traceback.format_exc());self.events.put(('failed',None))
        finally:ready.unlink(missing_ok=True)
    def poll(self):
        while True:
            try:kind,value=self.events.get_nowait()
            except queue.Empty:break
            if kind=='log':
                self.last_output=time.monotonic();self.text.configure(state='normal');self.text.insert('end',value+'\n');self.text.see('end');self.text.configure(state='disabled')
                match=re.search(r'\[\s*(\d+)%\]',value)
                if match and self.step==1:self.test_percent=int(match[1])
            elif kind=='stage':
                self.step,detail=value;self.step_started=time.monotonic();self.test_percent=None;self.stage.configure(text=STEPS[self.step]);self.detail.configure(text=detail)
            elif kind=='failed':
                self.done=True;self.stage.configure(text='Startup stopped — please review the log');self.close_button.configure(text='Close');self.detail.configure(text='The application was not confirmed ready. Save start_windows.log for troubleshooting.')
            elif kind=='ready':
                self.done=True;self.bar['value']=100;self.stage.configure(text='3 / 3 — Ready!');self.clock.configure(text=f'100% • Total startup time {duration(time.monotonic()-self.started)}');self.ui.after(1200,self.ui.destroy)
        if not self.done:
            now=time.monotonic();elapsed=now-self.step_started;percent,eta=progress(self.step,elapsed,self.estimates,self.test_percent)
            percent=max(self.last_percent,percent);self.last_percent=percent
            self.bar['value']=percent
            estimate='calculating — step taking longer than estimate' if elapsed>self.estimates[self.step] else '~'+duration(eta)
            self.clock.configure(text=f'{percent}% estimated • Elapsed {duration(now-self.started)} • ETA {estimate}')
            quiet=int(now-self.last_output)
            self.activity.configure(text=f'Last log activity {quiet}s ago. '+('Still waiting; the timer is live. Tests print thread traces after 60s of a slow test.' if quiet>=20 else ('ETA based on your last successful startup.' if self.historical else 'First-run ETA is approximate; future starts use measured durations.')))
        self.ui.after(150,self.poll)
    def open_log(self):
        self.log.flush();os.startfile(str(self.log_path))
    def close(self):
        from tkinter import messagebox
        if self.done:self.ui.destroy();return
        if not messagebox.askyesno('Cancel startup?','Stop setup/tests and leave the application closed?'):return
        self.cancelled.set()
        if self.process and self.process.poll() is None:
            subprocess.run(['taskkill','/PID',str(self.process.pid),'/T','/F'],capture_output=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        self.write('Cancellation requested by user.');self.close_button.configure(state='disabled')


def main():
    startup=Startup(Path(__file__).resolve().parent.parent);startup.ui.mainloop()

if __name__=='__main__':main()
