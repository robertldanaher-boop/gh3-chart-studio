"""Review explicit Medium-only repairs before exporting a complete song folder."""
import json
from pathlib import Path
from PySide6.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QLabel,QLineEdit,QPushButton,QCheckBox,QTextEdit,QDialogButtonBox,QFileDialog,QFormLayout,QComboBox,QScrollArea,QWidget,QGridLayout
from .song_export import prepare_medium
from .song_identity import FIELDS,fill_from_audio,export_folder_name
from .hopo import prefer_hopos

class SongExportDialog(QDialog):
    def __init__(self,song,audio_path='',parent=None):
        super().__init__(parent);self.song=song;self.setWindowTitle('Review & export your song');self.resize(820,700)
        outer=QVBoxLayout(self);scroll=QScrollArea();scroll.setWidgetResizable(True);outer.addWidget(scroll)
        content=QWidget();scroll.setWidget(content);layout=QVBoxLayout(content)
        from .workspace import heading
        layout.addWidget(heading('Ready for the next stage.', 'Review the recording and song details before creating a new folder.'))
        label=QLabel('Exports notes.chart + song.ogg + song.ini and validation details. Expert/Hard stay untouched.\nCleanup is optional and affects only Medium. Shortening sustains changes the exact Orange-only copy.');label.setWordWrap(True);layout.addWidget(label)
        layout.addWidget(QLabel('Recording from preview (used for this song’s export):'))
        row=QHBoxLayout();layout.addLayout(row);self.audio=QLineEdit(audio_path);row.addWidget(self.audio)
        browse=QPushButton('Change recording…');browse.clicked.connect(self.browse);row.addWidget(browse)
        form=QGridLayout();layout.addLayout(form);self.identity_fields={}
        identity=fill_from_audio(song.metadata,audio_path)
        for index,field in enumerate(FIELDS):
            edit=QLineEdit(identity.get(field,''));self.identity_fields[field]=edit
            row,col=divmod(index,2);form.addWidget(QLabel('Title' if field=='Name' else field),row*2,col)
            form.addWidget(edit,row*2+1,col);edit.textChanged.connect(self.update_identity)
        self.markers=QCheckBox('Remove existing Medium markers/open-note events (changes gameplay)');layout.addWidget(self.markers)
        self.sustains=QCheckBox('Shorten unsupported Medium sustains (review each change below)');layout.addWidget(self.sustains)
        self.hopo=QCheckBox('Favor HOPOs in Medium runs — experimental TheGHOST .chart profile');layout.addWidget(self.hopo)
        self.hopo_gap=QComboBox();self.hopo_gap.addItem('Fast runs: up to ½ beat',.5);self.hopo_gap.addItem('More generous: up to 1 beat',1.);layout.addWidget(self.hopo_gap)
        self.hopo_summary=QLabel('');self.hopo_summary.setWordWrap(True);layout.addWidget(self.hopo_summary)
        self.folder_label=QLabel();self.folder_label.setWordWrap(True);layout.addWidget(self.folder_label)
        self.readiness=QLabel();self.readiness.setWordWrap(True);self.readiness.setObjectName('nextStep');layout.addWidget(self.readiness)
        self.details=QTextEdit();self.details.setReadOnly(True);layout.addWidget(self.details)
        self.buttons=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel);outer.addWidget(self.buttons)
        self.buttons.button(QDialogButtonBox.Save).setText('Choose destination / export…')
        self.buttons.accepted.connect(self.accept);self.buttons.rejected.connect(self.reject)
        self.hopo.toggled.connect(self.refresh);self.hopo_gap.currentIndexChanged.connect(self.refresh);self.markers.toggled.connect(self.refresh);self.sustains.toggled.connect(self.refresh);self.audio.textChanged.connect(self.update_export_enabled);self.refresh()
    def browse(self):
        path,_=QFileDialog.getOpenFileName(self,'Select matching full mix','','Audio (*.wav *.flac *.ogg *.mp3)')
        if path:self.audio.setText(path)
    def refresh(self,*args):
        try:
            self.prepared,self.review=prepare_medium(self.song,self.markers.isChecked(),self.sustains.isChecked())
            self.hopo_summary.setText('No added HOPO assistance. Natural HOPOs may still occur.')
            if self.hopo.isChecked():
                self.prepared,hopo_review=prefer_hopos(self.prepared,self.hopo_gap.currentData())
                self.review['hopo_assistance']=hopo_review
                self.hopo_summary.setText(f"Estimated HOPOs: {hopo_review['estimated_hopo_events']} of {hopo_review['note_events']} events ({hopo_review['estimated_hopo_percent']}%). Notes unchanged by HOPO assistance. Set TheGHOST HOPO measure to 2.95.")
            lines=['COMPATIBILITY REVIEW']
            lines+=['Needs attention: '+e for e in self.review['remaining_errors']]
            if not self.review['remaining_errors']:lines.append('Structural checks passed. Target-game testing is still required.')
            lines+=['',f'Planned repairs: {len(self.review["changes"])}']
            for change in self.review['changes']:
                context=' / '.join(str(change[k]) for k in ('difficulty','tick','lane') if k in change)
                lines.append(change['action']+(' — '+context if context else '')+' — '+', '.join(f'{k}: {v}' for k,v in change.items() if k not in ('action','difficulty','tick','lane')))
            self.details.setPlainText('\n'.join(lines))
            valid=True
        except Exception as exc:
            self.details.setPlainText(str(exc));valid=False
        self.review_valid=valid;self.update_identity();self.update_export_enabled()
    def update_identity(self,*args):
        if hasattr(self,'prepared'):
            for field,edit in self.identity_fields.items():self.prepared.metadata[field]=edit.text()
            if hasattr(self,'folder_label'):self.folder_label.setText('Folder: '+export_folder_name(self.prepared.metadata))
    def update_export_enabled(self,*args):
        valid=getattr(self,'review_valid',False) and not self.review['remaining_errors'] and Path(self.audio.text()).is_file()
        self.buttons.button(QDialogButtonBox.Save).setEnabled(valid)
        if not getattr(self,'review_valid',False) or self.review.get('remaining_errors'):
            text='Needs attention: review the chart errors below. Optional repairs are listed above.'
        elif not Path(self.audio.text()).is_file():text='Choose the matching full recording to continue.'
        else:text='Ready. The next step asks where to save the new song folder.'
        self.readiness.setText(text)
