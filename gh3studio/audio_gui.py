"""Audio-only draft workflow; full-mix analysis, not instrument isolation."""
import json
from dataclasses import replace
from pathlib import Path
from PySide6.QtCore import Qt,QUrl
from PySide6.QtGui import QColor,QPen,QDesktopServices
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QPushButton,QLabel,QSpinBox,QDoubleSpinBox,
    QCheckBox,QFileDialog,QTextEdit,QGraphicsView,QGraphicsScene,QProgressBar,QSlider,
    QScrollArea,QStackedWidget,QTableView,QHeaderView,QGroupBox,QGridLayout)
from .audio_analysis import AudioSettings,analyze_audio
from .audio_chart import make_draft,alignment_report
from .onset_review import OnsetModel

class WavePreview(QGraphicsView):
    def __init__(self):
        super().__init__();self.setScene(QGraphicsScene(self));self.setMinimumHeight(200);self.analysis=None
        self.setBackgroundBrush(QColor('#101722'))
    def render(self,analysis,zoom=100):
        self.analysis=analysis;scene=self.scene();scene.clear();scale=zoom
        for t,low,high in analysis.waveform:
            scene.addLine(t*scale,90-low*70,t*scale,90-high*70,QPen(QColor('#56b5c2')))
        for t in analysis.beat_times[:10000]:scene.addLine(t*scale,10,t*scale,170,QPen(QColor('#344356')))
        for onset in analysis.onsets[:10000]:scene.addLine(onset['time']*scale,20,onset['time']*scale,160,QPen(QColor('#f4b860')))
        step=max(1,int(100/scale))
        for t in range(0,int(analysis.duration)+1,step):
            text=scene.addText(f'{t}s');text.setDefaultTextColor(QColor('#c6d4e3'));text.setPos(t*scale,165)
        scene.setSceneRect(0,0,max(800,analysis.duration*scale+50),200)

class AudioPanel(QWidget):
    def __init__(self,owner):
        super().__init__();self.owner=owner;self.path=None;self.analysis=None;self.last_diagnostics=None
        self.original_audio=None;self.last_draft_source=None
        layout=QVBoxLayout(self)
        self.title=QLabel('Audio Studio — choose → review → listen → export');self.title.setStyleSheet('font-size:20px;font-weight:600');self.title.setWordWrap(True);layout.addWidget(self.title)
        self.next_step=QLabel('Step 1: Choose a recording. No chart or pattern library is required.');self.next_step.setWordWrap(True);self.next_step.setObjectName('nextStep');layout.addWidget(self.next_step)
        self.open_export_button=QPushButton('Open exported song folder');self.open_export_button.clicked.connect(self.open_export_folder);self.open_export_button.hide();layout.addWidget(self.open_export_button)
        steps=QGridLayout();layout.addLayout(steps)
        self.open_button=QPushButton('1. Choose audio…');self.open_button.clicked.connect(self.choose_input);steps.addWidget(self.open_button,0,0)
        self.review_button=QPushButton('2. Review attacks');self.review_button.clicked.connect(self.review_step);steps.addWidget(self.review_button,0,1)
        self.listen_button=QPushButton('3. Listen / timing');self.listen_button.clicked.connect(self.show_listen);steps.addWidget(self.listen_button,1,0)
        self.export_button=QPushButton('4. Export song folder…');self.export_button.clicked.connect(owner.start_export);steps.addWidget(self.export_button,1,1)
        self.file_label=QLabel('Analysis source: none');self.file_label.setWordWrap(True);layout.addWidget(self.file_label)
        self.progress=QProgressBar();self.progress.setRange(0,1);layout.addWidget(self.progress)
        self.pages=QStackedWidget();layout.addWidget(self.pages,1)
        self.analysis_page=QWidget();page_layout=QVBoxLayout(self.analysis_page)
        self.scroll=QScrollArea();self.scroll.setWidgetResizable(True);page_layout.addWidget(self.scroll,1)
        body=QWidget();content=QVBoxLayout(body);self.scroll.setWidget(body)
        hint=QLabel('Detected attacks are suggestions, not identified guitar notes. Drums, vocals and other instruments can trigger them. Uncheck unwanted attacks below.')
        hint.setWordWrap(True);content.addWidget(hint)
        self.summary=QLabel('Choose a recording to begin.');self.summary.setWordWrap(True);content.addWidget(self.summary)
        row=QHBoxLayout();content.addLayout(row)
        self.stem_button=QPushButton('Analyze a guitar / instrument stem…');self.stem_button.clicked.connect(self.browse_stem);row.addWidget(self.stem_button)
        self.mix_button=QPushButton('Analyze original mix again');self.mix_button.clicked.connect(self.restore_mix);row.addWidget(self.mix_button)
        note=QLabel('Optional: supply an already-separated file with the same start time as the mix. This app does not separate instruments yet.');note.setWordWrap(True);content.addWidget(note)
        self.wave=WavePreview();self.wave.setMaximumHeight(230);content.addWidget(self.wave)
        row=QHBoxLayout();content.addLayout(row)
        row.addWidget(QLabel('Attacks: orange | Estimated beats: gray | Zoom'))
        self.zoom=QSlider(Qt.Horizontal);self.zoom.setRange(20,250);self.zoom.setValue(100);self.zoom.valueChanged.connect(self.redraw);row.addWidget(self.zoom)
        row=QHBoxLayout();content.addLayout(row)
        self.selection_label=QLabel('0 attacks selected');row.addWidget(self.selection_label,1)
        self.keep_all=QPushButton('Include all');self.keep_all.clicked.connect(lambda:self.onsets.select_all(True));row.addWidget(self.keep_all)
        self.keep_none=QPushButton('Exclude all');self.keep_none.clicked.connect(lambda:self.onsets.select_all(False));row.addWidget(self.keep_none)
        self.onsets=OnsetModel(self);self.onsets.selection_changed.connect(self.selection_changed)
        self.attack_table=QTableView();self.attack_table.setModel(self.onsets);self.attack_table.setMinimumHeight(130);self.attack_table.setMaximumHeight(200)
        self.attack_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch);content.addWidget(self.attack_table)
        self.attack_table.doubleClicked.connect(self.audition_attack)
        note=QLabel('Double-click an attack to listen from just before it. Attack strength is not guitar confidence.');note.setWordWrap(True);content.addWidget(note)
        self.advanced_toggle=QCheckBox('Optional settings: detection, tempo map and learned patterns');content.insertWidget(0,self.advanced_toggle)
        self.advanced=QGroupBox('Optional — defaults work without a chart or library');advanced=QVBoxLayout(self.advanced);content.insertWidget(1,self.advanced)
        self.advanced.setVisible(False);self.advanced_toggle.toggled.connect(self.advanced.setVisible)
        row=QHBoxLayout();advanced.addLayout(row)
        row.addWidget(QLabel('Sensitivity'));self.sensitivity=QSpinBox();self.sensitivity.setRange(1,6);self.sensitivity.setValue(4);row.addWidget(self.sensitivity)
        row.addWidget(QLabel('Minimum spacing (ms)'));self.spacing=QSpinBox();self.spacing.setRange(30,1000);self.spacing.setValue(70);row.addWidget(self.spacing)
        row.addWidget(QLabel('BPM override'));self.bpm=QDoubleSpinBox();self.bpm.setDecimals(3);self.bpm.setRange(0,300);self.bpm.setSpecialValueText('Automatic');row.addWidget(self.bpm)
        for widget in (self.sensitivity,self.spacing,self.bpm):widget.valueChanged.connect(self.invalidate)
        row=QHBoxLayout();advanced.addLayout(row)
        row.addWidget(QLabel('Draft shift (ms; + = later)'));self.shift=QDoubleSpinBox();self.shift.setRange(-10000,10000);self.shift.setDecimals(1);row.addWidget(self.shift)
        self.template=QCheckBox('Use the open chart’s tempo map (optional)');advanced.addWidget(self.template)
        self.learned=QCheckBox('Use local learned patterns (optional; successful library scan required)');advanced.addWidget(self.learned)
        self.compare_button=QPushButton('Compare timing with current chart');self.compare_button.clicked.connect(self.compare);advanced.addWidget(self.compare_button)
        self.save_button=QPushButton('Save analysis / diagnostics…');self.save_button.clicked.connect(self.save_report);advanced.addWidget(self.save_button)
        self.details=QTextEdit();self.details.setReadOnly(True);self.details.setMaximumHeight(140);advanced.addWidget(self.details)
        row=QHBoxLayout();page_layout.addLayout(row)
        self.analyze_button=QPushButton('Reanalyze audio');self.analyze_button.clicked.connect(self.start_analysis);row.addWidget(self.analyze_button)
        self.draft_button=QPushButton('Create draft → Listen');self.draft_button.setToolTip('Create a chart draft from the selected attacks, then listen and review.');self.draft_button.clicked.connect(self.create_draft);page_layout.addWidget(self.draft_button)
        self.cancel_button=QPushButton('Cancel');self.cancel_button.clicked.connect(owner.cancel);row.addWidget(self.cancel_button)
        self.pages.addWidget(self.analysis_page);self.pages.addWidget(owner.playback)
        self.controls=(self.open_button,self.sensitivity,self.spacing,self.bpm,self.shift,self.template,self.learned,self.attack_table,self.keep_all,self.keep_none)
    def open_export_folder(self):
        if self.owner.last_export_path:
            if not QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.owner.last_export_path.resolve()))):self.owner.log_line('Could not open export folder: '+str(self.owner.last_export_path))
    def set_mode(self,goal):
        orange=goal=='orange'
        self.title.setText('Four-fret Medium — keep the authored challenge' if orange else 'Audio Studio — turn a recording into a draft')
        self.open_button.setText('1. Open chart…' if orange else '1. Choose audio…')
        self.review_button.setText('2. Choose difficulty' if orange else '2. Review attacks')
        self.listen_button.setText('3. Listen / compare' if orange else '3. Listen / timing')
        self.file_label.setVisible(not orange)
        self.owner.playback.chart_open.setVisible(goal not in ('orange','audio'))
        if orange:self.owner.playback.hint.setText('Compare the original difficulty and the new Medium against your recording. White outlines estimate HOPO behavior; in-game verification is still required.')
        elif goal=='audio':self.owner.playback.hint.setText('Listen to the draft against your recording. Review which attacks became notes, then adjust timing if needed. White outlines are estimated HOPO candidates.')
    def choose_input(self):
        if self.owner.goal=='orange':self.owner.start_guided('orange')
        else:self.browse()
    def review_step(self):
        if self.owner.goal=='orange':self.show_listen();self.owner.playback.difficulty.setFocus()
        else:self.show_analysis()
    def show_analysis(self):
        self.pages.setCurrentWidget(self.analysis_page)
        if hasattr(self,"draft_button"):self.update_busy(self.owner.busy(),getattr(self.owner,"cancellable",False))
    def show_listen(self):
        self.owner.tabs.setCurrentWidget(self);self.pages.setCurrentWidget(self.owner.playback)
        self.update_busy(self.owner.busy(),getattr(self.owner,"cancellable",False))
    def selection_changed(self):
        count=sum(self.onsets.included);self.selection_label.setText(f'{count} of {len(self.onsets.included)} attacks included')
        if self.last_draft_source is not None and self.owner.song is self.last_draft_source:
            self.owner.song=None;self.owner.path=None;self.last_draft_source=None;self.owner.invalidate()
        self.owner.update_buttons()
    def audition_attack(self,index):
        if self.owner.busy() or not index.isValid():return
        if self.owner.playback.player.source().isEmpty() and self.original_audio:
            self.owner.playback.open_audio(self.original_audio)
        time=self.onsets.onsets[index.row()]['time']
        self.owner.playback.player.setPosition(max(0,int((time-.5)*1000)))
        self.show_listen();self.owner.playback.play()
    def browse_stem(self):
        path,_=QFileDialog.getOpenFileName(self,'Choose an already-separated instrument file with the same time origin','','Audio (*.wav *.flac *.ogg *.mp3)')
        if path:self.open_stem(path)
    def open_stem(self,path):
        if self.owner.busy() or self.original_audio is None:return
        self.path=Path(path);self.file_label.setText('Analysis stem: '+str(path)+' | Listening mix: '+self.original_audio.name)
        self.invalidate();self.show_analysis();self.start_analysis()
    def restore_mix(self):
        if self.original_audio:self.open_path(self.original_audio)
    def update_busy(self,busy,cancellable):
        for widget in self.controls:widget.setEnabled(not busy)
        self.analyze_button.setEnabled(not busy and self.path is not None)
        self.draft_button.setEnabled(not busy and self.analysis is not None and any(self.onsets.included))
        self.review_button.setEnabled(not busy and self.path is not None)
        self.listen_button.setEnabled(not busy and (self.path is not None or self.owner.song is not None))
        self.export_button.setEnabled(not busy and self.owner.converted is not None)
        self.stem_button.setEnabled(not busy and self.original_audio is not None)
        self.mix_button.setEnabled(not busy and self.original_audio is not None and self.path!=self.original_audio)
        if busy:self.next_step.setText('Working… wait for completion or cancel analysis.')
        elif self.owner.converted is not None and self.pages.currentWidget() is self.owner.playback:self.next_step.setText('Step 3: Listen and adjust. When satisfied, click 4. Export song folder.')
        elif self.pages.currentWidget() is self.owner.playback and self.owner.song is not None:self.next_step.setText('Select a display difficulty. Choose preview audio to listen, or copy Expert/Hard to Medium with Remove Orange.')
        elif self.analysis is not None:
            if self.analysis.bpm is None and not self.template.isChecked():self.next_step.setText('NEXT • Tempo needs review. Open Optional settings, enter the BPM, then Reanalyze before creating a draft.')
            else:self.next_step.setText('STEP 2 • Uncheck attacks you do not want to play. Then click Create draft from selected attacks → Listen.')
        elif self.path is not None:self.next_step.setText('Step 2: Run analysis. If BPM is unknown, set it under Optional settings and reanalyze.')
        self.compare_button.setEnabled(not busy and self.analysis is not None and self.owner.song is not None)
        self.save_button.setEnabled(not busy and self.analysis is not None)
        self.cancel_button.setEnabled(busy and cancellable)
        if getattr(self.owner,'goal',None)=='orange':
            self.review_button.setEnabled(not busy and self.owner.song is not None)
            if busy:self.next_step.setText('Working on your chart… the current operation will finish before you continue.')
            elif self.owner.converted is not None:
                source=(self.owner.report or {}).get('source_difficulty','selected track')
                self.next_step.setText(f'NEXT • Compare the new Medium with {source}, choose the recording and press Play. Then export: metadata and optional HOPOs are reviewed there.')
            elif self.owner.song is not None:self.next_step.setText('NEXT • Choose Hard or Expert in Display / copy source below, then click Remove Orange → Medium. All surviving notes keep their original timing.')
            else:self.next_step.setText('STEP 1 • Open an existing chart. We’ll help you choose its source difficulty next.')
        elif not busy and self.owner.converted is None and self.analysis is None and self.path is None:
            self.next_step.setText('STEP 1 • Choose a recording. You do not need an existing chart or a pattern library.')
        exported=getattr(self.owner,'last_export_path',None)
        self.open_export_button.setVisible(exported is not None);self.open_export_button.setEnabled(not busy)
        if exported is not None and not busy:self.next_step.setText('EXPORT COMPLETE • Your song folder is ready for import testing. Open it below, then use notes.chart + song.ogg in TheGHOST. Originals are unchanged.')
    def invalidate(self,*args):
        self.analysis=None;self.last_diagnostics=None;self.onsets.reset_onsets([]);self.wave.scene().clear();self.summary.setText('Settings changed; reanalyze before generating.')
        if self.owner.report and 'audio' in self.owner.report:self.owner.invalidate()
        self.owner.update_buttons()
    def browse(self):
        path,_=QFileDialog.getOpenFileName(self,'Open recording','','Audio (*.wav *.flac *.ogg *.mp3)')
        if path:self.open_path(path)
    def open_path(self,path):
        if self.owner.busy():return
        self.owner.playback.open_audio(path)
        self.original_audio=Path(path);self.path=Path(path);self.file_label.setText('Analysis and listening: '+str(path));self.show_analysis();self.invalidate();self.start_analysis()
    def start_analysis(self):
        if self.path is None or self.owner.busy():return
        self.owner.invalidate()  # A new analysis must not leave an older output exportable.
        settings=AudioSettings(self.sensitivity.value(),self.spacing.value(),self.bpm.value())
        self.analysis=None;self.last_diagnostics=None;self.onsets.reset_onsets([])
        def ready(result):
            self.analysis=result;self.summary.setText(f'{result.duration:.2f} seconds | {len(result.onsets)} attacks | BPM: {result.bpm or "unknown"} | beat fit: {result.beat_fit:.0%} (not confidence)')
            self.onsets.reset_onsets(result.onsets)
            self.details.setPlainText('\n'.join(result.warnings));self.redraw();self.owner.log_line(self.summary.text())
        self.owner.run_job('Analyzing audio locally…',lambda cancel:analyze_audio(self.path,settings,cancel,
            lambda done,total,text:self.owner.worker.progress.emit(done,total,text)),ready,True)
    def redraw(self,*args):
        if self.analysis:self.wave.render(self.analysis,self.zoom.value())
    def create_draft(self):
        if self.analysis is None or self.owner.busy():return
        analysis=replace(self.analysis,onsets=self.onsets.selected());template=self.owner.song if self.template.isChecked() else None
        if self.template.isChecked() and template is None:
            self.owner.job_failed('No chart is open. Uncheck the optional tempo-map setting to create from audio only.');return
        shift=self.shift.value();seed=self.owner.seed.value()
        excluded=[o['time'] for o,keep in zip(self.onsets.onsets,self.onsets.included) if not keep]
        try:store=self.owner.library.store() if self.learned.isChecked() else None
        except Exception as exc:self.owner.job_failed(str(exc));return
        def ready(value):
            song,report=value
            report['attack_review']={'detected':len(self.analysis.onsets),'included':len(analysis.onsets),'excluded_times_seconds':excluded}
            report['audio']['listening_path']=str(self.original_audio)
            report['audio']['external_stem']=self.path!=self.original_audio
            if self.path!=self.original_audio:
                report['warnings'].append('External stem supplied: same time origin as the original mix is assumed, not verified. Instrument separation was not performed by this app.')
            self.last_draft_source=song
            self.owner.original_song=None;self.owner.cleanup_report=None
            self.owner.song=song;self.owner.converted=song;self.owner.report=report;self.owner.path=Path(analysis.source_path);self.owner.variants={}
            available=[d for d in ('Expert','Hard') if song.tracks.get(d)]
            if available and self.owner.source.currentText() not in available:
                self.owner.source.blockSignals(True); self.owner.source.setCurrentText(available[0]); self.owner.source.blockSignals(False)
            self.owner.file_label.setText(Path(analysis.source_path).name+' — audio draft')
            self.owner.info.setText(f'Audio draft: {len(song.tracks["Medium"])} Medium gems. Review against the recording before use.')
            self.owner.refresh_preview();self.owner.log_line(json.dumps(report,indent=2));self.show_listen()
        self.owner.run_job('Creating onset-aligned four-fret draft…',lambda cancel:make_draft(analysis,shift,template,store,seed,cancel),ready,True)
    def compare(self):
        if self.analysis is None or self.owner.song is None or self.owner.busy():return
        song=self.owner.converted or self.owner.song;difficulty='Medium' if self.owner.converted else self.owner.source.currentText()
        shift=0;analysis=self.analysis
        def ready(report):self.last_diagnostics=report;self.details.setPlainText(json.dumps(report,indent=2));self.summary.setText(report['interpretation'])
        self.owner.run_job('Comparing chart notes with detected attacks…',lambda cancel:alignment_report(song,difficulty,analysis,shift),ready)
    def save_report(self):
        if self.analysis is None:return
        path,_=QFileDialog.getSaveFileName(self,'Save audio analysis','audio-analysis.json','JSON (*.json)')
        if path:
            try:Path(path).write_text(json.dumps({'analysis':self.analysis.report(),'included_attack_times':[o['time'] for o in self.onsets.selected()],'listening_path':str(self.original_audio),'alignment':self.last_diagnostics},indent=2),encoding='utf-8')
            except Exception as exc:self.owner.job_failed(str(exc))
