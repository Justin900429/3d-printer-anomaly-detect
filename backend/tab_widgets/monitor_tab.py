import time
from pathlib import Path
import queue

import cv2
import torch.nn
from PyQt5 import QtWidgets
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt

import numpy as np
from torchvision import transforms
import onnxruntime as ort
import timm

from backend.threads import VideoWorkerThread, PredictThread

weight_path = f"{Path(__file__).parent.parent.parent}/weights"

index_to_cls = [
    "<font color='green'>No defected</font>",
    "<font color='red'>Defect</font>"
]


def reload_weight(weight_path):
    weight = torch.load(weight_path, map_location="cpu")
    new_weight = dict()
    for key, val in weight.items():
        new_weight[key.replace("model.", "")] = val
    return new_weight


class MonitorTab(QtWidgets.QWidget):
    def __init__(self, parent, client, use_onnx=True):
        super(MonitorTab, self).__init__(parent)

        self.client = client
        self.use_onnx = use_onnx
        self.img_queue = queue.Queue(maxsize=200)

        # ================ Model ===================
        self.transform = transforms.Compose([
            transforms.Lambda(lambda x: cv2.cvtColor(x, cv2.COLOR_RGB2BGR)),
            transforms.ToTensor(),
            transforms.Resize((400, 400)),
            transforms.CenterCrop((352, 352)),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]),
            transforms.Lambda(lambda x: x.unsqueeze(0)) \
                if not self.use_onnx else transforms.Lambda(lambda x: x.unsqueeze(0).numpy())
        ])

        if use_onnx:
            self.model = ort.InferenceSession(f"{weight_path}/resnet.onnx")
        else:
            self.model = timm.create_model("resnet34", pretrained=False)
            self.model.fc = torch.nn.Linear(
                self.model.fc.weight.shape[1], 2)
            self.model.load_state_dict(reload_weight(f"{weight_path}/resnet.pt"))
            self.model.eval()

        self.video_display_label = QtWidgets.QLabel()
        self.video_display_label.setFixedSize(500, 500)

        # Set up line edit validator for input ip-address
        self.ip_address = QtWidgets.QLineEdit()
        self.ip_address.setPlaceholderText("IP Address")
        self.ip_address.setInputMask("000.000.000.000")

        self.start_button = QtWidgets.QPushButton("Start Monitor")
        self.start_button.clicked.connect(self.start_video)
        self.start_button.setStyleSheet(
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

        self.stop_button = QtWidgets.QPushButton("Stop Monitor")
        self.stop_button.clicked.connect(self.stop_current_video)
        self.stop_button.setStyleSheet(
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

        self.predict_label = QtWidgets.QLabel("Detection")
        self.predict_label.setStyleSheet("""
            QLabel {
                margin: 0;
                padding: 0;
                font-weight: bold;
            }
        """)
        self.predict_text = QtWidgets.QLabel("-")

        side_panel_v_box = QtWidgets.QVBoxLayout()
        side_panel_v_box.setAlignment(Qt.AlignTop)
        side_panel_v_box.addWidget(self.ip_address)
        side_panel_v_box.addWidget(self.start_button)
        side_panel_v_box.addWidget(self.stop_button)
        side_panel_v_box.addWidget(self.predict_label)
        side_panel_v_box.addWidget(self.predict_text)

        side_panel_frame = QtWidgets.QFrame()
        side_panel_frame.setMinimumWidth(150)
        side_panel_frame.setLayout(side_panel_v_box)
        side_panel_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid gray;
                border-radius: 5px;
            }
            
            QLabel {
                border: None
            } 
        """)

        main_h_box = QtWidgets.QHBoxLayout()
        main_h_box.addWidget(self.video_display_label, 1)
        main_h_box.addWidget(side_panel_frame)

        self.setLayout(main_h_box)
        self.thread_is_running = False

    def start_video(self):
        self.thread_is_running = True
        self.start_button.setEnabled(False)
        self.start_button.repaint()

        video_file = self.ip_address.text()
        self.video_thread_worker = VideoWorkerThread(self, video_file)
        self.predict_thread_worker = PredictThread(self)

        self.video_thread_worker.frame_data_updated.connect(self.update_video_frames)
        self.video_thread_worker.start()
        self.predict_thread_worker.trigger.connect(self.predict_img)
        self.predict_thread_worker.start()

    def stop_current_video(self):
        if self.thread_is_running:
            self.thread_is_running = False
            self.video_thread_worker.stop_thread()
            self.predict_thread_worker.stop_thread()

            self.video_display_label.clear()
            self.start_button.setEnabled(True)

            self.img_queue.queue.clear()
            self.predict_text.setText("-")

    @torch.no_grad()
    def predict_img(self):
        try:
            frame = self.img_queue.get_nowait()
        except queue.Empty:
            frame = None

        if (frame is not None) and \
                ("printing" in self.client.get_printed_progress()["job_state"].lower()):
            # Predict the image
            if self.use_onnx:
                outputs = self.model.run(None, {"input": self.transform(frame)})
                self.predict_text.setText(index_to_cls[int(outputs[0][0][1] > outputs[0][0][0])])
            else:
                outputs = self.model(self.transform(frame))
                self.predict_text.setText(index_to_cls[outputs.argmax(dim=-1).item()])
        else:
            self.predict_text.setText("-")

        time.sleep(0.1)

    def update_video_frames(self, video_frame):
        height, width, channels = video_frame.shape
        bytes_per_line = width * channels

        try:
            self.img_queue.put_nowait(video_frame)
        except queue.Full:
            self.img_queue.get_nowait()
            self.img_queue.put_nowait(video_frame)

        converted_Qt_image = QImage(
            video_frame, width, height, bytes_per_line, QImage.Format_RGB888)

        self.video_display_label.setPixmap(
            QPixmap.fromImage(converted_Qt_image).scaled(
                self.video_display_label.width(), self.video_display_label.height())
        )

    @staticmethod
    def pix_to_array(pixmap):
        h = pixmap.size().height()
        w = pixmap.size().width()

        q_image = pixmap.toImage()
        byte_str = q_image.bits().asstring(w * h * 4)

        img = np.frombuffer(byte_str, dtype=np.uint8).reshape((h, w, 4))
        return img
