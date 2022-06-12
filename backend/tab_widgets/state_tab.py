from PyQt5 import QtWidgets

from backend.threads import UpdateStatus


class StateTab(QtWidgets.QWidget):
    def __init__(self, parent, octo):
        super(StateTab, self).__init__(parent)

        self.octo = octo
        common_label_style_sheet = """
            QLabel {
                margin: 0;
                padding: 0;
                font-size: 17pt;
                font-weight: bold;
            }
        """
        common_container_style = """
            QFrame {
                background-color: white;
                border: 1px solid gray;
                border-radius: 5px;
            }
            
            QLabel {
                border: None
            }
        """
        # ========= User info ==========
        self.user_role_label = QtWidgets.QLabel()
        self.user_role_label.setText("User Role")
        self.user_role_label.setStyleSheet(common_label_style_sheet)
        self.user_role_text = QtWidgets.QLabel()
        self.user_name_label = QtWidgets.QLabel()
        self.user_name_label.setText("User name")
        self.user_name_label.setStyleSheet(common_label_style_sheet)
        self.user_name_text = QtWidgets.QLabel()

        user_role_v_layout = QtWidgets.QVBoxLayout()
        user_role_v_layout.addWidget(self.user_role_label)
        user_role_v_layout.addWidget(self.user_role_text)
        user_name_v_layout = QtWidgets.QVBoxLayout()
        user_name_v_layout.addWidget(self.user_name_label)
        user_name_v_layout.addWidget(self.user_name_text)

        user_h_layout = QtWidgets.QHBoxLayout()
        user_h_layout.addLayout(user_role_v_layout)
        user_h_layout.addLayout(user_name_v_layout)

        user_frame = QtWidgets.QFrame()
        user_frame.setStyleSheet(common_container_style)
        user_frame.setLayout(user_h_layout)

        # ========= Connected and Job State ==========
        self.connected_label = QtWidgets.QLabel()
        self.connected_label.setText("Connected State")
        self.connected_label.setStyleSheet(common_label_style_sheet)
        self.connected_state = QtWidgets.QLabel()

        self.job_label = QtWidgets.QLabel()
        self.job_label.setText("Job State")
        self.job_label.setStyleSheet(common_label_style_sheet)
        self.job_state = QtWidgets.QLabel()
        self.job_progress = QtWidgets.QProgressBar()
        self.job_progress.setMaximumWidth(300)
        self.job_progress.setMinimum(0)
        self.job_progress.setMaximum(100)
        self.job_progress_text = QtWidgets.QLabel()

        job_progress_h_layout = QtWidgets.QHBoxLayout()
        job_progress_h_layout.addWidget(self.job_progress)
        job_progress_h_layout.addWidget(self.job_progress_text)

        connect_job_v_layout = QtWidgets.QVBoxLayout()
        connect_job_v_layout.addWidget(self.connected_label)
        connect_job_v_layout.addWidget(self.connected_state)
        connect_job_v_layout.addWidget(self.job_label)
        connect_job_v_layout.addWidget(self.job_state)
        connect_job_v_layout.addLayout(job_progress_h_layout)

        connect_job_frame = QtWidgets.QFrame()
        connect_job_frame.setStyleSheet(common_container_style)
        connect_job_frame.setLayout(connect_job_v_layout)

        # ========= Temperature State ==========
        self.tool_temp_label = QtWidgets.QLabel()
        self.tool_temp_label.setText("Tool Temperature")
        self.tool_temp_label.setStyleSheet(common_label_style_sheet)
        self.tool_temp = QtWidgets.QLabel()

        self.bed_temp_label = QtWidgets.QLabel()
        self.bed_temp_label.setText("Bed Temperature")
        self.bed_temp_label.setStyleSheet(common_label_style_sheet)
        self.bed_temp = QtWidgets.QLabel()

        temp_state_v_layout = QtWidgets.QVBoxLayout()
        temp_state_v_layout.addWidget(self.tool_temp_label)
        temp_state_v_layout.addWidget(self.tool_temp)
        temp_state_v_layout.addWidget(self.bed_temp_label)
        temp_state_v_layout.addWidget(self.bed_temp)

        temp_frame = QtWidgets.QFrame()
        temp_frame.setStyleSheet(common_container_style)
        temp_frame.setLayout(temp_state_v_layout)

        # ========= Profile State ==========
        self.x_speed_label = QtWidgets.QLabel()
        self.x_speed_label.setText("Axes x")
        self.x_speed_label.setStyleSheet(common_label_style_sheet)
        self.x_speed = QtWidgets.QLabel()

        self.y_speed_label = QtWidgets.QLabel()
        self.y_speed_label.setText("Axes y")
        self.y_speed_label.setStyleSheet(common_label_style_sheet)
        self.y_speed = QtWidgets.QLabel()

        self.z_speed_label = QtWidgets.QLabel()
        self.z_speed_label.setText("Axes z")
        self.z_speed_label.setStyleSheet(common_label_style_sheet)
        self.z_speed = QtWidgets.QLabel()

        self.e_speed_label = QtWidgets.QLabel()
        self.e_speed_label.setText("Axes e")
        self.e_speed_label.setStyleSheet(common_label_style_sheet)
        self.e_speed = QtWidgets.QLabel()

        speed_x_z_layout = QtWidgets.QVBoxLayout()
        speed_x_z_layout.addWidget(self.x_speed_label)
        speed_x_z_layout.addWidget(self.x_speed)
        speed_x_z_layout.addWidget(self.z_speed_label)
        speed_x_z_layout.addWidget(self.z_speed)

        speed_y_e_layout = QtWidgets.QVBoxLayout()
        speed_y_e_layout.addWidget(self.y_speed_label)
        speed_y_e_layout.addWidget(self.y_speed)
        speed_y_e_layout.addWidget(self.e_speed_label)
        speed_y_e_layout.addWidget(self.e_speed)

        speed_h_layout = QtWidgets.QHBoxLayout()
        speed_h_layout.addLayout(speed_x_z_layout)
        speed_h_layout.addLayout(speed_y_e_layout)

        speed_frame = QtWidgets.QFrame()
        speed_frame.setStyleSheet(common_container_style)
        speed_frame.setLayout(speed_h_layout)

        # ========= Combine all ==========
        up_h_box = QtWidgets.QHBoxLayout()
        up_h_box.addWidget(connect_job_frame, 2)
        up_h_box.addWidget(temp_frame, 1)

        main_v_box = QtWidgets.QVBoxLayout()
        main_v_box.addWidget(user_frame, 1)
        main_v_box.addLayout(up_h_box, 2)
        main_v_box.addWidget(speed_frame, 2)

        self.setLayout(main_v_box)
        self.reset_state()

        self.check_thread = True
        self.update_status = UpdateStatus(self)
        self.update_status.start()

    def set_connected_state(self):
        self.connected_state.setText(
            "Connected 🟢" if self.octo.is_connected() else "Closed 🔴")

    def set_job_state(self):
        job_state = self.octo.get_printed_progress()

        if self.octo.check_bed_heated():
            self.job_state.setText("Board heated")
            self.job_progress.setValue(0)
            self.job_progress_text.setText("not printed")
        elif self.octo.check_tool_heated():
            self.job_state.setText("Tool heated")
            self.job_progress.setValue(0)
            self.job_progress_text.setText("not printed")
        elif "completion" in job_state:
            self.job_state.setText(job_state["job_state"])
            self.job_progress.setValue(job_state['completion'])
            self.job_progress_text.setText(f"{job_state['completion']:.2f}%")
        else:
            self.job_progress.setValue(0)
            self.job_state.setText(job_state["job_state"])
            self.job_progress_text.setText("not printed")

    def set_temp_state(self):
        try:
            temp_state = self.octo.get_all_temperature()
            self.tool_temp.setText(f"{temp_state['temperature']['tool0']['actual']}°C")
            self.bed_temp.setText(f"{temp_state['temperature']['bed']['actual']}°C")
        except KeyError:
            self.tool_temp.setText("NaN")
            self.bed_temp.setText("NaN")

    def set_speed_state(self):
        speed_state = self.octo.get_printer_profile()["axes"]
        annotations = ["x", "y", "z", "e"]
        targets = [self.x_speed, self.y_speed, self.z_speed, self.e_speed]

        for anno, target in zip(annotations, targets):
            speed_info = speed_state[anno]
            target.setText(f"Speed: {speed_info['speed']} Inverted: {speed_info['inverted']}")

    def set_user(self):
        user_profile = self.octo.get_current_user()
        self.user_role_text.setText(user_profile['role'])
        self.user_name_text.setText(user_profile["name"])

    def reset_state(self):
        self.set_connected_state()
        self.set_job_state()
        self.set_temp_state()
        self.set_speed_state()
        self.set_user()
