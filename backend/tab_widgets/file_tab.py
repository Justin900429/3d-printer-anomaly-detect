from pathlib import Path
import math

from PyQt5 import QtWidgets
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QMessageBox

from backend.tab_widgets.file_item import FileItem


class FileTab(QtWidgets.QWidget):
    def __init__(self, parent, oct_client):
        super(FileTab, self).__init__(parent)

        # Set up database
        self.oct_client = oct_client

        self.reload_btn = QtWidgets.QPushButton()
        self.reload_btn.setStyleSheet(
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
        self.reload_btn.setText("reload list")
        self.reload_btn.clicked.connect(self.reload_list)
        self.upload_btn = QtWidgets.QPushButton()
        self.upload_btn.setStyleSheet(
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
        self.upload_btn.setText("Upload file")
        self.upload_btn.clicked.connect(self.upload_file)

        self.list_view = QtWidgets.QListWidget()
        self.list_view.setStyleSheet(
            """
                QListWidget::item {
                    border: 0.5px solid gray;
                }
                QListWidget::item:selected {
                    border: 2px solid black;
                }
            """
        )
        self.load_file_list()

        side_h_box = QtWidgets.QHBoxLayout()
        side_h_box.addWidget(self.reload_btn)
        side_h_box.addWidget(self.upload_btn)
        side_v_box = QtWidgets.QVBoxLayout()
        side_v_box.addLayout(side_h_box)
        side_v_box.addWidget(self.list_view)

        self.setLayout(side_v_box)

    @staticmethod
    def readable_size_format(size_bytes):
        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        level = int(math.floor(math.log(size_bytes, 1024)))
        exp = math.pow(1024, level)
        base = round(size_bytes / exp, 2)
        return f"{base}{size_name[level]}"

    def load_file_list(self):
        file_info_list = self.oct_client.get_file_list()

        if len(file_info_list["files"]) > 0:
            for file_info in file_info_list["files"]:
                custom_widget = FileItem(self)
                custom_widget_item = QtWidgets.QListWidgetItem(self.list_view)
                custom_widget_item.setSizeHint(QSize(100, 100))
                custom_widget.set_file_name(f"{file_info['origin']}/{file_info['name']}")
                custom_widget.set_file_size(self.readable_size_format(file_info["size"]))

                self.list_view.addItem(custom_widget_item)
                self.list_view.setItemWidget(custom_widget_item, custom_widget)

    def reload_list(self):
        self.list_view.clear()
        self.load_file_list()

    def upload_file(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open File", str(Path.home()), filter="Gcode (*.gcode)")
        res = self.oct_client.upload_file(filename[0]).json()

        if res["done"]:
            QMessageBox.information(
                self, "Upload Result", "success",
                QMessageBox.Ok)
            self.reload_list()
        else:
            QMessageBox.critical(
                self, "Upload Result", "fail",
                QMessageBox.Ok)
