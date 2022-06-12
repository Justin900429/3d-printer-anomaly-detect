import time

from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal


class PredictThread(QThread):
    trigger = pyqtSignal()

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def run(self):
        while self.parent.thread_is_running:
            time.sleep(1)
            self.trigger.emit()

    def stop_thread(self):
        self.wait()
        QtWidgets.QApplication.processEvents()
