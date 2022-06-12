import json.decoder

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox


class FileItem(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.file_name = QtWidgets.QLabel()
        self.file_size = QtWidgets.QLabel()
        self.print_button = QtWidgets.QPushButton()
        self.print_button.setText("🤙")
        self.print_button.setStyleSheet("""
            QPushButton {
                margin: 0;
                padding: 0;
                border: None
            }
            QPushButton::hover {
                font-size: 25px;
            }
        """)
        self.print_button.clicked.connect(self.start_printing)
        self.setStyleSheet(
            """
            QLabel {
                margin: 0;
                padding: 0;
            }
            """
        )

        side_v_box = QtWidgets.QVBoxLayout()
        side_v_box.addWidget(self.file_name)
        side_v_box.addWidget(self.file_size)
        main_h_box = QtWidgets.QHBoxLayout()
        main_h_box.addLayout(side_v_box)
        main_h_box.addWidget(self.print_button)
        self.setLayout(main_h_box)

    def set_file_name(self, file_name):
        self.file_name.setText(file_name)

    def set_file_size(self, file_size):
        self.file_size.setText(file_size)

    def start_printing(self):
        res = self.parent().parent().parent().oct_client.print_selected_file(self.file_name.text())

        try:
            error = res.json()
            QMessageBox.critical(
                self, "Printing Status", error["error"],
                QMessageBox.Ok)
        except json.decoder.JSONDecodeError:
            QMessageBox.information(
                self, "Printing Status", "Start printing",
                QMessageBox.Ok)
