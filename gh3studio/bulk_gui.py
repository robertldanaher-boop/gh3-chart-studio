"""Bulk Medium queue reuses recursive discovery, repairs and export diagnostics."""
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QDialog,QVBoxLayout
from .cleaner_gui import CleanerPanel

class BulkDialog(QDialog):
    def __init__(self,owner,parent=None):
        super().__init__(parent);self.owner=owner;self.setWindowTitle('Bulk four-fret Medium');self.resize(1024,700)
        self.panel=CleanerPanel(owner,four_fret=True)
        layout=QVBoxLayout(self);layout.addWidget(self.panel)
        self.timer=QTimer(self);self.timer.timeout.connect(self.refresh);self.timer.start(100)
        self.refresh()
    def refresh(self):
        self.panel.update_busy(self.owner.busy(),True)
        if self.owner.busy() or self.owner.operation_label.text().startswith('Could not complete:'):self.panel.status.setText(self.owner.operation_label.text())
    def reject(self):
        if self.owner.busy():return
        self.timer.stop();super().reject()
