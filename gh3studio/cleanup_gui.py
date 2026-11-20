"""Review concrete chart changes before applying them to an in-memory copy."""
import json
from PySide6.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QCheckBox,QPushButton,QTextEdit,QLabel
from .editing import prepare_cleanup
from .window_fit import fit_size

class CleanupDialog(QDialog):
    def __init__(self,song,parent=None):
        super().__init__(parent);self.song=song;self.prepared=None;self.report=None
        self.setWindowTitle('Review GH3 cleanup — source file stays unchanged');fit_size(self,780,560)
        layout=QVBoxLayout(self)
        warning=QLabel('Choose changes, review the exact tick/lane list, then apply to a working copy.\nStripping tap/forced markers does not turn those notes into guaranteed no-strum notes.\nOpen-note events are removed; ordinary five-fret gems remain for four-fret conversion.')
        warning.setWordWrap(True);layout.addWidget(warning)
        self.strip=QCheckBox('Remove unsupported modifiers, solo markers and open-note events');self.strip.setChecked(True);layout.addWidget(self.strip)
        self.trim=QCheckBox('Shorten conflicting sustains: common shortest chord length, ending by the next onset');layout.addWidget(self.trim)
        self.details=QTextEdit();self.details.setReadOnly(True);layout.addWidget(self.details)
        row=QHBoxLayout();layout.addLayout(row)
        self.apply_button=QPushButton('Apply reviewed working copy');self.apply_button.clicked.connect(self.accept);row.addWidget(self.apply_button)
        cancel=QPushButton('Cancel');cancel.clicked.connect(self.reject);row.addWidget(cancel)
        self.strip.toggled.connect(self.preview);self.trim.toggled.connect(self.preview);self.preview()
    def preview(self,*args):
        try:
            self.prepared,self.report=prepare_cleanup(self.song,self.strip.isChecked(),self.trim.isChecked())
            self.details.setPlainText(json.dumps(self.report,indent=2,ensure_ascii=False))
            self.apply_button.setEnabled(not self.report['remaining_errors'] and bool(self.report['changes']))
        except Exception as exc:
            self.prepared=None;self.report=None;self.details.setPlainText(str(exc));self.apply_button.setEnabled(False)
