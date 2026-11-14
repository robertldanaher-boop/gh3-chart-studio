"""Local pattern-library workspace; shares the owner's queued worker lifecycle."""
import json
from pathlib import Path
from PySide6.QtCore import QStandardPaths
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QPushButton,QLabel,QLineEdit,
    QFileDialog,QComboBox,QTableWidget,QTableWidgetItem,QSpinBox,QHeaderView,QTextEdit)
from .patterns import PatternStore,scan_folder,extract,CATEGORIES

class LibraryPanel(QWidget):
    def __init__(self,owner):
        super().__init__();self.owner=owner;self.rows=[];self.last_scan=None
        layout=QVBoxLayout(self)
        title=QLabel('Local Pattern Learning');title.setStyleSheet('font-size:22px;font-weight:600');layout.addWidget(title)
        hint=QLabel('Scan authored charts, inspect extracted patterns, and rate useful examples.\nAll chart data and ratings remain on this computer. This is statistical pattern retrieval, not neural training.')
        hint.setWordWrap(True);layout.addWidget(hint)
        row=QHBoxLayout();layout.addLayout(row)
        local=QStandardPaths.writableLocation(QStandardPaths.AppLocalDataLocation)
        self.db_path=QLineEdit(str(Path(local)/'GH3ChartStudio'/'patterns.sqlite3'));row.addWidget(self.db_path,1)
        self.choose_db=QPushButton('Choose database…');self.choose_db.clicked.connect(self.browse_db);row.addWidget(self.choose_db)
        row=QHBoxLayout();layout.addLayout(row)
        self.scan_button=QPushButton('Scan chart folder…');self.scan_button.clicked.connect(self.choose_folder);row.addWidget(self.scan_button)
        self.filter=QComboBox();self.filter.addItems(['All categories',*CATEGORIES]);row.addWidget(self.filter)
        self.refresh_button=QPushButton('Browse patterns');self.refresh_button.clicked.connect(self.refresh);row.addWidget(self.refresh_button)
        self.similar_button=QPushButton('Find matches for open chart');self.similar_button.clicked.connect(self.find_matches);row.addWidget(self.similar_button)
        self.summary=QLabel('Choose a folder to build your library. Tables show at most 200 rows.');self.summary.setWordWrap(True);layout.addWidget(self.summary)
        self.table=QTableWidget(0,8);self.table.setHorizontalHeaderLabels(['ID','Song','Difficulty','Category','Events','Gems','Events/beat','Rating'])
        self.table.setSelectionBehavior(QTableWidget.SelectRows);self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers);self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True);self.table.itemSelectionChanged.connect(self.selection_changed);layout.addWidget(self.table,1)
        row=QHBoxLayout();layout.addLayout(row)
        row.addWidget(QLabel('Selected pattern preference:'))
        self.rating=QSpinBox();self.rating.setRange(1,5);self.rating.setValue(3);row.addWidget(self.rating)
        self.rate_button=QPushButton('Save rating');self.rate_button.clicked.connect(self.save_rating);row.addWidget(self.rate_button)
        self.report_button=QPushButton('Save scan report…');self.report_button.clicked.connect(self.save_report);row.addWidget(self.report_button)
        self.cancel_button=QPushButton('Cancel operation');self.cancel_button.clicked.connect(owner.cancel);row.addWidget(self.cancel_button)
        self.details=QTextEdit();self.details.setReadOnly(True);self.details.setMaximumHeight(180);layout.addWidget(self.details)
        self.controls=[self.db_path,self.choose_db,self.scan_button,self.filter,self.refresh_button,self.similar_button,self.rating,self.rate_button]
    def store(self):
        if not self.db_path.text().strip(): raise ValueError('Choose a database path')
        return PatternStore(self.db_path.text().strip())
    def update_busy(self,busy,cancellable):
        for widget in self.controls: widget.setEnabled(not busy)
        self.cancel_button.setEnabled(busy and cancellable)
    def browse_db(self):
        path,_=QFileDialog.getSaveFileName(self,'Select a new or existing GH3 SQLite database',self.db_path.text(),'SQLite (*.sqlite3 *.db)',options=QFileDialog.DontConfirmOverwrite)
        if path:self.db_path.setText(path);self.rows=[];self.table.setRowCount(0);self.summary.setText('Database selected; browse or scan to load it.')
    def choose_folder(self):
        path=QFileDialog.getExistingDirectory(self,'Select parent chart folder (scanned recursively)')
        if path:self.scan(path)
    def scan(self,path):
        if self.owner.busy():return
        try:store=self.store()
        except Exception as e:self.owner.job_failed(str(e));return
        mode='modern' if self.owner.phrase_mode.currentIndex()==0 else 'legacy'
        self.summary.setText('Scanning… Input MIDI mode follows the Converter tab.')
        def ready(report):
            self.last_scan=report
            self.summary.setText(f"Scan {report['state']}: {report['imported']} new, {report['duplicates']} duplicates, {report['failed']} failed; {report['summary']['patterns']} stored windows.")
            self.details.setPlainText(json.dumps(report,indent=2));self.owner.log_line(self.summary.text())
        self.owner.run_job('Scanning local pattern library…',lambda cancel:scan_folder(path,store,mode,cancel,
            lambda done,total,name:self.owner.worker.progress.emit(done,total,name)),ready,True)
    def refresh(self):
        if self.owner.busy():return
        try:store=self.store()
        except Exception as e:self.owner.job_failed(str(e));return
        category='' if self.filter.currentIndex()==0 else self.filter.currentText()
        def ready(value):
            rows,summary=value;self.display_rows(rows)
            self.summary.setText(f"{summary['sources']} unique chart contents | {summary['patterns']} windows | {summary['ratings']} rated patterns. Showing {len(rows)} rows.")
        self.owner.run_job('Loading pattern library…',lambda cancel:(store.browse(category),store.summary()),ready)
    def display_rows(self,rows):
        self.rows=rows;self.table.setRowCount(0)
        for row in rows:
            payload=json.loads(row['payload']);f=payload['features'];index=self.table.rowCount();self.table.insertRow(index)
            values=[row['id'],row.get('title','Matched source'),row['difficulty'],row['category'],f['events'],f['gems'],round(row['rate'],3),row['rating']]
            for column,value in enumerate(values):self.table.setItem(index,column,QTableWidgetItem(str(value)))
    def selection_changed(self):
        index=self.table.currentRow()
        if 0<=index<len(self.rows):
            row=self.rows[index];self.rating.setValue(row['rating'])
            self.details.setPlainText(json.dumps(json.loads(row['payload']),indent=2))
    def save_rating(self):
        index=self.table.currentRow()
        if self.owner.busy() or not 0<=index<len(self.rows):return
        row=self.rows[index];score=self.rating.value()
        try:store=self.store()
        except Exception as e:self.owner.job_failed(str(e));return
        def ready(_):
            row['rating']=score;self.table.item(index,7).setText(str(score));self.summary.setText('Preference saved locally; it affects future candidate ranking.')
        self.owner.run_job('Saving pattern preference…',lambda cancel:store.rate(row['id'],score),ready)
    def find_matches(self):
        if self.owner.busy():return
        if not self.owner.song:self.summary.setText('Open a chart in the Converter tab first.');return
        song=self.owner.song;diff=self.owner.source.currentText();category='' if self.filter.currentIndex()==0 else self.filter.currentText()
        try:store=self.store()
        except Exception as e:self.owner.job_failed(str(e));return
        def work(cancel):
            windows=extract(song,diff,cancel)
            if not windows:raise ValueError('No source patterns')
            return store.similar(windows[0]['features'],category,20)
        def ready(rows):self.display_rows(rows);self.summary.setText('Closest candidates for the first occupied eight-quarter-note window; preference-adjusted heuristic ranking.')
        self.owner.run_job('Finding similar patterns…',work,ready,True)
    def save_report(self):
        if self.last_scan is None:return
        path,_=QFileDialog.getSaveFileName(self,'Save scan report','scan-report.json','JSON (*.json)')
        if path:
            try:Path(path).write_text(json.dumps(self.last_scan,indent=2),encoding='utf-8')
            except Exception as e:self.owner.job_failed(str(e))
