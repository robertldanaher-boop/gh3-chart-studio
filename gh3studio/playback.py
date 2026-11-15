"""Audio-clock-driven chart review. This is not a gameplay engine."""
import copy
from pathlib import Path
from PySide6.QtCore import Qt, QUrl, QTimer, Slot
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput, QMediaDevices
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QPushButton,QLabel,QSlider,QDoubleSpinBox,QCheckBox,QFileDialog,QComboBox,QScrollArea
from .editing import timeline,shift_timing,remove_orange_to_medium
from .validation import ensure_valid

class Highway(QWidget):
    """Horizontal lanes matching the converter; notes scroll toward a playhead."""
    def __init__(self):
        super().__init__();self.notes=[];self.position=0.;self.shift=0.;self.highlight=True;self.setMinimumHeight(220)
    def note_geometry(self,note,lanes=None):
        start,end,lane,_=note
        if lanes is None:lanes=5 if any(n[2]==4 for n in self.notes) else 4
        hit=90;scale=max(1,(self.width()-hit-20)/6)
        y=35+lane*max(1,(self.height()-65)/max(1,lanes-1))
        return hit+(start+self.shift-self.position)*scale,hit+(end+self.shift-self.position)*scale,y
    def paintEvent(self,event):
        p=QPainter(self);p.fillRect(self.rect(),QColor('#101722'))
        colors=['#4cd964','#ef5350','#ffe066','#42a5f5','#ff9800']
        lanes=5 if any(n[2]==4 for n in self.notes) else 4
        width=self.width();height=self.height();scale=max(1,(width-110)/6)
        for lane in range(lanes):
            y=35+lane*max(1,(height-65)/max(1,lanes-1))
            p.setPen(QPen(QColor('#344356'),1));p.drawLine(40,int(y),width,int(y))
            p.setPen(QColor(colors[lane]));p.drawText(8,int(y)+5,'GRYBO'[lane])
        for second in range(max(0,int(self.position)-1),int(self.position)+8):
            x=90+(second-self.position)*scale
            if x<40 or x>width:continue
            p.setPen(QPen(QColor('#263346'),1));p.drawLine(int(x),25,int(x),height-18)
            p.setPen(QColor('#c6d4e3'));p.drawText(int(x)+3,16,f'{second}s')
        p.setPen(QPen(QColor('white'),2));p.drawLine(90,22,90,height-15)
        for note in self.notes:
            x,tail,y=self.note_geometry(note,lanes);lane=note[2];hopo=note[3]
            if tail<40 or x>width:continue
            p.setPen(QPen(QColor(colors[lane]),4))
            if tail>x:p.drawLine(int(max(40,x)),int(y),int(min(width,tail)),int(y))
            if 40<=x<=width:
                p.setBrush(QColor(colors[lane]));p.setPen(QPen(QColor('white') if hopo and self.highlight else QColor('#111111'),2))
                p.drawEllipse(int(x)-7,int(y)-7,14,14)
        p.end()

class PlaybackPanel(QWidget):
    def __init__(self,owner):
        super().__init__();self.owner=owner;self.current=None;self.undo_stack=[];self.redo_stack=[];self.pending_play=False;self.audio_name=""
        self.player=QMediaPlayer(self);self.output=QAudioOutput(self);self.player.setAudioOutput(self.output);self.output.setVolume(.7)
        outer=QVBoxLayout(self);scroll=QScrollArea();scroll.setWidgetResizable(True);outer.addWidget(scroll)
        body=QWidget();scroll.setWidget(body);layout=QVBoxLayout(body)
        hint=QLabel('Listen and compare. Notes move left toward the white playhead. White outlines mark estimated HOPO candidates, including exported flips—not guaranteed no-strum notes.\nNo chart is needed to play audio. Create an audio draft or convert a chart to preview and export notes.')
        self.hint=hint;hint.setWordWrap(True);layout.addWidget(hint)
        row=QHBoxLayout();layout.addLayout(row)
        self.chart_open=QPushButton('Open chart…');self.chart_open.clicked.connect(owner.browse);row.addWidget(self.chart_open)
        row.addWidget(QLabel('Display / copy source'))
        self.difficulty=QComboBox();self.difficulty.currentTextChanged.connect(self.select_difficulty);row.addWidget(self.difficulty)
        self.orange_button=QPushButton('Remove Orange → Medium');self.orange_button.clicked.connect(self.remove_orange);row.addWidget(self.orange_button)
        note=QLabel('Choose Hard or Expert above. Copies the displayed track minus Orange to Medium; source tracks stay unchanged.');note.setWordWrap(True);row.addWidget(note,1)
        self.orange_sustains=QCheckBox('Move Orange sustains to Blue (button 4) before removing Orange')
        self.orange_sustains.setToolTip('Preserves Orange sustain timing on Blue. Simultaneous Blue uses the longer sustain. Overlaps require review; Orange taps are removed.')
        layout.addWidget(self.orange_sustains)
        self.provenance=QLabel();layout.addWidget(self.provenance)
        row=QHBoxLayout();layout.addLayout(row)
        self.open_button=QPushButton('Choose preview audio…');self.open_button.clicked.connect(self.browse);row.addWidget(self.open_button)
        self.play_button=QPushButton('Play preview audio');self.play_button.clicked.connect(self.toggle);row.addWidget(self.play_button)
        stop=QPushButton('Stop');stop.clicked.connect(self.stop);row.addWidget(stop)
        self.label=QLabel('No audio selected — choose the matching recording');self.label.setWordWrap(True);row.addWidget(self.label,1)
        row=QHBoxLayout();layout.addLayout(row)
        row.addWidget(QLabel('Audio output'))
        self.devices=QComboBox();row.addWidget(self.devices,1)
        self.device_monitor=QMediaDevices(self)
        self.device_monitor.audioOutputsChanged.connect(self.refresh_devices,Qt.QueuedConnection)
        self.devices.currentIndexChanged.connect(self.select_device)
        self.refresh_devices()
        self.media_status=QLabel('No recording loaded');self.media_status.setWordWrap(True);row.addWidget(self.media_status,1)
        row=QHBoxLayout();layout.addLayout(row)
        row.addWidget(QLabel('Volume'));volume=QSlider(Qt.Horizontal);volume.setRange(0,100);volume.setValue(70);volume.valueChanged.connect(lambda v:self.output.setVolume(v/100));row.addWidget(volume)
        self.seek=QSlider(Qt.Horizontal);self.seek.setRange(0,0);self.seek.sliderMoved.connect(self.player.setPosition);layout.addWidget(self.seek)
        self.player.durationChanged.connect(self.duration_changed,Qt.QueuedConnection)
        self.player.positionChanged.connect(self.position_changed,Qt.QueuedConnection)
        self.player.errorOccurred.connect(self.media_error,Qt.QueuedConnection)
        self.player.mediaStatusChanged.connect(self.media_changed,Qt.QueuedConnection)
        self.player.playbackStateChanged.connect(self.playback_changed,Qt.QueuedConnection)
        self.highway=Highway();layout.addWidget(self.highway,1)
        row=QHBoxLayout();layout.addLayout(row)
        self.hopo=QCheckBox('Highlight estimated HOPOs');self.hopo.setChecked(True);self.hopo.toggled.connect(self.highlight);row.addWidget(self.hopo)
        row.addWidget(QLabel('Candidate gap ≤ beats'));self.threshold=QDoubleSpinBox();self.threshold.setDecimals(4);self.threshold.setRange(.01,1);self.threshold.setValue(1/3);self.threshold.valueChanged.connect(self.rebuild);row.addWidget(self.threshold)
        row=QHBoxLayout();layout.addLayout(row)
        row.addWidget(QLabel('Preview shift (ms; + = notes later)'));self.shift=QDoubleSpinBox();self.shift.setRange(-10000,10000);self.shift.setDecimals(1);self.shift.valueChanged.connect(self.shift_changed);row.addWidget(self.shift)
        self.apply_button=QPushButton('Apply shift to output');self.apply_button.clicked.connect(self.apply_shift);row.addWidget(self.apply_button)
        self.undo_button=QPushButton('Undo shift');self.undo_button.clicked.connect(self.undo);row.addWidget(self.undo_button)
        self.redo_button=QPushButton('Redo shift');self.redo_button.clicked.connect(self.redo);row.addWidget(self.redo_button)
        self.status=QLabel('Timing preview uses the media playback clock. Device latency still needs listening checks.');self.status.setWordWrap(True);layout.addWidget(self.status)
        self.timer=QTimer(self);self.timer.setInterval(33);self.timer.timeout.connect(self.tick);self.timer.start()
        self.update_busy(False,False)
    def refresh_devices(self):
        previous=self.devices.currentData()
        self.devices.blockSignals(True);self.devices.clear();self.devices.addItem('Windows / system default',None)
        for device in QMediaDevices.audioOutputs():self.devices.addItem(device.description(),bytes(device.id()))
        index=self.devices.findData(previous);self.devices.setCurrentIndex(max(0,index));self.devices.blockSignals(False)
        self.select_device()
    def select_device(self,*args):
        identity=self.devices.currentData()
        device=next((d for d in QMediaDevices.audioOutputs() if bytes(d.id())==identity),QMediaDevices.defaultAudioOutput())
        if self.output.device().id()!=device.id():self.output.setDevice(device)
    def clear_audio(self):
        self.pending_play=False;self.audio_name='';self.player.pause();self.player.setSource(QUrl())
        self.label.setText('No audio selected — click Play to choose the matching recording')
        self.media_status.setText('No recording loaded');self.play_button.setText('Play preview audio')
    def browse(self):
        path,_=QFileDialog.getOpenFileName(self,'Choose matching recording','','Audio (*.wav *.flac *.ogg *.mp3 *.opus)')
        return self.open_audio(path) if path else False
    def open_audio(self,path):
        path=Path(path).resolve()
        if not path.is_file():
            self.clear_audio();self.label.setText('Audio file not found: '+str(path));self.owner.log_line(self.label.text());return False
        self.pending_play=False;self.audio_name=path.name
        self.player.pause();self.player.setSource(QUrl.fromLocalFile(str(path)));self.label.setText(str(path))
        self.media_status.setText('Loading recording…');self.owner.log_line('Preview audio selected: '+str(path))
        return True
    def play(self):
        if self.player.source().isEmpty() and not self.browse():return
        self.select_device()
        if self.output.device().isNull():
            self.media_status.setText('No audio output device detected. Connect/select speakers or headphones.')
            self.owner.log_line(self.media_status.text())
        status=self.player.mediaStatus()
        if status==QMediaPlayer.InvalidMedia:
            self.pending_play=False;self.media_error(self.player.error(),self.player.errorString());return
        self.pending_play=status==QMediaPlayer.LoadingMedia
        if not self.pending_play:self.player.play()
    @Slot(QMediaPlayer.MediaStatus)
    def media_changed(self,status):
        if status in (QMediaPlayer.LoadedMedia,QMediaPlayer.BufferedMedia):
            if self.pending_play:self.pending_play=False;self.player.play()
            if not self.output.device().isNull():self.media_status.setText('Recording loaded — '+str(round(self.player.duration()/1000,1))+' seconds')
        elif status==QMediaPlayer.StalledMedia:self.media_status.setText('Audio playback stalled; see diagnostic log.')
        elif status==QMediaPlayer.InvalidMedia:self.media_error(self.player.error(),self.player.errorString())
        self.owner.log_line('Preview media status: '+status.name)
    @Slot(QMediaPlayer.PlaybackState)
    def playback_changed(self,state):
        self.play_button.setText('Pause preview audio' if state==QMediaPlayer.PlayingState else 'Play preview audio')
        device=self.output.device()
        self.owner.log_line(f'Preview {state.name}; output={device.description() or "NONE"}; volume={self.output.volume():.0%}; muted={self.output.isMuted()}')
    def stop(self):
        # Pause and rewind avoids Qt 6.8 FFmpeg stop/seek lock contention.
        self.pending_play=False;self.player.pause();self.player.setPosition(0)
    def shutdown(self):
        # QObject ownership releases the backend through deferred window deletion.
        self.timer.stop();self.player.pause()
    def toggle(self):
        if self.player.playbackState()==QMediaPlayer.PlayingState:self.pending_play=False;self.player.pause()
        else:self.play()
    @Slot(int)
    def duration_changed(self,duration):self.seek.setRange(0,duration)
    @Slot(QMediaPlayer.Error,str)
    def media_error(self,error,message):
        self.pending_play=False
        text='Playback error: '+(message or str(error))+'. Try a WAV/OGG copy and check the audio output selection.'
        self.media_status.setText(text);self.owner.log_line(text)
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
        available=[d for d in ('Expert','Hard','Medium','Easy') if song and song.tracks.get(d)]
        self.difficulty.blockSignals(True);self.difficulty.clear();self.difficulty.addItems(available)
        self.difficulty.setCurrentText(difficulty if difficulty in available else (available[0] if available else ''))
        self.difficulty.blockSignals(False)
        self.current=(song,self.difficulty.currentText()) if song else None
        self.undo_stack=[];self.redo_stack=[];self.shift.setValue(0);self.rebuild()
    def select_difficulty(self,difficulty):
        if self.current and difficulty:
            self.current=(self.current[0],difficulty);self.rebuild()
    def remove_orange(self):
        if self.owner.busy() or not self.current:return
        song,difficulty=self.current
        transfer_sustains=self.orange_sustains.isChecked()
        self.owner.converted=None;self.owner.report=None;self.rebuild()
        self.status.setText(f'Creating Medium from displayed {difficulty}…')
        def ready(value):
            self.owner.converted,self.owner.report=value
            self.owner.variants={};self.owner.variant_choice.blockSignals(True);self.owner.variant_choice.setCurrentIndex(0);self.owner.variant_choice.blockSignals(False)
            self.owner.refresh_preview();self.owner.log_line(str(self.owner.report))
            self.status.setText(f"Removed {self.owner.report['removed_orange_gems']} Orange gems; transferred {self.owner.report.get('transferred_orange_sustains',0)} sustains to Blue. Medium is ready for export checks; Expert/Hard were not edited.")
            self.owner.audio.show_listen()
        self.owner.run_job('Copying selected difficulty without Orange…',lambda cancel:remove_orange_to_medium(song,difficulty,strict=False,orange_sustains_to_blue=transfer_sustains),ready)
    def rebuild(self,*args):
        report=self.owner.report or {}
        if self.current:
            diff=self.current[1]
            label=f'Displaying {diff}'
            if self.current[0] is self.owner.converted and diff=='Medium':
                label+=f" — OUTPUT copied from {report.get('source_difficulty','generated chart')} | Orange: {sum(n.lane==4 for n in self.current[0].tracks.get(diff,[]))}"
                if report.get('transferred_orange_sustains'):label+=f" | {report['transferred_orange_sustains']} Orange sustains → Blue"
                elif report.get('retained_notes_exact'):label+=' | all surviving notes unchanged'
            else:label+=' — source track'
            self.provenance.setText(label)
        else:self.provenance.setText('No chart loaded')
        profile=(self.owner.report or {}).get('hopo_assistance') if self.current and self.current[0] is self.owner.converted and self.current[1]=='Medium' else None
        self.threshold.setEnabled(not bool(profile))
        threshold=1/profile['importer_hopo_measure'] if profile else self.threshold.value()
        self.highway.notes=timeline(*self.current,threshold) if self.current else []
        self.highway.update();self.update_busy(self.owner.busy(),False)
    def update_busy(self,busy,cancellable):
        self.orange_sustains.setEnabled(not busy)
        self.open_button.setEnabled(not busy)
        self.chart_open.setEnabled(not busy)
        self.difficulty.setEnabled(not busy and self.current is not None)
        self.orange_button.setEnabled(not busy and self.current is not None and self.difficulty.currentText() in ('Expert','Hard','Medium','Easy'))
        self.apply_button.setEnabled(not busy and self.owner.converted is not None)
        self.undo_button.setEnabled(not busy and bool(self.undo_stack));self.redo_button.setEnabled(not busy and bool(self.redo_stack))
    def snapshot(self):return (self.owner.converted,copy.deepcopy(self.owner.report))
    def publish(self,snapshot):
        # Keep history across our own refresh; unrelated conversions clear it.
        undo,redo=self.undo_stack,self.redo_stack
        self.owner.last_export_path=None
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
