"""Focused chart workflows; delegates musical edits to existing tested services."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget,QLabel,QVBoxLayout,QHBoxLayout,QPushButton,
    QComboBox,QCheckBox,QScrollArea,QFrame,QSizePolicy,QGridLayout,QStackedWidget)
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
        outer.addWidget(heading('Prepare your song.',
            'Create Medium + Easy and clean all four difficulties in one step.'))
        self.steps=StepStrip(['Choose songs','Prepare & review','Export']);outer.addWidget(self.steps)
        self.scroll=QScrollArea();self.scroll.setWidgetResizable(True);outer.addWidget(self.scroll,1)
        body=QWidget();self.body=QVBoxLayout(body);self.body.setContentsMargins(0,0,8,0);self.body.setSpacing(10);self.scroll.setWidget(body)
        row=QHBoxLayout();self.body.addLayout(row)
        self.open_button=QPushButton('Choose chart…');self.open_button.clicked.connect(lambda:owner.start_guided('orange'));
        self.identity=QLabel('No chart selected');self.identity.setWordWrap(True);self.identity.setObjectName('songTitle');row.addWidget(self.identity,1)
        row=QHBoxLayout();self.body.addLayout(row)
        row.addWidget(QLabel('Copy from'));self.source=QComboBox();self.source.setMinimumContentsLength(7);row.addWidget(self.source)
        arrow=QLabel('→  Medium · Green / Red / Yellow / Blue');arrow.setWordWrap(True);row.addWidget(arrow,1)
        self.create_button=QPushButton('Prepare song');primary(self.create_button);self.create_button.clicked.connect(self.create_medium);row.addWidget(self.create_button)
        self.preserve=QCheckBox('Keep Orange sustains on playable frets');self.preserve.setChecked(True)
        self.preserve.setToolTip('Use repeatable random placement among suitable frets. Orange taps are removed; sustain conflicts are reported before export.')
        self.body.addWidget(self.preserve)
        self.summary=QLabel('Choose a chart to see its available source difficulties.');self.summary.setWordWrap(True);self.summary.setObjectName('muted');self.body.addWidget(self.summary)
        self.preview_host=QVBoxLayout();self.body.addLayout(self.preview_host,1)
        self.next_step=QLabel('Choose an existing .chart or game-chart MIDI file to begin.');self.next_step.setWordWrap(True);self.next_step.setObjectName('nextStep');outer.addWidget(self.next_step)
        footer=QGridLayout();outer.addLayout(footer);footer.setColumnStretch(0,1);footer.setColumnStretch(1,1)
        self.restore_button=QPushButton('Review source');self.restore_button.clicked.connect(self.review_source);footer.addWidget(self.restore_button,0,0)
        self.output_preview=QPushButton('Review Medium');self.output_preview.clicked.connect(self.review_output);footer.addWidget(self.output_preview,0,1)
        self.open_output=QPushButton('Open exported folder');self.open_output.clicked.connect(owner.audio.open_export_folder);footer.addWidget(self.open_output,1,0)
        self.export_button=QPushButton('Review / export song…');primary(self.export_button);self.export_button.clicked.connect(owner.start_export);footer.addWidget(self.export_button,1,1)
        self.source.currentTextChanged.connect(self.review_source)
        # One workspace with two task views, no modal duplicate queue.
        single=QWidget();single.setLayout(outer)
        shell=QVBoxLayout(self);self.mode=QComboBox();self.mode.addItems(['One song','Collection'])
        mode_row=QHBoxLayout();shell.addLayout(mode_row);mode_row.addWidget(self.mode,1);mode_row.addWidget(self.open_button)
        self.folder_button=QPushButton('Choose folder…');self.folder_button.clicked.connect(lambda:owner.start_medium_collection())
        self.folder_button.setToolTip('Scan this folder and all nested song folders for four-fret conversion')
        mode_row.addWidget(self.folder_button)
        self.pages=QStackedWidget();shell.addWidget(self.pages)
        from .cleaner_gui import CleanerPanel
        self.bulk=CleanerPanel(owner,four_fret=True)
        self.bulk.scan_button.hide()  # Shared folder picker above serves both views.
        self.pages.addWidget(single);self.pages.addWidget(self.bulk)
        self.mode.currentIndexChanged.connect(self.pages.setCurrentIndex)

    def open_bulk(self):
        self.mode.setCurrentIndex(1)

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
        song=self.owner.song;busy=self.owner.busy();
        self.mode.setEnabled(not busy);self.folder_button.setEnabled(not busy)
        output=self.owner.converted;report=self.owner.report or {}
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
            if report.get('difficulty_completion'):
                self.summary.setText(self.summary.text()+f" · Easy: {len(output.tracks.get('Easy',[])):,} gems / 3 frets · all 4 difficulties populated")
            self.next_step.setText('Export complete. Open the song folder for import testing.' if self.owner.last_export_path else
                'Medium is prepared. Compare tracks below, listen, then review metadata and compatibility before export.')
        elif song:
            self.summary.setText('Original files stay untouched. All difficulties are cleaned; sustain repairs are reported. No automatic density reduction.')
            self.next_step.setText('Choose Expert or Hard, then Prepare song.' if self.source.count() else
                'This chart has no Expert or Hard notes. Use Clean songs to prepare its existing difficulties.')
