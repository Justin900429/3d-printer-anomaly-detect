from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QGraphicsDropShadowEffect


def check_in_db(machine_id, docs):
    for data in docs:
        if machine_id == data.to_dict()["id"]:
            return True


class Login(QtWidgets.QDialog):
    def __init__(self, firestore_client, parent=None):
        super(Login, self).__init__(parent)

        self.firestore_check_machine = firestore_client.collection(u"machines")

        self.setStyleSheet(
            "background-color: white;"
        )

        self.setFixedSize(350, 320)
        self.page_name = QtWidgets.QLabel("Login🔑", self)
        self.page_name.setStyleSheet(
            "font-size: 40pt;"
            "qproperty-alignment: AlignCenter;"
        )

        # Set up account label and edit line
        self.acc_label = QtWidgets.QLabel("Account:", self)
        self.acc_label.setStyleSheet(
            "font-size: 20pt;"
        )
        self.acc_edit = QtWidgets.QLineEdit(self)
        self.acc_edit.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.acc_edit.textChanged.connect(self.acc_text_change)
        self.acc_edit.setClearButtonEnabled(True)
        self.acc_edit.setPlaceholderText("Input your account")
        self.acc_edit.setStyleSheet(
            """
            QLineEdit {
                padding: 5px;
                border: 0.5px solid gray;
                border-radius: 5px;
                width: 180px;
            }
            QLineEdit[empty = "0"] {
                border: 1px solid red
            }
            QLineEdit[empty = "1"] {
            }
            QLineEdit::focus {
               border: 1.5px solid black;
            }
            """
        )
        acc_h_layout = QtWidgets.QHBoxLayout()
        acc_h_layout.addWidget(self.acc_label, 1, Qt.AlignLeft)
        acc_h_layout.addWidget(self.acc_edit, 2, Qt.AlignRight)

        # Set up password label and edit line
        self.pwd_label = QtWidgets.QLabel("Password:", self)
        self.pwd_label.setStyleSheet(
            "font-size: 20pt;"
        )
        self.pwd_edit = QtWidgets.QLineEdit(self)
        self.pwd_edit.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.pwd_edit.textChanged.connect(self.pwd_text_change)
        self.pwd_edit.setClearButtonEnabled(True)
        self.pwd_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.pwd_edit.setPlaceholderText("Input your password")
        self.pwd_edit.setProperty("empty", "1")
        self.pwd_edit.setStyleSheet(
            """
            QLineEdit {
                padding: 5px;
                border: 0.5px solid gray;
                border-radius: 5px;
                width: 180px;
            }
            QLineEdit[empty = "0"] {
                border: 1px solid red
            }
            QLineEdit[empty = "1"] {
            }
            QLineEdit::focus {
               border: 1.5px solid black;
            }
            """
        )
        pwd_h_layout = QtWidgets.QHBoxLayout()
        pwd_h_layout.addWidget(self.pwd_label, 1, Qt.AlignLeft)
        pwd_h_layout.addWidget(self.pwd_edit, 2, Qt.AlignRight)

        # Machine id
        self.machine_label = QtWidgets.QLabel("Machine ID:", self)
        self.machine_label.setStyleSheet(
            "font-size: 20pt;"
        )
        self.machine_edit = QtWidgets.QLineEdit(self)
        self.machine_edit.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.machine_edit.textChanged.connect(self.machine_text_change)
        self.machine_edit.setClearButtonEnabled(True)
        self.machine_edit.setPlaceholderText("Input your machine ID")
        self.machine_edit.setStyleSheet(
            """
            QLineEdit {
                padding: 5px;
                border: 0.5px solid gray;
                border-radius: 5px;
                width: 180px;
            }
            QLineEdit[empty = "0"] {
                border: 1px solid red
            }
            QLineEdit[empty = "1"] {
            }
            QLineEdit::focus {
               border: 1.5px solid black;
            }
            """
        )
        machine_h_layout = QtWidgets.QHBoxLayout()
        machine_h_layout.addWidget(self.machine_label, 1, Qt.AlignLeft)
        machine_h_layout.addWidget(self.machine_edit, 2, Qt.AlignRight)

        # Login button
        self.buttonLogin = QtWidgets.QPushButton('Login', self)
        shadow = QGraphicsDropShadowEffect()
        shadow.setColor(QColor(149, 157, 165, 51))
        shadow.setOffset(-5, 0)
        shadow.setBlurRadius(100)
        self.buttonLogin.setGraphicsEffect(shadow)
        self.buttonLogin.setStyleSheet(
            """
            QPushButton {
                padding: 5px;
                background-color: white;
            }
            QPushButton::hover {
                background-color: black;
                color: white;
            }
            """
        )
        self.buttonLogin.clicked.connect(self.check_login)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.page_name)
        layout.addLayout(acc_h_layout)
        layout.addLayout(pwd_h_layout)
        layout.addLayout(machine_h_layout)
        layout.addSpacing(25)
        layout.addWidget(self.buttonLogin)

    def check_login(self):
        if self.acc_edit.text().strip() == "" or self.pwd_edit.text().strip() == "":
            if self.acc_edit.text().strip() == "":
                self.acc_edit.setProperty("empty", "0")
                self.acc_edit.style().polish(self.acc_edit)
            if self.pwd_edit.text().strip() == "":
                self.pwd_edit.setProperty("empty", "0")
                self.pwd_edit.style().polish(self.pwd_edit)
        else:
            import os
            from dotenv import load_dotenv
            load_dotenv()

            account = self.acc_edit.text()
            password = os.getenv(account)

            if (password is not None) and (password == self.pwd_edit.text()) and \
                    check_in_db(self.machine_edit.text(), self.firestore_check_machine.stream()):
                self.get_id()
                self.acc_edit.clear()
                self.pwd_edit.clear()
                self.machine_edit.clear()
                self.accept()
            else:
                QtWidgets.QMessageBox.warning(self, "Error", 'Bad user or password')

    def acc_text_change(self, text):
        if text.strip() == "":
            self.acc_edit.setProperty("empty", "0")
        else:
            self.acc_edit.setProperty("empty", "1")
        self.acc_edit.style().polish(self.acc_edit)

    def pwd_text_change(self, text):
        if text.strip() == "":
            self.pwd_edit.setProperty("empty", "0")
        else:
            self.pwd_edit.setProperty("empty", "1")
        self.pwd_edit.style().polish(self.pwd_edit)

    def machine_text_change(self, text):
        if text.strip() == "":
            self.machine_edit.setProperty("empty", "0")
        else:
            self.machine_edit.setProperty("empty", "1")
        self.machine_edit.style().polish(self.machine_edit)

    def closeEvent(self, event):
        return self.reject()

    def get_id(self):
        self.machine_id = self.machine_edit.text()
