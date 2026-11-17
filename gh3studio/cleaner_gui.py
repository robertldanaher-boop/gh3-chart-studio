"""Guided review queue for one song folder or a recursive collection."""
import json
from pathlib import Path
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QTableWidget,QTableWidgetItem,QTextEdit,QCheckBox,QFileDialog,QDialog,QFormLayout,QLineEdit,QDialogButtonBox,QScrollArea)
from .cleaner import scan_charts,inspect_chart,export_cleaned
from .song_identity import FIELDS
from .appearance import primary


class CleanerPanel(QWidget):
    def __init__(self,owner):
        super().__init__();self.owner=owner;self.rows=[];self.root=None;self.last_output=None
        outer=QVBoxLayout(self);scroll=QScrollArea();scroll.setWidgetResizable(True);outer.addWidget(scroll)
        body=QWidget();scroll.setWidget(body);layout=QVBoxLayout(body)
        title=QLabel('Clean charts for GH3');title.setWordWrap(True);title.setStyleSheet('font-size:22px;font-weight:600');layout.addWidget(title)
        hint=QLabel('1. Scan a song folder or parent directory → 2. Review changes and metadata → 3. Export new folders.\nCleans every guitar difficulty: removes forced/tap/open-note markers, repairs sustains and removes Orange from Medium. Other instruments, stems and artwork are omitted. Originals stay untouched.');hint.setWordWrap(True);layout.addWidget(hint)
        row=QHBoxLayout();layout.addLayout(row)
        self.scan_button=QPushButton('1. Choose folder to scan…');self.scan_button.clicked.connect(self.browse);row.addWidget(self.scan_button)
        self.cancel_button=QPushButton('Cancel');self.cancel_button.clicked.connect(owner.cancel);row.addWidget(self.cancel_button)
        self.status=QLabel('Drop a folder here or choose one above.');self.status.setWordWrap(True);layout.addWidget(self.status)
        self.table=QTableWidget(0,5);self.table.setHorizontalHeaderLabels(['Export','Song','Artist','Review','Source'])
        self.table.horizontalHeader().setStretchLastSection(True);self.table.setSelectionBehavior(QTableWidget.SelectRows);self.table.setSelectionMode(QTableWidget.SingleSelection);self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.currentCellChanged.connect(self.show_details);layout.addWidget(self.table)
        row=QHBoxLayout();layout.addLayout(row)
        self.metadata_button=QPushButton('Edit selected metadata…');self.metadata_button.clicked.connect(self.edit_metadata);row.addWidget(self.metadata_button)
        self.audio_button=QPushButton('Select matching audio…');self.audio_button.clicked.connect(self.choose_audio);row.addWidget(self.audio_button)
        self.chart_button=QPushButton('Select chart…');self.chart_button.clicked.connect(self.choose_chart);row.addWidget(self.chart_button)
        self.details=QTextEdit();self.details.setReadOnly(True);self.details.setMinimumHeight(130);layout.addWidget(self.details)
        self.approve=QCheckBox('Review complete');self.approve.setToolTip('I reviewed changes and verified the metadata and matching audio.');outer.addWidget(self.approve)
        warning=QLabel('Title and artist are required. Other missing fields are flagged, never invented. Existing Ogg may be re-encoded if its tags need correction. GH3 runtime compatibility still needs importer/game testing.');warning.setWordWrap(True);outer.addWidget(warning)
        self.export_button=QPushButton('3. Export checked songs…');primary(self.export_button);self.export_button.clicked.connect(self.browse_export);outer.addWidget(self.export_button)
        self.open_output=QPushButton('Open last export folder');self.open_output.clicked.connect(self.open_folder);outer.addWidget(self.open_output)
    def browse(self):
        path=QFileDialog.getExistingDirectory(self,'Choose a song folder or parent directory')
        if path:self.scan(path)
    def scan(self,path):
        if self.owner.busy():return
        self.root=Path(path).resolve();self.approve.setChecked(False);self.last_output=None;self.rows=[];self.render()
        self.owner.run_job('Scanning charts and preparing cleanup review…',lambda cancel:scan_charts(self.root,cancel,lambda done,total,name:self.owner.worker.progress.emit(done,total,name)),self.scanned,True)
    def scanned(self,rows):
        self.rows=rows;self.render()
        self.status.setText(f'{len(rows)} song folders found; {sum(not r["errors"] for r in rows)} ready for review. Select each row to inspect changes. Cancelled scans may show partial results.')
    def render(self):
        self.table.setRowCount(0)
        for index,row in enumerate(self.rows):
            self.table.insertRow(index)
            check=QTableWidgetItem();check.setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable|Qt.ItemIsUserCheckable);check.setCheckState(Qt.Unchecked if row['errors'] else Qt.Checked);self.table.setItem(index,0,check)
            values=[row['metadata'].get('Name',''),row['metadata'].get('Artist',''),'Needs correction' if row['errors'] else f'{len(row["changes"])} changes',row['path']]
            for col,value in enumerate(values,1):self.table.setItem(index,col,QTableWidgetItem(value))
        if self.rows:self.table.selectRow(0)
        self.show_details()
    def selected(self):
        index=self.table.currentRow()
        return index if 0<=index<len(self.rows) else None
    def show_details(self,*args):
        index=self.selected()
        if index is None:self.details.clear();return
        row=self.rows[index]
        lines=['NEEDS CORRECTION' if row['errors'] else 'READY FOR YOUR REVIEW']
        lines += ['• '+message for message in row['errors']]
        lines += ['', 'PLANNED CHANGES — '+str(len(row['changes']))]
        for change in row['changes']:
            context=' / '.join(str(change[k]) for k in ('difficulty','tick','lane') if k in change)
            detail=', '.join(f'{key}: {value}' for key,value in change.items() if key not in ('action','difficulty','tick','lane','transfers'))
            lines.append('• '+change['action']+(' ['+context+']' if context else '')+(' — '+detail if detail else ''))
            for transfer in change.get('transfers',[]):lines.append('  Tick '+str(transfer['tick'])+' → '+('Green','Red','Yellow','Blue')[transfer['lane']]+', sustain '+str(transfer['result_length'])+' ticks')
        if not row['changes']:lines.append('No chart-note repairs proposed.')
        lines+=['','METADATA']+[f'{key}: {row["metadata"].get(key,"") or "(missing)"}' for key in FIELDS]
        lines+=['','AUDIO: '+(row['audio'] or '(select matching recording)'),'OUTPUT: notes.chart + song.ogg + song.ini + validation/import reports','','REVIEW NOTES']
        lines+=['• '+message for message in row['warnings']]
        lines+=['','SOURCE: '+row['path']]
        self.details.setPlainText('\n'.join(lines))
    def recheck(self,index,**overrides):
        if self.owner.busy():return
        row=self.rows[index];path=overrides.pop('path',row['path']);audio=overrides.pop('audio',row['audio'] or None);metadata=overrides.pop('metadata',{k:v for k,v in row['metadata'].items() if k in FIELDS})
        self.approve.setChecked(False)
        if metadata is not None:
            row['metadata'].update(metadata)
            self.table.item(index,1).setText(row['metadata'].get('Name',''))
            self.table.item(index,2).setText(row['metadata'].get('Artist',''))
            self.show_details()
        def ready(value):
            self.rows[index]=value;self.render();self.table.selectRow(index);self.show_details()
            self.status.setText('Edits retained in this review. '+('Chart still needs correction: '+ '; '.join(value['errors']) if value['errors'] else 'Ready for review and export.')+' Export writes these edits to a new folder; originals stay unchanged.')
        self.owner.run_job('Rechecking selected song…',lambda cancel:inspect_chart(path,audio,metadata),ready)
    def edit_metadata(self):
        index=self.selected()
        if index is None:return
        dialog=QDialog(self);dialog.setWindowTitle('Verify song metadata');form=QFormLayout(dialog);fields={}
        for key in FIELDS:
            edit=QLineEdit(self.rows[index]['metadata'].get(key,''));form.addRow(key+(' *' if key in ('Name','Artist') else ''),edit);fields[key]=edit
        buttons=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel);buttons.accepted.connect(dialog.accept);buttons.rejected.connect(dialog.reject);form.addRow(buttons)
        if dialog.exec()==QDialog.Accepted:self.recheck(index,metadata={k:e.text().strip() for k,e in fields.items()})
    def choose_audio(self):
        index=self.selected()
        if index is None:return
        path,_=QFileDialog.getOpenFileName(self,'Choose matching full recording','','Audio (*.ogg *.wav *.flac *.mp3 *.opus)')
        if path:self.recheck(index,audio=path)
    def choose_chart(self):
        index=self.selected()
        if index is None:return
        path,_=QFileDialog.getOpenFileName(self,'Choose chart for this song',self.rows[index]['path'],'Charts (*.chart *.mid *.midi)')
        if path:self.recheck(index,path=path,audio=None)
    def browse_export(self):
        if not self.approve.isChecked():self.status.setText('Review changes, verify metadata/audio, then tick the review checkbox.');return
        path=QFileDialog.getExistingDirectory(self,'Choose output parent outside the scanned source directory')
        if path:
            from datetime import datetime
            self.export_to(Path(path)/('GH3 Cleaned - '+datetime.now().strftime('%Y%m%d_%H%M%S_%f')))
    def export_to(self,path):
        if self.owner.busy() or not self.approve.isChecked():return
        selected=[row for i,row in enumerate(self.rows) if self.table.item(i,0).checkState()==Qt.Checked]
        if not selected or any(r['errors'] for r in selected):self.status.setText('Check at least one song and resolve errors on every checked row.');return
        def ready(results):
            self.last_output=Path(path);self.status.setText(f'Export finished: {sum(r["status"]=="exported" for r in results)} exported, {sum(r["status"]=="failed" for r in results)} failed; {len(selected)-len(results)} unprocessed. See cleanup_summary.json.');self.details.setPlainText(json.dumps(results,indent=2));self.approve.setChecked(False)
        self.owner.run_job('Cleaning and exporting song folders…',lambda cancel:export_cleaned(selected,path,self.root,cancel,lambda done,total,name:self.owner.worker.progress.emit(done,total,name)),ready,True)
    def open_folder(self):
        if self.last_output:QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.last_output)))
    def update_busy(self,busy,cancellable):
        for widget in (self.scan_button,self.metadata_button,self.audio_button,self.chart_button,self.table,self.approve,self.export_button):widget.setEnabled(not busy)
        self.cancel_button.setEnabled(busy and cancellable)
        self.open_output.setEnabled(not busy and self.last_output is not None)
