"""Audio-clock-driven chart review. This is not a gameplay engine."""
import copy
from pathlib import Path
from PySide6.QtCore import Qt, QUrl, QTimer, Slot
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput, QMediaDevices
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QPushButton,QLabel,QSlider,QDoubleSpinBox,QCheckBox,QFileDialog
from .editing import timeline,shift_timing
from .validation import ensure_valid

class Highway(QWidget):
    def __init__(self):
        super().__init__();self.notes=[];self.position=0.;self.shift=0.;self.highlight=True;self.setMinimumHeight(240)
    def paintEvent(self,event):
        p=QPainter(self);p.fillRect(self.rect(),QColor('#101722'))
        width=self.width();height=self.height();hit=height-35;scale=(height-55)/3
        colors=['#4cd964','#ef5350','#ffe066','#42a5f5','#ff9800']
        # Five source lanes are shown when needed; exported Medium stays four.
        lanes=5 if any(n[2]==4 for n in self.notes) else 4
        lane_width=width/lanes
        p.setPen(QPen(QColor('#344356'),1))
        for lane in range(lanes+1):p.drawLine(int(lane*lane_width),0,int(lane*lane_width),height)
        p.setPen(QPen(QColor('white'),2));p.drawLine(0,hit,width,hit)
        for start,end,lane,hopo in self.notes:
            y=hit-(start+self.shift-self.position)*scale
            tail=hit-(end+self.shift-self.position)*scale
            if tail>height or y<0:continue
            x=int((lane+.5)*lane_width);p.setPen(QPen(QColor(colors[lane]),5))
            if end>start:p.drawLine(x,int(max(0,tail)),x,int(min(height,y)))
            if 0<=y<=height:
                p.setBrush(QColor(colors[lane]));p.setPen(QPen(QColor('white') if hopo and self.highlight else QColor('#111111'),3))
                p.drawEllipse(x-10,int(y)-7,20,14)
        for lane in range(lanes):
            p.setPen(QColor(colors[lane]));p.drawText(int(lane*lane_width),height-25,int(lane_width),22,Qt.AlignCenter,'GRYBO'[lane])
        p.end()

class PlaybackPanel(QWidget):
    def __init__(self,owner):
        super().__init__();self.owner=owner;self.current=None;self.undo_stack=[];self.redo_stack=[]
        self.player=QMediaPlayer(self);self.output=QAudioOutput(self);self.player.setAudioOutput(self.output);self.output.setVolume(.7)
        layout=QVBoxLayout(self)
        hint=QLabel('Listen and review timing. White outlines mark estimated natural HOPO candidates, not guaranteed no-strum notes.\nNo chart is needed to play audio. Create an audio draft or convert a chart to preview and export notes.')
        hint.setWordWrap(True);layout.addWidget(hint)
        row=QHBoxLayout();layout.addLayout(row)
        self.open_button=QPushButton('Choose preview audio…');self.open_button.clicked.connect(self.browse);row.addWidget(self.open_button)
        self.play_button=QPushButton('Play / pause');self.play_button.clicked.connect(self.toggle);row.addWidget(self.play_button)
        stop=QPushButton('Stop');stop.clicked.connect(self.stop);row.addWidget(stop)
        self.label=QLabel('No audio selected');row.addWidget(self.label,1)
        row=QHBoxLayout();layout.addLayout(row)
        row.addWidget(QLabel('Volume'));volume=QSlider(Qt.Horizontal);volume.setRange(0,100);volume.setValue(70);volume.valueChanged.connect(lambda v:self.output.setVolume(v/100));row.addWidget(volume)
        self.seek=QSlider(Qt.Horizontal);self.seek.setRange(0,0);self.seek.sliderMoved.connect(self.player.setPosition);layout.addWidget(self.seek)
        self.player.durationChanged.connect(self.duration_changed,Qt.QueuedConnection)
        self.player.positionChanged.connect(self.position_changed,Qt.QueuedConnection)
        self.player.errorOccurred.connect(self.media_error,Qt.QueuedConnection)
        self.highway=Highway();layout.addWidget(self.highway,1)
        row=QHBoxLayout();layout.addLayout(row)
        self.hopo=QCheckBox('Highlight natural HOPO candidates');self.hopo.setChecked(True);self.hopo.toggled.connect(self.highlight);row.addWidget(self.hopo)
        row.addWidget(QLabel('Candidate gap ≤ beats'));self.threshold=QDoubleSpinBox();self.threshold.setDecimals(4);self.threshold.setRange(.01,1);self.threshold.setValue(1/3);self.threshold.valueChanged.connect(self.rebuild);row.addWidget(self.threshold)
        row=QHBoxLayout();layout.addLayout(row)
        row.addWidget(QLabel('Preview shift (ms; + = notes later)'));self.shift=QDoubleSpinBox();self.shift.setRange(-10000,10000);self.shift.setDecimals(1);self.shift.valueChanged.connect(self.shift_changed);row.addWidget(self.shift)
        self.apply_button=QPushButton('Apply shift to output');self.apply_button.clicked.connect(self.apply_shift);row.addWidget(self.apply_button)
        self.undo_button=QPushButton('Undo shift');self.undo_button.clicked.connect(self.undo);row.addWidget(self.undo_button)
        self.redo_button=QPushButton('Redo shift');self.redo_button.clicked.connect(self.redo);row.addWidget(self.redo_button)
        self.status=QLabel('Timing preview uses the media playback clock. Device latency still needs listening checks.');self.status.setWordWrap(True);layout.addWidget(self.status)
        self.timer=QTimer(self);self.timer.setInterval(33);self.timer.timeout.connect(self.tick);self.timer.start()
        self.update_busy(False,False)
    def browse(self):
        path,_=QFileDialog.getOpenFileName(self,'Choose matching recording','','Audio (*.wav *.flac *.ogg *.mp3)')
        if path:self.open_audio(path)
    def open_audio(self,path):
        self.player.pause();self.player.setSource(QUrl.fromLocalFile(str(Path(path).resolve())));self.label.setText(Path(path).name)
        if QMediaDevices.defaultAudioOutput().isNull():self.label.setText(Path(path).name+' — no audio output device detected')
    def stop(self):
        # Pause and rewind avoids Qt 6.8 FFmpeg stop/seek lock contention.
        self.player.pause();self.player.setPosition(0)
    def shutdown(self):
        # QObject ownership releases the backend through deferred window deletion.
        self.timer.stop();self.player.pause()
    def toggle(self):
        if self.player.playbackState()==QMediaPlayer.PlayingState:self.player.pause()
        else:self.player.play()
    @Slot(int)
    def duration_changed(self,duration):self.seek.setRange(0,duration)
    @Slot(QMediaPlayer.Error,str)
    def media_error(self,error,message):self.label.setText('Playback error: '+message)
    @Slot(int)
    def position_changed(self,position):
        if not self.seek.isSliderDown():self.seek.setValue(position)
        self.tick()
    def tick(self):
        if not self.isVisible():return
        self.highway.position=self.player.position()/1000;self.highway.update()
    def highlight(self,value):self.highway.highlight=value;self.highway.update()
    def shift_changed(self,value):self.highway.shift=value/1000;self.highway.update()
    def set_chart(self,song,difficulty):
        if self.current and self.current[0] is song and self.current[1]==difficulty:return
        self.current=(song,difficulty) if song else None
        self.undo_stack=[];self.redo_stack=[];self.shift.setValue(0);self.rebuild()
    def rebuild(self,*args):
        self.highway.notes=timeline(*self.current,self.threshold.value()) if self.current else []
        self.highway.update();self.update_busy(self.owner.busy(),False)
    def update_busy(self,busy,cancellable):
        self.open_button.setEnabled(not busy)
        self.apply_button.setEnabled(not busy and self.owner.converted is not None)
        self.undo_button.setEnabled(not busy and bool(self.undo_stack));self.redo_button.setEnabled(not busy and bool(self.redo_stack))
    def snapshot(self):return (self.owner.converted,copy.deepcopy(self.owner.report))
    def publish(self,snapshot):
        # Keep history across our own refresh; unrelated conversions clear it.
        undo,redo=self.undo_stack,self.redo_stack
        self.owner.converted,self.owner.report=snapshot
        self.owner.variants={};self.owner.variant_choice.blockSignals(True);self.owner.variant_choice.setCurrentIndex(0);self.owner.variant_choice.blockSignals(False)
        self.owner.refresh_preview();self.undo_stack,self.redo_stack=undo,redo
        self.shift.setValue(0);self.owner.update_buttons()
    def apply_shift(self):
        if self.owner.busy() or self.owner.converted is None or self.shift.value()==0:return
        try:
            changed=shift_timing(self.owner.converted,self.shift.value());report=copy.deepcopy(self.owner.report)
            report.setdefault('timing_edits_ms',[]).append(self.shift.value());report['warnings']=list(dict.fromkeys(report.get('warnings',[])+ensure_valid(changed,True)['warnings']))
            report['timing']='Explicit seconds-based shift; tempo/meter retained; note/phrase endpoints rounded to ticks'
            self.undo_stack.append(self.snapshot());self.redo_stack=[];self.publish((changed,report))
            self.status.setText('Shift applied to the output working copy. Export to a new folder; Undo restores exact previous ticks.')
        except Exception as exc:self.status.setText(str(exc))
    def undo(self):
        if self.undo_stack and not self.owner.busy():
            previous=self.undo_stack.pop();self.redo_stack.append(self.snapshot());self.publish(previous)
    def redo(self):
        if self.redo_stack and not self.owner.busy():
            next_value=self.redo_stack.pop();self.undo_stack.append(self.snapshot());self.publish(next_value)
