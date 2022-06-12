from pathlib import Path
from PyQt5 import QtWidgets
import joblib
from PyQt5.QtGui import QDoubleValidator

weight_path = f"{Path(__file__).parent.parent.parent}/weights"

infill_pattern_dict = {
    "grid": [1, 0],
    "honeycomb":      [0, 1]
}

material_dict = {
    "abs": [1, 0],
    "pla": [0, 1]
}


def not_empty(text):
    return text.strip() != ""


class MaterialTab(QtWidgets.QWidget):
    def __init__(self, parent):
        super(MaterialTab, self).__init__(parent)
        self.model = joblib.load(f"{weight_path}/material_cls")
        common_frame_style = """
            QFrame {
                background-color: white;
                border: 1px solid gray;
                border-radius: 5px;
            }

            QLabel {
                border: None
            }
            
            QLineEdit {
                padding: 5px;
                border: 0.5px solid gray;
                border-radius: 5px;
            }
            
            QLineEdit::focus {
               border: 1.5px solid black;
            }
        """
        # ========== Input area =============
        input_grid_layout = QtWidgets.QGridLayout()

        self.layer_height_label = QtWidgets.QLabel("Layer Height (mm)")
        self.layer_height_input = QtWidgets.QLineEdit()
        self.layer_height_input.setValidator(QDoubleValidator() )
        self.layer_height_input.editingFinished.connect(self.predict_outcome)
        layer_height_v_layout = self.get_v_layout(self.layer_height_label, self.layer_height_input)
        input_grid_layout.addLayout(layer_height_v_layout, 0, 0)

        self.wall_thickness_label = QtWidgets.QLabel("Wall Thickness (mm)")
        self.wall_thickness_input = QtWidgets.QLineEdit()
        self.wall_thickness_input.setValidator(QDoubleValidator())
        self.wall_thickness_input.editingFinished.connect(self.predict_outcome)
        wall_thickness_v_layout = self.get_v_layout(self.wall_thickness_label, self.wall_thickness_input)
        input_grid_layout.addLayout(wall_thickness_v_layout, 0, 1)

        self.infill_density_label = QtWidgets.QLabel("Infill Density (%)")
        self.infill_density_input = QtWidgets.QLineEdit()
        self.infill_density_input.setValidator(QDoubleValidator())
        self.infill_density_input.editingFinished.connect(self.predict_outcome)
        infill_density_v_layout = self.get_v_layout(self.infill_density_label, self.infill_density_input)
        input_grid_layout.addLayout(infill_density_v_layout, 1, 0)

        self.infill_pattern_label = QtWidgets.QLabel("Infill Pattern")
        self.infill_pattern_input = QtWidgets.QComboBox()
        self.infill_pattern_input.currentIndexChanged.connect(self.predict_outcome)
        self.infill_pattern_input.addItems(["honeycomb", "grid"])
        infill_pattern_v_layout = self.get_v_layout(self.infill_pattern_label, self.infill_pattern_input)
        input_grid_layout.addLayout(infill_pattern_v_layout, 1, 1)

        self.nozzle_temp_label = QtWidgets.QLabel("Nozzle Temperature (°C)")
        self.nozzle_temp_input = QtWidgets.QLineEdit()
        self.nozzle_temp_input.setValidator(QDoubleValidator())
        self.nozzle_temp_input.editingFinished.connect(self.predict_outcome)
        nozzle_temp_v_layout = self.get_v_layout(self.nozzle_temp_label, self.nozzle_temp_input)
        input_grid_layout.addLayout(nozzle_temp_v_layout, 2, 0)

        self.bed_temp_label = QtWidgets.QLabel("Bed Temperature (°C)")
        self.bed_temp_input = QtWidgets.QLineEdit()
        self.bed_temp_input.setValidator(QDoubleValidator())
        self.bed_temp_input.editingFinished.connect(self.predict_outcome)
        bed_temp_v_layout = self.get_v_layout(self.bed_temp_label, self.bed_temp_input)
        input_grid_layout.addLayout(bed_temp_v_layout, 2, 1)

        self.print_speed_label = QtWidgets.QLabel("Print Speed (mm/s)")
        self.print_speed_input = QtWidgets.QLineEdit()
        self.print_speed_input.setValidator(QDoubleValidator())
        self.print_speed_input.editingFinished.connect(self.predict_outcome)
        print_speed_v_layout = self.get_v_layout(self.print_speed_label, self.print_speed_input)
        input_grid_layout.addLayout(print_speed_v_layout, 3, 0)

        self.material_label = QtWidgets.QLabel("Material")
        self.material_input = QtWidgets.QComboBox()
        self.material_input.currentIndexChanged.connect(self.predict_outcome)
        self.material_input.addItems(["abs", "pla"])
        material_v_layout = self.get_v_layout(self.material_label, self.material_input)
        input_grid_layout.addLayout(material_v_layout, 3, 1)

        self.fan_speed_label = QtWidgets.QLabel("Fan Speed (%)")
        self.fan_speed_input = QtWidgets.QLineEdit()
        self.fan_speed_input.setValidator(QDoubleValidator())
        self.fan_speed_input.editingFinished.connect(self.predict_outcome)
        fan_speed_v_layout = self.get_v_layout(self.fan_speed_label, self.fan_speed_input)
        input_grid_layout.addLayout(fan_speed_v_layout, 4, 0)
        input_frame = QtWidgets.QFrame()
        input_frame.setStyleSheet(common_frame_style)
        input_frame.setLayout(input_grid_layout)

        # ========== Predict =============
        predict_grid_layout = QtWidgets.QGridLayout()

        self.roughness_label = QtWidgets.QLabel("Roughness (µm)")
        self.roughness_predict = QtWidgets.QLabel("-")
        roughness_v_layout = self.get_v_layout(self.roughness_label, self.roughness_predict)
        predict_grid_layout.addLayout(roughness_v_layout, 0, 0)

        self.tension_label = QtWidgets.QLabel("Tension Strength (MPa)")
        self.tension_predict = QtWidgets.QLabel("-")
        tension_v_layout = self.get_v_layout(self.tension_label, self.tension_predict)
        predict_grid_layout.addLayout(tension_v_layout, 0, 1)

        self.elongation_label = QtWidgets.QLabel("Elongation (%)")
        self.elongation_predict = QtWidgets.QLabel("-")
        elongation_v_layout = self.get_v_layout(self.elongation_label, self.elongation_predict)
        predict_grid_layout.addLayout(elongation_v_layout, 1, 0)

        predict_frame = QtWidgets.QFrame()
        predict_frame.setStyleSheet(common_frame_style)
        predict_frame.setLayout(predict_grid_layout)

        # ========== Combine all =============
        main_v_layout = QtWidgets.QVBoxLayout()
        main_v_layout.addWidget(input_frame)
        main_v_layout.addWidget(predict_frame)

        self.setLayout(main_v_layout)

    @staticmethod
    def get_v_layout(*args):
        v_layout = QtWidgets.QVBoxLayout()
        for arg in args:
            v_layout.addWidget(arg)
        return v_layout

    def predict_outcome(self):
        if self.check_all_filled():
            get_features = self.obtain_features_from_val()
            predict = self.model.predict(get_features)
            self.roughness_predict.setText(f"{predict[0][0]:.3f}")
            self.tension_predict.setText(f"{predict[0][1]:.3f}")
            self.elongation_predict.setText(f"{predict[0][2]:.3f}")

    def obtain_features_from_val(self):
        layer_height = float(self.layer_height_input.text())
        wall_thickness = float(self.wall_thickness_input.text())
        infill_density = float(self.infill_density_input.text())
        infill_pattern = infill_pattern_dict[self.infill_pattern_input.currentText()]
        nozzle_temp = float(self.nozzle_temp_input.text())
        bed_temp = float(self.bed_temp_input.text())
        print_speed = float(self.print_speed_input.text())
        material = material_dict[self.material_input.currentText()]
        fan_speed = float(self.print_speed_input.text())

        return [[
            layer_height, wall_thickness, infill_density,
            nozzle_temp, bed_temp, print_speed,
            fan_speed, *infill_pattern, *material
        ]]

    def check_all_filled(self):
        return not_empty(self.layer_height_input.text()) and not_empty(self.wall_thickness_input.text()) and \
               not_empty(self.infill_density_input.text()) and not_empty(self.nozzle_temp_input.text()) and \
               not_empty(self.bed_temp_input.text()) and not_empty(self.print_speed_input.text()) and \
               not_empty(self.fan_speed_input.text())
