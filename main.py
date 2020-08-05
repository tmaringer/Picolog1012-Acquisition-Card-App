import ctypes
import json
import sys
from datetime import datetime
import time
import scipy.fftpack
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
listacq = []
listplot = []
dictvalue = {"PL1000_CHANNEL_1": np.arange(0), "PL1000_CHANNEL_2": np.arange(0),
        "PL1000_CHANNEL_3": np.arange(0), "PL1000_CHANNEL_4": np.arange(0),
        "PL1000_CHANNEL_5": np.arange(0), "PL1000_CHANNEL_6": np.arange(0),
        "PL1000_CHANNEL_7": np.arange(0), "PL1000_CHANNEL_8": np.arange(0),
        "PL1000_CHANNEL_9": np.arange(0), "PL1000_CHANNEL_10": np.arange(0),
        "PL1000_CHANNEL_11": np.arange(0)}
dicttime = {"PL1000_CHANNEL_1": np.arange(0), "PL1000_CHANNEL_2": np.arange(0),
            "PL1000_CHANNEL_3": np.arange(0), "PL1000_CHANNEL_4": np.arange(0),
            "PL1000_CHANNEL_5": np.arange(0), "PL1000_CHANNEL_6": np.arange(0),
            "PL1000_CHANNEL_7": np.arange(0), "PL1000_CHANNEL_8": np.arange(0),
            "PL1000_CHANNEL_9": np.arange(0), "PL1000_CHANNEL_10": np.arange(0),
            "PL1000_CHANNEL_11": np.arange(0)}
dictinfo = {"PL1000_CHANNEL_1": ["A", "DC current"], "PL1000_CHANNEL_2": ["V", "DC voltage"],
            "PL1000_CHANNEL_3": ["A", "AC current 1"], "PL1000_CHANNEL_4": ["V", "AC voltage 1"],
            "PL1000_CHANNEL_5": ["A", "AC current 2"], "PL1000_CHANNEL_6": ["V", "AC voltage 2"],
            "PL1000_CHANNEL_7": ["A", "AC current 3"], "PL1000_CHANNEL_8": ["V", "AC voltage 3"],
            "PL1000_CHANNEL_9": ["m/s2", "X axis"], "PL1000_CHANNEL_10": ["m/s2", "Y axis"],
            "PL1000_CHANNEL_11": ["m/s2", "Z axis"]}


class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setWindowIcon(QIcon('icon.png'))
        self.title = 'Picolog 1012 Acquisition Card - Mirmex Motor'
        self.sizeObject = QDesktopWidget().screenGeometry()
        self.setWindowState(Qt.WindowMaximized)
        self.initUI(self.sizeObject.width(), self.sizeObject.height())
        self.setLayout(self.layout)

    def initUI(self, width, height):
        self.setWindowTitle(self.title)
        mainmenu = self.menuBar()
        self.filemenu = mainmenu.addMenu('File')
        editmenu = mainmenu.addMenu('Config')
        self.toolsmenu = mainmenu.addMenu('Tools')
        p = QWidget()
        self.login = QGridLayout()
        label = QLabel()
        pixmap = QPixmap("pico.png")
        pixmap2 = pixmap.scaledToHeight(height - 200)
        label.setPixmap(pixmap2)
        self.login.addWidget(label, 0, 0, 9, 1, Qt.AlignRight)
        text = QLabel(
            "Welcome to the \"Picolog 1012 Data Acquisition Card App\". \nDon't forget to connect the accelerometer if necessary \nand the external power supply.\nPlease refer to the user manual if in doubt. \n\n-Thibaut Maringer")
        text.setFont(QFont('Arial', 15))
        self.login.addWidget(text, 0, 1, 7, 1, Qt.AlignLeft)
        self.testbutton = QPushButton('Connection to the Picolog', self)

        self.testbutton.setFixedSize(180, 35)
        self.testbutton.setStyleSheet('QPushButton {background-color: #5CDB95; color: #05386B;}')
        self.testbutton.move(((width - 180) / 2), ((height - 35) / 2))
        self.testbutton.clicked.connect(self.test_connection_pl)
        self.login.addWidget(self.testbutton, 7, 1, Qt.AlignLeft)
        p.setLayout(self.login)
        self.setCentralWidget(p)
        self.plconnection = QAction('Connection to the Picolog', self)
        self.plconnection.triggered.connect(self.test_connection_pl)
        self.filemenu.addAction(self.plconnection)
        self.numb = QAction('Mean, minimum and maximum', self)
        self.numb.triggered.connect(self.showintvalue)
        self.numb.setDisabled(True)
        self.toolsmenu.addAction(self.numb)
        self.gr = QAction('Display better specific plot', self)
        self.gr.triggered.connect(self.showplotsep)
        self.gr.setDisabled(True)
        self.toolsmenu.addAction(self.gr)
        self.grfft = QAction('Display better specific plot [FFT]', self)
        self.grfft.triggered.connect(self.showplotsepfft)
        self.grfft.setDisabled(True)
        self.toolsmenu.addAction(self.grfft)
        self.configmenu = QAction('Edit configuration file', self)
        self.configmenu.triggered.connect(self.setconfig)
        editmenu.addAction(self.configmenu)
        self.singlemenu = QAction('Single mode', self)
        self.singlemenu.triggered.connect(self.single_display)
        self.singlemenu.setDisabled(True)
        editmenu.addAction(self.singlemenu)
        self.chanmenu = QAction('Select channels', self)
        self.chanmenu.triggered.connect(self.setchan)
        editmenu.addAction(self.chanmenu)
        self.showdata = QAction('Save data', self)
        self.showdata.setDisabled(True)
        self.showdata.triggered.connect(self.showdatatable)
        self.filemenu.addAction(self.showdata)
        exitButton = QAction(QIcon('exit24.png'), 'Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.setStatusTip('Exit application')
        exitButton.triggered.connect(self.close)
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

    @pyqtSlot()
    def showplotsep(self):
        listplot.clear()
        self.datavalue = DialogValue(0)
        self.layout.addWidget(self.datavalue)
        self.datavalue.show()

    @pyqtSlot()
    def setchan(self):
        chan = SetChannel()
        self.layout.addWidget(chan)
        chan.show()
        if "PL1000_CHANNEL_9" in listacq:
            chan.checkBoxX.setChecked(True)
        if "PL1000_CHANNEL_10" in listacq:
            chan.checkBoxY.setChecked(True)
        if "PL1000_CHANNEL_11" in listacq:
            chan.checkBoxZ.setChecked(True)
        if "PL1000_CHANNEL_1" in listacq:
            chan.checkBoxDCC.setChecked(True)
        if "PL1000_CHANNEL_2" in listacq:
            chan.checkBoxDCV.setChecked(True)
        if "PL1000_CHANNEL_3" in listacq:
            chan.checkBoxACC1.setChecked(True)
        if "PL1000_CHANNEL_4" in listacq:
            chan.checkBoxACV1.setChecked(True)
        if "PL1000_CHANNEL_5" in listacq:
            chan.checkBoxACC2.setChecked(True)
        if "PL1000_CHANNEL_6" in listacq:
            chan.checkBoxACV2.setChecked(True)
        if "PL1000_CHANNEL_7" in listacq:
            chan.checkBoxACC3.setChecked(True)
        if "PL1000_CHANNEL_8" in listacq:
            chan.checkBoxACV3.setChecked(True)

    @pyqtSlot()
    def showplotsepfft(self):
        listplot.clear()
        self.datavalue = DialogValue(1)
        self.layout.addWidget(self.datavalue)
        self.datavalue.show()

    @pyqtSlot()
    def showintvalue(self):
        datavalue = DialogIntValue()
        self.layout.addWidget(datavalue)
        datavalue.show()

    @pyqtSlot()
    def test_connection_pl(self):
        self.testcon = QTimer()
        try:
            status["openUnit"] = pl.pl1000OpenUnit(ctypes.byref(chandle))
            assert_pico_ok(status["openUnit"])
            self.testcon.stop()
            self.statusBar().setStyleSheet("background-color : #5CDB95; color: #EDF5E1")
            self.statusBar().showMessage('Picolog connected')
            self.all_display()

        except:
            self.testcon.setInterval(500)
            self.testcon.setTimerType(Qt.PreciseTimer)
            self.b = 1
            self.testcon.timeout.connect(lambda: self.warning('Error while connecting to the Picolog'))
            self.testcon.start()

    def all_display(self):
        w = QtGui.QWidget()
        self.single = 0
        self.singlemenu.setText("Single mode")
        self.singlemenu.triggered.connect(self.single_display)
        self.plotX = pg.PlotWidget()
        self.plotY = pg.PlotWidget()
        self.plotZ = pg.PlotWidget()
        self.plotX.setTitle('X axis')
        self.plotX.setLabel('bottom', "time", units='s')
        self.plotX.setYRange(-16, 16)
        self.plotX.setLabel('left', "acceleration", units="m/s2")
        self.plotY.setTitle('Y axis')
        self.plotY.setLabel('bottom', "time", units='s')
        self.plotY.setYRange(-16, 16)
        self.plotY.setLabel('left', "acceleration", units="m/s2")
        self.plotZ.setTitle('Z axis')
        self.plotZ.setLabel('bottom', "time", units='s')
        self.plotZ.setYRange(-16, 16)
        self.plotZ.setLabel('left', "acceleration", units="m/s2")
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
        self.plotX.showGrid(True, True, 0.5)
        self.plotX.setMenuEnabled(False)
        self.plotY.showGrid(True, True, 0.5)
        self.plotY.setMenuEnabled(False)
        self.plotZ.showGrid(True, True, 0.5)
        self.plotZ.setMenuEnabled(False)
        self.plotDCV.showGrid(True, True, 0.5)
        self.plotDCV.setMenuEnabled(False)
        self.plotDCC.showGrid(True, True, 0.5)
        self.plotDCC.setMenuEnabled(False)
        self.plotACV.showGrid(True, True, 0.5)
        self.plotACV.setMenuEnabled(False)
        self.plotACC.showGrid(True, True, 0.5)
        self.plotACC.setMenuEnabled(False)
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
        self.stopplot = QPushButton('Stop plotting', self)
        self.stopplot.setFixedSize(100, 35)
        self.stopplot.setDisabled(True)
        self.stopplot.clicked.connect(self.stopview)

        self.resetplot = QPushButton('Delete all', self)
        self.resetplot.setFixedSize(100, 35)
        self.resetplot.setDisabled(True)
        self.resetplot.clicked.connect(self.deleteview)

        butt.addRow(self.stopplot, self.resetplot)
        layout.addRow(self.startplot, butt)
        grid.addLayout(layout, 7, 0)

        butt1 = QFormLayout()
        layout1 = QFormLayout()
        self.leg1 = QLabel("          Phase 1        ")
        self.leg1.setStyleSheet('QLabel {background-color: #05386B; color: magenta;}')
        self.leg2 = QLabel("Phase 2        ")
        self.leg2.setStyleSheet('QLabel {background-color: #05386B; color: #5CDB95;}')
        self.leg3 = QLabel("Phase 3        ")
        self.leg3.setStyleSheet('QLabel {background-color: #05386B; color: #EDF5E1;}')
        butt1.addRow(self.leg2, self.leg3)
        layout1.addRow(self.leg1, butt1)
        grid.addLayout(layout1, 7, 1)
        self.switch = QPushButton("Start motor")
        self.switch.clicked.connect(self.motor)
        self.switch.setFixedSize(100, 35)
        self.switch.setStyleSheet('QPushButton {background-color: #5CDB95; color: #05386B;}')
        grid.addWidget(self.switch, 7, 5, Qt.AlignRight)

    def single_display(self):
        w = QtGui.QWidget()
        self.single = 1
        self.singlemenu.setText("Multi mode")
        self.singlemenu.triggered.connect(self.all_display)
        self.plotChan = pg.PlotWidget()
        self.plotChan.setTitle('Single channel')
        self.plotChan.setLabel('bottom', "time", units='s')
        self.plotChan.setYRange(-16, 16)
        self.plotChan.showGrid(True, True, 0.5)
        self.plotChan.setMenuEnabled(False)
        grid = QGridLayout()
        w.setLayout(grid)
        grid.addWidget(self.plotChan, 1, 0, 6, 6)
        self.setCentralWidget(w)
        butt = QFormLayout()
        layout = QFormLayout()
        self.startplot_single = QPushButton('Start plotting', self)
        self.startplot_single.setStyleSheet('QPushButton {background-color: #5CDB95; color: #05386B;}')
        self.startplot_single.setFixedSize(100, 35)
        self.startplot_single.clicked.connect(self.startview_single)
        self.stopplot_single = QPushButton('Stop plotting', self)
        self.stopplot_single.setFixedSize(100, 35)
        self.stopplot_single.setDisabled(True)
        #self.stopplot.clicked.connect(self.stopview_single)
        self.resetplot_single = QPushButton('Delete all', self)
        self.resetplot_single.setFixedSize(100, 35)
        self.resetplot_single.setDisabled(True)
        #self.resetplot.clicked.connect(self.deleteview_single)

        butt.addRow(self.stopplot, self.resetplot)
        layout.addRow(self.startplot, butt)
        grid.addLayout(layout, 7, 0)
        self.switch = QPushButton("Start motor")
        self.switch.clicked.connect(self.motor)
        self.switch.setFixedSize(100, 35)
        self.switch.setStyleSheet('QPushButton {background-color: #5CDB95; color: #05386B;}')
        grid.addWidget(self.switch, 7, 5, Qt.AlignRight)

    @pyqtSlot()
    def motor(self):
        if self.switch.text() == "Start motor":
            self.switch.setText("Stop motor")
            status["SetDo"] = pl.pl1000SetDo(chandle, 1, 1)
            self.switch.setStyleSheet('QPushButton {background-color: #FFDF00; color: #05386B;}')
        else:
            self.switch.setText("Start motor")
            status["SetDo"] = pl.pl1000SetDo(chandle, 0, 1)
            self.switch.setStyleSheet('QPushButton {background-color: #5CDB95; color: #05386B;}')

    @pyqtSlot()
    def startview(self):
        self.gr.setDisabled(True)
        self.grfft.setDisabled(True)
        self.numb.setDisabled(True)
        self.test = QTimer()
        if len(listacq) == 0:
            self.test.setInterval(500)
            self.test.setTimerType(Qt.PreciseTimer)
            self.b = 1
            self.test.timeout.connect(lambda: self.warning("No channel selected, go to Config > Select channels"))
            self.test.start()
        else:
            self.test.stop()
            self.statusBar().setStyleSheet("background-color : #5CDB95; color: #EDF5E1")
            self.statusBar().showMessage('In progress...')
            self.plotX.clear()
            self.plotY.clear()
            self.plotZ.clear()
            self.plotACC.clear()
            self.plotACV.clear()
            self.plotDCC.clear()
            self.plotDCV.clear()
            dictvalue["PL1000_CHANNEL_9"] = np.arange(0)
            dictvalue["PL1000_CHANNEL_10"] = np.arange(0)
            dictvalue["PL1000_CHANNEL_11"] = np.arange(0)
            dictvalue["PL1000_CHANNEL_2"] = np.arange(0)
            dictvalue["PL1000_CHANNEL_1"] = np.arange(0)
            dictvalue["PL1000_CHANNEL_4"] = np.arange(0)
            dictvalue["PL1000_CHANNEL_6"] = np.arange(0)
            dictvalue["PL1000_CHANNEL_8"] = np.arange(0)
            dictvalue["PL1000_CHANNEL_3"] = np.arange(0)
            dictvalue["PL1000_CHANNEL_5"] = np.arange(0)
            dictvalue["PL1000_CHANNEL_7"] = np.arange(0)
            dicttime["PL1000_CHANNEL_9"] = np.arange(0)
            dicttime["PL1000_CHANNEL_10"] = np.arange(0)
            dicttime["PL1000_CHANNEL_11"] = np.arange(0)
            dicttime["PL1000_CHANNEL_2"] = np.arange(0)
            dicttime["PL1000_CHANNEL_1"] = np.arange(0)
            dicttime["PL1000_CHANNEL_4"] = np.arange(0)
            dicttime["PL1000_CHANNEL_6"] = np.arange(0)
            dicttime["PL1000_CHANNEL_8"] = np.arange(0)
            dicttime["PL1000_CHANNEL_3"] = np.arange(0)
            dicttime["PL1000_CHANNEL_5"] = np.arange(0)
            dicttime["PL1000_CHANNEL_7"] = np.arange(0)
            self.timer = QTimer()
            self.timer.setTimerType(Qt.PreciseTimer)
            status["SetDo"] = pl.pl1000SetDo(chandle, 1, 0)
            self.timer.timeout.connect(self.update_accel)
            self.startplot.setDisabled(True)
            self.startplot.setStyleSheet('QPushButton {background-color: #5CDB95; color: #5CDB95;}')
            self.showdata.setDisabled(False)
            self.stopplot.setDisabled(False)
            self.stopplot.setStyleSheet('QPushButton {background-color: #5CDB95; color: #05386B;}')
            self.timer.start()

    @pyqtSlot()
    def startview_single(self):
        self.gr.setDisabled(True)
        self.grfft.setDisabled(True)
        self.numb.setDisabled(True)
        self.test = QTimer()
        if len(listacq) == 0:
            self.test.setInterval(500)
            self.test.setTimerType(Qt.PreciseTimer)
            self.b = 1
            self.test.timeout.connect(lambda: self.warning("No channel selected, go to Config > Select channels"))
            self.test.start()
        else:
            self.test.stop()
            self.statusBar().setStyleSheet("background-color : #5CDB95; color: #EDF5E1")
            self.statusBar().showMessage('In progress...')
            self.plotChan.clear()
            self.plotChanData = np.arange(0)
            self.timer_single = QTimer()
            self.timer_single.setTimerType(Qt.PreciseTimer)
            status["SetDo"] = pl.pl1000SetDo(chandle, 1, 0)
            self.timer_single.timeout.connect(self.update_accel_single)
            self.startplot_single.setDisabled(True)
            self.startplot_single.setStyleSheet('QPushButton {background-color: #5CDB95; color: #5CDB95;}')
            self.showdata_single.setDisabled(False)
            self.stopplot_single.setDisabled(False)
            self.stopplot_single.setStyleSheet('QPushButton {background-color: #5CDB95; color: #05386B;}')
            self.usForBlock = ctypes.c_uint32(100000)
            self.noOfValues = ctypes.c_uint32(10000)
            channels = ctypes.c_int16(9)
            status["setInterval"] = pl.pl1000SetInterval(chandle, ctypes.byref(self.usForBlock), self.noOfValues,
                                                         ctypes.byref(channels), 1)
            assert_pico_ok(status["setInterval"])
            self.mode = pl.PL1000_BLOCK_METHOD["BM_STREAM"]
            self.timer_single.start()

    def warning(self, a):
        if self.b == 1:
            self.statusBar().showMessage(a)
            self.statusBar().setStyleSheet("background-color : red; color: #EDF5E1")
            self.b = 0
        else:
            self.statusBar().showMessage(a)
            self.statusBar().setStyleSheet("background-color : #EDF5E1; color: red")
            self.b = 1

    @pyqtSlot()
    def stopview(self):
        self.timer.stop()
        self.gr.setDisabled(False)
        self.grfft.setDisabled(False)
        self.numb.setDisabled(False)
        self.stopplot.setDisabled(True)
        self.stopplot.setStyleSheet('QPushButton {background-color: #5CDB95; color: #5CDB95;}')
        self.statusBar().setStyleSheet("background-color : #5CDB95; color: #EDF5E1")
        self.statusBar().showMessage('Stopped')
        self.showdata.setDisabled(False)
        self.resetplot.setDisabled(False)
        self.resetplot.setStyleSheet('QPushButton {background-color: #5CDB95; color: #05386B;}')
        status["SetDo"] = pl.pl1000SetDo(chandle, 0, 0)
        with open("config.json", "r") as read_file:
            config = json.load(read_file)
        l = dicttime[listacq[0]][0]
        for i in listacq:
            dicttime[i] = dicttime[i] - l
        self.g = QLabel("speed: " + str(int(len(dictvalue[listacq[0]])/(dicttime[listacq[0]][-1] - dicttime[listacq[0]][0]))) + " S/s    ")
        self.g.setStyleSheet("background-color : #5CDB95; color: #EDF5E1")
        self.statusBar().addPermanentWidget(self.g)
        try:
            dictvalue["PL1000_CHANNEL_9"] = ((dictvalue["PL1000_CHANNEL_9"] - dictvalue["PL1000_CHANNEL_9"][
                0]) * 2.5 / 4092) * 9.81 / float(
                config["accelerometer"][0]["X"])
            self.plotX.plot(dicttime["PL1000_CHANNEL_9"],
                            dictvalue["PL1000_CHANNEL_9"], pen=pg.mkPen('#5CDB95'))
        except:
            pass
        try:
            dictvalue["PL1000_CHANNEL_10"] = ((dictvalue["PL1000_CHANNEL_10"] - dictvalue["PL1000_CHANNEL_10"][
                0]) * 2.5 / 4092) * 9.81 / float(
                config["accelerometer"][0]["Y"])
            self.plotY.plot(dicttime["PL1000_CHANNEL_10"],
                            dictvalue["PL1000_CHANNEL_10"], pen=pg.mkPen('#5CDB95'))
        except:
            pass
        try:
            dictvalue["PL1000_CHANNEL_11"] = ((dictvalue["PL1000_CHANNEL_11"] - dictvalue["PL1000_CHANNEL_11"][
                0]) * 2.5 / 4092) * 9.81 / float(
                config["accelerometer"][0]["Z"])
            self.plotZ.plot(dicttime["PL1000_CHANNEL_11"],
                            dictvalue["PL1000_CHANNEL_11"], pen=pg.mkPen('#5CDB95'))
        except:
            pass
        dictvalue["PL1000_CHANNEL_2"] = (dictvalue["PL1000_CHANNEL_2"] / 4092) * 60.37
        self.plotDCV.plot(dicttime["PL1000_CHANNEL_2"], dictvalue["PL1000_CHANNEL_2"], pen=pg.mkPen('#5CDB95'))
        dictvalue["PL1000_CHANNEL_1"] = (((dictvalue["PL1000_CHANNEL_1"] - int(
            config["DCcurrent"][0]["offset"])) / 4092) * 2.5) * 2 / 0.066
        self.plotDCC.plot(dicttime["PL1000_CHANNEL_1"], dictvalue["PL1000_CHANNEL_1"], pen=pg.mkPen('#5CDB95'))
        dictvalue["PL1000_CHANNEL_4"] = (((dictvalue["PL1000_CHANNEL_4"]/ 4092) * 102/2) - ((np.amin(dictvalue["PL1000_CHANNEL_4"])/ 4092) * 102/2))
        self.plotACV.plot(dicttime["PL1000_CHANNEL_4"], dictvalue["PL1000_CHANNEL_4"], pen=pg.mkPen('m'))
        dictvalue["PL1000_CHANNEL_6"] = ((dictvalue["PL1000_CHANNEL_6"] - int(
            config["ACvoltage"][0]["offset2"])) / 4092) * 2.5 * 102 / 2
        self.plotACV.plot(dicttime["PL1000_CHANNEL_6"], dictvalue["PL1000_CHANNEL_6"], pen=pg.mkPen('#5CDB95'))
        dictvalue["PL1000_CHANNEL_8"] = ((dictvalue["PL1000_CHANNEL_8"] - int(
            config["ACvoltage"][0]["offset3"])) / 4092) * 60
        self.plotACV.plot(dicttime["PL1000_CHANNEL_8"], dictvalue["PL1000_CHANNEL_8"], pen=pg.mkPen('#EDF5E1'))
        dictvalue["PL1000_CHANNEL_3"] = ((dictvalue["PL1000_CHANNEL_3"] - int(
            config["ACcurrent"][0]["offset1"])) / 4092) * 5 / 0.066
        self.plotACC.plot(dicttime["PL1000_CHANNEL_3"], dictvalue["PL1000_CHANNEL_3"], pen=pg.mkPen('m'))
        dictvalue["PL1000_CHANNEL_5"] = ((dictvalue["PL1000_CHANNEL_5"] - int(
            config["ACcurrent"][0]["offset2"])) / 4092) * 5 / 0.066
        self.plotACC.plot(dicttime["PL1000_CHANNEL_5"], dictvalue["PL1000_CHANNEL_5"], pen=pg.mkPen('#5CDB95'))
        dictvalue["PL1000_CHANNEL_7"] = ((dictvalue["PL1000_CHANNEL_7"] - int(
            config["ACcurrent"][0]["offset3"])) / 4092) * 5 / 0.066
        self.plotACC.plot(dicttime["PL1000_CHANNEL_7"], dictvalue["PL1000_CHANNEL_7"], pen=pg.mkPen('#EDF5E1'))
        self.plotX.sigRangeChanged.connect(self.onSigRangeChanged)
        self.plotY.sigRangeChanged.connect(self.onSigRangeChanged)
        self.plotZ.sigRangeChanged.connect(self.onSigRangeChanged)
        self.plotDCV.sigRangeChanged.connect(self.onSigRangeChanged)
        self.plotDCC.sigRangeChanged.connect(self.onSigRangeChanged)
        self.plotACV.sigRangeChanged.connect(self.onSigRangeChanged)
        self.plotACC.sigRangeChanged.connect(self.onSigRangeChanged)

    @pyqtSlot()
    def stopview_single(self):
        self.timer_single.stop()
        self.gr.setDisabled(False)
        self.grfft.setDisabled(False)
        self.numb.setDisabled(False)
        self.stopplot_single.setDisabled(True)
        self.stopplot_single.setStyleSheet('QPushButton {background-color: #5CDB95; color: #5CDB95;}')
        self.statusBar().setStyleSheet("background-color : #5CDB95; color: #EDF5E1")
        self.statusBar().showMessage('Stopped')
        self.showdata_single.setDisabled(False)
        self.resetplot_single.setDisabled(False)
        self.resetplot_single.setStyleSheet('QPushButton {background-color: #5CDB95; color: #05386B;}')
        status["SetDo"] = pl.pl1000SetDo(chandle, 0, 0)

    @pyqtSlot()
    def deleteview(self):
        self.all_display()
        self.statusBar().setStyleSheet("background-color : #FFDF00; color: #05386B")
        self.statusBar().showMessage('All reset')
        listacq.clear()
        self.statusBar().removeWidget(self.g)
        self.resetplot.setDisabled(True)
        self.resetplot.setStyleSheet('QPushButton {background-color: #5CDB95; color: #5CDB95;}')
        self.startplot.setDisabled(False)
        self.startplot.setStyleSheet('QPushButton {background-color: #5CDB95; color: #05386B;}')
        self.gr.setDisabled(True)
        self.grfft.setDisabled(True)
        self.numb.setDisabled(True)

    @pyqtSlot()
    def deleteview_single(self):
        self.single_display()
        self.statusBar().setStyleSheet("background-color : #FFDF00; color: #05386B")
        self.statusBar().showMessage('All reset')
        listacq.clear()
        self.statusBar().removeWidget(self.g)
        self.resetplot_single.setDisabled(True)
        self.resetplot_single.setStyleSheet('QPushButton {background-color: #5CDB95; color: #5CDB95;}')
        self.startplot_single.setDisabled(False)
        self.startplot_single.setStyleSheet('QPushButton {background-color: #5CDB95; color: #05386B;}')
        self.gr.setDisabled(True)
        self.grfft.setDisabled(True)
        self.numb.setDisabled(True)

    def update_accel(self):
        for i in listacq:
            dicttime[i], dictvalue[i] = self.measure(dicttime[i], dictvalue[i], i, chandle)

    def measure(self, countdataX, dataX, channel, chandle):
        value = ctypes.c_int16()
        status["getSingle"] = pl.pl1000GetSingle(chandle, pl.PL1000Inputs[channel], ctypes.byref(value))
        return [np.append(countdataX, [time.time()]), np.append(dataX, [(value.value)])]

    def update_accel_single(self):
        status["run"] = pl.pl1000Run(chandle, 10000, self.mode)
        time.sleep(self.usForBlock.value / 1000000)
        values = (ctypes.c_uint16 * self.noOfValues.value)()
        oveflow = ctypes.c_uint16()
        status["getValues"] = pl.pl1000GetValues(chandle, ctypes.byref(values), ctypes.byref(self.noOfValues),
                                                 ctypes.byref(oveflow), None)
        self.plotChanData = np.append(self.plotChanData, [values])


    def onSigRangeChanged(self, r):
        self.plotX.sigRangeChanged.disconnect(self.onSigRangeChanged)
        self.plotY.sigRangeChanged.disconnect(self.onSigRangeChanged)
        self.plotZ.sigRangeChanged.disconnect(self.onSigRangeChanged)
        self.plotDCV.sigRangeChanged.disconnect(self.onSigRangeChanged)
        self.plotDCC.sigRangeChanged.disconnect(self.onSigRangeChanged)
        self.plotACV.sigRangeChanged.disconnect(self.onSigRangeChanged)
        self.plotACC.sigRangeChanged.disconnect(self.onSigRangeChanged)
        if self.plotX == r:
            self.plotY.setRange(xRange=r.getAxis('bottom').range)
            self.plotZ.setRange(xRange=r.getAxis('bottom').range)
            self.plotDCV.setRange(xRange=r.getAxis('bottom').range)
            self.plotDCC.setRange(xRange=r.getAxis('bottom').range)
            self.plotACV.setRange(xRange=r.getAxis('bottom').range)
            self.plotACC.setRange(xRange=r.getAxis('bottom').range)
        elif self.plotY == r:
            self.plotX.setRange(xRange=r.getAxis('bottom').range)
            self.plotZ.setRange(xRange=r.getAxis('bottom').range)
            self.plotDCV.setRange(xRange=r.getAxis('bottom').range)
            self.plotDCC.setRange(xRange=r.getAxis('bottom').range)
            self.plotACV.setRange(xRange=r.getAxis('bottom').range)
            self.plotACC.setRange(xRange=r.getAxis('bottom').range)
        elif self.plotZ == r:
            self.plotX.setRange(xRange=r.getAxis('bottom').range)
            self.plotY.setRange(xRange=r.getAxis('bottom').range)
            self.plotDCV.setRange(xRange=r.getAxis('bottom').range)
            self.plotDCC.setRange(xRange=r.getAxis('bottom').range)
            self.plotACV.setRange(xRange=r.getAxis('bottom').range)
            self.plotACC.setRange(xRange=r.getAxis('bottom').range)
        elif self.plotDCV == r:
            self.plotX.setRange(xRange=r.getAxis('bottom').range)
            self.plotY.setRange(xRange=r.getAxis('bottom').range)
            self.plotZ.setRange(xRange=r.getAxis('bottom').range)
            self.plotDCC.setRange(xRange=r.getAxis('bottom').range)
            self.plotACV.setRange(xRange=r.getAxis('bottom').range)
            self.plotACC.setRange(xRange=r.getAxis('bottom').range)
        elif self.plotDCC == r:
            self.plotX.setRange(xRange=r.getAxis('bottom').range)
            self.plotY.setRange(xRange=r.getAxis('bottom').range)
            self.plotZ.setRange(xRange=r.getAxis('bottom').range)
            self.plotDCV.setRange(xRange=r.getAxis('bottom').range)
            self.plotACV.setRange(xRange=r.getAxis('bottom').range)
            self.plotACC.setRange(xRange=r.getAxis('bottom').range)
        elif self.plotACV == r:
            self.plotX.setRange(xRange=r.getAxis('bottom').range)
            self.plotY.setRange(xRange=r.getAxis('bottom').range)
            self.plotZ.setRange(xRange=r.getAxis('bottom').range)
            self.plotDCV.setRange(xRange=r.getAxis('bottom').range)
            self.plotDCC.setRange(xRange=r.getAxis('bottom').range)
            self.plotACC.setRange(xRange=r.getAxis('bottom').range)
        elif self.plotACC == r:
            self.plotX.setRange(xRange=r.getAxis('bottom').range)
            self.plotY.setRange(xRange=r.getAxis('bottom').range)
            self.plotZ.setRange(xRange=r.getAxis('bottom').range)
            self.plotDCV.setRange(xRange=r.getAxis('bottom').range)
            self.plotDCC.setRange(xRange=r.getAxis('bottom').range)
            self.plotACV.setRange(xRange=r.getAxis('bottom').range)

        self.plotX.sigRangeChanged.connect(self.onSigRangeChanged)
        self.plotY.sigRangeChanged.connect(self.onSigRangeChanged)
        self.plotZ.sigRangeChanged.connect(self.onSigRangeChanged)
        self.plotDCV.sigRangeChanged.connect(self.onSigRangeChanged)
        self.plotDCC.sigRangeChanged.connect(self.onSigRangeChanged)
        self.plotACV.sigRangeChanged.connect(self.onSigRangeChanged)
        self.plotACC.sigRangeChanged.connect(self.onSigRangeChanged)

    @pyqtSlot()
    def showdatatable(self):
        self.warr = QTimer()
        try:
            z = list()
            income_sheets = {}
            listdataframe = []
            for i in listacq:
                z.append(dictinfo[i][1] + " time" + " [s]")
                z.append(dictinfo[i][1] + " data" + " [" + dictinfo[i][0] + "]")
                index = listacq.index(i)
                df = pd.DataFrame({z[index * 2]: dicttime[i], z[(index + 1) * 2 - 1]: dictvalue[i]})
                listdataframe.append(df)
                income_sheets[dictinfo[i][1]] = listdataframe[listacq.index(i)]
            filepath = 'data_DAC1012-' + datetime.now().strftime("%m-%d-%Y_%H%M%S") + '.xlsx'
            writer = pd.ExcelWriter(filepath, engine='xlsxwriter')
            workbook = writer.book
            for sheet_name in income_sheets.keys():
                income_sheets[sheet_name].to_excel(writer, sheet_name=sheet_name, index=False)
                writer.sheets[sheet_name].conditional_format('B2:B' + str(len(dictvalue[listacq[0]]) + 1),
                                                             {'type': '3_color_scale', 'min_color': "red",
                                                              'mid_color': "yellow",
                                                              'max_color': "green",
                                                              'mid_type': "num"})
                chart = workbook.add_chart({'type': 'line'})
                max_row = len(dictvalue[listacq[0]]) + 1
                chart.add_series({
                    'name': [sheet_name, 0, 1],
                    'categories': [sheet_name, 2, 0, max_row, 0],
                    'values': [sheet_name, 2, 1, max_row, 1],
                    'line': {
                    'color': 'orange',
                    'width': 1,
                    },
                })
                writer.sheets[sheet_name].insert_chart('D6', chart, {'x_scale': 3, 'y_scale': 2})
                cell_format = workbook.add_format()
                cell_format.set_bold()
                cell_format.set_font_color('black')
                cell_format.set_font_size(40)
                writer.sheets[sheet_name].set_column(0, 1, 20)
                writer.sheets[sheet_name].write(0, 4, sheet_name + " data acquisition", cell_format)
            writer.save()
            workbook.close()
            self.statusBar().setStyleSheet("background-color : #5CDB95; color: #EDF5E1")
            self.statusBar().showMessage('Excel file saved')
        except:
            self.warr.setInterval(500)
            self.warr.setTimerType(Qt.PreciseTimer)
            self.b = 1
            self.warr.timeout.connect(lambda: self.warning("Error while saving the data"))
            self.warr.start()

class DialogConfig(QDialog):
    NumGridRows = 3
    NumButtons = 4

    def __init__(self):
        super(DialogConfig, self).__init__()
        self.createFormGroupBox()
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        self.setLayout(mainLayout)
        self.setWindowIcon(QIcon('icon.png'))
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
        layout.addRow(QLabel("X axis sensitivity:"), self.qline8)
        self.qline9 = QLineEdit()
        layout.addRow(QLabel("Y axis sensitivity:"), self.qline9)
        self.qline10 = QLineEdit()
        layout.addRow(QLabel("Z axis sensitivity:"), self.qline10)
        layout.addRow(QLabel("Time of sampling"))
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
        with open('config.json', 'w') as outfile:
            json.dumps(data, indent=4)
            json.dump(data, outfile)
        self.hide()


class SetChannel(QDialog):
    NumGridRows = 3
    NumButtons = 4

    def __init__(self):
        super(SetChannel, self).__init__()
        self.createFormGroupBox()
        self.setWindowIcon(QIcon('icon.png'))
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        self.setLayout(mainLayout)

        self.setWindowTitle("Channels selection")

    def createFormGroupBox(self):
        self.formGroupBox = QGroupBox("Choose channels")
        layout = QFormLayout()
        acq = QFormLayout()
        self.checkBoxX = QCheckBox("X Axis")
        self.checkBoxX.stateChanged.connect(
            lambda: self.checkBoxChangedAction("PL1000_CHANNEL_9", self.checkBoxX.isChecked()))
        self.checkBoxY = QCheckBox("Y Axis")
        self.checkBoxY.stateChanged.connect(
            lambda: self.checkBoxChangedAction("PL1000_CHANNEL_10", self.checkBoxY.isChecked()))
        self.checkBoxZ = QCheckBox("Z Axis")
        self.checkBoxZ.stateChanged.connect(
            lambda: self.checkBoxChangedAction("PL1000_CHANNEL_11", self.checkBoxZ.isChecked()))
        self.checkBoxDCV = QCheckBox("DC voltage")
        self.checkBoxDCV.stateChanged.connect(
            lambda: self.checkBoxChangedAction("PL1000_CHANNEL_2", self.checkBoxDCV.isChecked()))
        self.checkBoxDCC = QCheckBox("DC current")
        self.checkBoxDCC.stateChanged.connect(
            lambda: self.checkBoxChangedAction("PL1000_CHANNEL_1", self.checkBoxDCC.isChecked()))
        self.checkBoxACV1 = QCheckBox("AC voltage 1")
        self.checkBoxACV1.stateChanged.connect(
            lambda: self.checkBoxChangedAction("PL1000_CHANNEL_4", self.checkBoxACV1.isChecked()))
        self.checkBoxACV2 = QCheckBox("AC voltage 2")
        self.checkBoxACV2.stateChanged.connect(
            lambda: self.checkBoxChangedAction("PL1000_CHANNEL_6", self.checkBoxACV2.isChecked()))
        self.checkBoxACV3 = QCheckBox("AC voltage 3")
        self.checkBoxACV3.stateChanged.connect(
            lambda: self.checkBoxChangedAction("PL1000_CHANNEL_8", self.checkBoxACV3.isChecked()))
        self.checkBoxACC1 = QCheckBox("AC current 1")
        self.checkBoxACC1.stateChanged.connect(
            lambda: self.checkBoxChangedAction("PL1000_CHANNEL_3", self.checkBoxACC1.isChecked()))
        self.checkBoxACC2 = QCheckBox("AC current 2")
        self.checkBoxACC2.stateChanged.connect(
            lambda: self.checkBoxChangedAction("PL1000_CHANNEL_5", self.checkBoxACC2.isChecked()))
        self.checkBoxACC3 = QCheckBox("AC current 3")
        self.checkBoxACC3.stateChanged.connect(
            lambda: self.checkBoxChangedAction("PL1000_CHANNEL_7", self.checkBoxACC3.isChecked()))
        AC1 = QFormLayout()
        AC1.addRow(self.checkBoxACV1, self.checkBoxACC1)
        AC2 = QFormLayout()
        AC2.addRow(self.checkBoxACV2, self.checkBoxACC2)
        AC3 = QFormLayout()
        AC3.addRow(self.checkBoxACV3, self.checkBoxACC3)
        acq.addRow(self.checkBoxX, AC1)
        acq.addRow(self.checkBoxY, AC2)
        acq.addRow(self.checkBoxZ, AC3)
        acq.addRow(self.checkBoxDCV, self.checkBoxDCC)
        layout.addRow(acq)
        self.formGroupBox.setLayout(layout)

    def checkBoxChangedAction(self, channel, state):
        if state == True:
            if (channel in listacq) == False:
                listacq.append(channel)
            else:
                pass
        elif state == False:
            if (channel in listacq) == True:
                listacq.remove(channel)
            else:
                pass
        else:
            pass


class DialogValue(QDialog):
    NumGridRows = 3
    NumButtons = 4

    def __init__(self, fft):
        super(DialogValue, self).__init__()
        self.createFormGroupBox()
        self.setWindowIcon(QIcon('icon.png'))
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        self.setLayout(mainLayout)
        self.fft = fft
        self.setWindowTitle("Configuration")

    def createFormGroupBox(self):
        self.formGroupBox = QGroupBox("Show detailed plots")
        layout = QFormLayout()
        acq = QFormLayout()
        self.checkBoxX = QCheckBox("X Axis")
        self.checkBoxX.stateChanged.connect(
            lambda: self.checkBoxChangedAction("PL1000_CHANNEL_9", self.checkBoxX.isChecked()))
        self.checkBoxY = QCheckBox("Y Axis")
        self.checkBoxY.stateChanged.connect(
            lambda: self.checkBoxChangedAction("PL1000_CHANNEL_10", self.checkBoxY.isChecked()))
        self.checkBoxZ = QCheckBox("Z Axis")
        self.checkBoxZ.stateChanged.connect(
            lambda: self.checkBoxChangedAction("PL1000_CHANNEL_11", self.checkBoxZ.isChecked()))
        self.checkBoxDCV = QCheckBox("DC voltage")
        self.checkBoxDCV.stateChanged.connect(
            lambda: self.checkBoxChangedAction("PL1000_CHANNEL_2", self.checkBoxDCV.isChecked()))
        self.checkBoxDCC = QCheckBox("DC current")
        self.checkBoxDCC.stateChanged.connect(
            lambda: self.checkBoxChangedAction("PL1000_CHANNEL_1", self.checkBoxDCC.isChecked()))
        self.checkBoxACV1 = QCheckBox("AC voltage 1")
        self.checkBoxACV1.stateChanged.connect(
            lambda: self.checkBoxChangedAction("PL1000_CHANNEL_4", self.checkBoxACV1.isChecked()))
        self.checkBoxACV2 = QCheckBox("AC voltage 2")
        self.checkBoxACV2.stateChanged.connect(
            lambda: self.checkBoxChangedAction("PL1000_CHANNEL_6", self.checkBoxACV2.isChecked()))
        self.checkBoxACV3 = QCheckBox("AC voltage 3")
        self.checkBoxACV3.stateChanged.connect(
            lambda: self.checkBoxChangedAction("PL1000_CHANNEL_8", self.checkBoxACV3.isChecked()))
        self.checkBoxACC1 = QCheckBox("AC current 1")
        self.checkBoxACC1.stateChanged.connect(
            lambda: self.checkBoxChangedAction("PL1000_CHANNEL_3", self.checkBoxACC1.isChecked()))
        self.checkBoxACC2 = QCheckBox("AC current 2")
        self.checkBoxACC2.stateChanged.connect(
            lambda: self.checkBoxChangedAction("PL1000_CHANNEL_5", self.checkBoxACC2.isChecked()))
        self.checkBoxACC3 = QCheckBox("AC current 3")
        self.checkBoxACC3.stateChanged.connect(
            lambda: self.checkBoxChangedAction("PL1000_CHANNEL_7", self.checkBoxACC3.isChecked()))
        AC1 = QFormLayout()
        AC1.addRow(self.checkBoxACV1, self.checkBoxACC1)
        AC2 = QFormLayout()
        AC2.addRow(self.checkBoxACV2, self.checkBoxACC2)
        AC3 = QFormLayout()
        AC3.addRow(self.checkBoxACV3, self.checkBoxACC3)
        acq.addRow(self.checkBoxX, AC1)
        acq.addRow(self.checkBoxY, AC2)
        acq.addRow(self.checkBoxZ, AC3)
        acq.addRow(self.checkBoxDCV, self.checkBoxDCC)
        layout.addRow(acq)
        save = QPushButton("Show plots separately")
        save.setStyleSheet('QPushButton {background-color: #5CDB95; color: #05386B;}')
        save.clicked.connect(lambda: self.showdata(self.fft))
        layout.addRow(QLabel(" "), QLabel(" "))
        layout.addRow(QLabel(" "), save)
        self.formGroupBox.setLayout(layout)

    def checkBoxChangedAction(self, channel, state):
        if state == True:
            listplot.append(channel)
        else:
            listplot.remove(channel)

    @pyqtSlot()
    def showdata(self, fft):
        layout = QVBoxLayout()
        self.setLayout(layout)
        for i in listplot:
            if fft == 0:
                dataplot = DialogPlot(i)
            else:
                dataplot = DialogPlotFFT(i, 0)
                dataplot1 = DialogPlotFFT(i, 1)
                layout.addWidget(dataplot1)
                dataplot1.show()
            layout.addWidget(dataplot)
            dataplot.show()
        self.hide()


class DialogPlot(QWidget):

    def __init__(self, channel):
        super(DialogPlot, self).__init__()
        self.channel = channel
        self.graphWidget = pg.PlotWidget()
        layout = QVBoxLayout()
        self.setWindowIcon(QIcon('icon.png'))
        self.setLayout(layout)
        layout.addWidget(self.graphWidget)
        self.graphWidget.showGrid(True, True, 0.5)
        self.graphWidget.setMenuEnabled(False)
        self.setWindowTitle(channel)
        self.graphWidget.plot(dicttime[channel], dictvalue[channel], pen=pg.mkPen('#5CDB95'))


class DialogPlotFFT(QWidget):

    def __init__(self, channel, i):
        super(DialogPlotFFT, self).__init__()
        self.channel = channel
        self.graphWidget = pg.PlotWidget()
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setWindowIcon(QIcon('icon.png'))
        layout.addWidget(self.graphWidget)
        if i == 0:
            self.setWindowTitle(channel + ' - signal with reverse FFT')
        else:
            self.setWindowTitle(channel + '- FFT')
        N = len(dictvalue[channel])
        T = (dicttime[channel][-1] - dicttime[channel][0]) / len(dictvalue[channel])
        y = dictvalue[channel]
        sig_fft = scipy.fft(y)
        sample_freq = scipy.fftpack.fftfreq(N, T)
        power = np.abs(sig_fft)
        pos_mask = np.where(sample_freq > 0)
        freqs = sample_freq[pos_mask]
        peak_freq = freqs[power[pos_mask].argmax()]
        high_freq_fft = sig_fft.copy()
        high_freq_fft[np.abs(sample_freq) > peak_freq] = 0
        filtered_sig = np.real_if_close(scipy.fftpack.ifft(high_freq_fft))
        self.graphWidget.showGrid(True, True, 0.5)
        self.graphWidget.setMenuEnabled(False)
        if i == 0:
            self.graphWidget.plot(dicttime[channel], filtered_sig, pen=pg.mkPen('m'))
            self.graphWidget.plot(dicttime[channel], dictvalue[channel], pen=pg.mkPen('#5CDB95'))
        else:
            #self.graphWidget.plot(sample_freq, power
                                  #, pen=pg.mkPen('#5CDB95'))
            yf = scipy.fftpack.fft(y)
            xf = np.linspace(0.0, 1.0 // (2.0 * T), N // 2)
            self.graphWidget.plot(xf, 2.0/N * np.abs(yf[:N//2]))


class DialogIntValue(QDialog):
    NumGridRows = 3
    NumButtons = 4

    def __init__(self):
        super(DialogIntValue, self).__init__()
        self.createFormGroupBox()
        self.setWindowIcon(QIcon('icon.png'))
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.scroll)
        self.setLayout(mainLayout)
        self.setWindowTitle("Interesting values")

    def createFormGroupBox(self):
        self.scroll = QScrollArea()
        self.formGroupBox = QGroupBox()
        layout = QFormLayout()
        for i in listacq:
            layout.addRow(QLabel(dictinfo[i][1]))
            layout.addRow(QLabel("Mean: "), QLabel(str(np.mean(dictvalue[i])) + " " + dictinfo[i][0]))
            layout.addRow(QLabel("Minimum: "), QLabel(str(np.amin(dictvalue[i])) + " " + dictinfo[i][0]))
            layout.addRow(QLabel("Maximum: "), QLabel(str(np.amax(dictvalue[i])) + " " + dictinfo[i][0]))
            layout.addRow(QLabel(" "))
        self.formGroupBox.setLayout(layout)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.formGroupBox)


if __name__ == '__main__':
    sys_argv = sys.argv
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QColor(5, 56, 107))
    palette.setColor(QtGui.QPalette.WindowText, QColor(92, 219, 149))
    palette.setColor(QtGui.QPalette.Base, QColor(92, 219, 149))
    palette.setColor(QtGui.QPalette.Text, QColor(5, 56, 107))
    palette.setColor(QtGui.QPalette.Button, QColor(92, 219, 149))
    palette.setColor(QtGui.QPalette.ButtonText, QColor(92, 219, 149))
    palette.setColor(QtGui.QPalette.Disabled, QPalette.Light, Qt.transparent)
    palette.setColor(QtGui.QPalette.Highlight, QColor(92, 219, 149))
    palette.setColor(QtGui.QPalette.HighlightedText, QColor(5, 56, 107))
    app.setPalette(palette)
    ex = App()
    sys.exit(app.exec_())
