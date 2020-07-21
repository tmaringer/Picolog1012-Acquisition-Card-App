import ctypes
import json
import sys
from datetime import datetime

import numpy as np
import pandas as pd
import pyqtgraph as pg
from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from picosdk.functions import assert_pico_ok
from picosdk.pl1000 import pl1000 as pl

myappid = 'mirmex.dataacquisitioncardapp'
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except:
    pass
pg.setConfigOption('background', '#05386B')
pg.setConfigOption('foreground', '#5CDB95')
chandle = ctypes.c_int16()
status = {}
acceldataY = []
acceldataZ = []
count1 = 0


class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setWindowIcon(QIcon('icon.png'))
        self.title = 'Picolog 1012 Acquisition Card - Mirmex Motor'
        self.sizeObject = QDesktopWidget().screenGeometry()
        self.setWindowState(Qt.WindowMaximized)
        self.initUI(self.sizeObject.width(), self.sizeObject.height())
        self.dataX = np.arange(0)
        self.dataY = np.arange(0)
        self.dataZ = np.arange(0)
        self.dataDCV = np.arange(0)
        self.dataDCC = np.arange(0)
        self.dataACV1 = np.arange(0)
        self.dataACV2 = np.arange(0)
        self.dataACV3 = np.arange(0)
        self.dataACC1 = np.arange(0)
        self.dataACC2 = np.arange(0)
        self.dataACC3 = np.arange(0)
        self.countdataX = np.arange(0)
        self.countdataY = np.arange(0)
        self.countdataZ = np.arange(0)
        self.countdataDCV = np.arange(0)
        self.countdataDCC = np.arange(0)
        self.countdataACV1 = np.arange(0)
        self.countdataACV2 = np.arange(0)
        self.countdataACV3 = np.arange(0)
        self.countdataACC1 = np.arange(0)
        self.countdataACC2 = np.arange(0)
        self.countdataACC3 = np.arange(0)
        self.setLayout(self.layout)

    def initUI(self, width, height):
        self.setWindowTitle(self.title)
        mainmenu = self.menuBar()
        self.filemenu = mainmenu.addMenu('File')
        editmenu = mainmenu.addMenu('Config')
        self.viewMenu = mainmenu.addMenu('View')
        self.testbutton = QPushButton('Connection to the Picolog', self)
        self.testbutton.setToolTip('This is an example button')
        self.testbutton.setFixedSize(180, 35)
        self.testbutton.setStyleSheet('QPushButton {background-color: #5CDB95; color: #05386B;}')
        self.testbutton.move(((width - 180) / 2), ((height - 35) / 2))
        self.testbutton.clicked.connect(self.test_connection_pl)
        self.plconnection = QAction('Connection to the Picolog', self)
        self.plconnection.triggered.connect(self.test_connection_pl)
        self.filemenu.addAction(self.plconnection)
        self.configmenu = QAction('Edit configuration file', self)
        self.configmenu.triggered.connect(self.setconfig)
        editmenu.addAction(self.configmenu)
        exitButton = QAction(QIcon('exit24.png'), 'Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.setStatusTip('Exit application')
        exitButton.triggered.connect(self.close)
        full = QAction('Fullscreen', self)
        full.triggered.connect(self.fullscreennow)
        maxim = QAction('Maximized', self)
        maxim.triggered.connect(self.maximnow)
        self.viewMenu.addAction(full)
        self.viewMenu.addAction(maxim)
        self.filemenu.addAction(exitButton)
        self.show()

    @pyqtSlot()
    def setconfig(self):
        self.configf = DialogConfig()
        self.layout.addWidget(self.configf)
        self.configf.show()
        with open("config.json", "r") as read_file:
            config1 = json.load(read_file)
        self.configf.qline1.setText(config1["DCcurrent"][0]["offset"])
        self.configf.qline2.setText(config1["ACvoltage"][0]["offset1"])
        self.configf.qline3.setText(config1["ACvoltage"][0]["offset2"])
        self.configf.qline4.setText(config1["ACvoltage"][0]["offset3"])
        self.configf.qline5.setText(config1["ACcurrent"][0]["offset1"])
        self.configf.qline6.setText(config1["ACcurrent"][0]["offset2"])
        self.configf.qline7.setText(config1["ACcurrent"][0]["offset3"])
        self.configf.qline8.setText(config1["accelerometer"][0]["X"])
        self.configf.qline9.setText(config1["accelerometer"][0]["Y"])
        self.configf.qline10.setText(config1["accelerometer"][0]["Z"])
        self.configf.qline11.setText(config1["time"][0]["time"])

    @pyqtSlot()
    def test_connection_pl(self):
        try:
            status["openUnit"] = pl.pl1000OpenUnit(ctypes.byref(chandle))
            assert_pico_ok(status["openUnit"])
            self.statusBar().setStyleSheet("background-color : #5CDB95; color: #EDF5E1")
            self.statusBar().showMessage('Picolog connected')
            self.testbutton.hide()
            self.plconnection.setDisabled(True)
            self.all_display()

        except:
            self.statusBar().showMessage('Error while connecting to the Picolog')
            self.statusBar().setStyleSheet("background-color : red")

    def fullscreennow(self):
        self.showFullScreen()

    def maximnow(self):
        self.showMaximized
        self.setWindowState(Qt.WindowMaximized)

    def all_display(self):
        w = QtGui.QWidget()
        self.plotX = pg.PlotWidget()
        self.plotY = pg.PlotWidget()
        self.plotZ = pg.PlotWidget()
        self.plotX.setTitle('X axis')
        self.plotX.setLabel('bottom', "time", units='s')
        self.plotX.setYRange(-16, 16)
        self.plotX.setLabel('left', "acceleration", units="g")
        self.plotY.setTitle('Y axis')
        self.plotY.setLabel('bottom', "time", units='s')
        self.plotY.setYRange(-16, 16)
        self.plotY.setLabel('left', "acceleration", units="g")
        self.plotZ.setTitle('Z axis')
        self.plotZ.setLabel('bottom', "time", units='s')
        self.plotZ.setYRange(-16, 16)
        self.plotZ.setLabel('left', "acceleration", units="g")
        self.plotDCV = pg.PlotWidget()
        self.plotDCV.setTitle('Power supply voltage')
        self.plotDCV.setLabel('bottom', "time", units='s')
        self.plotDCV.setYRange(0, 60)
        self.plotDCV.setLabel('left', "voltage", units="V")
        self.plotACV = pg.PlotWidget()
        self.plotACV.setTitle('Three phase voltages')
        self.plotACV.setLabel('bottom', "time", units='s')
        self.plotACV.setYRange(-60, 60)
        self.plotACV.setLabel('left', "voltage", units="V")
        self.plotDCC = pg.PlotWidget()
        self.plotDCC.setTitle('Power supply current')
        self.plotDCC.setLabel('bottom', "time", units='s')
        self.plotDCC.setYRange(0, 30)
        self.plotDCC.setLabel('left', "ampere", units="A")
        self.plotACC = pg.PlotWidget()
        self.plotACC.setTitle('Three phase currents')
        self.plotACC.setLabel('bottom', "time", units='s')
        self.plotACC.setYRange(-30, 30)
        self.plotACC.setLabel('left', "ampere", units="A")
        grid = QGridLayout()
        w.setLayout(grid)
        grid.addWidget(self.plotX, 1, 0, 2, 1)
        grid.addWidget(self.plotY, 3, 0, 2, 1)
        grid.addWidget(self.plotZ, 5, 0, 2, 1)
        grid.addWidget(self.plotDCV, 1, 1, 3, 1)
        grid.addWidget(self.plotACV, 4, 1, 3, 1)
        grid.addWidget(self.plotDCC, 1, 5, 3, 1)
        grid.addWidget(self.plotACC, 4, 5, 3, 1)
        self.setCentralWidget(w)
        butt = QFormLayout()
        layout = QFormLayout()
        self.startplot = QPushButton('Start plotting', self)
        self.startplot.setStyleSheet('QPushButton {background-color: #5CDB95; color: #05386B;}')
        self.startplot.setFixedSize(100, 35)
        self.startplot.clicked.connect(self.startview)
        self.resetplot = QPushButton('Reset plotting', self)
        self.resetplot.setToolTip('This is an example button')
        self.resetplot.setFixedSize(100, 35)
        self.resetplot.setDisabled(True)
        self.resetplot.clicked.connect(self.resetview)
        self.showdata = QPushButton('Show and Save data', self)
        self.showdata.setToolTip('This is an example button')
        self.showdata.setFixedSize(150, 35)
        self.showdata.setDisabled(True)
        self.showdata.clicked.connect(self.showdatatable)
        butt.addRow(self.resetplot, self.showdata)
        layout.addRow(self.startplot, butt)
        grid.addLayout(layout, 7, 0)

    @pyqtSlot()
    def startview(self):
        self.update_accel()
        self.startplot.setDisabled(True)
        self.startplot.setStyleSheet('QPushButton {background-color: #5CDB95; color: #5CDB95;}')
        self.showdata.setDisabled(False)
        self.showdata.setStyleSheet('QPushButton {background-color: #5CDB95; color: #05386B;}')
        self.resetplot.setDisabled(False)
        self.resetplot.setStyleSheet('QPushButton {background-color: #5CDB95; color: #05386B;}')

    @pyqtSlot()
    def resetview(self):
        self.plotX.clear()
        self.plotY.clear()
        self.plotZ.clear()
        self.plotACC.clear()
        self.plotACV.clear()
        self.plotDCC.clear()
        self.plotDCV.clear()
        self.dataX = np.arange(0)
        self.dataY = np.arange(0)
        self.dataZ = np.arange(0)
        self.dataDCV = np.arange(0)
        self.dataDCC = np.arange(0)
        self.dataACV1 = np.arange(0)
        self.dataACV2 = np.arange(0)
        self.dataACV3 = np.arange(0)
        self.dataACC1 = np.arange(0)
        self.dataACC2 = np.arange(0)
        self.dataACC3 = np.arange(0)
        self.countdataX = np.arange(0)
        self.countdataY = np.arange(0)
        self.countdataZ = np.arange(0)
        self.countdataDCV = np.arange(0)
        self.countdataDCC = np.arange(0)
        self.countdataACV1 = np.arange(0)
        self.countdataACV2 = np.arange(0)
        self.countdataACV3 = np.arange(0)
        self.countdataACC1 = np.arange(0)
        self.countdataACC2 = np.arange(0)
        self.countdataACC3 = np.arange(0)
        self.resetplot.setDisabled(True)
        self.resetplot.setStyleSheet('QPushButton {background-color: #5CDB95; color: #5CDB95;}')
        self.showdata.setDisabled(True)
        self.showdata.setStyleSheet('QPushButton {background-color: #5CDB95; color: #5CDB95;}')
        self.startplot.setDisabled(False)
        self.startplot.setStyleSheet('QPushButton {background-color: #5CDB95; color: #05386B;}')

    def update_accel(self):
        start = datetime.now()
        start = start.hour * 3600000000 + start.minute * 60000000 + start.second * 1000000 + start.microsecond
        now = datetime.now()
        now = now.hour * 3600000000 + now.minute * 60000000 + now.second * 1000000 + now.microsecond
        with open("config.json", "r") as read_file:
            time = json.load(read_file)
        while (now - start) < int(time["time"][0]["time"]):
            status["SetDo"] = pl.pl1000SetDo(chandle, 1, 0)
            now = datetime.now()
            now = now.hour * 3600000000 + now.minute * 60000000 + now.second * 1000000 + now.microsecond
            self.countdataX, self.dataX = self.measure(self.countdataX, self.dataX, "PL1000_CHANNEL_9", chandle, start)
            self.countdataY, self.dataY = self.measure(self.countdataY, self.dataY, "PL1000_CHANNEL_10", chandle, start)
            self.countdataZ, self.dataZ = self.measure(self.countdataZ, self.dataZ, "PL1000_CHANNEL_11", chandle, start)
            self.countdataDCC, self.dataDCC = self.measure(self.countdataDCC, self.dataDCC, "PL1000_CHANNEL_1", chandle,
                                                           start)
            now = datetime.now()
            now = now.hour * 3600000000 + now.minute * 60000000 + now.second * 1000000 + now.microsecond
            status["SetDo"] = pl.pl1000SetDo(chandle, 0, 0)
            self.countdataDCV, self.dataDCV = self.measure(self.countdataDCV, self.dataDCV, "PL1000_CHANNEL_2", chandle,
                                                           start)
            self.countdataACC1, self.dataACC1 = self.measure(self.countdataACC1, self.dataACC1, "PL1000_CHANNEL_3",
                                                             chandle, start)
            self.countdataACV1, self.dataACV1 = self.measure(self.countdataACV1, self.dataACV1, "PL1000_CHANNEL_4",
                                                             chandle, start)
            self.countdataACC2, self.dataACC2 = self.measure(self.countdataACC2, self.dataACC2, "PL1000_CHANNEL_5",
                                                             chandle, start)
            now = datetime.now()
            now = now.hour * 3600000000 + now.minute * 60000000 + now.second * 1000000 + now.microsecond
            status["SetDo"] = pl.pl1000SetDo(chandle, 1, 0)
            self.countdataACV2, self.dataACV2 = self.measure(self.countdataACV2, self.dataACV2, "PL1000_CHANNEL_6",
                                                             chandle, start)
            self.countdataACC3, self.dataACC3 = self.measure(self.countdataACC3, self.dataACC3, "PL1000_CHANNEL_7",
                                                             chandle, start)
            self.countdataACV3, self.dataACV3 = self.measure(self.countdataACV3, self.dataACV3, "PL1000_CHANNEL_8",
                                                             chandle, start)
            now = datetime.now()
            now = now.hour * 3600000000 + now.minute * 60000000 + now.second * 1000000 + now.microsecond
            status["SetDo"] = pl.pl1000SetDo(chandle, 0, 0)
        status["SetDo"] = pl.pl1000SetDo(chandle, 0, 0)
        status["SetDo"] = pl.pl1000SetDo(chandle, 0, 1)
        with open("config.json", "r") as read_file:
            config = json.load(read_file)
        self.plotX.plot(self.countdataX, self.dataX, pen=pg.mkPen('#5CDB95'))
        self.plotY.plot(self.countdataY, self.dataY, pen=pg.mkPen('#5CDB95'))
        self.plotZ.plot(self.countdataZ, self.dataZ, pen=pg.mkPen('#5CDB95'))
        self.dataDCV = (self.dataDCV / 4092) * 60
        self.plotDCV.plot(self.countdataDCV, self.dataDCV, pen=pg.mkPen('#5CDB95'))
        self.dataDCC = ((self.dataDCC - int(config["DCcurrent"][0]["offset"])) / 4092) * 30
        self.plotDCC.plot(self.countdataDCC, self.dataDCC, pen=pg.mkPen('#5CDB95'))
        self.dataACV1 = ((self.dataACV1 - int(config["ACvoltage"][0]["offset1"])) / 4092) * 60
        self.plotACV.plot(self.countdataACV1, self.dataACV1, pen=pg.mkPen('m'))
        self.dataACV2 = ((self.dataACV2 - int(config["ACvoltage"][0]["offset2"])) / 4092) * 60
        self.plotACV.plot(self.countdataACV2, self.dataACV2, pen=pg.mkPen('#5CDB95'))
        self.dataACV3 = ((self.dataACV3 - int(config["ACvoltage"][0]["offset3"])) / 4092) * 60
        self.plotACV.plot(self.countdataACV3, self.dataACV3, pen=pg.mkPen('#EDF5E1'))
        self.dataACC1 = ((self.dataACC1 - int(config["ACcurrent"][0]["offset1"])) / 4092) * 30
        self.plotACC.plot(self.countdataACC1, self.dataACC1, pen=pg.mkPen('m'))
        self.dataACC2 = ((self.dataACC2 - int(config["ACcurrent"][0]["offset2"])) / 4092) * 30
        self.plotACC.plot(self.countdataACC2, self.dataACC2, pen=pg.mkPen('#5CDB95'))
        self.dataACC3 = ((self.dataACC3 - int(config["ACcurrent"][0]["offset3"])) / 4092) * 30
        self.plotACC.plot(self.countdataACC3, self.dataACC3, pen=pg.mkPen('#EDF5E1'))

    def measure(self, countdataX, dataX, channel, chandle, start):
        value = ctypes.c_int16()
        status["getSingle"] = pl.pl1000GetSingle(chandle, pl.PL1000Inputs[channel], ctypes.byref(value))
        now = datetime.now()
        now = now.hour * 3600000000 + now.minute * 60000000 + now.second * 1000000 + now.microsecond
        countdataX = np.append(countdataX, [(now - start) * 0.000001])
        dataX = np.append(dataX, [(value.value)])
        assert_pico_ok(status["getSingle"])
        return [countdataX, dataX]

    @pyqtSlot()
    def showdatatable(self):
        self.table = QTableView()

        data = np.array([
            self.countdataX,
            self.dataX,
            self.countdataY,
            self.dataY,
            self.countdataZ,
            self.dataZ,
            self.countdataDCV,
            self.dataDCV,
            self.countdataDCC,
            self.dataDCV,
            self.countdataACV1,
            self.dataACV1,
            self.countdataACV2,
            self.dataACV2,
            self.countdataACV3,
            self.dataACV3,
            self.countdataACC1,
            self.dataACC1,
            self.countdataACC2,
            self.dataACC2,
            self.countdataACC3,
            self.dataACC3,
        ])
        self.dataex = np.transpose(data)
        self.model = TableModel(self.dataex)
        header_labels = ['Time X', 'Data X', 'Time Y', 'Data Y', 'Time Z', 'Data Z', 'Time DCV', 'Data DCV', 'Time DCC',
                         'Data DCC', 'Time ACV1', 'Data ACV1', 'Time ACV2', 'Data ACV2', 'Time ACV3', 'Data ACV3',
                         'Time ACC1', 'Data ACC1', 'Time ACC2', 'Data ACC2', 'Time ACC3', 'Data ACC3']
        df = pd.DataFrame(
            {header_labels[0]: data[0], header_labels[1]: data[1], header_labels[2]: data[2], header_labels[3]: data[3],
             header_labels[4]: data[4], header_labels[5]: data[5], header_labels[6]: data[6], header_labels[7]: data[7],
             header_labels[8]: data[8], header_labels[9]: data[9], header_labels[10]: data[10],
             header_labels[11]: data[11], header_labels[12]: data[12], header_labels[13]: data[13],
             header_labels[14]: data[14], header_labels[15]: data[15], header_labels[16]: data[16],
             header_labels[17]: data[17], header_labels[18]: data[18], header_labels[19]: data[19],
             header_labels[20]: data[20], header_labels[21]: data[21]})

        filepath = 'data_DAC1012-' + datetime.now().strftime("%m-%d-%Y_%H%M%S") + '.xlsx'
        df.to_excel(filepath, index=False)

        self.table.setModel(self.model)
        self.table.setStyleSheet('QHeaderView::section { background-color: #5CDB95; color: #05386B}')
        self.layout.addWidget(self.table)
        self.table.show()


class DialogConfig(QDialog):
    NumGridRows = 3
    NumButtons = 4

    def __init__(self):
        super(DialogConfig, self).__init__()
        self.createFormGroupBox()
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        self.setLayout(mainLayout)

        self.setWindowTitle("Configuration")

    def createFormGroupBox(self):
        self.formGroupBox = QGroupBox("Config parameters")
        layout = QFormLayout()
        title1 = QLabel("DC current")
        layout.addRow(title1)
        self.qline1 = QLineEdit()
        layout.addRow(QLabel("offset:"), self.qline1)
        layout.addRow(QLabel("AC voltages"))
        self.qline2 = QLineEdit()
        layout.addRow(QLabel("offset AC1:"), self.qline2)
        self.qline3 = QLineEdit()
        layout.addRow(QLabel("offset AC2:"), self.qline3)
        self.qline4 = QLineEdit()
        layout.addRow(QLabel("offset AC3:"), self.qline4)
        layout.addRow(QLabel("AC currents"))
        self.qline5 = QLineEdit()
        layout.addRow(QLabel("offset AC1:"), self.qline5)
        self.qline6 = QLineEdit()
        layout.addRow(QLabel("offset AC2:"), self.qline6)
        self.qline7 = QLineEdit()
        layout.addRow(QLabel("offset AC3:"), self.qline7)
        layout.addRow(QLabel("Accelerometer"))
        self.qline8 = QLineEdit()
        layout.addRow(QLabel("X axis:"), self.qline8)
        self.qline9 = QLineEdit()
        layout.addRow(QLabel("Y axis:"), self.qline9)
        self.qline10 = QLineEdit()
        layout.addRow(QLabel("Z axis:"), self.qline10)
        layout.addRow(QLabel("Time of sampling"))
        self.qline11 = QLineEdit()
        layout.addRow(QLabel("Nbr of microseconds:"), self.qline11)
        save = QPushButton("Save")
        save.setStyleSheet('QPushButton {background-color: #5CDB95; color: #05386B;}')
        save.clicked.connect(self.saveconfig)
        layout.addRow(QLabel(" "), QLabel(" "))
        layout.addRow(QLabel(" "), save)
        self.formGroupBox.setLayout(layout)

    def saveconfig(self):
        data = {}
        data['accelerometer'] = []
        data['accelerometer'].append({
            'X': self.qline8.text(),
            'Y': self.qline9.text(),
            'Z': self.qline10.text()
        })
        data['DCcurrent'] = []
        data['DCcurrent'].append({
            'offset': self.qline1.text()
        })
        data['ACvoltage'] = []
        data['ACvoltage'].append({
            'offset1': self.qline2.text(),
            'offset2': self.qline3.text(),
            'offset3': self.qline4.text()

        })
        data['ACcurrent'] = []
        data['ACcurrent'].append({
            'offset1': self.qline5.text(),
            'offset2': self.qline6.text(),
            'offset3': self.qline7.text()

        })
        data["time"] = []
        data["time"].append({
            'time': self.qline11.text()
        })
        with open('config.json', 'w') as outfile:
            json.dumps(data, indent=4)
            json.dump(data, outfile)
        self.hide()


class TableModel(QAbstractTableModel):

    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data
        self.header_labels = ['Time X', 'Data X', 'Time Y', 'Data Y', 'Time Z', 'Data Z', 'Time DCV', 'Data DCV',
                              'Time DCC', 'Data DCC', 'Time ACV1', 'Data ACV1', 'Time ACV2', 'Data ACV2', 'Time ACV3',
                              'Data ACV3', 'Time ACC1', 'Data ACC1', 'Time ACC2', 'Data ACC2', 'Time ACC3', 'Data ACC3']

    def data(self, index, role):
        if role == Qt.DisplayRole:
            value = self._data[index.row(), index.column()]
            return str(value)
        elif role == Qt.BackgroundColorRole:
            return QColor(5, 56, 107)
        elif role == Qt.ForegroundRole:
            return QColor(92, 219, 149)

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.header_labels[section]
        return QAbstractTableModel.headerData(self, section, orientation, role)


if __name__ == '__main__':
    sys_argv = sys.argv
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QColor(5, 56, 107))
    palette.setColor(QtGui.QPalette.WindowText, QColor(92, 219, 149))
    palette.setColor(QtGui.QPalette.Base, QColor(92, 219, 149))
    palette.setColor(QtGui.QPalette.AlternateBase, QColor(0, 0, 0))
    palette.setColor(QtGui.QPalette.ToolTipBase, Qt.white)
    palette.setColor(QtGui.QPalette.ToolTipText, QColor(0, 0, 0))
    palette.setColor(QtGui.QPalette.Text, QColor(5, 56, 107))
    palette.setColor(QtGui.QPalette.Button, QColor(92, 219, 149))
    palette.setColor(QtGui.QPalette.ButtonText, QColor(92, 219, 149))
    palette.setColor(QtGui.QPalette.Disabled, QPalette.Light, Qt.transparent)
    palette.setColor(QtGui.QPalette.BrightText, Qt.red)
    palette.setColor(QtGui.QPalette.Highlight, QColor(92, 219, 149))
    palette.setColor(QtGui.QPalette.HighlightedText, QColor(5, 56, 107))
    app.setPalette(palette)
    ex = App()
    sys.exit(app.exec_())
