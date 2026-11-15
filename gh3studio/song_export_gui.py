"""Review explicit Medium-only repairs before exporting a complete song folder."""
import json
from pathlib import Path
from PySide6.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QLabel,QLineEdit,QPushButton,QCheckBox,QTextEdit,QDialogButtonBox,QFileDialog
from .song_export import prepare_medium

class SongExportDialog(QDialog):
    def __init__(self,song,audio_path='',parent=None):
        super().__init__(parent);self.song=song;self.setWindowTitle('Review Medium and export song folder');self.resize(760,600)
        layout=QVBoxLayout(self)
        label=QLabel('Exports notes.chart + song.wav + song.ini and validation details. Expert/Hard stay untouched.\nCleanup is optional and affects only Medium. Shortening sustains changes the exact Orange-only copy.');label.setWordWrap(True);layout.addWidget(label)
        row=QHBoxLayout();layout.addLayout(row);self.audio=QLineEdit(audio_path);row.addWidget(self.audio)
        browse=QPushButton('Choose full-mix audio…');browse.clicked.connect(self.browse);row.addWidget(browse)
        self.markers=QCheckBox('Remove unsupported Medium markers/open-note events (changes gameplay)');layout.addWidget(self.markers)
        self.sustains=QCheckBox('Shorten unsupported Medium sustains (review each change below)');layout.addWidget(self.sustains)
        self.details=QTextEdit();self.details.setReadOnly(True);layout.addWidget(self.details)
        self.buttons=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel);layout.addWidget(self.buttons)
        self.buttons.button(QDialogButtonBox.Save).setText('Export reviewed song folder…')
        self.buttons.accepted.connect(self.accept);self.buttons.rejected.connect(self.reject)
        self.markers.toggled.connect(self.refresh);self.sustains.toggled.connect(self.refresh);self.audio.textChanged.connect(self.refresh);self.refresh()
    def browse(self):
        path,_=QFileDialog.getOpenFileName(self,'Select matching full mix','','Audio (*.wav *.flac *.ogg *.mp3)')
        if path:self.audio.setText(path)
    def refresh(self,*args):
        try:
            self.prepared,self.review=prepare_medium(self.song,self.markers.isChecked(),self.sustains.isChecked())
            self.details.setPlainText(json.dumps(self.review,indent=2))
            valid=not self.review['remaining_errors'] and Path(self.audio.text()).is_file()
        except Exception as exc:
            self.details.setPlainText(str(exc));valid=False
        self.buttons.button(QDialogButtonBox.Save).setEnabled(valid)
