"""Goal-based entry points and credits for a single-song workflow."""
import sys
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor,QPainter,QPen
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QFrame,QScrollArea,QDialog,QTextBrowser,QDialogButtonBox,QTabWidget
from .appearance import primary
from . import __version__
from .window_fit import fit_size

CREDITS_HTML='''
<h1>Built with a community behind it</h1>
<p>GH3 Chart Studio is developed for Robert (Bob) Danaher. Thank you to the maintainers, researchers and chart authors whose work makes tools like this possible.</p>
<h2>Compatibility references</h2>
<p><b>Nanook and TeamGHOST — TheGHOST</b><br>
TheGHOST's chart importer, HOPO viewer behavior and documentation inform our Wii import profile. Credit to Nanook, SciFi, Humour4Fun, UnsteadyCarrot and GameZelda.<br>
<a href="https://github.com/Nanook/TheGHOST">TheGHOST project and source</a></p>
<p><b>TheNathannator and contributors — GuitarGame_ChartFormats</b><br>
Reference documentation for chart, MIDI and song.ini formats.<br>
<a href="https://github.com/TheNathannator/GuitarGame_ChartFormats">Chart format documentation</a></p>
<p>These projects were studied as compatibility references. Their implementations are not bundled or copied into this application. These credits do not imply endorsement or verified game compatibility.</p>
<h2>Libraries used by the application</h2>
<ul><li><b>Python / Python Software Foundation</b> — runtime and standard library, including Tkinter startup UI.</li>
<li><b>Qt / PySide6 / Shiboken — The Qt Company and contributors</b> — desktop interface and media playback; bundled notices cover applicable LGPL/GPL terms.</li>
<li><b>Mido</b> — MIDI reading and writing (MIT).</li>
<li><b>NumPy and SciPy communities</b> — numerical and audio analysis (BSD licenses).</li>
<li><b>SoundFile and libsndfile contributors</b> — audio decoding/encoding and metadata (BSD / LGPL).</li>
<li><b>CFFI and pycparser</b> — native-library bindings (MIT / BSD).</li></ul>
<h2>Development and packaging</h2>
<p>pytest, PyInstaller, pyinstaller-hooks-contrib, setuptools, packaging and their supporting dependencies. These tools have their own licenses; applicable notices are included in the <b>licenses</b> folder and collected for Windows builds.</p>
<p>GH3 Chart Studio's own code is MIT licensed. Source chart authors and artists retain their own credits; the export workflow preserves song/artist/charter metadata.</p>
<p><b>Scope:</b> existing-chart cleanup and four-fret adaptation. Recursive collection cleanup is available; instrument separation is not built in. TheGHOST/Wii/Dolphin acceptance is still a separate test.</p>
'''

class FretMotif(QWidget):
    def __init__(self):super().__init__();self.setMinimumHeight(82);self.setMaximumHeight(90)
    def paintEvent(self,event):
        p=QPainter(self);p.setRenderHint(QPainter.Antialiasing)
        colors=['#69e2ac','#ff7b88','#f0d779','#75b9ff']
        for lane,color in enumerate(colors):
            y=14+lane*18;p.setPen(QPen(QColor('#2b3c51'),1));p.drawLine(0,y,self.width(),y)
            for beat in range(7):
                x=25+beat*(self.width()-50)/7+lane*13
                if x>self.width()-20:continue
                if (beat+lane)%3==0:
                    p.setPen(QPen(QColor(color),3));p.drawLine(int(x),y,int(x+35),y)
                    p.setBrush(QColor(color));p.drawEllipse(int(x)-4,y-4,8,8)
        p.end()


class WelcomePanel(QWidget):
    def __init__(self,owner):
        super().__init__();self.owner=owner;self.actions={}
        outer=QVBoxLayout(self);scroll=QScrollArea();scroll.setWidgetResizable(True);outer.addWidget(scroll)
        body=QWidget();scroll.setWidget(body);layout=QVBoxLayout(body);layout.setContentsMargins(24,20,24,20);layout.setSpacing(14)
        eyebrow=QLabel('BUILT FOR YOUR GH3 WII COLLECTION');eyebrow.setObjectName('eyebrow');layout.addWidget(eyebrow)
        title=QLabel('Great charts. Your way to play.');title.setObjectName('hero');title.setWordWrap(True);layout.addWidget(title)
        intro=QLabel('Start with songs that are already charted. Conversion and compatibility cleanup now happen together.');intro.setWordWrap(True);intro.setObjectName('muted');layout.addWidget(intro)
        layout.addWidget(FretMotif())
        cards=QHBoxLayout();cards.setSpacing(16);layout.addLayout(cards)
        for key,number,title,description,steps,action in [
            ('orange','01','Prepare songs for GH3 Wii','Create challenging four-fret Medium and three-fret Easy from Expert or Hard. Clean all difficulties and export chart, audio and metadata together.','Choose songs → Review → Export · One song or a collection','Prepare my songs')]:
            card=QFrame();card.setObjectName('card');col=QVBoxLayout(card);col.setContentsMargins(22,18,22,20);col.setSpacing(12)
            num=QLabel(number);num.setObjectName('cardNumber');col.addWidget(num)
            label=QLabel(title);label.setObjectName('cardTitle');label.setWordWrap(True);col.addWidget(label)
            label=QLabel(description);label.setObjectName('cardBody');label.setWordWrap(True);col.addWidget(label)
            col.addStretch();label=QLabel(steps);label.setWordWrap(True);label.setObjectName('muted');col.addWidget(label)
            button=QPushButton(action);primary(button);button.clicked.connect(lambda checked=False,g=key:owner.enter_workspace(g));col.addWidget(button);self.actions[key]=button;cards.addWidget(card,1)
        clean=QPushButton('Clean only — keep existing difficulties');clean.clicked.connect(lambda:owner.enter_workspace('clean'));layout.addWidget(clean);self.actions['clean']=clean
        row=QHBoxLayout();layout.addLayout(row)
        self.resume=QPushButton('Continue current work');self.resume.clicked.connect(owner.resume_workflow);row.addWidget(self.resume);row.addStretch()
        self.current=QLabel('Choose Prepare my songs, then select a chart or a collection folder.');self.current.setObjectName('muted');self.current.setWordWrap(True);layout.addWidget(self.current)
        note=QLabel('Original files stay untouched. Audio experiments and pattern tools are available under Tools in reserve.');note.setObjectName('muted');note.setWordWrap(True);layout.addWidget(note)
        layout.addStretch()
    def update_state(self):
        for button in self.actions.values():button.setEnabled(not self.owner.busy())
        self.resume.setEnabled(not self.owner.busy() and (bool(self.owner.cleaner.rows) or self.owner.song is not None or self.owner.audio.path is not None))
        if self.owner.goal=='clean' and self.owner.cleaner.rows:self.current.setText(f'Current collection: {len(self.owner.cleaner.rows)} song folders. Continue to review or export.')
        elif self.owner.song:self.current.setText('Current song: '+self.owner.song.metadata.get('Name','Untitled')+' • '+self.owner.song.metadata.get('Artist','Unknown artist'))
        elif self.owner.audio.path:self.current.setText('Reserved audio experiment: '+self.owner.audio.path.name)


def legal_notice_text():
    root=Path(sys._MEIPASS) if getattr(sys,'frozen',False) else Path(__file__).resolve().parents[1]
    notice=(root/'docs'/'LICENSE_AND_DISCLAIMER.md').read_text(encoding='utf-8')
    license_text=(root/'LICENSE').read_text(encoding='utf-8')
    return notice+'\n\n# Full MIT License\n\n'+license_text


class AboutDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent);self.setWindowTitle('About, credits & license — GH3 Chart Studio '+__version__);fit_size(self,760,680)
        layout=QVBoxLayout(self);self.tabs=QTabWidget();layout.addWidget(self.tabs)
        credits=QTextBrowser();credits.setOpenExternalLinks(True);credits.setHtml(CREDITS_HTML);self.tabs.addTab(credits,'Credits')
        self.legal=QTextBrowser()
        try:self.legal.setMarkdown(legal_notice_text())
        except OSError as exc:self.legal.setPlainText('License documents could not be loaded. Extract the complete package, including LICENSE and docs/LICENSE_AND_DISCLAIMER.md.\n'+str(exc))
        self.tabs.addTab(self.legal,'License && disclaimer')
        buttons=QDialogButtonBox(QDialogButtonBox.Close);buttons.rejected.connect(self.reject);layout.addWidget(buttons)


def show_credits(parent):
    dialog=AboutDialog(parent);dialog.exec();dialog.deleteLater()
