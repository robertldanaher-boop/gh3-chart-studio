"""One-time, per-user acknowledgement before opening the studio."""
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextBrowser, QPushButton, QHBoxLayout, QMessageBox
from .welcome import legal_notice_text
from .appearance import apply_style, primary

ACCEPTED_KEY = 'onboarding/license_notice_accepted'


def has_accepted(settings):
    return settings.value(ACCEPTED_KEY, False, type=bool)


class FirstRunDialog(QDialog):
    def __init__(self, settings=None):
        super().__init__()
        self.settings = settings if settings is not None else QSettings('GH3ChartStudio', 'GH3ChartStudio')
        self.setWindowTitle('Welcome — License & disclaimer')
        self.resize(780, 680)
        apply_style(self)
        layout = QVBoxLayout(self)
        heading = QLabel('Before you begin')
        heading.setStyleSheet('font-size: 24px; font-weight: bold;')
        layout.addWidget(heading)
        intro = QLabel('For Wii chart workflows and other compatible chart-based games.\nPlease review the notice below. Your choice is saved for this Windows user.')
        intro.setWordWrap(True)
        layout.addWidget(intro)
        self.notice = QTextBrowser()
        layout.addWidget(self.notice)
        buttons = QHBoxLayout()
        self.decline = QPushButton('Disagree and close')
        self.agree = QPushButton('Agree and continue')
        primary(self.agree)
        self.agree.setAutoDefault(False)
        self.decline.setAutoDefault(False)
        buttons.addWidget(self.decline)
        buttons.addStretch()
        buttons.addWidget(self.agree)
        layout.addLayout(buttons)
        self.decline.clicked.connect(self.reject)
        self.agree.clicked.connect(self.save_acceptance)
        try:
            self.notice.setMarkdown(legal_notice_text())
        except OSError:
            self.notice.setPlainText('The license documents could not be loaded. Extract the complete application package and try again.')
            self.agree.setEnabled(False)

    def save_acceptance(self):
        self.settings.setValue(ACCEPTED_KEY, True)
        self.settings.sync()
        if self.settings.status() != QSettings.Status.NoError:
            QMessageBox.warning(self, 'Could not save your choice', 'Your acceptance could not be saved. Check your user settings permissions and try again, or close the application.')
            return
        self.accept()
