"""Goal-based entry points and credits for a single-song workflow."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor,QPainter,QPen
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QFrame,QScrollArea,QDialog,QTextBrowser,QDialogButtonBox
from .appearance import primary
from . import __version__

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
<p><b>Scope:</b> single-song workflow first. No built-in instrument separation or batch queue. TheGHOST/Wii/Dolphin acceptance is still a separate test.</p>
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
        eyebrow=QLabel('YOUR SONG. FOUR FRETS.');eyebrow.setObjectName('eyebrow');layout.addWidget(eyebrow)
        title=QLabel('What would you like to make?');title.setObjectName('hero');title.setWordWrap(True);layout.addWidget(title)
        intro=QLabel('Pick a starting point. We’ll guide one song from source to preview to an Ogg song folder.');intro.setWordWrap(True);intro.setObjectName('muted');layout.addWidget(intro)
        layout.addWidget(FretMotif())
        cards=QHBoxLayout();cards.setSpacing(16);layout.addLayout(cards)
        for key,number,title,body,steps,action in [
            ('orange','01','Keep the challenge. Lose Orange.','Start with an authored chart. Copy Hard or Expert into four-fret Medium, preserving every surviving note.','Open chart  →  Choose difficulty  →  Remove Orange  →  Listen & export','Open an existing chart'),
            ('audio','02','Start with the recording.','No chart yet? Analyze audio, choose the musical attacks to keep, then create and review a draft.','Choose audio  →  Review attacks  →  Create draft  →  Listen & export','Choose a recording')]:
            card=QFrame();card.setObjectName('card');col=QVBoxLayout(card);col.setContentsMargins(22,18,22,20);col.setSpacing(12)
            num=QLabel(number);num.setObjectName('cardNumber');col.addWidget(num)
            label=QLabel(title);label.setObjectName('cardTitle');label.setWordWrap(True);col.addWidget(label)
            label=QLabel(body);label.setObjectName('cardBody');label.setWordWrap(True);col.addWidget(label)
            col.addStretch();label=QLabel(steps);label.setWordWrap(True);label.setObjectName('muted');col.addWidget(label)
            button=QPushButton(action);primary(button);button.clicked.connect(lambda checked=False,g=key:owner.start_guided(g));col.addWidget(button);self.actions[key]=button;cards.addWidget(card,1)
        row=QHBoxLayout();layout.addLayout(row)
        refine=QPushButton('Advanced chart conversion / variations');refine.clicked.connect(lambda:owner.start_guided('refine'));row.addWidget(refine);self.actions['refine']=refine
        library=QPushButton('Browse local patterns');library.clicked.connect(lambda:owner.tabs.setCurrentWidget(owner.library));row.addWidget(library)
        self.resume=QPushButton('Continue current song');self.resume.clicked.connect(owner.resume_workflow);row.addWidget(self.resume)
        self.current=QLabel('One song at a time. Original files stay untouched.');self.current.setObjectName('muted');self.current.setWordWrap(True);layout.addWidget(self.current)
        layout.addStretch()
    def update_state(self):
        for button in self.actions.values():button.setEnabled(not self.owner.busy())
        self.resume.setEnabled(not self.owner.busy() and (self.owner.song is not None or self.owner.audio.path is not None))
        if self.owner.song:self.current.setText('Current song: '+self.owner.song.metadata.get('Name','Untitled')+' • '+self.owner.song.metadata.get('Artist','Unknown artist'))
        elif self.owner.audio.path:self.current.setText('Current recording: '+self.owner.audio.path.name)


def show_credits(parent):
    dialog=QDialog(parent);dialog.setWindowTitle('About & credits — GH3 Chart Studio '+__version__);dialog.resize(720,650)
    layout=QVBoxLayout(dialog);browser=QTextBrowser();browser.setOpenExternalLinks(True);browser.setHtml(CREDITS_HTML);layout.addWidget(browser)
    buttons=QDialogButtonBox(QDialogButtonBox.Close);buttons.rejected.connect(dialog.reject);layout.addWidget(buttons);dialog.exec();dialog.deleteLater()
