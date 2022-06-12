import time

from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread


class CheckConnection(QThread):
    def __init__(self, parent, client, connected_state_text=None):
        super().__init__()
        self.parent = parent
        self.client = client
        self.connected_state_text = connected_state_text

    def run(self):
        while self.parent.check_thread:
            self.connected_state_text.setText(
                "Connected 🟢" if self.client.is_connected() else "Closed 🔴")
            time.sleep(5)

    def stop_thread(self):
        self.wait()
        QtWidgets.QApplication.processEvents()


class UpdateStatus(QThread):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def run(self):
        while self.parent.check_thread:
            self.parent.reset_state()
            time.sleep(5)

    def stop_thread(self):
        self.wait()
        QtWidgets.QApplication.processEvents()
