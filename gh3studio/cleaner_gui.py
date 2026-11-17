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
        row=QHBoxLayout();outer.insertLayout(0,row)
        self.scan_button=QPushButton('1. Choose folder to scan…');self.scan_button.clicked.connect(self.browse);row.addWidget(self.scan_button)
        self.cancel_button=QPushButton('Cancel');self.cancel_button.clicked.connect(owner.cancel);row.addWidget(self.cancel_button)
        self.status=QLabel('Drop a folder here or choose one above.');self.status.setWordWrap(True);outer.insertWidget(1,self.status)
        self.table=QTableWidget(0,5);self.table.setHorizontalHeaderLabels(['Export','Song','Artist','Review','Source'])
        self.table.horizontalHeader().setStretchLastSection(True);self.table.setSelectionBehavior(QTableWidget.SelectRows);self.table.setSelectionMode(QTableWidget.SingleSelection);self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.currentCellChanged.connect(self.show_details);layout.addWidget(self.table)
        row=QHBoxLayout();layout.addLayout(row)
        self.metadata_button=QPushButton('Edit selected metadata…');self.metadata_button.clicked.connect(self.edit_metadata);row.addWidget(self.metadata_button)
        self.audio_button=QPushButton('Select matching audio…');self.audio_button.clicked.connect(self.choose_audio);row.addWidget(self.audio_button)
        self.chart_button=QPushButton('Select chart…');self.chart_button.clicked.connect(self.choose_chart);row.addWidget(self.chart_button)
        self.save_report=QPushButton('Save scan report…');self.save_report.clicked.connect(self.save_scan_report);layout.addWidget(self.save_report)
        self.details=QTextEdit();self.details.setReadOnly(True);self.details.setMinimumHeight(130);layout.addWidget(self.details)
        self.approve=QCheckBox('Apply the reviewed cleanup changes');self.approve.setToolTip('I reviewed changes and verified the metadata and matching audio.');outer.insertWidget(2,self.approve)
        warning=QLabel('Title and artist are required. Other missing fields are flagged, never invented. Existing Ogg may be re-encoded if its tags need correction. GH3 runtime compatibility still needs importer/game testing.');warning.setWordWrap(True);outer.addWidget(warning)
        self.export_button=QPushButton('START CLEANING');primary(self.export_button);self.export_button.clicked.connect(self.browse_export);outer.insertWidget(3,self.export_button)
        self.open_output=QPushButton('Open results folder (after cleaning)');self.open_output.clicked.connect(self.open_folder);outer.addWidget(self.open_output)
        bulk=QHBoxLayout();outer.insertLayout(2,bulk)
        self.select_all=QPushButton('Select all');self.select_all.clicked.connect(lambda:self.set_checked(True));bulk.addWidget(self.select_all)
        self.select_ready=QPushButton('Select ready only');self.select_ready.clicked.connect(lambda:self.set_checked(True,ready_only=True));bulk.addWidget(self.select_ready)
        self.select_none=QPushButton('Clear selection');self.select_none.clicked.connect(lambda:self.set_checked(False));bulk.addWidget(self.select_none)
        self.selection_summary=QLabel();self.selection_summary.setWordWrap(True);bulk.addWidget(self.selection_summary,1)
        output_row=QHBoxLayout();outer.insertLayout(4,output_row)
        self.output_path=QLineEdit();self.output_path.setPlaceholderText('Output parent folder — set automatically after scanning');output_row.addWidget(self.output_path,1)
        self.output_button=QPushButton('Change output folder…');self.output_button.clicked.connect(self.choose_output);output_row.addWidget(self.output_button)
        self.table.itemChanged.connect(self.selection_changed)
        self.selection_changed()
    def selection_changed(self,*args):
        checked=sum(self.table.item(i,0) is not None and self.table.item(i,0).checkState()==Qt.Checked for i in range(len(self.rows)))
        blocked=sum(bool(r['errors']) for r in self.rows)
        self.selection_summary.setText(f'{checked} checked of {len(self.rows)} • {blocked} blocked (see Review column)')
    def set_checked(self,checked,ready_only=False):
        if self.owner.busy():return
        self.table.blockSignals(True)
        for i,row in enumerate(self.rows):self.table.item(i,0).setCheckState(Qt.Checked if checked and (not ready_only or not row['errors']) else Qt.Unchecked)
        self.table.blockSignals(False);self.approve.setChecked(False);self.selection_changed()
        self.status.setText('Selection updated. Blocked songs cannot export; their reasons will be recorded in the results. Review changes, tick Apply, then START CLEANING.' if checked else 'Selection cleared.')
    def browse(self):
        path=QFileDialog.getExistingDirectory(self,'Choose a song folder or parent directory')
        if path:self.scan(path)
    def scan(self,path):
        if self.owner.busy():return
        self.owner.goal='clean'
        self.root=Path(path).resolve();self.output_path.setText(str(self.root.parent/'GH3 Cleaned Output'));self.approve.setChecked(False);self.last_output=None;self.rows=[];self.render()
        self.owner.run_job('Scanning charts and preparing cleanup review…',lambda cancel:scan_charts(self.root,cancel,lambda done,total,name:self.owner.worker.progress.emit(done,total,name)),self.scanned,True)
    def scanned(self,rows):
        self.rows=rows;self.render()
        self.status.setText(f'{len(rows)} song folders found; {sum(not r["errors"] for r in rows)} ready for review. Select each row to inspect changes. Cancelled scans may show partial results.')
    def render(self,preserve_selection=False):
        previous={self.rows[i]['path']:self.table.item(i,0).checkState() for i in range(min(len(self.rows),self.table.rowCount())) if self.table.item(i,0)} if preserve_selection else {}
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        for index,row in enumerate(self.rows):
            self.table.insertRow(index)
            check=QTableWidgetItem();check.setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable|Qt.ItemIsUserCheckable);check.setCheckState(Qt.Unchecked if row['errors'] else previous.get(row['path'],Qt.Checked));self.table.setItem(index,0,check)
            values=[row['metadata'].get('Name',''),row['metadata'].get('Artist',''),'BLOCKED: '+'; '.join(row['errors']) if row['errors'] else f'{len(row["changes"])} changes',row['path']]
            for col,value in enumerate(values,1):
                item=QTableWidgetItem(value);item.setToolTip(value);self.table.setItem(index,col,item)
        self.table.blockSignals(False)
        if self.rows:self.table.selectRow(0)
        self.show_details();self.selection_changed()
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
            self.rows[index]=value;self.render(preserve_selection=True);self.table.selectRow(index);self.show_details()
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
    def save_scan_report(self):
        path,_=QFileDialog.getSaveFileName(self,'Save scan diagnostics','GH3_scan_report.txt','Text (*.txt)')
        if not path:return
        from datetime import datetime
        lines=['GH3 Chart Studio scan report',datetime.now().astimezone().isoformat(),
               'Source: '+str(self.root),self.selection_summary.text()]
        for row in self.rows:
            lines+=['',row['path'],'Title: '+row['metadata'].get('Name',''),
                    'Artist: '+row['metadata'].get('Artist',''),'Audio: '+row['audio']]
            lines+=['ERROR: '+e for e in row['errors']]+['WARNING: '+w for w in row['warnings']]
            if not row['errors']:lines.append('READY')
        try:
            Path(path).write_text('\n'.join(lines)+'\n',encoding='utf-8')
            self.status.setText('Scan report saved: '+path)
        except OSError as exc:self.status.setText('Could not save scan report: '+str(exc))
    def choose_output(self):
        path=QFileDialog.getExistingDirectory(self,'Choose where cleaned song folders will be saved',self.output_path.text())
        if path:self.output_path.setText(path)
    def browse_export(self):
        if self.owner.busy():return
        if not self.rows:self.status.setText('Choose a folder to scan first.');return
        if not any(self.table.item(i,0).checkState()==Qt.Checked for i in range(len(self.rows))):self.status.setText('No songs checked. Click Select all or check individual rows.');return
        if not self.approve.isChecked():self.status.setText('Tick Apply the reviewed cleanup changes, then click START CLEANING.');return
        if not self.output_path.text().strip():self.status.setText('Set an output folder using Change output folder.');return
        from datetime import datetime
        self.export_to(Path(self.output_path.text().strip())/('GH3 Cleaned - '+datetime.now().strftime('%Y%m%d_%H%M%S_%f')))
    def export_to(self,path):
        if self.owner.busy() or not self.approve.isChecked():return
        selected=[row for i,row in enumerate(self.rows) if self.table.item(i,0).checkState()==Qt.Checked]
        if not selected:self.status.setText('Check at least one song.');return
        path=Path(path).resolve()
        if path==self.root or path.is_relative_to(self.root):self.status.setText('Cannot start: output must be outside the scanned source folder. Change output folder above.');return
        if path.exists():self.status.setText('Cannot start: output folder already exists. Choose a new output location.');return
        self.owner.goal='clean'
        self.status.setText(f'Starting cleanup of {len(selected)} checked songs. Output: {path}')
        def ready(results):
            self.last_output=Path(path) if any(r['status']=='exported' for r in results) else None;self.status.setText(f'Export finished: {sum(r["status"]=="exported" for r in results)} exported, {sum(r["status"]=="failed" for r in results)} failed; {len(selected)-len(results)} unprocessed. See cleanup.log and cleanup_summary.json.');self.details.setPlainText(json.dumps(results,indent=2));self.approve.setChecked(False)
        self.owner.run_job('Cleaning and exporting song folders…',lambda cancel:export_cleaned(selected,path,self.root,cancel,lambda done,total,name:self.owner.worker.progress.emit(done,total,name)),ready,True)
    def open_folder(self):
        if self.last_output:QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.last_output)))
    def update_busy(self,busy,cancellable):
        for widget in (self.scan_button,self.metadata_button,self.audio_button,self.chart_button,self.table,self.approve,self.export_button,self.select_all,self.select_ready,self.select_none,self.output_path,self.output_button,self.save_report):widget.setEnabled(not busy)
        self.cancel_button.setEnabled(busy and cancellable)
        self.open_output.setEnabled(not busy and self.last_output is not None)
