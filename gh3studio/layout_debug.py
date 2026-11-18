"""Read-only layout evidence included automatically in failed GUI size assertions."""
import json
from PySide6.QtCore import qVersion
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QWidget,QScrollArea


def layout_report(window):
    def size(value):return [value.width(),value.height()]
    def describe(widget):
        text=getattr(widget,'text',lambda:'')()
        return {'type':type(widget).__name__,'name':widget.objectName(),
                'text':str(text)[:100],'visible':widget.isVisible(),
                'size':size(widget.size()),'minimum':size(widget.minimumSize()),
                'minimum_hint':size(widget.minimumSizeHint()),'font':widget.font().toString()}
    central=window.centralWidget();layout=central.layout()
    report={'qt':qVersion(),'platform':QGuiApplication.platformName(),
            'style':window.style().objectName(),'pixel_ratio':window.devicePixelRatioF(),
            'logical_dpi':window.logicalDpiX(),'window':describe(window),
            'central_rows':[size(layout.itemAt(i).minimumSize()) for i in range(layout.count())],
            'pages':{name:describe(getattr(window,name)) for name in
                     ('welcome','cleaner','adapt','audio','converter','library','playback','tabs')}}
    widest=sorted(central.findChildren(QWidget),key=lambda w:w.minimumSizeHint().width(),reverse=True)[:16]
    report['widest_widgets']=[describe(widget) for widget in widest]
    report['scroll_areas']=[{'size':size(w.size()),'horizontal_max':w.horizontalScrollBar().maximum(),
                            'vertical_max':w.verticalScrollBar().maximum()} for w in central.findChildren(QScrollArea)]
    return json.dumps(report,indent=2,ensure_ascii=True)
