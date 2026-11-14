"""One-window desktop converter. File parsing/conversion/export run off the UI thread."""
import json
import sys
from datetime import datetime
from pathlib import Path
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QColor, QPen, QBrush
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QSpinBox, QSlider, QTextEdit, QFileDialog,
    QGraphicsView, QGraphicsScene, QSplitter, QGroupBox, QFormLayout, QProgressBar)
from .converter import Settings, convert
from .service import load, export_bundle

class Worker(QThread):
    succeeded=Signal(object)
    failed=Signal(str)
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
        self.song=None; self.converted=None; self.report=None; self.path=None; self.worker=None
        self.setWindowTitle('GH3 Chart Studio 0.1.0 — Expert Medium')
        self.resize(1120,800); self.setAcceptDrops(True)
        root=QWidget(); self.setCentralWidget(root); layout=QVBoxLayout(root)
        title=QLabel('GH3 Chart Studio  |  Four-fret technical Medium')
        title.setStyleSheet('font-size:22px;font-weight:600;padding:8px;'); layout.addWidget(title)
        layout.addWidget(QLabel('Drop a .chart or .mid file here. Originals are never overwritten.'))
        row=QHBoxLayout(); layout.addLayout(row)
        self.open_button=QPushButton('Open chart…'); self.open_button.clicked.connect(self.browse); row.addWidget(self.open_button)
        self.phrase_mode=QComboBox(); self.phrase_mode.addItems(['Modern MIDI (116 Star Power)','Legacy MIDI / TheGHOST'])
        row.addWidget(self.phrase_mode)
        self.file_label=QLabel('No chart loaded'); row.addWidget(self.file_label,1)
        self.info=QLabel('Choose a chart to begin.'); self.info.setWordWrap(True); layout.addWidget(self.info)
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
        self.convert_button=QPushButton('Convert & validate'); self.convert_button.clicked.connect(self.start_convert); row.addWidget(self.convert_button)
        self.export_button=QPushButton('Export .chart + MIDI…'); self.export_button.clicked.connect(self.start_export); row.addWidget(self.export_button)
        self.save_settings=QPushButton('Save settings…'); self.save_settings.clicked.connect(self.save_config); row.addWidget(self.save_settings)
        self.load_settings=QPushButton('Load settings…'); self.load_settings.clicked.connect(self.load_config); row.addWidget(self.load_settings)
        self.cancel_button=QPushButton('Cancel'); self.cancel_button.clicked.connect(self.cancel); row.addWidget(self.cancel_button)
        self.progress=QProgressBar(); self.progress.setRange(0,1); self.progress.setValue(0); layout.addWidget(self.progress)
        row=QHBoxLayout(); row.addWidget(QLabel('Note preview (first 2,000 gems; scroll horizontally):'))
        self.view_choice=QComboBox(); self.view_choice.addItems(['Converted Medium','Source']); self.view_choice.currentIndexChanged.connect(self.refresh_preview)
        row.addWidget(self.view_choice); layout.addLayout(row)
        split=QSplitter(Qt.Vertical); self.preview=Preview(); split.addWidget(self.preview)
        self.log=QTextEdit(); self.log.setReadOnly(True); split.addWidget(self.log); layout.addWidget(split,1)
        save_log=QPushButton('Save diagnostic log…'); save_log.clicked.connect(self.save_diagnostics); layout.addWidget(save_log)
        self.log_line('Ready. Structural checks do not certify TheGHOST or in-game compatibility.')
        self.update_buttons()
    def log_line(self,text):
        self.log.append(datetime.now().strftime('%H:%M:%S')+'  '+str(text).replace('&','&amp;').replace('<','&lt;').replace('\n','<br>'))
    def busy(self): return self.worker is not None
    def update_buttons(self):
        busy=self.busy()
        for widget in (self.open_button,self.source,self.max_chord,self.phrase_mode,self.save_settings,self.load_settings,*self.sliders.values()): widget.setEnabled(not busy)
        self.convert_button.setEnabled(not busy and self.song is not None)
        self.export_button.setEnabled(not busy and self.converted is not None)
        self.cancel_button.setEnabled(busy and getattr(self,'cancellable',False))
    def invalidate(self,*args):
        self.converted=None; self.report=None; self.update_buttons(); self.refresh_preview()
    def settings(self):
        return Settings(self.source.currentText(),self.sliders['Density'].value(),self.sliders['Chords'].value(),self.sliders['Movement'].value(),self.max_chord.value())
    def run_job(self,label,fn,on_success,cancellable=False):
        self.cancellable=cancellable; self.log_line(label); self.progress.setRange(0,0)
        self.worker=Worker(fn,self)
        self.worker.succeeded.connect(on_success); self.worker.failed.connect(self.job_failed)
        self.worker.finished.connect(self.job_finished)
        self.update_buttons(); self.worker.start()
    def job_failed(self,error): self.log_line('ERROR — '+error)
    def job_finished(self):
        worker=self.worker; self.worker=None; worker.deleteLater()
        self.progress.setRange(0,1); self.progress.setValue(1); self.update_buttons()
    def browse(self):
        filename,_=QFileDialog.getOpenFileName(self,'Open authored chart','','Charts (*.chart *.mid *.midi)')
        if filename: self.open_path(filename)
    def open_path(self,path):
        if self.busy(): return
        self.song=None; self.converted=None; self.report=None; self.path=None
        self.info.setText('Loading…'); self.preview.scene().clear()
        mode='modern' if self.phrase_mode.currentIndex()==0 else 'legacy'
        def ready(song):
            self.song=song; self.path=Path(path); self.file_label.setText(str(path))
            available=[d for d in ('Expert','Hard') if song.tracks.get(d)]
            if available: self.source.setCurrentText(available[0])
            self.info.setText(f"{song.metadata.get('Name',Path(path).stem)} — {song.metadata.get('Artist','Unknown artist')} | PPQ {song.resolution} | "+' · '.join(f'{d}: {len(n)} gems' for d,n in song.tracks.items()))
            self.log_line('Imported. '+ ' '.join(song.warnings)); self.refresh_preview()
        self.run_job('Reading chart…',lambda cancel:load(path,mode),ready)
    def start_convert(self):
        if self.song is None or self.busy(): return
        settings=self.settings(); self.converted=None; self.report=None
        def ready(value):
            self.converted,self.report=value
            self.log_line(json.dumps(self.report,indent=2)); self.refresh_preview()
        self.run_job('Converting authored rhythm…',lambda cancel:convert(self.song,settings,cancel),ready,True)
    def refresh_preview(self,*args):
        if self.view_choice.currentIndex()==0 and self.converted:
            self.preview.show_notes(self.converted,'Medium')
        elif self.song: self.preview.show_notes(self.song,self.source.currentText())
        else: self.preview.scene().clear()
    def start_export(self):
        if self.converted is None or self.busy(): return
        parent=QFileDialog.getExistingDirectory(self,'Choose parent folder for a NEW export folder')
        if not parent: return
        name=self.path.stem+'_ExpertMedium_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        self.export_to(Path(parent)/name)
    def export_to(self,destination):
        self.run_job('Writing and reopening both exports…',lambda cancel:export_bundle(self.converted,self.report,destination,self.path),
                     lambda details:self.log_line('Export verified: '+str(destination)+'\n'+ '\n'.join(details['warnings'])))
    def cancel(self):
        if self.worker and self.cancellable: self.worker.requestInterruption(); self.log_line('Cancellation requested…')
    def save_config(self):
        from dataclasses import asdict
        path,_=QFileDialog.getSaveFileName(self,'Save settings','expert-medium.json','JSON (*.json)')
        if path:
            try: Path(path).write_text(json.dumps(asdict(self.settings()),indent=2),encoding='utf-8')
            except Exception as e: self.job_failed(str(e))
    def load_config(self):
        path,_=QFileDialog.getOpenFileName(self,'Load settings','','JSON (*.json)')
        if path:
            try:
                settings=Settings(**json.loads(Path(path).read_text(encoding='utf-8'))); settings.check()
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
        if len(paths)!=1: self.log_line('Milestone 1 accepts one chart at a time; folder/batch import is planned.'); return
        self.open_path(paths[0]); event.acceptProposedAction()
    def closeEvent(self,event):
        if self.busy():
            self.cancel(); self.log_line('Wait for the current operation to finish before closing.'); event.ignore()
        else: event.accept()

def main():
    app=QApplication(sys.argv); app.setStyle('Fusion')
    window=Window(); window.show(); sys.exit(app.exec())
