# -*- coding: utf-8 -*-

from typing import Optional

from PySide6.QtCore import Qt, Slot

from PySide6.QtWidgets import (
    QDialog, QWidget, QDialogButtonBox, QVBoxLayout, QLabel, QComboBox, QCheckBox, QGridLayout
)


class RasterLayerDialog(QDialog):

    def __init__(self, input_bands: list[str], nb_output_bands: int,
                 output_bands_names: list[str], parent: Optional[QWidget] = None):
        assert len(output_bands_names) == nb_output_bands
        super().__init__(parent)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setModal(True)
        self.setWindowTitle("Choose 1B layer bands")
        # band comboboxes and labels
        self.band_comboboxes = []
        self.band_labels = []
        for i in range(nb_output_bands):
            self.band_comboboxes.append(QComboBox())
            self.band_comboboxes[i].addItems(input_bands)
            if len(input_bands) in (nb_output_bands, nb_output_bands+1):
                self.band_comboboxes[i].setCurrentIndex(i)
            else:
                self.band_comboboxes[i].setCurrentIndex(-1)
            self.band_comboboxes[i].activated.connect(self.test_enable_ok)
            self.band_labels.append(QLabel(output_bands_names[i]))
        # mask combobox label and checkbox
        self.mask_combobox = QComboBox()
        self.mask_combobox.addItems(input_bands)
        if len(input_bands) == nb_output_bands + 1:
            self.mask_combobox.setCurrentIndex(nb_output_bands)
        else:
            self.mask_combobox.setCurrentIndex(-1)
        self.mask_combobox.activated.connect(self.test_enable_ok)
        self.mask_combobox.setDisabled(True)
        self.mask_label = QLabel("Mask")
        self.mask_label.setDisabled(True)
        self.mask_checkbox = QCheckBox()
        self.mask_checkbox.stateChanged.connect(self.mask_combobox.setEnabled)
        self.mask_checkbox.stateChanged.connect(self.mask_label.setEnabled)
        self.mask_checkbox.stateChanged.connect(self.test_enable_ok)
        self.mask_checkbox.setChecked(False)
        # input layout
        self.input_layout = QGridLayout()
        for i in range(nb_output_bands):
            self.input_layout.addWidget(self.band_labels[i], i, 1)
            self.input_layout.addWidget(self.band_comboboxes[i], i, 2)
        self.input_layout.addWidget(self.mask_checkbox, nb_output_bands, 0)
        self.input_layout.addWidget(self.mask_label, nb_output_bands, 1)
        self.input_layout.addWidget(self.mask_combobox, nb_output_bands, 2)
        # buttons
        self.button_box = QDialogButtonBox()
        self.cancel_button = self.button_box.addButton(QDialogButtonBox.StandardButton.Cancel)
        self.cancel_button.clicked.connect(self.reject)
        self.ok_button = self.button_box.addButton(QDialogButtonBox.StandardButton.Ok)
        self.ok_button.clicked.connect(self.accept)
        # main layout
        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.input_layout)
        self.main_layout.addWidget(self.button_box)
        self.setLayout(self.main_layout)
        self.test_enable_ok()

    @Slot()
    def test_enable_ok(self) -> None:
        enable_ok = True
        for combobox in self.band_comboboxes:
            if combobox.currentIndex() == -1:
                enable_ok = False
        if self.mask_checkbox.checkState() == Qt.CheckState.Checked and self.mask_combobox.currentIndex() == -1:
            enable_ok = False
        self.ok_button.setEnabled(enable_ok)
