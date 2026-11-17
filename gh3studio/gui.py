"""One-window desktop converter. File parsing/conversion/export run off the UI thread."""
import json
import sys
from datetime import datetime
from pathlib import Path
from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtGui import QColor, QPen, QBrush
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QSpinBox, QSlider, QTextEdit, QFileDialog,
    QGraphicsView, QGraphicsScene, QSplitter, QGroupBox, QFormLayout, QProgressBar, QTabWidget, QScrollArea)
from .converter import Settings, convert
from .service import load, export_bundle
from .library_gui import LibraryPanel
from .audio_gui import AudioPanel
from .playback import PlaybackPanel
from .cleanup_gui import CleanupDialog
from .variations import generate_variations, VARIANTS
from .patterns import CATEGORIES
from . import __version__
from .appearance import apply_style,primary
from .welcome import WelcomePanel,show_credits

class Worker(QThread):
    succeeded=Signal(object)
    failed=Signal(str)
    progress=Signal(int,int,str)
    def __init__(self, operation, parent=None):
        super().__init__(parent); self.operation=operation
    def run(self):
        try: self.succeeded.emit(self.operation(self.isInterruptionRequested))
        except Exception as exc: self.failed.emit(f'{type(exc).__name__}: {exc}')

class Preview(QGraphicsView):
    def __init__(self):
        super().__init__(); self.setScene(QGraphicsScene(self)); self.setMinimumHeight(220)
        self.setBackgroundBrush(QColor('#101722'))
    def show_notes(self,song,difficulty):
        scene=self.scene(); scene.clear()
        notes=song.tracks.get(difficulty,[])[:2000]
        scale=80/song.resolution
        width=max(800,max((n.tick+n.length for n in notes),default=0)*scale+120)
        colors=['#55d179','#ff6978','#f3d25b','#61a6ff','#f9a35b']
        for lane,color in enumerate(colors[:4] if difficulty=='Medium' else colors):
            y=30+lane*28
            scene.addLine(0,y,width,y,QPen(QColor('#344356')))
            label=scene.addText('GRYBO'[lane]); label.setDefaultTextColor(QColor(color)); label.setPos(0,y-15)
        for beat in range(min(20000,int(width/80)+1)):
            scene.addLine(50+beat*80,10,50+beat*80,155,QPen(QColor('#263346')))
        for n in notes:
            x=50+n.tick*scale; y=30+n.lane*28; color=QColor(colors[n.lane])
            if n.length: scene.addLine(x,y,x+n.length*scale,y,QPen(color,4))
            scene.addEllipse(x-5,y-5,10,10,QPen(color),QBrush(color))
        scene.setSceneRect(0,0,width+60,180)

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose,True)
        self.song=None; self.converted=None; self.report=None; self.path=None; self.worker=None
        self.variants={};self.goal=None;self.last_export_path=None
        apply_style(self)
        self.setWindowTitle(f'GH3 Chart Studio {__version__} — Expert Medium')
        self.resize(1180,840); self.setAcceptDrops(True)
        shell=QWidget();shell_layout=QVBoxLayout(shell);shell_layout.setContentsMargins(14,10,14,12);self.setCentralWidget(shell)
        header=QHBoxLayout();shell_layout.addLayout(header)
        brand=QLabel('GH3  /  CHART STUDIO');brand.setObjectName('brand');brand.setWordWrap(True);header.addWidget(brand)
        badge=QLabel('Chart studio  •  '+__version__);badge.setObjectName('versionBadge');badge.setWordWrap(True);header.addWidget(badge);header.addStretch()
        header=QHBoxLayout();shell_layout.addLayout(header);header.addStretch()
        self.home_button=QPushButton('Start / choose a goal');self.home_button.setObjectName('quietAction');self.home_button.clicked.connect(lambda:self.tabs.setCurrentWidget(self.welcome));header.addWidget(self.home_button)
        credits=QPushButton('About / credits');credits.setObjectName('quietAction');credits.clicked.connect(lambda:show_credits(self));header.addWidget(credits)
        self.tabs=QTabWidget();self.tabs.setUsesScrollButtons(True);shell_layout.addWidget(self.tabs)
        root=QWidget();self.converter=root; self.tabs.addTab(root,'Chart Converter');outer=QVBoxLayout(root)
        scroll=QScrollArea();scroll.setWidgetResizable(True);outer.addWidget(scroll);body=QWidget();scroll.setWidget(body);layout=QVBoxLayout(body)
        title=QLabel('GH3 Chart Studio  |  Four-fret technical Medium')
        title.setStyleSheet('font-size:22px;font-weight:600;padding:8px;'); layout.addWidget(title)
        layout.addWidget(QLabel('Drop a chart, audio file or chart folder here. Originals are never overwritten.'))
        row=QHBoxLayout(); layout.addLayout(row)
        self.open_button=QPushButton('Open chart…'); self.open_button.clicked.connect(self.browse); row.addWidget(self.open_button)
        self.audio_start=QPushButton('Start audio workflow…'); self.audio_start.clicked.connect(self.start_from_audio); row.addWidget(self.audio_start)
        self.cleanup_button=QPushButton('Review GH3 cleanup…'); self.cleanup_button.clicked.connect(self.review_cleanup); row.addWidget(self.cleanup_button)
        self.restore_button=QPushButton('Restore original chart'); self.restore_button.clicked.connect(self.restore_original); row.addWidget(self.restore_button)
        self.cleanup_report=None; self.original_song=None
        self.phrase_mode=QComboBox(); self.phrase_mode.addItems(['Modern MIDI (116 Star Power)','Legacy MIDI / TheGHOST'])
        row=QHBoxLayout();layout.addLayout(row);row.addWidget(self.phrase_mode)
        self.file_label=QLabel('No chart loaded');self.file_label.setWordWrap(True); row.addWidget(self.file_label,1)
        self.info=QLabel('Open a chart, or choose Start from audio to create a draft without a chart.'); self.info.setWordWrap(True); layout.addWidget(self.info)
        box=QGroupBox('Conversion settings'); form=QHBoxLayout(box); layout.addWidget(box)
        self.source=QComboBox(); self.source.addItems(['Expert','Hard'])
        source_form=QFormLayout(); source_form.addRow('Source',self.source); form.addLayout(source_form)
        self.sliders={}
        for key,value in [('Density',6),('Chords',4),('Movement',5)]:
            col=QVBoxLayout(); label=QLabel(f'{key}: {value}/6'); slider=QSlider(Qt.Horizontal)
            slider.setRange(1,6); slider.setValue(value)
            slider.valueChanged.connect(lambda v,l=label,k=key:l.setText(f'{k}: {v}/6'))
            slider.valueChanged.connect(self.invalidate)
            col.addWidget(label); col.addWidget(slider); form.addLayout(col); self.sliders[key]=slider
        self.max_chord=QSpinBox(); self.max_chord.setRange(1,3); self.max_chord.setValue(3)
        col=QFormLayout(); col.addRow('Max chord gems',self.max_chord); form.addLayout(col)
        self.source.currentTextChanged.connect(self.invalidate); self.max_chord.valueChanged.connect(self.invalidate)
        layout.addWidget(QLabel('Density 6 keeps every onset • Chords 1–2: singles, 3–4: pairs, 5–6: up to 3 • Movement 1 favors short travel'))
        row=QHBoxLayout(); layout.addLayout(row)
        self.convert_button=QPushButton('Convert and validate'); self.convert_button.clicked.connect(self.start_convert); row.addWidget(self.convert_button)
        self.export_button=QPushButton('Export song folder…'); self.export_button.clicked.connect(self.start_export); row.addWidget(self.export_button)
        self.save_settings=QPushButton('Save settings…'); self.save_settings.clicked.connect(self.save_config); row.addWidget(self.save_settings)
        self.load_settings=QPushButton('Load settings…'); self.load_settings.clicked.connect(self.load_config); row.addWidget(self.load_settings)
        self.listen_button=QPushButton('Listen / timing…');self.listen_button.clicked.connect(lambda:self.audio.show_listen());row.addWidget(self.listen_button)
        self.cancel_button=QPushButton('Cancel'); self.cancel_button.clicked.connect(self.cancel); row.addWidget(self.cancel_button)
        row=QHBoxLayout(); layout.addLayout(row)
        self.generate_button=QPushButton('Generate 3 learned variations'); self.generate_button.clicked.connect(self.start_variations); row.addWidget(self.generate_button)
        row.addWidget(QLabel('Seed:')); self.seed=QSpinBox(); self.seed.setRange(0,2147483647); self.seed.valueChanged.connect(self.invalidate); row.addWidget(self.seed)
        self.pattern_style=QComboBox();self.pattern_style.addItems(['All styles',*CATEGORIES]);self.pattern_style.currentIndexChanged.connect(self.invalidate);row.addWidget(self.pattern_style)
        self.variant_choice=QComboBox(); self.variant_choice.addItems(['Choose generated variation',*VARIANTS]); self.variant_choice.currentIndexChanged.connect(self.select_variant); row.addWidget(self.variant_choice,1)
        self.progress=QProgressBar(); self.progress.setRange(0,1); self.progress.setValue(0); layout.addWidget(self.progress)
        row=QHBoxLayout(); row.addWidget(QLabel('Note preview (first 2,000 gems; scroll horizontally):'))
        self.view_choice=QComboBox(); self.view_choice.addItems(['Converted Medium','Source']); self.view_choice.currentIndexChanged.connect(self.refresh_preview)
        row.addWidget(self.view_choice); layout.addLayout(row)
        split=QSplitter(Qt.Vertical); self.preview=Preview(); split.addWidget(self.preview)
        self.log=QTextEdit(); self.log.setReadOnly(True); split.addWidget(self.log); layout.addWidget(split,1)
        save_log=QPushButton('Save diagnostic log…'); save_log.clicked.connect(self.save_diagnostics); layout.addWidget(save_log)
        self.log_line('Ready. Structural checks do not certify TheGHOST or in-game compatibility.')
        self.library=LibraryPanel(self); self.tabs.addTab(self.library,'Pattern Library')
        self.playback=PlaybackPanel(self)
        self.audio=AudioPanel(self); self.tabs.addTab(self.audio,'Audio Studio')
        from .cleaner_gui import CleanerPanel
        self.cleaner=CleanerPanel(self);self.tabs.addTab(self.cleaner,'Clean charts')
        self.welcome=WelcomePanel(self);self.tabs.insertTab(0,self.welcome,'Start');self.tabs.setCurrentWidget(self.welcome)
        for button in (self.convert_button,self.export_button,self.audio.draft_button,self.audio.export_button,self.playback.orange_button):primary(button)
        self.update_buttons()
    def start_guided(self,goal,path=None):
        if self.busy():return False
        if goal=='clean':
            if path is None:path=QFileDialog.getExistingDirectory(self,'Choose song folder or parent directory')
            if not path:return False
            self.goal='clean';self.tabs.setCurrentWidget(self.cleaner);self.cleaner.scan(path);return True
        if goal not in ('orange','audio','refine'):raise ValueError('Unknown workflow')
        if path is None:
            title='Choose a recording to chart' if goal=='audio' else 'Choose the chart to work on'
            filters='Audio (*.wav *.flac *.ogg *.mp3)' if goal=='audio' else 'Charts (*.chart *.mid *.midi)'
            path,_=QFileDialog.getOpenFileName(self,title,'',filters)
        if not path:return False
        self.goal=goal;self.audio.set_mode(goal)
        if goal=='audio':
            self.song=None;self.original_song=None;self.path=None;self.cleanup_report=None
            self.converted=None;self.report=None;self.variants={};self.playback.set_chart(None,'Medium')
            self.file_label.setText('Audio-only workflow — no chart template loaded')
            self.tabs.setCurrentWidget(self.audio);self.audio.template.setChecked(False);self.audio.open_path(path)
        else:
            self.tabs.setCurrentWidget(self.audio if goal=='orange' else self.converter)
            if goal=='orange':self.audio.show_listen()
            self.open_path(path)
        return True
    def resume_workflow(self):
        if self.goal=='clean':self.tabs.setCurrentWidget(self.cleaner)
        elif self.goal=='refine':self.tabs.setCurrentWidget(self.converter)
        elif self.converted is not None or (self.song is not None and self.goal!='audio'):self.audio.show_listen()
        else:self.tabs.setCurrentWidget(self.audio)
    def log_line(self,text):
        self.log.append(datetime.now().strftime('%H:%M:%S')+'  '+str(text).replace('&','&amp;').replace('<','&lt;').replace('\n','<br>'))
    def busy(self): return self.worker is not None
    def update_buttons(self):
        busy=self.busy()
        if hasattr(self,'cleaner'):self.cleaner.update_busy(busy,getattr(self,'cancellable',False))
        self.progress.setVisible(busy)
        if hasattr(self,'audio'):self.audio.progress.setVisible(busy)
        if self.converted is None:self.last_export_path=None
        for widget in (self.open_button,self.source,self.max_chord,self.phrase_mode,self.seed,self.pattern_style,self.variant_choice,self.save_settings,self.load_settings,*self.sliders.values()): widget.setEnabled(not busy)
        self.audio_start.setEnabled(not busy)
        self.listen_button.setEnabled(not busy and self.song is not None)
        self.cleanup_button.setEnabled(not busy and self.song is not None)
        self.restore_button.setEnabled(not busy and self.original_song is not None and self.song is not self.original_song)
        self.convert_button.setEnabled(not busy and self.song is not None)
        self.export_button.setEnabled(not busy and self.converted is not None)
        self.generate_button.setEnabled(not busy and self.song is not None)
        if hasattr(self,'library'): self.library.update_busy(busy,getattr(self,'cancellable',False))
        if hasattr(self,'audio'): self.audio.update_busy(busy,getattr(self,'cancellable',False))
        if hasattr(self,'playback'): self.playback.update_busy(busy,False)
        self.cancel_button.setEnabled(busy and getattr(self,'cancellable',False))
        if hasattr(self,'welcome'):self.welcome.update_state()
    def invalidate(self,*args):
        self.converted=None; self.report=None; self.variants={}
        self.variant_choice.blockSignals(True); self.variant_choice.setCurrentIndex(0); self.variant_choice.blockSignals(False)
        self.update_buttons(); self.refresh_preview()
    def settings(self):
        return Settings(self.source.currentText(),self.sliders['Density'].value(),self.sliders['Chords'].value(),self.sliders['Movement'].value(),self.max_chord.value())
    def run_job(self,label,fn,on_success,cancellable=False):
        self.cancellable=cancellable; self.log_line(label); self.progress.setRange(0,0)
        self.worker=Worker(fn,self)
        self.success_callback=on_success
        self.worker.succeeded.connect(self.job_succeeded, Qt.QueuedConnection)
        self.worker.failed.connect(self.job_failed, Qt.QueuedConnection)
        self.worker.finished.connect(self.job_finished, Qt.QueuedConnection)
        self.worker.progress.connect(self.job_progress, Qt.QueuedConnection)
        self.update_buttons(); self.worker.start()
    @Slot(int,int,str)
    def job_progress(self,done,total,name):
        if hasattr(self,'cleaner') and self.goal=='clean':self.cleaner.status.setText(f'{done}/{total} — {name}')
        self.progress.setRange(0,total); self.progress.setValue(done)
        self.library.summary.setText(f'{done}/{total} — {name}' if total else name)
        if hasattr(self,'audio'):
            self.audio.progress.setRange(0,total); self.audio.progress.setValue(done)
            self.audio.summary.setText(f'{done}/{total} — {name}' if total else name)
    @Slot(object)
    def job_succeeded(self,value):
        try: self.success_callback(value)
        except Exception as exc: self.job_failed(f"Result display failed: {exc}")
    @Slot(str)
    def job_failed(self,error):
        self.log_line('ERROR — '+error)
        if hasattr(self,'cleaner') and self.goal=='clean':self.cleaner.status.setText('Operation failed: '+error)
        if hasattr(self,'playback'):self.playback.status.setText('Operation failed: '+error)
        if hasattr(self,'library'): self.library.summary.setText('Operation failed: '+error)
        if hasattr(self,'audio'): self.audio.summary.setText('Operation failed: '+error)
    @Slot()
    def job_finished(self):
        worker=self.worker; self.worker=None
        self.success_callback=None; worker.operation=None; worker.deleteLater()
        self.progress.setRange(0,1); self.progress.setValue(1)
        if hasattr(self,'audio'): self.audio.progress.setRange(0,1); self.audio.progress.setValue(1)
        self.update_buttons()
    def start_from_audio(self):
        self.start_guided('audio')
    def review_cleanup(self):
        if self.song is None or self.busy(): return
        dialog=CleanupDialog(self.song,self)
        if dialog.exec() and dialog.prepared is not None:
            if self.cleanup_report:dialog.report["changes"]=self.cleanup_report["changes"]+dialog.report["changes"]
            self.song=dialog.prepared; self.cleanup_report=dialog.report; self.invalidate()
            self.log_line('Applied working-copy cleanup: '+json.dumps(dialog.report,ensure_ascii=False))
            self.info.setText(f"Cleanup applied: {len(dialog.report['changes'])} changes. Original file unchanged. Convert or generate variations next.")
        dialog.deleteLater()
    def restore_original(self):
        if self.original_song is not None and not self.busy():
            self.song=self.original_song; self.cleanup_report=None; self.invalidate(); self.info.setText('Original imported chart restored; cleanup changes discarded.')
    def browse(self):
        filename,_=QFileDialog.getOpenFileName(self,'Open authored chart','','Charts (*.chart *.mid *.midi)')
        if filename: self.open_path(filename)
    def open_path(self,path):
        if self.busy(): return
        self.song=None; self.original_song=None; self.cleanup_report=None; self.converted=None; self.report=None; self.path=None; self.variants={}
        self.playback.clear_audio()
        self.info.setText('Loading…'); self.preview.scene().clear(); self.playback.set_chart(None,'Medium')
        mode='modern' if self.phrase_mode.currentIndex()==0 else 'legacy'
        def ready(song):
            self.song=song; self.original_song=song; self.path=Path(path); self.file_label.setText(str(path))
            available=[d for d in ('Expert','Hard') if song.tracks.get(d)]
            if available: self.source.setCurrentText(available[0])
            self.info.setText(f"{song.metadata.get('Name',Path(path).stem)} — {song.metadata.get('Artist','Unknown artist')} | PPQ {song.resolution} | "+' · '.join(f'{d}: {len(n)} gems' for d,n in song.tracks.items()))
            self.log_line('Imported. '+ ' '.join(song.warnings)); self.refresh_preview()
            from .preview_audio import matching_audio
            recording=matching_audio(path,song.metadata)
            if recording:self.playback.open_audio(recording)
            else:self.log_line('No unambiguous matching audio found. Click Play preview audio to select the recording.')
            if self.goal=='orange':self.audio.show_listen()
            elif self.goal=='refine':self.tabs.setCurrentWidget(self.converter)
        self.run_job('Reading chart for review…',lambda cancel:load(path,mode,learning_only=True),ready)
    def start_convert(self):
        if self.song is None or self.busy(): return
        settings=self.settings(); self.converted=None; self.report=None; self.variants={}
        def ready(value):
            self.converted,self.report=value
            if self.cleanup_report:self.report["source_cleanup"]=self.cleanup_report
            self.log_line(json.dumps(self.report,indent=2)); self.refresh_preview()
        self.run_job('Converting authored rhythm…',lambda cancel:convert(self.song,settings,cancel),ready,True)
    def start_variations(self):
        if self.song is None or self.busy(): return
        settings=self.settings(); seed=self.seed.value(); category=self.pattern_style.currentText() if self.pattern_style.currentIndex() else ""
        try: store=self.library.store()
        except Exception as exc: self.job_failed(str(exc)); return
        self.converted=None; self.report=None; self.variants={}
        def ready(results):
            if self.cleanup_report:
                for _,report in results.values():report["source_cleanup"]=self.cleanup_report
            self.variants=results
            self.variant_choice.blockSignals(True); self.variant_choice.setCurrentIndex(1); self.variant_choice.blockSignals(False)
            self.select_variant()
            self.log_line('Generated three candidates. Select each to compare and export; some may be identical with a small corpus.')
        self.run_job('Retrieving patterns and generating variations…',lambda cancel:generate_variations(self.song,settings,store,seed,cancel,category),ready,True)
    def select_variant(self,*args):
        name=self.variant_choice.currentText()
        if name in self.variants:
            self.last_export_path=None
            self.converted,self.report=self.variants[name]
            self.refresh_preview(); self.log_line(json.dumps(self.report,indent=2)); self.update_buttons()
    def refresh_preview(self,*args):
        if self.view_choice.currentIndex()==0 and self.converted:
            self.preview.show_notes(self.converted,'Medium')
        elif self.song: self.preview.show_notes(self.song,self.source.currentText())
        else: self.preview.scene().clear()
        if hasattr(self,'playback'):
            self.playback.set_chart(self.converted or self.song,'Medium' if self.converted else self.source.currentText())
    def start_export(self):
        if self.converted is None or self.busy(): return
        from .song_export_gui import SongExportDialog
        dialog=SongExportDialog(self.converted,self.playback.player.source().toLocalFile(),self)
        if not dialog.exec():dialog.deleteLater();return
        prepared,review,audio=dialog.prepared,dialog.review,dialog.audio.text()
        dialog.deleteLater()
        parent=QFileDialog.getExistingDirectory(self,'Choose parent folder for a NEW song folder')
        if not parent:return
        import copy
        report=copy.deepcopy(self.report);report['medium_export_cleanup']=review
        if review.get('hopo_assistance'):report['hopo_assistance']=review['hopo_assistance']
        if any(c['action']=='shorten sustain' for c in review['changes']):report['retained_notes_exact']=False
        from .song_identity import export_folder_name
        name=export_folder_name(prepared.metadata)
        self.export_song_to(Path(parent)/name,audio,prepared,report)
    def export_song_to(self,destination,audio,song=None,report=None):
        from .song_export import export_song_folder
        song=song if song is not None else self.converted
        report=report if report is not None else self.report
        def ready(details):
            self.converted,self.report=song,report;self.last_export_path=Path(destination);self.refresh_preview()
            if Path(self.playback.player.source().toLocalFile()).resolve()!=Path(audio).resolve():
                self.playback.open_audio(audio)
            self.log_line('Song folder verified: '+str(destination)+'\n'+'\n'.join(details['warnings']))
            self.playback.status.setText('Exported song folder: '+str(destination))
            if report.get('hopo_assistance'):
                self.playback.threshold.setValue(1/2.95)
                self.playback.status.setText('Exported with HOPO assistance. Set TheGHOST HOPO measure to 2.95 and verify in-game. '+str(report['hopo_assistance']['estimated_hopo_percent'])+'% estimated HOPO events.')
        self.run_job('Exporting chart, full-mix audio and song.ini…',lambda cancel:export_song_folder(song,report,destination,audio,self.path),ready)
    def export_to(self,destination):
        self.run_job('Writing and reopening both exports…',lambda cancel:export_bundle(self.converted,self.report,destination,self.path),
                     lambda details:self.log_line('Export verified: '+str(destination)+'\n'+ '\n'.join(details['warnings'])))
    def cancel(self):
        if self.worker and self.cancellable: self.worker.requestInterruption(); self.log_line('Cancellation requested…')
    def save_config(self):
        from dataclasses import asdict
        path,_=QFileDialog.getSaveFileName(self,'Save settings','expert-medium.json','JSON (*.json)')
        if path:
            try:
                config=self.report['settings'] if self.report and 'audio' in self.report else dict(asdict(self.settings()),seed=self.seed.value(),pattern_style=self.pattern_style.currentText() if self.pattern_style.currentIndex() else '')
                Path(path).write_text(json.dumps(config,indent=2),encoding='utf-8')
            except Exception as e: self.job_failed(str(e))
    def load_config(self):
        path,_=QFileDialog.getOpenFileName(self,'Load settings','','JSON (*.json)')
        if path:
            try:
                config=json.loads(Path(path).read_text(encoding='utf-8'))
                settings=Settings(**{k:v for k,v in config.items() if k in Settings.__dataclass_fields__}); settings.check()
                if 'seed' in config: self.seed.setValue(int(config['seed']))
                if 'pattern_style' in config:self.pattern_style.setCurrentText(config['pattern_style'] or 'All styles')
                if 'audio_analysis' in config:
                    from .audio_analysis import AudioSettings
                    audio_settings=AudioSettings(**config['audio_analysis']); audio_settings.validate()
                    self.audio.sensitivity.setValue(audio_settings.sensitivity); self.audio.spacing.setValue(audio_settings.min_interval_ms); self.audio.bpm.setValue(audio_settings.manual_bpm)
                    self.audio.shift.setValue(float(config.get('shift_ms',0)))
                    self.audio.template.setChecked(bool(config.get('use_authored_tempo_map',False))); self.audio.learned.setChecked(bool(config.get('use_learned_patterns',False)))
                    self.log_line('Audio settings loaded. Select the matching recording and reanalyze before creating a draft.')
                self.source.setCurrentText(settings.source); self.max_chord.setValue(settings.max_chord)
                for name,attr in [('Density','density'),('Chords','chords'),('Movement','movement')]: self.sliders[name].setValue(getattr(settings,attr))
            except Exception as e: self.job_failed(str(e))
    def save_diagnostics(self):
        path,_=QFileDialog.getSaveFileName(self,'Save diagnostic log','gh3-studio.log','Log (*.log)')
        if path:
            try: Path(path).write_text(self.log.toPlainText(),encoding='utf-8')
            except Exception as e: self.job_failed(str(e))
    def dragEnterEvent(self,event):
        if not self.busy() and event.mimeData().hasUrls(): event.acceptProposedAction()
    def dropEvent(self,event):
        paths=[u.toLocalFile() for u in event.mimeData().urls() if u.isLocalFile()]
        if len(paths)!=1: self.log_line('Drop one chart or a single parent folder for recursive pattern scanning.'); return
        if Path(paths[0]).is_dir():
            if self.tabs.currentWidget() is self.library:self.library.scan(paths[0])
            else:self.start_guided('clean',paths[0])
            event.acceptProposedAction(); return
        if self.tabs.currentWidget() is self.welcome and not Path(paths[0]).is_dir():
            goal='audio' if Path(paths[0]).suffix.lower() in ('.wav','.flac','.ogg','.mp3') else 'orange'
            self.start_guided(goal,paths[0]);event.acceptProposedAction();return
        if Path(paths[0]).suffix.lower() in ('.wav','.flac','.ogg','.mp3'):
            self.tabs.setCurrentWidget(self.audio); self.audio.open_path(paths[0]); event.acceptProposedAction(); return
        self.open_path(paths[0]); event.acceptProposedAction()
    def closeEvent(self,event):
        if self.busy():
            self.cancel(); self.log_line('Wait for the current operation to finish before closing.'); event.ignore()
        else:
            self.playback.shutdown(); event.accept()

def main():
    app=QApplication(sys.argv); app.setOrganizationName('GH3ChartStudio'); app.setApplicationName('GH3ChartStudio'); app.setStyle('Fusion')
    from .first_run import FirstRunDialog, has_accepted
    from PySide6.QtCore import QSettings
    settings=QSettings('GH3ChartStudio','GH3ChartStudio')
    # A visible first-run dialog counts as ready: never time out while reading.
    app.setQuitOnLastWindowClosed(False)
    windows=[]
    def open_studio():
        window=Window(); windows.append(window); window.show()
        app.setQuitOnLastWindowClosed(True)
    if has_accepted(settings):
        open_studio()
    else:
        gate=FirstRunDialog(settings); windows.append(gate)
        gate.accepted.connect(open_studio)
        gate.rejected.connect(app.quit)
        gate.show()
    import os
    from PySide6.QtCore import QTimer
    ready=os.environ.get('GH3_STARTUP_READY')
    if ready:
        # Report only after the event loop has started and the window was shown.
        QTimer.singleShot(0,lambda:Path(ready).write_text('ready',encoding='utf-8'))
    sys.exit(app.exec())
