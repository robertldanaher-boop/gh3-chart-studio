"""Checkbox review of detected attack candidates; no instrument classification."""
from PySide6.QtCore import QAbstractTableModel,Qt,Signal

class OnsetModel(QAbstractTableModel):
    selection_changed=Signal()
    def __init__(self,parent=None):
        super().__init__(parent);self.onsets=[];self.included=[]
    def reset_onsets(self,onsets):
        self.beginResetModel();self.onsets=list(onsets);self.included=[True]*len(onsets);self.endResetModel();self.selection_changed.emit()
    def rowCount(self,parent=None):return len(self.onsets)
    def columnCount(self,parent=None):return 3
    def headerData(self,section,orientation,role=Qt.DisplayRole):
        if role==Qt.DisplayRole:return ('Include','Time (s)','Attack strength')[section] if orientation==Qt.Horizontal else str(section+1)
    def data(self,index,role=Qt.DisplayRole):
        if not index.isValid():return None
        row,col=index.row(),index.column()
        if role==Qt.CheckStateRole and col==0:return Qt.Checked if self.included[row] else Qt.Unchecked
        if role==Qt.DisplayRole:
            if col==1:return f'{self.onsets[row]["time"]:.3f}'
            if col==2:return f'{self.onsets[row]["strength"]:.2f}'
        return None
    def flags(self,index):
        flags=Qt.ItemIsEnabled|Qt.ItemIsSelectable
        return flags|Qt.ItemIsUserCheckable if index.column()==0 else flags
    def setData(self,index,value,role=Qt.EditRole):
        if role!=Qt.CheckStateRole or not index.isValid() or index.column()!=0:return False
        self.included[index.row()]=value in (Qt.Checked,Qt.Checked.value)
        self.dataChanged.emit(index,index,[Qt.CheckStateRole]);self.selection_changed.emit();return True
    def select_all(self,value):
        self.included=[value]*len(self.onsets)
        if self.onsets:self.dataChanged.emit(self.index(0,0),self.index(len(self.onsets)-1,0),[Qt.CheckStateRole])
        self.selection_changed.emit()
    def selected(self):return [o for o,keep in zip(self.onsets,self.included) if keep]
