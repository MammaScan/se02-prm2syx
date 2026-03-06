import sys
import subprocess
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QRadioButton, QGroupBox, QFileDialog, QFrame, QButtonGroup
)

class SE02ToolGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SE-02 PRM → SYX")
        self.resize(520, 320)

        title = QLabel("SE-02 PRM → SYX")
        subtitle = QLabel("GUI prototype")

        mode_box = QGroupBox("Converter Mode")
        self.straight_radio = QRadioButton("Straight Convert")
        self.evolve_radio = QRadioButton("Patch Evolve")
        self.straight_radio.setChecked(True)

        self.mode_desc = QLabel("Convert PRM → SYX without modification.")

        mode_layout = QVBoxLayout()
        mode_layout.addWidget(self.straight_radio)
        mode_layout.addWidget(self.evolve_radio)
        mode_layout.addWidget(self.mode_desc)
        mode_box.setLayout(mode_layout)

        input_box = QGroupBox("Input Type")
        self.input_single = QRadioButton("Single Patch (.PRM)")
        self.input_folder = QRadioButton("Folder")
        self.input_single.setChecked(True)

        self.input_group = QButtonGroup()
        self.input_group.addButton(self.input_single)
        self.input_group.addButton(self.input_folder)

        input_layout = QVBoxLayout()
        input_layout.addWidget(self.input_single)
        input_layout.addWidget(self.input_folder)
        input_box.setLayout(input_layout)

        self.select_file_button = QPushButton("Select PRM file")
        self.select_output_button = QPushButton("Select output folder")
        self.convert_button = QPushButton("Convert")
        self.convert_button.setEnabled(False)

        self.input_label = QLabel("Input: No file or folder selected")
        self.output_label = QLabel("Output folder: out_sysex (next to input)")
        self.status_label = QLabel("Status: Ready")

        info_box = QFrame()
        info_box.setFrameShape(QFrame.StyledPanel)
        info_layout = QVBoxLayout()
        info_layout.addWidget(self.input_label)
        info_layout.addWidget(self.output_label)
        info_layout.addWidget(self.status_label)
        info_box.setLayout(info_layout)

        button_row = QHBoxLayout()
        button_row.addWidget(self.select_file_button)
        button_row.addWidget(self.select_output_button)
        button_row.addWidget(self.convert_button)

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(mode_box)
        layout.addWidget(input_box)
        layout.addWidget(info_box)
        layout.addLayout(button_row)
        self.setLayout(layout)

        self.selected_input = None
        self.selected_output_dir = None

        self.select_file_button.clicked.connect(self.select_file)
        self.select_output_button.clicked.connect(self.select_output_folder)
        self.convert_button.clicked.connect(self.convert_file)
        self.straight_radio.toggled.connect(self.update_mode_text)
        self.evolve_radio.toggled.connect(self.update_mode_text)
        self.input_single.toggled.connect(self.update_input_button_text)
        self.input_folder.toggled.connect(self.update_input_button_text)

        self.update_input_button_text()

    def update_mode_text(self):
        if self.straight_radio.isChecked():
            self.mode_desc.setText("Convert PRM → SYX without modification.")
            self.convert_button.setText("Convert")
        else:
            self.mode_desc.setText("Generate new patches by evolving seed patches.")
            self.convert_button.setText("Evolve")

    def update_input_button_text(self):
        if self.input_single.isChecked():
            self.select_file_button.setText("Select patch")
        elif self.input_folder.isChecked():
            self.select_file_button.setText("Select folder")

    def select_file(self):
        if self.input_folder.isChecked():
            folder_path = QFileDialog.getExistingDirectory(self, "Select PRM folder")
            if folder_path:
                self.selected_input = folder_path
                self.input_label.setText(f"Input folder: {Path(folder_path).name}")
        else:
            title = "Select PRM patch"
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                title,
                "",
                "PRM files (*.PRM);;All files (*)"
            )
            if file_path:
                self.selected_input = file_path
                self.input_label.setText(f"Input: {Path(file_path).name}")

        if self.selected_input:
            self.convert_button.setEnabled(True)
            self.status_label.setText("Status: Ready")

    def select_output_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select output folder")
        if folder_path:
            self.selected_output_dir = folder_path
            self.output_label.setText(f"Output folder: {Path(folder_path).name}")
            self.status_label.setText("Status: Ready")

    def convert_file(self):
        if not self.selected_input:
            return

        if self.evolve_radio.isChecked():
            self.status_label.setText("Status: Patch Evolve not implemented yet")
            return

        input_path = Path(self.selected_input)
        project_root = Path(__file__).resolve().parent.parent
        converter_path = project_root / "bin" / "prm2syx"

        cmd = [str(converter_path), str(input_path)]
        if self.selected_output_dir:
            cmd.extend(["--outdir", str(self.selected_output_dir)])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                if self.selected_output_dir:
                    self.output_label.setText(f"Output folder: {Path(self.selected_output_dir).name}")
                else:
                    self.output_label.setText("Output folder: out_sysex (next to input)")
                self.status_label.setText("Status: Conversion complete")
            else:
                error_text = result.stderr.strip() or result.stdout.strip() or "Unknown error"
                self.status_label.setText(f"Error: {error_text}")
        except Exception as e:
            self.status_label.setText(f"Error: {e}")

app = QApplication(sys.argv)
window = SE02ToolGUI()
window.show()
sys.exit(app.exec())
