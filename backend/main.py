import sys

import firebase_admin
import firebase_admin
from PyQt5.QtCore import QCoreApplication
from firebase_admin import firestore, credentials

from PyQt5 import QtWidgets

from octoclient import OctoClient
from backend.login import Login
from backend.tab_widgets import FileTab, StateTab, MonitorTab, MaterialTab
from backend.threads import CheckConnection


class VLine(QtWidgets.QFrame):
    """VLine taken from
    https://stackoverflow.com/a/57944421/12751554
    """
    def __init__(self):
        super(VLine, self).__init__()
        self.setFrameShape(self.VLine | self.Sunken)


class TabWidget(QtWidgets.QTabWidget):
    def __init__(self, octo, firestore_client, parent=None):
        super(TabWidget, self).__init__(parent)
        self.octo = octo
        self.firestore_client = firestore_client

    def init_ui(self, machine_id):
        self.state_tab = StateTab(self, self.octo)
        self.file_tab = FileTab(self, self.octo)
        self.monitor_tab = MonitorTab(self, self.octo, self.firestore_client, machine_id)
        self.material_tab = MaterialTab(self)

        self.addTab(self.state_tab, "Status")
        self.addTab(self.file_tab, "Files")
        self.addTab(self.monitor_tab, "Monitor")
        self.addTab(self.material_tab, "Material")

    def closeEvent(self, event):
        if self.monitor_tab.thread_is_running:
            self.monitor_tab.video_thread_worker.quit()
            self.monitor_tab.predict_thread_worker.quit()

    def log_out(self):
        if self.monitor_tab.thread_is_running:
            self.monitor_tab.video_thread_worker.quit()
            self.monitor_tab.predict_thread_worker.quit()
        self.close()
        if self.parent().login_window.exec_() == QtWidgets.QDialog.Accepted:
            self.show()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Set up firestore authorization for monitor tab
        cred = credentials.Certificate("service_account.json")
        firebase_admin.initialize_app(cred)
        firestore_client = firestore.client()

        octo = OctoClient(use_cap=False)
        self.login_window = Login(firestore_client, parent=self)
        self.main_widget = TabWidget(octo, firestore_client, parent=self)
        self.machine_id = None

        self.connected = QtWidgets.QLabel()
        self.connected.setStyleSheet("border: none")
        self.connected.setText("Connected 🟢" if octo.is_connected() else "Closed 🔴")
        self.log_out_button = QtWidgets.QPushButton("Log out")
        self.log_out_button.clicked.connect(self.main_widget.log_out)
        self.log_out_button.setStyleSheet(
            """
            QPushButton {
                padding: 5px;
                border: 1px solid gray;
                border-radius: 5px;
                background-color: white;
            }
            QPushButton::hover {
                background-color: black;
                color: white;
            }
            """
        )

        self.statusBar().setStyleSheet('border: 0; background-color: #FFF8DC;')
        self.statusBar().setStyleSheet("QStatusBar::item {border: none;}")
        self.statusBar().addPermanentWidget(VLine())
        self.statusBar().addPermanentWidget(self.connected)
        self.statusBar().addPermanentWidget(VLine())
        self.statusBar().addPermanentWidget(self.log_out_button)

        self.check_thread = True
        if self.login_window.exec_() == QtWidgets.QDialog.Accepted:
            self.machine_id = self.login_window.machine_id
            windows = QtWidgets.QMessageBox()
            windows.setIcon(QtWidgets.QMessageBox.Information)
            windows.setText("Loading...")
            windows.addButton(QtWidgets.QMessageBox.Ok)
            windows.button(QtWidgets.QMessageBox.Ok).hide()
            windows.show()
            QtWidgets.QApplication.processEvents()

            self.main_widget.init_ui(self.machine_id)
            self.init_ui()

            windows.done(0)
            self.check_connected = CheckConnection(self, octo, self.connected)
            self.check_connected.start()
        else:
            sys.exit(0)

    def init_ui(self):
        self.setCentralWidget(self.main_widget)
        self.show()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    app.exec_()
