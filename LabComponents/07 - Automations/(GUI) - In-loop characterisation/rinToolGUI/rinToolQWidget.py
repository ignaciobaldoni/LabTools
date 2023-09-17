# -*- coding: utf-8 -*-
"""
Created on Tue Nov  9 15:26:16 2021

@author: akordts
"""
import datetime
import functools
import logging
import sys
import time
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
# %% imports
# %%% standard python classes
from PyQt5.QtCore import Qt
from PyQt5 import QtCore
from PyQt5.QtWidgets import (QApplication, QGridLayout, QGroupBox, QLabel, QLineEdit,
                             QPushButton, QRadioButton, QStyleFactory, QVBoxLayout, QFileDialog)

# import tool classes
from ESA_ElectricalSpectrumAnalyzer.ESA_HP_89410A import HP89410A
# standard utilities for saving data
from Utilities import saveDictToHdf5
from rinToolGUI.getScalarRangeData import getScalarRangeData
from rinToolGUI.initESAforRINmeasurement import initESAforRINmeasurement
from rinToolGUI.plotRinFigures import plotRinFigures

# region setup logging
logging.getLogger('pyvisa').setLevel(logging.INFO)

logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s] [%(name)s]   %(message)s")
logger = logging.getLogger('root')
logger.setLevel(logging.DEBUG)

filePath = r"."
time_str = time.strftime("%Y%m%d-%H%M%S")
filePath = filePath + '\\' + time_str + '-Igorevna-Log.txt'

fileHandler = logging.FileHandler(filePath)
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)
# endregion


@dataclass
class IntervalSpec:
    meas_time_interval: float = 0
    number_of_avgs: int = 0
    interval_label: str = ''
    interval_freqs: list = field(default_factory=list)


# noinspection PyArgumentList,PyTypeChecker
class RinToolQWidget(QGroupBox):
    # class members

    @staticmethod
    def init_freq_intervals():
        measTimes = [22 * 60, 130, 13, 1.3, 0.13, 0.05, 0.05, 0.05]
        standard_number_of_avgs = [0, 4, 15, 40, 80, 160, 200, 200]
        freq_range_values = 10. ** np.arange(-1, 8, 1)
        freq_range_values[0] = 0
        labels = ['0-1Hz', '1-10Hz', '10-100Hz', '100Hz-1kHz', '1-10kHz', '10-100kHz', '100KHz-1MHz', '1-10MHz']

        intervals = []
        for index in np.arange(len(measTimes)):
            interval = IntervalSpec()
            interval.meas_time_interval = measTimes[index]
            interval.interval_freqs = [freq_range_values[index], freq_range_values[index+1]]
            interval.number_of_avgs = standard_number_of_avgs[index]
            interval.interval_label = labels[index] + ' / ' + str(measTimes[index]) + 'sec'
            intervals = intervals + [interval]

        return intervals

    # signals
    spec_file_name_changed = QtCore.pyqtSignal(str)
    save_file_name_changed = QtCore.pyqtSignal(str)
    estimated_time_changed = QtCore.pyqtSignal(str)

    # region properties
    @property
    def freq_intervals(self):
        return self._freq_intervals

    @property
    def save_file_path(self):
        if self._save_file_path == '':
            return None
        else:
            return self._save_file_path

    @save_file_path.setter
    def save_file_path(self, file_name):
        self._save_file_path = file_name

    @property
    def spec_file_name(self):
        if self._spec_file_name == '':
            return None
        else:
            return self._spec_file_name

    @spec_file_name.setter
    def spec_file_name(self, file_name):
        self._spec_file_name = file_name

    @property
    def meas_label_text(self):
        return self._meas_label_text

    @meas_label_text.setter
    def meas_label_text(self, text):
        self._meas_label_text = text

    @property
    def spec_label_text(self):
        return self._meas_label_text

    @spec_label_text.setter
    def spec_label_text(self, text):
        self._spec_label_text = text

    # endregion

    # region class initialization
    def __init__(self, parent=None, file_meta_data=None, **kwds):
        super(RinToolQWidget, self).__init__(parent, **kwds)

        self.fileMetaData = file_meta_data

        self.hpTool = None

        self._is_cross_cor_conf = None
        self._dc_voltage = None
        self._freq_intervals = self.init_freq_intervals()

        self._save_file_path = ''
        self._spec_file_name = ''
        self._meas_label_text = ''
        self._spec_label_text = ''

        self.spec_file_name_changed.connect(
            functools.partial(
                RinToolQWidget.spec_file_name.fset,
                self
            ))

        # define duration per trace values in s
        self.measAvgs = []
        self.editList = []

        # defines elements
        self.define_main_layout()

    def __del__(self):
        self.disconnect_hp89410a()

    # endregion

    # region device connection
    def connect_to_hp89410a(self):

        if self.hpTool is None:
            try:
                self.hpTool = HP89410A()
                self.init_hp()
            except Exception as exc:
                logger.exception(exc)
                self.hpTool = None

    def init_hp(self):
        button = self.sender()
        self.hpTool.visaobj.timeout = None

        if isinstance(button, QPushButton):
            button.setStyleSheet("background-color: green")
        else:
            logger.debug("HP connected")

        data = self.hpTool.queryCmd('*IDN?')
        logger.debug(data)

        initESAforRINmeasurement(self.hpTool.visaobj, self._is_cross_cor_conf())

    def disconnect_hp89410a(self):
        if self.hpTool is not None:
            self.hpTool.disconnect()

    # endregion

    # region layout definition functions

    def define_main_layout(self):

        layout = QVBoxLayout()
        self.setLayout(layout)

        # define configuration selection group section
        configuration_selection_group = self.define_configuration_selection_group()
        layout.addWidget(configuration_selection_group)

        # frequenccy intervals section
        set_frequency_intervals_group = self.define_set_frequency_intervals_group()
        layout.addWidget(set_frequency_intervals_group)

        # file location section
        file_location_group = self.define_file_location_group()
        layout.addWidget(file_location_group)

        # plot setting section
        plot_settings_group = self.define_plot_settings_group()
        layout.addWidget(plot_settings_group)

        # start button
        start_measurement_button = QPushButton("Press to Start Measurement")
        start_measurement_button.setDefault(True)
        start_measurement_button.clicked.connect(self.start_measurement)
        layout.addWidget(start_measurement_button)

    def define_file_location_group(self):

        file_location_group = QGroupBox('File Location', alignment=Qt.AlignHCenter)
        layout = QVBoxLayout()
        file_location_group.setLayout(layout)

        # save file localtion
        save_file_location_push_button = QPushButton("Press to Set Savefile Name and Location (no filetype)")
        save_file_location_push_button.setDefault(True)
        # save_file_location_push_button.setStyleSheet("background-color: red")
        save_file_location_push_button.clicked.connect(self.set_save_file_location_push_button)
        layout.addWidget(save_file_location_push_button)

        save_file_path_label = QLineEdit('File location not set!', alignment=Qt.AlignHCenter)
        save_file_path_label.setStyleSheet("color: black")
        save_file_path_label.setReadOnly(True)

        # save_file_path_label.setDisabled(True)

        def check_file_value(text):
            if text == '':
                save_file_path_label.setText('File location not set!')
                save_file_path_label.setStyleSheet("background-color: red")
            else:
                save_file_path_label.setStyleSheet("background-color: green")

        save_file_path_label.textChanged.connect(check_file_value)

        save_file_path_label.setStyleSheet("background-color: red")
        self.save_file_name_changed.connect(save_file_path_label.setText)
        layout.addWidget(save_file_path_label)

        if self.fileMetaData is not None:
            # save metadata folder 
            meta_save_file_location_push_button = QPushButton("MetaSave option")
            meta_save_file_location_push_button.setDefault(True)
            meta_save_file_location_push_button.clicked.connect(self.meta_save_file_location_push_button)
            layout.addWidget(meta_save_file_location_push_button)

        return file_location_group

    def define_plot_settings_group(self):

        plot_settings_group = QGroupBox('Plot Settings', alignment=Qt.AlignHCenter)

        layout = QGridLayout()
        layout.setAlignment(Qt.AlignCenter)
        plot_settings_group.setLayout(layout)

        # Measurement label: label and lineEdit
        # DC-Value setting
        meas_label_line_edit = QLineEdit('Measurement', alignment=Qt.AlignHCenter)
        meas_label_line_edit.textChanged.connect(
            functools.partial(
                RinToolQWidget.meas_label_text.fset,
                self
            )
        )
        layout.addWidget(QLabel('Measurement plot label text'), 0, 0, 1, 1)
        layout.addWidget(meas_label_line_edit, 0, 1, 1, 1)

        spec_label_text = QLineEdit('Spec. (T)', alignment=Qt.AlignHCenter)
        spec_label_text.textChanged.connect(
            functools.partial(
                RinToolQWidget.spec_label_text.fset,
                self
            )
        )
        layout.addWidget(QLabel('Spec plot label text'), 1, 0, 1, 1)
        layout.addWidget(spec_label_text, 1, 1, 1, 1)

        # spec file loading
        spec_file_location_push_button = QPushButton("Press to Load Spec File")
        spec_file_location_push_button.setDefault(True)
        spec_file_location_push_button.clicked.connect(self.set_spec_file_location_push_button)
        layout.addWidget(spec_file_location_push_button, 2, 0, 1, 2)

        spec_file_name_label = QLabel('', alignment=Qt.AlignHCenter)
        self.spec_file_name_changed.connect(spec_file_name_label.setText)
        layout.addWidget(spec_file_name_label, 3, 0, 1, 2)

        return plot_settings_group

    def define_dc_voltage_line_edit(self):
        dc_voltage_value = QLineEdit('0.0', alignment=Qt.AlignHCenter)

        def get_dc_voltage():
            value = dc_voltage_value.text()
            return float(value)

        self._dc_voltage = get_dc_voltage

        def dc_value_changed():
            value = get_dc_voltage()

            if value <= 0:
                dc_voltage_value.setStyleSheet("background-color: red")
            elif value <= 1:
                dc_voltage_value.setStyleSheet("background-color: orange")
            else:
                dc_voltage_value.setStyleSheet("background-color: green")

        dc_voltage_value.setStyleSheet("background-color: red")
        dc_voltage_value.textChanged.connect(dc_value_changed)

        return dc_voltage_value

    def define_configuration_selection_group(self):

        configuration_selection_group = QGroupBox('Device Setup', alignment=Qt.AlignHCenter)

        layout = QGridLayout()
        layout.setAlignment(Qt.AlignCenter)
        configuration_selection_group.setLayout(layout)

        cross_configuration_radio_button = QRadioButton(
            'Cross-spectrum configuration')
        direct_configuration_radio_button = QRadioButton(
            'Direct-spectrum configuration')

        direct_configuration_radio_button.setChecked(True)
        layout.addWidget(direct_configuration_radio_button, 0, 0, 1, 1)
        layout.addWidget(cross_configuration_radio_button, 0, 1, 1, 1)

        # define callable to check for chosen configuration option
        self._is_cross_cor_conf = cross_configuration_radio_button.isChecked

        # DC-Value setting
        layout.addWidget(QLabel('DC-Voltage [V] (decimal point)'), 1, 0, 1, 1)
        dc_voltage_value = self.define_dc_voltage_line_edit()
        layout.addWidget(dc_voltage_value, 1, 1, 1, 1)

        # connect button
        connect_to_hp_trace_push_button = QPushButton("Press to Connect to HP89410A")
        connect_to_hp_trace_push_button.setDefault(True)
        connect_to_hp_trace_push_button.clicked.connect(self.connect_to_hp89410a)
        connect_to_hp_trace_push_button.setStyleSheet("background-color: red")

        layout.addWidget(connect_to_hp_trace_push_button, 2, 0, 1, 2)

        return configuration_selection_group

    def define_set_frequency_intervals_group(self):

        set_frequency_intervals_group = QGroupBox(
            'Averages per Interval',
            alignment=Qt.AlignHCenter)

        layout = QGridLayout()
        layout.setAlignment(Qt.AlignCenter)
        set_frequency_intervals_group.setLayout(layout)

        grid_index = 0
        for interval in self.freq_intervals:
            label = QLabel(interval.interval_label)
            edit = QLineEdit(str(interval.number_of_avgs), alignment=Qt.AlignHCenter)

            def wrapper(interval_inst: IntervalSpec):
                def update_interval(text: str):
                    if text.isdigit():
                        interval_inst.number_of_avgs = int(text)
                    else:
                        interval_inst.number_of_avgs = 0

                    self.update_estimation_total_time()
                return update_interval

            edit.textChanged.connect(wrapper(interval))
            layout.addWidget(label, grid_index, 0, 1, 1, Qt.AlignHCenter)
            layout.addWidget(edit, grid_index, 1, 1, 1, Qt.AlignHCenter)
            self.editList = self.editList + [edit]

            grid_index = grid_index + 1

        time_estimation_q_label = QLabel('Here is some time')
        time_estimation_q_label.setAlignment(Qt.AlignHCenter)
        self.estimated_time_changed.connect(time_estimation_q_label.setText)
        layout.addWidget(time_estimation_q_label, 8, 0, 1, 3, Qt.AlignHCenter)

        self.update_estimation_total_time()

        return set_frequency_intervals_group

    # endregion

    # region action functions

    def file_paths_defined(self):
        if self.save_file_path is None:
            logger.debug('File path is not defined')
            return False
        else:
            logger.debug('File path is defined: ' + self.save_file_path)
            return True

    def tool_is_connected(self):
        if self.hpTool is not None:
            if self.hpTool.is_connected():
                return True
            else:
                logger.debug('ESA not connected')
        else:
            logger.debug('ESA not initialized')
        return False

    def make_measurement(self):
        button = self.sender()
        button.setStyleSheet("background-color: orange")
        button.setText('Measurement running!')
        button.repaint()

        data_file_path = self.save_file_path + '.h5'
        figure_file_path_spec = self.save_file_path + '.png'
        figure_file_path_raw = self.save_file_path + '_raw.png'
        csv_file_path = self.save_file_path + '.csv'

        dict_measurement_result = {'SettingsData/avgNumValues': np.asarray(self.measAvgs)}

        # predefined frequency ranges
        dict_measurement_result['SettingsData/freq_range_values'] \
            = np.asarray(self.freq_range_values)

        dc_voltage_voltage = self._dc_voltage()
        dict_measurement_result['MeasurementData/dc_voltage_voltage'] \
            = np.asarray(dc_voltage_voltage)

        freq_values = []
        pow_values = []
        psd_vals_vrms_per_rthertz = []
        rbw_values = []

        arr_temp = np.array(self.measAvgs)
        selected_intervals = arr_temp != 0

        for index in np.arange(len(selected_intervals)):
            if selected_intervals[index]:
                # measure dc value
                # measure spectrum

                # currently maximum points are used
                # sweep_pts = sweepPointValues[index]
                sweep_pts = None

                start_freq = freq_range_values[index]
                stop_freq = freq_range_values[index + 1]
                avg_pts = self.measAvgs[index]

                freqs, pows, rbw_value = getScalarRangeData(
                    self.hpTool.visaobj,
                    sweep_pts,
                    start_freq,
                    stop_freq,
                    avg_pts
                )

                print('rbw_value: ' + str(rbw_value))

                psd_vs_voltrms_per_rthertz = np.sqrt(np.array(pows) / rbw_value)

                freq_values = freq_values + freqs
                pow_values = pow_values + pows
                psd_vals_vrms_per_rthertz = psd_vals_vrms_per_rthertz + psd_vs_voltrms_per_rthertz.tolist()
                rbw_values = rbw_values + [rbw_value]

                rin_val = 20 * np.log10(np.array(psd_vals_vrms_per_rthertz) / dc_voltage_voltage)

                # save data
                # update data dict
                dict_measurement_result['MeasurementData/rbw_values'] \
                    = np.asarray(rbw_values)
                dict_measurement_result['MeasurementData/freqValues_Hz'] \
                    = np.asarray(freq_values)
                dict_measurement_result['MeasurementData/powValues_Vrms2'] \
                    = np.asarray(pow_values)
                dict_measurement_result['MeasurementData/powValues_Vrms_rtHz'] \
                    = np.asarray(psd_vals_vrms_per_rthertz)
                dict_measurement_result['MeasurementData/RinValues_dBc_Hz'] \
                    = rin_val

                # continously save Data and figure
                saveDictToHdf5.save_dict_to_hdf5(
                    dict_measurement_result,
                    data_file_path)

                # save as csv
                data_arr = [freq_values, pow_values, psd_vals_vrms_per_rthertz]
                df = pd.DataFrame(data_arr)
                df.to_csv(csv_file_path)

                df = pd.DataFrame(
                    {
                        "freqValues_Hz": freq_values,
                        "RinValues_dBc_Hz": rin_val,
                        "powValues_Vrms2": pow_values,
                        "powValues_Vrms_rtHz": psd_vals_vrms_per_rthertz
                    }
                )

                df.to_csv(csv_file_path, index=False)

                # pumpdiode spec reference plot
                plotRinFigures(
                    freq_values,
                    rin_val,
                    dc_voltage_voltage,
                    figure_file_path_spec,
                    measLabel=self.meas_label_text,
                    specLabel=self.spec_label_text,
                    plotNum=1,
                    filename_spec=self.spec_file_name
                )

                plotRinFigures(
                    freq_values,
                    rin_val,
                    dc_voltage_voltage,
                    figure_file_path_raw,
                    presetLimits=False,
                    showFig=True,
                    plotNum=2,
                    measLabel=self.spec_file_name)

        button.setStyleSheet("background-color: green")
        button.setText('Measurement finished!')
        button.repaint()

    def dc_level_in_range(self):
        dc_voltage_voltage = self._dc_voltage()
        if dc_voltage_voltage > 0:
            return True
        else:
            logger.debug('DC voltage not set')
            return False

    def start_measurement(self):
        try:
            # make pre checks
            if self.file_paths_defined() \
                    and self.tool_is_connected() \
                    and self.dc_level_in_range():
                self.make_measurement()

        except Exception as exc:
            logger.exception(exc)

    def meta_save_file_location_push_button(self):
        pass

    def set_spec_file_location_push_button(self):
        spec_file_path, _ = QFileDialog.getOpenFileName(
            self,
            'Save File',
            '.')
        if spec_file_path != '':
            self.spec_file_name_changed.emit(spec_file_path)

    def set_save_file_location_push_button(self):
        save_file_path, _ = QFileDialog.getSaveFileName(
            self,
            'Save File',
            '.')
        self.save_file_name_changed.emit(save_file_path)

    def update_estimation_total_time(self):

        avgs = [o.number_of_avgs for o in self.freq_intervals]
        meas_times = [o.meas_time_interval for o in self.freq_intervals]

        duration = np.sum(
            np.asarray(avgs) *
            np.asarray(meas_times)
        )

        t_delta = datetime.timedelta(seconds=duration)

        days = t_delta.days
        seconds = t_delta.seconds
        hours = seconds // 3600
        minutes = (seconds // 60) % 60

        duration_str = \
            'Rough estimation of the total duration:\n\t' + \
            str(days) + " days " + \
            str(hours) + " hours " + \
            str(minutes) + " minutes"

        self.estimated_time_changed.emit(duration_str)

    # endregion


# %% main
if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    QApplication.setStyle(QStyleFactory.create("Fusion"))
    app.setApplicationName('Igorevna')
    gallery = RinToolQWidget()

    gallery.show()
    sys.exit(app.exec_())
