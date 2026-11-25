"""One playback/editor surface for a selected queue song; export stays in the queue."""
import copy
from types import SimpleNamespace
from PySide6.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QComboBox,QLabel,QPushButton
from .playback import PlaybackPanel
from .window_fit import fit_size
from .model import ChartError


class SongReviewDialog(QDialog):
    def __init__(self,queue,row):
        super().__init__(queue);self.queue=queue;self.row=row
        self.setWindowTitle('Review song — original / prepared');fit_size(self,940,680)
        layout=QVBoxLayout(self)
        self.message=QLabel('Compare tracks, listen and edit the prepared copy. Export is always in the Songs queue. Timing changes use Timing tools.');self.message.setWordWrap(True);layout.addWidget(self.message)
        self.view=QComboBox();self.view.addItems(['Original','Prepared']);layout.addWidget(self.view)
        # Isolate playback from the advanced converter's working state.
        proxy=SimpleNamespace(report=row.get('conversion',{}),converted=row.get('song'),
            busy=queue.owner.busy,log_line=queue.owner.log_line,browse=lambda:None)
        self.panel=PlaybackPanel(proxy);self.panel.set_focused(True);layout.addWidget(self.panel,1)
        self.panel.review_edit=self.edit
        self.panel.open_button.hide()  # Change matching audio in the queue, then recheck.
        self.panel.options_toggle.setText('Playback options')
        for group in (self.panel.shift_row,self.panel.shift_buttons,self.panel.sustain_row):
            for i in range(group.count()):
                widget=group.itemAt(i).widget()
                if widget:widget.hide()
        self.view.currentIndexChanged.connect(self.compare)
        close=QPushButton('Back to review');close.clicked.connect(self.accept);layout.addWidget(close)
        self.compare()
        if row.get('song'):self.view.setCurrentIndex(1)
        audio=row.get('audio','')
        if row.get('audio_stems'):
            self.message.setText(self.message.text()+' Preparing full-mix preview…')
            from .stems import cached_mix
            queue.owner.run_job('Preparing preview mix…',lambda cancel:cached_mix(row['audio_stems'],cancel=cancel),self.mixed)
        elif audio:self.panel.open_audio(audio)

    def mixed(self,value):
        self.panel.open_audio(value[0])
        self.message.setText('Full-mix preview ready. Export uses the original audio tracks. Timing changes use Timing tools.')

    def compare(self,*args):
        prepared=self.view.currentIndex()==1
        song=self.row.get('song') if prepared else self.row.get('sync_source')
        self.panel.set_chart(song,'Medium' if prepared else 'Expert')
        # Preview against the original recording, which has no exported padding.
        sync=self.row.get('synchronization',{})
        self.panel.highway.shift=-sync.get('audio_padding_seconds',0) if prepared else self.row.get('sync_values',{}).get('delay_ms',0)/1000
        self.panel.highway.update()
        self.panel.edit_button.setEnabled(bool(prepared and song) and not self.queue.owner.busy() and not (self.queue.unified and self.queue.goal_choice.currentIndex()==0))
        if prepared and not song:self.message.setText('Prepared output is blocked. Read the listed issues, adjust repair choices or correct the source, then rescan.')

    def edit(self):
        if self.view.currentIndex()!=1 or not self.row.get('song'):return
        if self.queue.unified and self.queue.goal_choice.currentIndex()==0:return
        from .editor_gui import ChartEditorDialog
        dialog=ChartEditorDialog(self.panel,apply_callback=self.apply_edits)
        dialog.exec();dialog.deleteLater();self.compare()

    def apply_edits(self,song,changes):
        from .chart_editor import check_editor_song
        from .editing import prepare_cleanup
        from .hopo import is_flip
        check_editor_song(song)
        if any(n.lane==4 for n in song.tracks.get('Medium',[])):raise ChartError('Orange is prohibited in Medium')
        checked,report=prepare_cleanup(song,True,True)
        if report['remaining_errors'] or checked.tracks!=song.tracks:raise ChartError('Edits need compatibility repairs; correct sustains before applying.')
        if any(not is_flip(m) for ms in song.modifiers.values() for _,m in ms):raise ChartError('Unsupported markers remain')
        if not any(song.tracks.values()):raise ChartError('Cannot apply an empty chart')
        self.row['song']=copy.deepcopy(song);self.panel.owner.converted=self.row['song']
        self.row['changes'].append(dict(action='manual chart edits',edits=copy.deepcopy(changes)))
        from .cleaner import difficulty_summary
        self.row['summary']=difficulty_summary(self.row['sync_source'],song)
        self.queue.approve.setChecked(False);self.queue.show_details()

    def dispose(self):
        self.panel.shutdown()

    def done(self,result):
        if self.queue.owner.busy():return
        self.dispose();super().done(result)
