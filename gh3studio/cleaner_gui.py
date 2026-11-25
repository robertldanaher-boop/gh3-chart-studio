"""Guided review queue for one song folder or a recursive collection."""
import json
from pathlib import Path
from PySide6.QtCore import Qt, QUrl, QTimer, QPoint
from PySide6.QtGui import QDesktopServices,QColor,QBrush
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QTableWidget,QTableWidgetItem,QTextEdit,QCheckBox,QFileDialog,QDialog,QFormLayout,QLineEdit,QDialogButtonBox,QScrollArea,QSplitter,QHeaderView,QComboBox,QTabWidget,QSizePolicy)
from .cleaner import scan_charts,inspect_chart,export_cleaned
from .song_identity import FIELDS
from .appearance import primary


class CleanerPanel(QWidget):
    def __init__(self,owner,four_fret=False,unified=False):
        super().__init__();self.unified=unified;self.four_fret=four_fret;self.owner=owner;self.rows=[];self.root=None;self.last_output=None
        from .workspace import StepStrip,heading
        outer=QVBoxLayout(self);outer.setContentsMargins(18,14,18,14);outer.setSpacing(8)
        outer.addWidget(heading('Your songs', 'Choose a goal, review the exact changes, then export a separate copy.' if unified else 'Review compatibility and difficulty changes before exporting.'))
        self.goal_choice=QComboBox();self.goal_choice.addItems(['Check charts — report only','Repair existing charts','Create challenging Medium'])
        self.goal_choice.setCurrentIndex(2 if four_fret else 1)
        if unified:outer.addWidget(self.goal_choice)
        else:self.goal_choice.hide()
        self.bulk_source=QComboBox();self.bulk_source.addItems(['Expert then Hard','Expert','Hard'])
        self.bulk_sustains=QCheckBox('Move Orange sustains to allowed frets');self.bulk_sustains.setChecked(not unified)
        self.bulk_sustains.setToolTip('Orange taps are removed. Sustain transfers use repeatable placement and are listed for review; this is not musical-context remapping.')
        self.create_easy=QCheckBox('Also create / replace three-fret Easy');self.create_easy.setChecked(not unified)
        self.fill_missing=QCheckBox('Fill missing Hard / Expert with source copies');self.fill_missing.setChecked(not unified)
        self.repair_others=QCheckBox('Allow repairs to other difficulties');self.repair_others.setChecked(not unified)
        self.repair_sustains=QCheckBox('Allow listed sustain shortening / chord repairs');self.repair_sustains.setChecked(not unified)
        self.repair_orange=QCheckBox('Remove Orange from existing Medium');self.repair_orange.setChecked(not unified)
        self.goal_hint=QLabel();self.goal_hint.setWordWrap(True)
        if four_fret or unified:
            # Hidden stacked pages also contribute their minimum width to the window.
            # Keep this explanation wrappable with Windows fonts and larger text.
            self.bulk_source_hint=QLabel('Copy Medium from (changing options rescans and clears approval)')
            self.bulk_source_hint.setObjectName('bulkSourceHint');self.bulk_source_hint.setWordWrap(True)
            # A wrapped label must not shrink below its height-for-width hint.
            self.bulk_source_hint.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Minimum)
            self.bulk_source.currentIndexChanged.connect(self.rescan_bulk);self.bulk_sustains.toggled.connect(self.rescan_bulk)
        else:self.bulk_source.hide();self.bulk_sustains.hide()
        self.steps=StepStrip(['Choose songs','Review','Export']);outer.addWidget(self.steps)
        scroll=QScrollArea();self.review_scroll=scroll;self.scroll_timer=QTimer(self);self.scroll_timer.setSingleShot(True);self.scroll_timer.timeout.connect(self.reveal_review);scroll.setWidgetResizable(True);outer.addWidget(scroll,1)
        body=QWidget();scroll.setWidget(body);content=QVBoxLayout(body);content.setContentsMargins(0,0,8,0);content.setSpacing(8)
        if four_fret or unified:
            content.addWidget(self.goal_hint)
            if unified:
                source_row=QHBoxLayout();content.addLayout(source_row)
                self.bulk_source_hint.setText('Source for Medium')
                source_row.addWidget(self.bulk_source_hint);source_row.addWidget(self.bulk_source,1)
                self.option_toggle=QPushButton('Optional changes — none enabled');self.option_toggle.setCheckable(True);content.addWidget(self.option_toggle)
                self.optional_changes=QWidget();optional_layout=QVBoxLayout(self.optional_changes);optional_layout.setContentsMargins(0,0,0,0)
                for control in (self.bulk_sustains,self.create_easy,self.fill_missing,self.repair_others,self.repair_sustains,self.repair_orange):optional_layout.addWidget(control)
                content.addWidget(self.optional_changes);self.optional_changes.hide();self.option_toggle.toggled.connect(self.optional_changes.setVisible)
                for control in (self.bulk_sustains,self.create_easy,self.fill_missing,self.repair_others,self.repair_sustains,self.repair_orange):control.toggled.connect(self.update_option_label)
            else:
                for control in (self.bulk_source_hint,self.bulk_source,self.bulk_sustains,self.create_easy,self.fill_missing,self.repair_others,self.repair_sustains,self.repair_orange):content.addWidget(control)
            for control in (self.create_easy,self.fill_missing,self.repair_others,self.repair_sustains,self.repair_orange):control.toggled.connect(self.rescan_bulk)
        else:
            for control in (self.create_easy,self.fill_missing,self.repair_others,self.repair_sustains,self.repair_orange):control.hide()
        row=QHBoxLayout();content.addLayout(row)
        self.chart_file_button=QPushButton('Choose chart…');self.chart_file_button.clicked.connect(self.browse_chart);row.addWidget(self.chart_file_button)
        self.scan_button=QPushButton('Choose folder…');self.scan_button.clicked.connect(self.browse);row.addWidget(self.scan_button)
        self.source_label=QLabel('Choose a collection folder; all subfolders are scanned.' if four_fret else 'Or drop a folder anywhere in this workspace');self.source_label.setObjectName('muted');self.source_label.setWordWrap(True);row.addWidget(self.source_label,1)
        self.cancel_button=QPushButton('Cancel');self.cancel_button.clicked.connect(owner.cancel);row.addWidget(self.cancel_button)
        row=QHBoxLayout();content.addLayout(row)
        self.search=QLineEdit();self.search.setPlaceholderText('Find a song or artist…')
        # Text boxes would swallow a dropped folder as typed text (hiding every row or
        # replacing the output path); let the drop reach the window, which scans it.
        self.search.setAcceptDrops(False);self.search.textChanged.connect(self.filter_rows);row.addWidget(self.search,1)
        self.filter=QComboBox();self.filter.addItems(['All songs','Needs help','Ready']);self.filter.currentIndexChanged.connect(self.filter_rows);row.addWidget(self.filter)
        self.select_all=QPushButton('Select all');self.select_all.clicked.connect(lambda:self.set_checked(True));row.addWidget(self.select_all)
        self.select_ready=QPushButton('Ready only');self.select_ready.clicked.connect(lambda:self.set_checked(True,ready_only=True));row.addWidget(self.select_ready)
        self.select_none=QPushButton('Clear');self.select_none.clicked.connect(lambda:self.set_checked(False));row.addWidget(self.select_none)
        self.selection_summary=QLabel();self.selection_summary.setObjectName('muted');self.selection_summary.setWordWrap(True);content.addWidget(self.selection_summary)
        split=QSplitter(Qt.Horizontal);split.setMinimumHeight(220);split.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Ignored);content.addWidget(split,1)
        self.table=QTableWidget(0,5);self.table.setHorizontalHeaderLabels(['Use','Song','Artist','Status / action needed','Source'])
        self.table.setColumnHidden(4,True);self.table.verticalHeader().hide();self.table.verticalHeader().setDefaultSectionSize(36);self.table.setAlternatingRowColors(True);self.table.setShowGrid(False)
        self.table.setColumnWidth(0,44);self.table.setColumnWidth(1,175);self.table.setColumnWidth(2,120)
        self.table.horizontalHeader().setSectionResizeMode(3,QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows);self.table.setSelectionMode(QTableWidget.SingleSelection);self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.currentCellChanged.connect(self.show_details);self.table.setMinimumHeight(125);split.addWidget(self.table)
        self.detail_tabs=QTabWidget();self.detail_tabs.setMinimumHeight(90);split.addWidget(self.detail_tabs)
        self.details=QTextEdit();self.details.setReadOnly(True);self.detail_tabs.addTab(self.details,'Selected song')
        self.results=QTextEdit();self.results.setReadOnly(True);self.results.setPlainText('Your cleanup results and log location will appear here.');self.detail_tabs.addTab(self.results,'Results')
        split.setSizes([640,330]);split.setStretchFactor(0,2);split.setStretchFactor(1,1)
        row=QHBoxLayout();content.addLayout(row)
        self.metadata_button=QPushButton('Edit song details…');self.metadata_button.clicked.connect(self.edit_metadata);row.addWidget(self.metadata_button)
        self.audio_button=QPushButton('Choose audio…');self.audio_button.clicked.connect(self.choose_audio);row.addWidget(self.audio_button)
        row=QHBoxLayout();content.addLayout(row)
        self.chart_button=QPushButton('Replace selected chart…');self.chart_button.clicked.connect(self.choose_chart);row.addWidget(self.chart_button)
        self.preview_button=QPushButton('Preview / edit…');self.preview_button.clicked.connect(self.preview_song);row.addWidget(self.preview_button)
        self.save_report=QPushButton('Save scan report…');self.save_report.clicked.connect(self.save_scan_report);row.addWidget(self.save_report)
        row=QHBoxLayout();content.addLayout(row)
        self.sync_button=QPushButton('Timing tools (optional)…');self.sync_button.clicked.connect(self.review_sync);row.addWidget(self.sync_button)
        hint=QLabel('song.ini delay is applied automatically. Open timing tools only to override it.');hint.setWordWrap(True);row.addWidget(hint,1)
        row=QHBoxLayout();outer.addLayout(row);row.addWidget(QLabel('Save to'))
        self.output_path=QLineEdit();self.output_path.setPlaceholderText('Existing exports here will be updated');self.output_path.setAcceptDrops(False);row.addWidget(self.output_path,1)
        self.output_button=QPushButton('Change…');self.output_button.clicked.connect(self.choose_output);row.addWidget(self.output_button)
        self.approve=QCheckBox('Apply the reviewed conversion and repairs' if four_fret else 'Apply the cleanup changes I reviewed');self.approve.setToolTip('Approve the listed repairs and difficulty changes. Originals stay untouched; exported arrangements may change.');outer.addWidget(self.approve)
        self.status=QLabel('Step 1 · Choose a folder. Charts, audio and metadata are matched inside each song folder.');self.status.setWordWrap(True);self.status.setObjectName('nextStep');outer.addWidget(self.status)
        row=QHBoxLayout();outer.addLayout(row)
        self.open_output=QPushButton('Open results / logs');self.open_output.clicked.connect(self.open_folder);row.addWidget(self.open_output)
        self.export_button=QPushButton('Start cleaning');primary(self.export_button);self.export_button.clicked.connect(self.browse_export);row.addWidget(self.export_button,1)
        self.table.itemChanged.connect(self.selection_changed);self.selection_changed()
        if unified:
            self.goal_choice.currentIndexChanged.connect(self.change_goal);self.change_goal()
    def update_option_label(self,*args):
        controls=(self.bulk_sustains,self.create_easy,self.fill_missing,self.repair_others,self.repair_sustains,self.repair_orange)
        count=sum(c.isChecked() and not c.isHidden() for c in controls)
        self.option_toggle.setText(f'Optional changes — {count} enabled (expand to review)' if count else 'Optional changes — none enabled (expand to choose)')
    def inspection_options(self):
        if not self.unified:
            return dict(medium_source=self.bulk_source.currentText(),preserve_sustains=self.bulk_sustains.isChecked()) if self.four_fret else {}
        options=dict(allow_empty_fallback=False,repair_sustains=self.repair_sustains.isChecked(),repair_medium_orange=self.repair_orange.isChecked(),preserve_sustains=self.bulk_sustains.isChecked())
        if self.four_fret:options.update(medium_source=self.bulk_source.currentText(),preserve_sustains=self.bulk_sustains.isChecked(),create_easy=self.create_easy.isChecked(),fill_missing=self.fill_missing.isChecked(),repair_others=self.repair_others.isChecked())
        return options
    def change_goal(self,*args):
        self.four_fret=self.goal_choice.currentIndex()==2
        for control in (self.bulk_source_hint,self.bulk_source,self.bulk_sustains,self.create_easy,self.fill_missing,self.repair_others):control.setVisible(self.four_fret)
        self.repair_orange.setVisible(not self.four_fret and self.goal_choice.currentIndex()!=0)
        self.goal_hint.setText('Copy Expert or Hard to Medium. Orange taps are removed; G/R/Y/B notes retain their rhythm. Easy and other tracks stay as authored unless you choose otherwise.' if self.four_fret else 'Keep existing difficulty arrangements. Compatibility repairs may remove unsupported events. Sustain shortening and Medium Orange removal require the choices below. Check-only mode saves a report and cannot export.')
        self.goal_hint.setText(self.goal_hint.text()+' Changing the goal or options rescans and clears unsaved review edits.')
        self.approve.setText('Apply the difficulty changes and repairs I reviewed' if self.four_fret else 'Apply the repairs I reviewed')
        if self.unified:self.update_option_label()
        self.rescan_bulk();self.selection_changed()
    def set_goal(self,goal):
        self.goal_choice.setCurrentIndex(2 if goal=='orange' else 1)
    def browse_chart(self):
        path,_=QFileDialog.getOpenFileName(self,'Choose an existing game chart','','Charts (*.chart *.mid *.midi)')
        if path:self.scan(path)
    def preview_song(self):
        index=self.selected()
        if index is None or self.owner.busy():return
        from .review_gui import SongReviewDialog
        dialog=SongReviewDialog(self,self.rows[index])
        dialog.exec();dialog.dispose();dialog.deleteLater()

    def rescan_bulk(self,*args):
        if self.root and not self.owner.busy():self.scan(getattr(self,'input_path',self.root))
    def filter_rows(self,*args):
        query=self.search.text().casefold().strip();mode=self.filter.currentIndex()
        for i,row in enumerate(self.rows):
            text=' '.join([row['path'],*row['metadata'].values()]).casefold()
            visible=(not query or query in text) and (mode==0 or (mode==1 and bool(row['errors'])) or (mode==2 and not row['errors']))
            self.table.setRowHidden(i,not visible)
        if self.table.currentRow()>=0 and self.table.isRowHidden(self.table.currentRow()):
            self.table.clearSelection();self.table.setCurrentCell(-1,-1)
            for i in range(len(self.rows)):
                if not self.table.isRowHidden(i):self.table.selectRow(i);break
    def selection_changed(self,*args):
        checked=sum(self.table.item(i,0) is not None and self.table.item(i,0).checkState()==Qt.Checked for i in range(len(self.rows)))
        blocked=sum(bool(r['errors']) for r in self.rows)
        self.selection_summary.setText(f'{checked} checked of {len(self.rows)} • {blocked} blocked / need help • Selection applies to the whole queue')
        self.export_button.setText(f'Start cleaning · {checked} '+('song' if checked==1 else 'songs') if checked else 'Start cleaning')
        if self.four_fret:self.export_button.setText(f'Prepare && export · {checked} songs')
        if self.unified:
            checking=self.goal_choice.currentIndex()==0
            self.export_button.setText('Check only — save scan report' if checking else f'Export reviewed copies · {checked} songs')
            self.export_button.setEnabled(not checking and bool(checked) and not self.owner.busy())
            self.approve.setEnabled(not checking and not self.owner.busy())
    def set_checked(self,checked,ready_only=False):
        if self.owner.busy():return
        self.table.blockSignals(True)
        for i,row in enumerate(self.rows):self.table.item(i,0).setCheckState(Qt.Checked if checked and (not ready_only or not row['errors']) else Qt.Unchecked)
        self.table.blockSignals(False);self.approve.setChecked(False);self.selection_changed()
        self.status.setText('Selection updated. Blocked songs cannot export; their reasons will be recorded in the results. Review changes, approve the reviewed changes, then export.' if checked else 'Selection cleared.')
    def browse(self):
        path=QFileDialog.getExistingDirectory(self,'Choose a song folder or parent directory')
        if path:self.scan(path)
    def scan(self,path):
        if self.owner.busy():return
        self.owner.goal='orange' if self.four_fret else 'clean'
        # A new batch starts with no leftover search text or status filter hiding its songs.
        self.search.blockSignals(True);self.search.clear();self.search.blockSignals(False)
        self.filter.blockSignals(True);self.filter.setCurrentIndex(0);self.filter.blockSignals(False)
        self.detail_tabs.setCurrentWidget(self.details)
        self.input_path=Path(path).resolve();self.root=self.input_path.parent if self.input_path.is_file() else self.input_path;self.source_label.setText(self.root.name or str(self.root));self.source_label.setToolTip(str(self.root));self.steps.set_step(0);self.output_path.setText(str(self.root.parent/('GH3 Four Fret Output' if self.four_fret else 'GH3 Cleaned Output')));self.approve.setChecked(False);self.last_output=None;self.rows=[];self.render()
        options=self.inspection_options()
        self.owner.run_job('Scanning charts and preparing cleanup review…',lambda cancel:scan_charts(self.input_path,cancel,lambda done,total,name:self.owner.worker.progress.emit(done,total,name),inspect_options=options),self.scanned,True)
    def scanned(self,rows):
        self.rows=rows;self.render();self.steps.set_step(1)
        if self.unified and rows:self.scroll_timer.start(0)
        self.status.setText(f'{len(rows)} song folders found; {sum(not r["errors"] for r in rows)} ready for review. Select each row to inspect changes. Cancelled scans may show partial results.')
    def reveal_review(self):
        if not self.isVisible():return
        body=self.review_scroll.widget();body.layout().activate();body.adjustSize()
        self.review_scroll.verticalScrollBar().setValue(self.table.mapTo(body,QPoint(0,0)).y())
    def render(self,preserve_selection=False):
        previous={self.rows[i]['path']:self.table.item(i,0).checkState() for i in range(min(len(self.rows),self.table.rowCount())) if self.table.item(i,0)} if preserve_selection else {}
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        for index,row in enumerate(self.rows):
            self.table.insertRow(index)
            check=QTableWidgetItem();check.setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable|Qt.ItemIsUserCheckable);check.setCheckState(Qt.Unchecked if row['errors'] else previous.get(row['path'],Qt.Checked));self.table.setItem(index,0,check)
            fallback=Path(row['path']).parent.name if Path(row['path']).suffix.lower() in ('.chart','.mid','.midi') else Path(row['path']).name
            values=[row['metadata'].get('Name','') or fallback,row['metadata'].get('Artist','') or '(missing)','BLOCKED: '+'; '.join(row['errors']) if row['errors'] else ('Ready · '+str(len(row['changes']))+' changes' if row['changes'] else 'Ready · no note repairs'),row['path']]
            for col,value in enumerate(values,1):
                item=QTableWidgetItem(value);item.setToolTip(value)
                if col==3:item.setForeground(QBrush(QColor('#ffb4a8' if row['errors'] else '#86dfba')))
                self.table.setItem(index,col,item)
        self.table.blockSignals(False)
        if self.rows:self.table.selectRow(0)
        self.show_details();self.selection_changed();self.filter_rows()
    def selected(self):
        index=self.table.currentRow()
        return index if 0<=index<len(self.rows) else None
    def show_details(self,*args):
        index=self.selected()
        self.sync_button.setEnabled(index is not None and bool(self.rows[index].get('sync_source')) and bool(self.rows[index].get('audio_format')) and not self.owner.busy())
        self.preview_button.setEnabled(index is not None and bool(self.rows[index].get('sync_source')) and not self.owner.busy())
        if index is None:self.details.clear();return
        row=self.rows[index]
        lines=['NEEDS CORRECTION' if row['errors'] else 'READY FOR YOUR REVIEW',
               'Song: '+(row['metadata'].get('Name','') or Path(row['path']).parent.name),
               'Artist: '+(row['metadata'].get('Artist','') or '(missing)'),
               'Audio: '+(Path(row['audio']).name if row['audio'] else '(needs matching recording)'),'',
               ('Scope: create Medium from selected Expert/Hard; additional difficulty choices are listed below.' if self.four_fret else 'Scope: retain difficulty arrangements; apply only reviewed compatibility repairs. Forced intent is converted to TheGHOST flips; taps become HOPOs.'),'']
        if row.get('sync_values'):
            values=row['sync_values'];lines += [f"Stored Offset: {values['offset_seconds']:g} s; song.ini delay: {values['delay_ms']:g} ms",'Synchronization: '+('manually reviewed for this source' if row.get('sync_review') else ('automatic — song.ini delay only' if row.get('synchronization',{}).get('automatic') else 'no adjustment needed')),'']
        lines += row.get('summary',[])
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
        sync_review=overrides.pop('sync_review',row.get('sync_review'))
        self.approve.setChecked(False)
        if metadata is not None:
            row['metadata'].update(metadata)
            self.table.item(index,1).setText(row['metadata'].get('Name',''))
            self.table.item(index,2).setText(row['metadata'].get('Artist',''))
            self.show_details()
        def ready(value):
            self.rows[index]=value;self.render(preserve_selection=True);self.table.selectRow(index);self.show_details()
            self.status.setText('Edits retained in this review. '+('Chart still needs correction: '+ '; '.join(value['errors']) if value['errors'] else 'Ready for review and export.')+' Export writes these edits to a new folder; originals stay unchanged.')
        options=self.inspection_options()
        self.owner.run_job('Rechecking selected song…',lambda cancel:inspect_chart(path,audio,metadata,sync_review=sync_review,**options),ready)
    def review_sync(self):
        index=self.selected()
        if index is None or self.owner.busy():return
        row=self.rows[index]
        if not row.get('sync_source') or not row.get('audio_format'):
            self.status.setText('Choose a valid chart and matching recording before synchronization review.');return
        from .sync_gui import SynchronizationDialog
        try:dialog=SynchronizationDialog(row,self)
        except Exception as exc:self.status.setText('Cannot preview synchronization: '+str(exc));return
        try:
            if dialog.exec()==QDialog.Accepted:self.recheck(index,sync_review=dialog.review)
        finally:dialog.stop_media();dialog.deleteLater()
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
            if row.get('sync_values'):lines+=['TIMING: '+json.dumps(row['sync_values'])]
            if row.get('synchronization'):lines+=['REVIEWED SYNC: '+json.dumps(row['synchronization'])]
            for anchor in row.get('anchor_checks',[]):lines+=['ANCHOR: '+json.dumps(anchor)]
            lines+=row.get('summary',[])
            lines+=['CHANGE: '+json.dumps(c,ensure_ascii=False) for c in row['changes']]
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
        if not self.approve.isChecked():self.status.setText('Check the review approval above, then use the export button.');return
        if not self.output_path.text().strip():self.status.setText('Set an output folder using Change output folder.');return
        self.export_to(Path(self.output_path.text().strip()))
    def export_to(self,path):
        if self.owner.busy() or not self.approve.isChecked():return
        if self.unified and self.goal_choice.currentIndex()==0:return
        selected=[row for i,row in enumerate(self.rows) if self.table.item(i,0).checkState()==Qt.Checked]
        if not selected:self.status.setText('Check at least one song.');return
        path=Path(path).resolve()
        if path==self.root or path.is_relative_to(self.root):self.status.setText('Cannot start: output must be outside the scanned source folder. Change output folder above.');return
        self.owner.goal='orange' if self.four_fret else 'clean';self.steps.set_step(2)
        self.status.setText(f'Starting cleanup of {len(selected)} checked songs. Output: {path}')
        def ready(results):
            self.last_output=Path(path) if (Path(path)/'cleanup_summary.json').exists() else None
            self.status.setText(f'Export finished: {sum(r["status"]=="exported" for r in results)} exported, {sum(r["status"]=="failed" for r in results)} failed; {len(selected)-len(results)} unprocessed. Open results & logs for details.')
            lines=['OUTPUT: '+str(path),'LOG: '+str(Path(path)/'cleanup.log'),'']
            for result in results:
                lines.append(('EXPORTED: ' if result['status']=='exported' else 'NEEDS HELP: ')+result['source'])
                lines.append(result.get('folder',result.get('error','')))
                if result.get('audio_recovered'):lines.append('Audio recovered automatically with FFmpeg; see validation.json for checks.')
                lines.append('')
            self.results.setPlainText('\n'.join(lines));self.detail_tabs.setCurrentWidget(self.results);self.approve.setChecked(False)
        self.owner.run_job('Cleaning and exporting song folders…',lambda cancel:export_cleaned(selected,path,self.root,cancel,lambda done,total,name:self.owner.worker.progress.emit(done,total,name)),ready,True)
    def open_folder(self):
        if self.last_output:QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.last_output)))
    def update_busy(self,busy,cancellable):
        for widget in (self.goal_choice,self.option_toggle if self.unified else self.goal_choice,self.create_easy,self.fill_missing,self.repair_others,self.repair_sustains,self.repair_orange,self.chart_file_button,self.preview_button,self.bulk_source,self.bulk_sustains,self.scan_button,self.metadata_button,self.audio_button,self.chart_button,self.table,self.approve,self.export_button,self.select_all,self.select_ready,self.select_none,self.output_path,self.output_button,self.save_report,self.search,self.filter,self.sync_button):widget.setEnabled(not busy)
        self.export_button.setEnabled(not busy and bool(self.rows))
        self.cancel_button.setEnabled(busy and cancellable)
        self.open_output.setEnabled(not busy and self.last_output is not None)
        if not busy:self.show_details();self.selection_changed()
