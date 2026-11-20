"""Interactive working-copy chart editor, using the existing audio clock."""
from pathlib import Path
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QPen, QKeySequence, QShortcut
from PySide6.QtWidgets import (QDialog,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,
    QComboBox,QSlider,QCheckBox,QMenu,QInputDialog,QFileDialog,QMessageBox)
from .playback import Highway
from .chart_editor import EditSession, check_editor_song
from .audio_chart import TempoClock
from .editing import timeline
from .model import ChartError
from .window_fit import fit_size


class EditHighway(Highway):
    def __init__(self, editor):
        super().__init__(); self.editor=editor; self.drag=None; self.ghost=None; self.setMinimumHeight(260)

    def lane_count(self):return 4 if self.editor.difficulty.currentText()=='Medium' else 5

    def note_geometry(self,note,lanes=None):return super().note_geometry(note,self.lane_count())

    def location(self, pos):
        e=self.editor; song=e.session.song
        seconds=max(0,self.position+(pos.x()-90)/max(1,(self.width()-110)/6))
        tick=TempoClock(song).tick(seconds); step=e.step()
        tick=max(0,round(tick/step)*step)
        lane=max(0,min(self.lane_count()-1,round((pos.y()-35)/max(1,(self.height()-65)/(self.lane_count()-1)))))
        return tick,lane

    def hit(self,pos):
        song=self.editor.session.song; diff=self.editor.difficulty.currentText()
        for note in reversed(song.tracks.get(diff,[])):
            x,tail,y=self.note_geometry((song.seconds(note.tick),song.seconds(note.tick+note.length),note.lane,False))
            if abs(pos.y()-y)<=12:
                if abs(pos.x()-x)<=10:return note,'move'
                if note.length and abs(pos.x()-tail)<=12:return note,'resize'
        return None,None

    def mousePressEvent(self,event):
        if event.button()==Qt.LeftButton:
            note,kind=self.hit(event.position())
            if note:
                self.editor.panel.player.pause(); self.drag=(note,kind);self.grabMouse()
                self.editor.status.setText('Drag note head to move; sustain tail to resize. Release to apply; invalid edits are rejected.')
        super().mousePressEvent(event)

    def mouseMoveEvent(self,event):
        if self.drag:
            tick,lane=self.location(event.position());note,kind=self.drag
            self.ghost=(tick if kind=='move' else note.tick,lane if kind=='move' else note.lane,note.length if kind=='move' else max(0,tick-note.tick));self.update()
            self.editor.status.setText(f'{kind.title()}: tick {tick}, fret {"GRYBO"[lane]}, sustain {max(0,tick-note.tick)} ticks. Release to apply.')
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self,event):
        if self.drag and event.button()==Qt.LeftButton:
            note,kind=self.drag;self.drag=None;self.ghost=None;self.releaseMouse()
            tick,lane=self.location(event.position())
            self.editor.edit(kind,note=note,tick=tick,lane=lane,length=max(0,tick-note.tick))
        super().mouseReleaseEvent(event)

    def contextMenuEvent(self,event):
        self.editor.panel.player.pause()
        tick,lane=self.location(event.pos());note,_=self.hit(event.pos())
        if note: tick,lane=note.tick,note.lane
        menu=QMenu(self)
        def add(label,action,**kw):menu.addAction(label,lambda:self.editor.edit(action,**kw))
        add('Add note here','add',tick=tick,lane=lane)
        if note:
            add('Delete note','delete',note=note)
            menu.addAction('Set sustain length…',lambda:self.editor.sustain(note))
            for label,action in [('Prefer HOPO (TheGHOST 2.95)','hopo'),('Prefer strum','strum'),('Natural HOPO / strum','natural')]:add(label,action,tick=tick)
        menu.addSeparator()
        menu.addAction('Add star power phrase…',lambda:self.editor.star(tick))
        add('Remove star power here','remove_star',tick=tick)
        menu.addAction('Insert note pattern…',lambda:self.editor.pattern(tick))
        menu.exec(event.globalPos())

    def paintEvent(self,event):
        # Include a non-visible fifth-lane sentinel so Hard/Expert lane geometry stays stable.
        original=self.notes
        if self.lane_count()==5:self.notes=original+[(1e20,1e20,4,False)]
        super().paintEvent(event);self.notes=original
        p=QPainter(self);p.setPen(QPen(QColor('#ffffff'),2))
        song=self.editor.session.song
        for phrase in song.phrases.get(self.editor.difficulty.currentText(),[]):
            if phrase.kind!=2:continue
            x,tail,_=self.note_geometry((song.seconds(phrase.tick),song.seconds(phrase.tick+phrase.length),0,False))
            if tail>=40 and x<=self.width():
                p.fillRect(int(max(40,x)),22,int(max(1,min(self.width(),tail)-max(40,x))),5,QColor('#b789ff'))
        for note in self.notes:
            x,tail,y=self.note_geometry(note)
            if tail>x and 40<=tail<=self.width():p.drawRect(int(tail)-4,int(y)-5,8,10)
        if self.ghost:
            tick,lane,length=self.ghost
            x,tail,y=self.note_geometry((song.seconds(tick),song.seconds(tick+length),lane,False))
            p.setPen(QPen(QColor('#ffffff'),2,Qt.DashLine));p.drawLine(int(x),int(y),int(tail),int(y));p.drawEllipse(int(x)-9,int(y)-9,18,18)
        p.end()


class ChartEditorDialog(QDialog):
    def __init__(self,panel):
        super().__init__(panel);self.panel=panel;self.session=EditSession(panel.current[0]);self.setWindowTitle('Edit chart — working copy');fit_size(self,960,680)
        layout=QVBoxLayout(self)
        hint=QLabel('Right-click to add notes, star power or patterns. Drag note heads to move; drag square sustain handles to resize. Short notes: right-click → Set sustain length. Changes affect this copy only.');hint.setWordWrap(True);layout.addWidget(hint)
        row=QHBoxLayout();layout.addLayout(row);self.difficulty=QComboBox();self.difficulty.addItems([d for d in ('Expert','Hard','Medium','Easy') if self.session.song.tracks.get(d)]);self.difficulty.setCurrentText(panel.current[1]);row.addWidget(self.difficulty)
        row.addWidget(QLabel('Snap'));self.snap=QComboBox();self.snap.addItems(['¼ beat','½ beat','1 beat','⅓ beat','1 tick']);row.addWidget(self.snap)
        play=QPushButton('Play / pause');play.clicked.connect(panel.toggle);row.addWidget(play)
        self.follow=QCheckBox('Follow audio');self.follow.setChecked(True);row.addWidget(self.follow)
        self.view=EditHighway(self);layout.addWidget(self.view,1)
        self.seek=QSlider(Qt.Horizontal);self.seek.setRange(0,max(panel.player.duration(),int(max((self.session.song.seconds(n.tick+n.length) for ns in self.session.song.tracks.values() for n in ns),default=0)*1000)+6000));layout.addWidget(self.seek);self.seek.sliderMoved.connect(self.seek_to)
        self.status=QLabel('HOPO edits use TheGHOST measure 2.95 and require a starting strum. Purple bars indicate star power.');self.status.setWordWrap(True);layout.addWidget(self.status)
        row=QHBoxLayout();layout.addLayout(row)
        for label,callback in [('Undo',self.undo),('Redo',self.redo),('Export edited song…',self.export),('Close editor',self.reject)]:
            button=QPushButton(label);button.clicked.connect(callback);row.addWidget(button)
        for key,callback in [('Ctrl+Z',self.undo),('Ctrl+Y',self.redo)]:
            shortcut=QShortcut(QKeySequence(key),self);shortcut.activated.connect(callback)
        self.difficulty.currentTextChanged.connect(self.refresh)
        self.timer=QTimer(self);self.timer.timeout.connect(self.tick);self.timer.start(33);self.refresh()
        self.exported=False

    def step(self):return max(1,round(self.session.song.resolution*[.25,.5,1,1/3,0][self.snap.currentIndex()]))
    def refresh(self):self.view.notes=timeline(self.session.song,self.difficulty.currentText(),1/2.95);self.view.update()
    def seek_to(self,value):self.panel.player.pause();self.panel.player.setPosition(value);self.view.position=value/1000;self.view.update()
    def tick(self):
        if self.follow.isChecked() and self.panel.player.isPlaying():
            self.view.position=self.panel.player.position()/1000;self.seek.setValue(self.panel.player.position());self.view.update()
    def edit(self,action,**kwargs):
        try:
            self.session.change(self.difficulty.currentText(),action,**kwargs);self.refresh();self.status.setText('Edit applied to working copy. Export to save; Ctrl+Z to undo.');self.exported=False
        except Exception as exc:self.status.setText('Edit not applied: '+str(exc))
    def undo(self):self.session.undo();self.refresh();self.exported=False
    def redo(self):self.session.redo();self.refresh();self.exported=False
    def sustain(self,note):
        beats,ok=QInputDialog.getDouble(self,'Sustain','Length in beats (0 = tap):',note.length/self.session.song.resolution,0,128,3)
        if ok:self.edit('resize',note=note,length=round(beats*self.session.song.resolution))
    def star(self,tick):
        beats,ok=QInputDialog.getDouble(self,'Star power','Phrase length in beats:',4,.01,128,3)
        if ok:self.edit('star',tick=tick,length=max(1,round(beats*self.session.song.resolution)))
    def pattern(self,tick):
        value,ok=QInputDialog.getItem(self,'Insert pattern','One note per snap interval; starts at the clicked tick:', ['G R Y B','B Y R G','G R G R','B Y B','G Y R B'],0,True)
        if ok:
            try:lanes=['GRYBO'.index(x.upper()) for x in value.split()]
            except ValueError:self.status.setText('Use space-separated G R Y B (O only outside Medium).');return
            self.edit('pattern',tick=tick,lanes=lanes,step=self.step())
    def export(self):
        try:check_editor_song(self.session.song)
        except ChartError as exc:self.status.setText(str(exc));return
        audio=self.panel.player.source().toLocalFile()
        if not Path(audio).is_file():
            audio,_=QFileDialog.getOpenFileName(self,'Choose matching audio','','Audio (*.ogg *.opus *.mp3 *.wav *.flac)')
            if not audio:return
        parent=QFileDialog.getExistingDirectory(self,'Choose output parent (existing song export will be updated)')
        if not parent:return
        from .song_export import export_song_folder
        from .song_identity import export_folder_path
        destination=export_folder_path(parent,self.session.song.metadata,self.panel.owner.path)
        self.status.setText('Exporting edited chart and Ogg audio…')
        # Use the application's worker so audio conversion does not block the UI.
        owner=self.panel.owner
        def ready(result):
            self.exported=True;self.status.setText('Exported: '+str(destination));owner.log_line('Editor export: '+str(destination))
        owner.run_job('Exporting edited song…',lambda cancel:export_song_folder(self.session.song,{'editor_edits':self.session.log,'warnings':['Manual HOPO edits require TheGHOST measure 2.95; verify in game.']},destination,audio,owner.path,editor_all=True,overwrite=True),ready)
        # Prevent further edits while worker holds the snapshot; modal progress belongs to owner.
        self.setEnabled(False)
        self.poll=QTimer(self);self.poll.timeout.connect(self.export_finished);self.poll.start(100)
    def export_finished(self):
        if not self.panel.owner.busy():
            self.poll.stop();self.setEnabled(True)
            if not self.exported:self.status.setText(self.panel.owner.operation_label.text())

    def reject(self):
        if self.panel.owner.busy():return
        if self.session.log and not self.exported:
            if QMessageBox.question(self,'Unsaved edits','Close and discard unexported edits?',QMessageBox.Discard|QMessageBox.Cancel)!=QMessageBox.Discard:return
        self.panel.player.pause();self.timer.stop();super().reject()
