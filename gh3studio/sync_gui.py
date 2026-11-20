"""Per-song timing review; never alters source media or the main conversion state."""
import copy
from pathlib import Path
import soundfile as sf
from PySide6.QtCore import Qt,QUrl,QTimer
from PySide6.QtMultimedia import QMediaPlayer,QAudioOutput,QMediaDevices
from PySide6.QtWidgets import (QDialog,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,
    QDoubleSpinBox,QPushButton,QCheckBox,QSlider,QScrollArea,QWidget)
from .playback import Highway
from .synchronization import normalize
from .window_fit import fit_size


class SynchronizationDialog(QDialog):
    def __init__(self,row,parent=None):
        super().__init__(parent);self.setWindowTitle('Review synchronization');fit_size(self,940,660)
        self.row=row;self.song=row['sync_source'];self.review=None;self.plan=None
        self.rate=sf.info(row['audio']).samplerate
        outer=QVBoxLayout(self)
        title=QLabel('Review synchronization · '+row['metadata'].get('Name',Path(row['path']).stem));title.setWordWrap(True);outer.addWidget(title)
        scroll=QScrollArea();scroll.setWidgetResizable(True);outer.addWidget(scroll,1)
        body=QWidget();scroll.setWidget(body);layout=QVBoxLayout(body)
        def label(text):
            value=QLabel(text);value.setWordWrap(True);layout.addWidget(value);return value
        values=row['sync_values']
        label(f"1 · Stored timing: chart Offset = {values['offset_seconds']:g} seconds; song.ini delay = {values['delay_ms']:g} ms.")
        label('Choose the intended timing, then listen. Different source tools may handle these fields differently. Both values are shown; they are never added automatically. Positive shift = notes later relative to the recording. Negative = notes earlier.')
        self.mode=QComboBox();self.mode.setMinimumContentsLength(20);self.mode.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        self.mode.addItems(['Choose timing interpretation…','Use song.ini delay','Use chart Offset × 1000 as notes shift','Use opposite chart Offset as notes shift','Custom total shift (including any offsets)'])
        layout.addWidget(self.mode)
        line=QHBoxLayout();layout.addLayout(line);line.addWidget(QLabel('Total notes shift (ms)'))
        self.shift=QDoubleSpinBox();self.shift.setRange(-60000,60000);self.shift.setDecimals(3);self.shift.setSingleStep(10);self.shift.setEnabled(False);line.addWidget(self.shift)
        label('2 · Listen and compare near the beginning, middle and end. A constant shift cannot repair drift or a different recording.')
        self.difficulty=QComboBox();self.difficulty.addItems([d for d in ('Expert','Hard','Medium','Easy') if self.song.tracks.get(d)]);layout.addWidget(self.difficulty)
        self.player=QMediaPlayer(self);self.output=QAudioOutput(self);self.player.setAudioOutput(self.output);self.output.setVolume(.7)
        self.devices=QComboBox();self.devices.setMinimumContentsLength(18);self.devices.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        self.devices.setPlaceholderText('No audio output detected')
        devices=QMediaDevices.audioOutputs()
        for device in devices:self.devices.addItem(device.description(),device)
        default=QMediaDevices.defaultAudioOutput()
        for i,device in enumerate(devices):
            if device.id()==default.id():self.devices.setCurrentIndex(i)
        self.devices.currentIndexChanged.connect(self.select_device);self.select_device();label('Audio output');layout.addWidget(self.devices)
        self.highway=Highway();self.highway.setMinimumHeight(140);self.highway.highlight=False;layout.addWidget(self.highway)
        self.seek=QSlider(Qt.Horizontal);self.seek.setRange(0,0);self.seek.sliderMoved.connect(self.player.setPosition);layout.addWidget(self.seek)
        line=QHBoxLayout();layout.addLayout(line)
        self.play=QPushButton('Play / pause');self.play.clicked.connect(self.toggle);line.addWidget(self.play)
        stop=QPushButton('Stop');stop.clicked.connect(self.player.stop);line.addWidget(stop)
        self.clock=QLabel('0.0 s');line.addWidget(self.clock)
        volume=QSlider(Qt.Horizontal);volume.setRange(0,100);volume.setValue(70);volume.valueChanged.connect(lambda v:self.output.setVolume(v/100));line.addWidget(QLabel('Volume'));line.addWidget(volume)
        self.media_status=label('Preview uses the original recording clock. Export may add a shared lead-in; no source audio is trimmed.')
        self.outcome=label('Choose a timing interpretation to see the proposed export changes.')
        self.anchor_confirm=QCheckBox('Keep existing BPM map; discard editor anchors')
        self.anchor_conflicts=[a for a in row.get('anchor_checks',[]) if a['needs_review']]
        if row.get('anchor_checks'):
            label('Editor anchors are not playable notes. BPM timing is used in this preview. No tempo is inferred from anchors.')
            for anchor in row['anchor_checks'][:12]:
                label(f"Anchor tick {anchor['tick']}: stored {anchor['anchor_microseconds']/1000000:.6f} s; BPM map {anchor['bpm_map_seconds']:.6f} s; difference {anchor['difference_ms']:+.3f} ms.")
            if len(row['anchor_checks'])>12:label('More anchors are listed in the selected-song changes and export report.')
        layout.addWidget(self.anchor_confirm);self.anchor_confirm.setVisible(bool(self.anchor_conflicts))
        self.anchor_confirm.toggled.connect(self.update_apply)
        self.confirm=QCheckBox('I checked the beginning, middle and end')
        # Keep long confirmation text in the scrollable body rather than widening the dialog.
        layout.addWidget(self.confirm)
        line=QHBoxLayout();outer.addLayout(line)
        cancel=QPushButton('Cancel');cancel.clicked.connect(self.reject);line.addWidget(cancel)
        self.apply=QPushButton('Use reviewed timing');self.apply.setObjectName('primaryAction');self.apply.setEnabled(False);self.apply.clicked.connect(self.accept_review);line.addWidget(self.apply)
        self.mode.currentIndexChanged.connect(self.mode_changed);self.shift.valueChanged.connect(self.changed)
        self.difficulty.currentTextChanged.connect(self.preview_notes);self.confirm.toggled.connect(self.update_apply)
        self.player.positionChanged.connect(self.position_changed);self.player.durationChanged.connect(lambda value:self.seek.setRange(0,value))
        self.player.errorOccurred.connect(lambda *args:self.media_status.setText('Playback error: '+self.player.errorString()+'. Check the selected audio output and recording.'))
        self.player.setSource(QUrl.fromLocalFile(str(Path(row['audio']).resolve())))
        self.timer=QTimer(self);self.timer.setInterval(33)
        self.timer.timeout.connect(self.tick);self.timer.start()
        self.preview_notes()
        if row.get('sync_review'):
            self.mode.setCurrentIndex(4);self.shift.setValue(row['sync_review']['shift_ms'])
        elif row.get('synchronization',{}).get('automatic'):
            self.mode.setCurrentIndex(1)
        self.finished.connect(self.stop_media)
    def select_device(self,*args):
        if self.devices.currentData() is not None:self.output.setDevice(self.devices.currentData())
    def toggle(self):
        if self.player.playbackState()==QMediaPlayer.PlayingState:self.player.pause()
        else:self.player.play()
    def tick(self):
        if self.player.playbackState()==QMediaPlayer.PlayingState:self.position_changed(self.player.position())
    def stop_media(self,*args):
        self.timer.stop();self.player.stop();self.player.setSource(QUrl())
    def position_changed(self,value):
        self.highway.position=value/1000;self.highway.update();self.clock.setText(f'{value/1000:.1f} s')
        if not self.seek.isSliderDown():self.seek.setValue(value)
    def mode_changed(self,index):
        values=self.row['sync_values'];self.shift.setEnabled(index==4)
        preset={1:values['delay_ms'],2:values['offset_seconds']*1000,3:-values['offset_seconds']*1000}
        if index in preset:
            value=preset[index]
            if abs(value)>60000:
                self.mode.setCurrentIndex(0);self.outcome.setText('Stored timing exceeds ±60 seconds. Review this source externally.');return
            self.shift.setValue(value)
        self.changed()
    def preview_notes(self,*args):
        self.highway.notes=[(self.song.seconds(n.tick),self.song.seconds(n.tick+n.length),n.lane,False)
                            for n in self.song.tracks.get(self.difficulty.currentText(),[])]
        self.highway.shift=self.shift.value()/1000;self.highway.update()
    def changed(self,*args):
        self.confirm.setChecked(False);self.plan=None;self.preview_notes()
        if self.mode.currentIndex():
            try:
                _,self.plan=normalize(self.song,self.shift.value(),self.rate)
                p=self.plan
                self.outcome.setText(f"3 · Export: notes shift {p['effective_shift_ms']:+.3f} ms relative to the recording. Chart lead-in {p['chart_lead_seconds']:.3f} s; audio silence {p['audio_padding_seconds']:.3f} s. Offset and delay become zero. All chart objects and tempo changes move together; note lengths stay intact. Existing cleanup repairs are separate. Original files stay untouched.")
            except Exception as exc:self.outcome.setText(str(exc))
        else:self.outcome.setText('Choose a timing interpretation to see the proposed export changes.')
        self.update_apply()
    def update_apply(self,*args):self.apply.setEnabled(self.plan is not None and self.confirm.isChecked() and (not self.anchor_conflicts or self.anchor_confirm.isChecked()))
    def accept_review(self):
        if not self.apply.isEnabled():return
        self.review={'shift_ms':self.shift.value(),'source_hashes':copy.deepcopy(self.row['hashes']),
                     'chart_path':self.row['path'],'audio_path':self.row['audio'],'accept_anchor_map':self.anchor_confirm.isChecked()}
        self.accept()
