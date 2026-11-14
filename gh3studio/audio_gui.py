"""Audio analysis workspace; no simulated playback or claimed instrument isolation."""
import json
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor,QPen
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QPushButton,QLabel,QSpinBox,QDoubleSpinBox,
    QCheckBox,QFileDialog,QTextEdit,QGraphicsView,QGraphicsScene,QProgressBar,QSlider)
from .audio_analysis import AudioSettings,analyze_audio
from .audio_chart import make_draft,alignment_report

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
        layout=QVBoxLayout(self)
        title=QLabel('Audio Analysis — reviewable onset drafts');title.setStyleSheet('font-size:22px;font-weight:600');layout.addWidget(title)
        hint=QLabel('Detect attack candidates in the full mix. This does not isolate guitar or prove transcription accuracy.\nOrange is prohibited in generated Medium charts. Original audio stays unchanged.')
        hint.setWordWrap(True);layout.addWidget(hint)
        row=QHBoxLayout();layout.addLayout(row)
        self.open_button=QPushButton('Open audio…');self.open_button.clicked.connect(self.browse);row.addWidget(self.open_button)
        self.file_label=QLabel('WAV • FLAC • OGG • MP3');self.file_label.setWordWrap(True);row.addWidget(self.file_label,1)
        row=QHBoxLayout();layout.addLayout(row)
        row.addWidget(QLabel('Sensitivity'));self.sensitivity=QSpinBox();self.sensitivity.setRange(1,6);self.sensitivity.setValue(4);row.addWidget(self.sensitivity)
        row.addWidget(QLabel('Min spacing (ms)'));self.spacing=QSpinBox();self.spacing.setRange(30,1000);self.spacing.setValue(70);row.addWidget(self.spacing)
        row.addWidget(QLabel('BPM override'));self.bpm=QDoubleSpinBox();self.bpm.setDecimals(3);self.bpm.setRange(0,300);self.bpm.setSpecialValueText('Automatic');row.addWidget(self.bpm)
        self.analyze_button=QPushButton('Analyze / reanalyze');self.analyze_button.clicked.connect(self.start_analysis);row.addWidget(self.analyze_button)
        for widget in (self.sensitivity,self.spacing,self.bpm):widget.valueChanged.connect(self.invalidate)
        self.progress=QProgressBar();self.progress.setRange(0,1);layout.addWidget(self.progress)
        self.summary=QLabel('Open a recording to begin. Analysis runs locally.');self.summary.setWordWrap(True);layout.addWidget(self.summary)
        self.wave=WavePreview();layout.addWidget(self.wave,1)
        row=QHBoxLayout();layout.addLayout(row)
        row.addWidget(QLabel('Orange lines: detected attacks • Gray lines: estimated beats | Zoom'))
        self.zoom=QSlider(Qt.Horizontal);self.zoom.setRange(20,250);self.zoom.setValue(100);self.zoom.valueChanged.connect(self.redraw);row.addWidget(self.zoom)
        row=QHBoxLayout();layout.addLayout(row)
        row.addWidget(QLabel('Draft shift (ms; + = later)'));self.shift=QDoubleSpinBox();self.shift.setRange(-10000,10000);self.shift.setDecimals(1);row.addWidget(self.shift)
        self.template=QCheckBox('Use open chart tempo map when available');self.template.setChecked(True);row.addWidget(self.template)
        self.learned=QCheckBox('Use local learned patterns');row.addWidget(self.learned)
        row=QHBoxLayout();layout.addLayout(row)
        self.draft_button=QPushButton('Create four-fret draft');self.draft_button.clicked.connect(self.create_draft);row.addWidget(self.draft_button)
        self.compare_button=QPushButton('Compare timing with current chart');self.compare_button.clicked.connect(self.compare);row.addWidget(self.compare_button)
        self.save_button=QPushButton('Save analysis / diagnostics…');self.save_button.clicked.connect(self.save_report);row.addWidget(self.save_button)
        self.cancel_button=QPushButton('Cancel');self.cancel_button.clicked.connect(owner.cancel);row.addWidget(self.cancel_button)
        self.details=QTextEdit();self.details.setReadOnly(True);self.details.setMaximumHeight(180);layout.addWidget(self.details)
        self.controls=(self.open_button,self.sensitivity,self.spacing,self.bpm,self.shift,self.template,self.learned)
    def update_busy(self,busy,cancellable):
        for widget in self.controls:widget.setEnabled(not busy)
        self.analyze_button.setEnabled(not busy and self.path is not None)
        self.draft_button.setEnabled(not busy and self.analysis is not None and bool(self.analysis.onsets))
        self.compare_button.setEnabled(not busy and self.analysis is not None and self.owner.song is not None)
        self.save_button.setEnabled(not busy and self.analysis is not None)
        self.cancel_button.setEnabled(busy and cancellable)
    def invalidate(self,*args):
        self.analysis=None;self.last_diagnostics=None;self.wave.scene().clear();self.summary.setText('Settings changed; reanalyze before generating.')
        if self.owner.report and 'audio' in self.owner.report:self.owner.invalidate()
        self.owner.update_buttons()
    def browse(self):
        path,_=QFileDialog.getOpenFileName(self,'Open recording','','Audio (*.wav *.flac *.ogg *.mp3)')
        if path:self.open_path(path)
    def open_path(self,path):
        if self.owner.busy():return
        self.path=Path(path);self.file_label.setText(str(path));self.invalidate();self.start_analysis()
    def start_analysis(self):
        if self.path is None or self.owner.busy():return
        settings=AudioSettings(self.sensitivity.value(),self.spacing.value(),self.bpm.value())
        self.analysis=None;self.last_diagnostics=None
        def ready(result):
            self.analysis=result;self.summary.setText(f'{result.duration:.2f} seconds | {len(result.onsets)} attacks | BPM: {result.bpm or "unknown"} | beat fit: {result.beat_fit:.0%} (not confidence)')
            self.details.setPlainText('\n'.join(result.warnings));self.redraw();self.owner.log_line(self.summary.text())
        self.owner.run_job('Analyzing audio locally…',lambda cancel:analyze_audio(self.path,settings,cancel,
            lambda done,total,text:self.owner.worker.progress.emit(done,total,text)),ready,True)
    def redraw(self,*args):
        if self.analysis:self.wave.render(self.analysis,self.zoom.value())
    def create_draft(self):
        if self.analysis is None or self.owner.busy():return
        analysis=self.analysis;template=self.owner.song if self.template.isChecked() else None
        shift=self.shift.value();seed=self.owner.seed.value()
        try:store=self.owner.library.store() if self.learned.isChecked() else None
        except Exception as exc:self.owner.job_failed(str(exc));return
        def ready(value):
            song,report=value
            self.owner.song=song;self.owner.converted=song;self.owner.report=report;self.owner.path=Path(analysis.source_path);self.owner.variants={}
            available=[d for d in ('Expert','Hard') if song.tracks.get(d)]
            if available and self.owner.source.currentText() not in available:
                self.owner.source.blockSignals(True); self.owner.source.setCurrentText(available[0]); self.owner.source.blockSignals(False)
            self.owner.file_label.setText(Path(analysis.source_path).name+' — audio draft')
            self.owner.info.setText(f'Audio draft: {len(song.tracks["Medium"])} Medium gems. Review against the recording before use.')
            self.owner.refresh_preview();self.owner.log_line(json.dumps(report,indent=2));self.owner.tabs.setCurrentIndex(0)
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
            try:Path(path).write_text(json.dumps({'analysis':self.analysis.report(),'alignment':self.last_diagnostics},indent=2),encoding='utf-8')
            except Exception as exc:self.owner.job_failed(str(exc))
