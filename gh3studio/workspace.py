"""Focused chart workflows; delegates musical edits to existing tested services."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget,QLabel,QVBoxLayout,QHBoxLayout,QPushButton,
    QComboBox,QCheckBox,QScrollArea,QFrame,QSizePolicy)
from .appearance import primary


class StepStrip(QWidget):
    def __init__(self,steps):
        super().__init__();row=QHBoxLayout(self);row.setContentsMargins(0,0,0,0);row.setSpacing(8);self.labels=[]
        for i,text in enumerate(steps,1):
            label=QLabel(f'{i:02d}  {text}');label.setWordWrap(True);label.setObjectName('step');row.addWidget(label,1);self.labels.append(label)
        self.set_step(0)
    def set_step(self,index):
        for i,label in enumerate(self.labels):
            label.setProperty('active',i==index);label.setProperty('complete',i<index)
            label.style().unpolish(label);label.style().polish(label)


def heading(title,subtitle):
    frame=QWidget();layout=QVBoxLayout(frame);layout.setContentsMargins(0,0,0,0);layout.setSpacing(4)
    label=QLabel(title);label.setObjectName('pageTitle');label.setWordWrap(True);layout.addWidget(label)
    label=QLabel(subtitle);label.setObjectName('muted');label.setWordWrap(True);layout.addWidget(label)
    return frame


class AdaptPanel(QWidget):
    def __init__(self,owner):
        super().__init__();self.owner=owner;self.loaded_song=None
        outer=QVBoxLayout(self);outer.setContentsMargins(18,14,18,14);outer.setSpacing(10)
        outer.addWidget(heading('Four frets. Keep the challenge.',
            'Copy an authored Expert or Hard track into Medium. Keep the rhythm; reduce the buttons.'))
        self.steps=StepStrip(['Choose chart','Create Medium','Listen & export']);outer.addWidget(self.steps)
        self.scroll=QScrollArea();self.scroll.setWidgetResizable(True);outer.addWidget(self.scroll,1)
        body=QWidget();self.body=QVBoxLayout(body);self.body.setContentsMargins(0,0,8,0);self.body.setSpacing(10);self.scroll.setWidget(body)
        row=QHBoxLayout();self.body.addLayout(row)
        self.open_button=QPushButton('Choose chart…');self.open_button.clicked.connect(lambda:owner.start_guided('orange'));row.addWidget(self.open_button)
        self.identity=QLabel('No chart selected');self.identity.setWordWrap(True);self.identity.setObjectName('songTitle');row.addWidget(self.identity,1)
        row=QHBoxLayout();self.body.addLayout(row)
        row.addWidget(QLabel('Copy from'));self.source=QComboBox();self.source.setMinimumContentsLength(7);row.addWidget(self.source)
        arrow=QLabel('→  Medium · Green / Red / Yellow / Blue');arrow.setWordWrap(True);row.addWidget(arrow,1)
        self.create_button=QPushButton('Create four-fret Medium');primary(self.create_button);self.create_button.clicked.connect(self.create_medium);row.addWidget(self.create_button)
        self.preserve=QCheckBox('Keep Orange sustains on playable frets');self.preserve.setChecked(True)
        self.preserve.setToolTip('Use repeatable random placement among suitable frets. Orange taps are removed; sustain conflicts are reported before export.')
        self.body.addWidget(self.preserve)
        self.summary=QLabel('Choose a chart to see its available source difficulties.');self.summary.setWordWrap(True);self.summary.setObjectName('muted');self.body.addWidget(self.summary)
        self.preview_host=QVBoxLayout();self.body.addLayout(self.preview_host,1)
        self.next_step=QLabel('Choose an existing .chart or game-chart MIDI file to begin.');self.next_step.setWordWrap(True);self.next_step.setObjectName('nextStep');outer.addWidget(self.next_step)
        row=QHBoxLayout();outer.addLayout(row)
        self.restore_button=QPushButton('Review source');self.restore_button.clicked.connect(self.review_source);row.addWidget(self.restore_button)
        self.output_preview=QPushButton('Review Medium');self.output_preview.clicked.connect(self.review_output);row.addWidget(self.output_preview)
        self.open_output=QPushButton('Open exported folder');self.open_output.clicked.connect(owner.audio.open_export_folder);row.addWidget(self.open_output)
        self.export_button=QPushButton('Review / export song…');primary(self.export_button);self.export_button.clicked.connect(owner.start_export);row.addWidget(self.export_button,1)
        self.source.currentTextChanged.connect(self.review_source)
    def attach_preview(self):
        self.preview_host.addWidget(self.owner.playback)
        self.owner.playback.set_focused(True);self.owner.playback.show()
        self.update_state()
    def review_source(self,*args):
        if self.owner.busy() or not self.owner.song:return
        # Compare against the loaded chart without changing the prepared output.
        self.owner.playback.set_chart(self.owner.song,self.source.currentText())
    def review_output(self):
        if not self.owner.busy() and self.owner.converted:self.owner.playback.set_chart(self.owner.converted,'Medium')
    def create_medium(self):
        if self.owner.busy() or not self.owner.song or not self.source.currentText():return
        self.owner.goal='orange';self.owner.playback.orange_sustains.setChecked(self.preserve.isChecked())
        self.owner.playback.remove_orange(source=(self.owner.song,self.source.currentText()))
    def update_state(self):
        song=self.owner.song;busy=self.owner.busy();output=self.owner.converted;report=self.owner.report or {}
        if self.loaded_song is not song:
            self.loaded_song=song;self.source.blockSignals(True);self.source.clear()
            self.source.addItems([d for d in ('Expert','Hard') if song and song.tracks.get(d)])
            self.source.blockSignals(False)
        if song:
            self.identity.setText(song.metadata.get('Name','Untitled')+'  •  '+song.metadata.get('Artist','Unknown artist'))
            self.identity.setToolTip(str(self.owner.path or ''))
        else:self.identity.setText('No chart selected')
        for widget in (self.open_button,self.source,self.preserve):widget.setEnabled(not busy)
        self.create_button.setEnabled(not busy and self.source.count()>0)
        self.restore_button.setEnabled(not busy and song is not None)
        self.export_button.setEnabled(not busy and output is not None)
        self.output_preview.setEnabled(not busy and output is not None)
        self.open_output.setVisible(self.owner.last_export_path is not None);self.open_output.setEnabled(not busy)
        self.steps.set_step(2 if output else 1 if song else 0)
        if busy:return  # Preserve operation/error text while a worker runs.
        if output:
            notes=output.tracks.get('Medium',[]);events=len({n.tick for n in notes});sustains=sum(n.length>0 for n in notes)
            self.summary.setText(f'Medium from {report.get("source_difficulty","draft")}: {events:,} note events · {len(notes):,} fret gems · {sustains:,} sustains · {sum(n.lane==4 for n in notes)} Orange')
            self.next_step.setText('Export complete. Open the song folder for import testing.' if self.owner.last_export_path else
                'Medium is prepared. Compare tracks below, listen, then review metadata and compatibility before export.')
        elif song:
            self.summary.setText('Source file stays untouched. Orange taps are removed; surviving notes keep their timing. No automatic density reduction.')
            self.next_step.setText('Choose Expert or Hard, then Create four-fret Medium.' if self.source.count() else
                'This chart has no Expert or Hard notes. Use Clean songs to prepare its existing difficulties.')
