import sys
import json
from time import sleep
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtGui
import pyqtgraph as pg
from datetime import datetime
import ctypes
import numpy as np
from picosdk.pl1000 import pl1000 as pl
# import matplotlib.pyplot as plt
from picosdk.functions import adc2mV, assert_pico_ok
import ctypes
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
        self.initUI(self.sizeObject.width(),self.sizeObject.height())
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
        mainMenu = self.menuBar()
        self.fileMenu = mainMenu.addMenu('File')
        editMenu = mainMenu.addMenu('Config')
        self.viewMenu = mainMenu.addMenu('View')
        self.testbutton = QPushButton('Connection to the Picolog', self)
        self.testbutton.setToolTip('This is an example button')
        self.testbutton.setFixedSize(180,35)
        self.testbutton.setStyleSheet('QPushButton {background-color: #5CDB95; color: #05386B;}')
        self.testbutton.move(((width - 180)/2),((height - 35)/2))
        self.testbutton.clicked.connect(self.test_connection_pl)
        self.plconnection = QAction('Connection to the Picolog', self)
        self.plconnection.triggered.connect(self.test_connection_pl)
        self.fileMenu.addAction(self.plconnection)
        self.configmenu = QAction('Edit configuration file', self)
        self.configmenu.triggered.connect(self.setconfig)
        editMenu.addAction(self.configmenu)
        exitButton = QAction(QIcon('exit24.png'), 'Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.setStatusTip('Exit application')
        exitButton.triggered.connect(self.close)
        full = QAction('Fullscreen',self)
        full.triggered.connect(self.fullscreennow)
        maxim = QAction('Maximized',self)
        maxim.triggered.connect(self.maximnow)
        self.viewMenu.addAction(full)
        self.viewMenu.addAction(maxim)
        self.fileMenu.addAction(exitButton)
        self.show()

    @pyqtSlot()
    def setconfig(self):
        config = DialogConfig()
        self.layout.addWidget(config)

        config.show()

    @pyqtSlot()
    def test_connection_pl(self):
        try:
            status["openUnit"] = pl.pl1000OpenUnit(ctypes.byref(chandle))
            assert_pico_ok(status["openUnit"])
            self.statusBar().showMessage('Picolog connected')
            self.statusBar().setStyleSheet("background-color : #5CDB95; color: #EDF5E1")
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
        self.plotX.setYRange(-16,16)
        self.plotX.setLabel('left', "acceleration", units="g")
        self.plotY.setTitle('Y axis')
        self.plotY.setLabel('bottom', "time", units='s')
        self.plotY.setYRange(-16,16)
        self.plotY.setLabel('left', "acceleration", units="g")
        self.plotZ.setTitle('Z axis')
        self.plotZ.setLabel('bottom', "time", units='s')
        self.plotZ.setYRange(-16,16)
        self.plotZ.setLabel('left', "acceleration", units="g")
        self.plotDCV = pg.PlotWidget()
        self.plotDCV.setTitle('Power supply voltage')
        self.plotDCV.setLabel('bottom', "time", units='s')
        self.plotDCV.setYRange(0,60)
        self.plotDCV.setLabel('left', "voltage", units="V")
        self.plotACV = pg.PlotWidget()
        self.plotACV.setTitle('Three phase voltages')
        self.plotACV.setLabel('bottom', "time", units='s')
        self.plotACV.setYRange(-60,60)
        self.plotACV.setLabel('left', "voltage", units="V")
        self.plotDCC = pg.PlotWidget()
        self.plotDCC.setTitle('Power supply current')
        self.plotDCC.setLabel('bottom', "time", units='s')
        self.plotDCC.setYRange(0,30)
        self.plotDCC.setLabel('left', "ampere", units="A")
        self.plotACC = pg.PlotWidget()
        self.plotACC.setTitle('Three phase currents')
        self.plotACC.setLabel('bottom', "time", units='s')
        self.plotACC.setYRange(-30,30)
        self.plotACC.setLabel('left', "ampere", units="A")
        grid = QGridLayout()
        w.setLayout(grid)
        grid.addWidget(self.plotX, 1,0,2,1)
        grid.addWidget(self.plotY, 3,0,2,1)
        grid.addWidget(self.plotZ, 5,0,2,1)
        grid.addWidget(self.plotDCV, 1,1,3,1)
        grid.addWidget(self.plotACV, 4,1,3,1)
        grid.addWidget(self.plotDCC, 1,5,3,1)
        grid.addWidget(self.plotACC, 4,5,3,1)
        self.setCentralWidget(w)
        #grid.show()
        # width = self.sizeObject.width() / 300
        # height = (self.sizeObject.height() - 160) / 300
        # self.x = PlotCanvasX(self, width, height)
        # self.x.move(0, 20)
        # self.layout.addWidget(self.x)
        # self.x.show()
        # self.y = PlotCanvasY(self, width, height)
        # self.y.move(0, (20 + height * 100))
        # self.layout.addWidget(self.y)
        # self.y.show()
        # self.z = PlotCanvasZ(self, width, height)
        # self.z.move(0, (20 + height * 200 - 1))
        # self.layout.addWidget(self.z)
        # self.z.show()
        # self.x.plotX(0, self.countdataX, self.dataX)
        # self.y.plotY(0, self.countdataY, self.dataY)
        # self.z.plotZ(0, self.countdataZ, self.dataY)
        # self.qTimer = QTimer()
        # self.qTimer.setInterval(100)
        # # connect timeout signal to signal handler
        # self.qTimer.timeout.connect(self.update_accel)
        self.startplot = QPushButton('Start plotting', self)
        self.startplot.setStyleSheet('QPushButton {background-color: #5CDB95; color: #05386B;}')
        # self.startplot.setToolTip('This is an example button')
        self.startplot.setFixedSize(100, 35)
        # self.startplot.move(((self.sizeObject.width() / 3 - 200) / 3), (self.sizeObject.height() - 130))
        self.startplot.clicked.connect(self.update_accel)
        grid.addWidget(self.startplot,7,0)

        # self.resetplot = QPushButton('Reset plotting', self)
        # self.resetplot.setToolTip('This is an example button')
        # self.resetplot.setFixedSize(100, 35)
        # self.resetplot.move(((self.sizeObject.width() *2/3 - 100) / 3), (self.sizeObject.height() - 130))
        # self.resetplot.clicked.connect(self.resetview)

        # self.stopplot = QPushButton('Stop plotting', self)
        # self.stopplot.setToolTip('This is an example button')
        # self.stopplot.setFixedSize(100, 35)
        # self.stopplot.move(((self.sizeObject.width() / 3 - 200) / 3), (self.sizeObject.height() - 130))
        # self.layout.addWidget(self.stopplot)
        # # self.startaccel.move(((self.sizeObject.width() * 1 / 1.3) + (self.sizeObject.width() - (self.sizeObject.width() * 1 / 1.3) - 150) / 2), 85)
        # self.stopplot.clicked.connect(self.stopview)
        # #TODO: error with accel values
        # self.layout.addWidget(self.startplot)
        # self.layout.addWidget(self.stopplot)
        # # self.calib.show()
        # self.startplot.show()
        # self.resetplot.show()
        # self.resetplot.setDisabled(True)
        # self.plotDC()
        # self.plotAC()

    def plotDC(self):
        width = self.sizeObject.width() / 300
        height = (self.sizeObject.height() - 160) / 200
        #self.DCV = PlotCanvasDCVoltage(self, width, height)
        self.DCV.move(width*100, 20)
        self.layout.addWidget(self.DCV)
        self.DCV.show()
        #self.DCC = PlotCanvasDCCurrent(self, width, height)
        self.DCC.move(200*width, 20)
        self.layout.addWidget(self.DCC)
        self.DCC.show()
        self.DCV.plotDCVol(0)
        self.DCC.plotDCCur(0)

    def plotAC(self):
        width = self.sizeObject.width() / 300
        height = ((self.sizeObject.height() - 160) / 200)
        #self.ACV = PlotCanvasACVoltage(self, width, height)
        self.ACV.move((width * 100), (20 + height*100))
        self.layout.addWidget(self.ACV)
        self.ACV.show()
        #self.ACC = PlotCanvasACCurrent(self, width, height)
        self.ACC.move((200 * width), (20 + height*100))
        self.layout.addWidget(self.ACC)
        self.ACC.show()
        self.ACV.plotACVol(0)
        self.ACC.plotACCur(0)

    @pyqtSlot()
    def startview(self):
        self.qTimer = QTimer()
        self.qTimer.setInterval(100)
        self.i = 0
        self.qTimer.timeout.connect(self.update_accel)
        self.startplot.setText("In progress")
        self.plotX.clear()
        self.plotY.clear()
        self.plotZ.clear()
        self.countdataX = np.arange(0)
        self.countdataZ = np.arange(0)
        self.countdataY = np.arange(0)
        self.dataX = np.arange(0)
        self.dataY = np.arange(0)
        self.dataZ = np.arange(0)
        self.qTimer.start()
        self.startplot.hide()
        self.stopplot.show()

    @pyqtSlot()
    def stopview(self):
        self.qTimer.stop()
        # self.update_accel()
        self.startplot.show()
        self.stopplot.hide()
        self.resetplot.setDisabled(False)

    @pyqtSlot()
    def resetview(self):
        # self.update_accel()
        self.dataX = np.arange(0)
        self.dataY = np.arange(0)
        self.dataZ = np.arange(0)
        # self.x.plotX(1, self.countdata, self.dataX)
        # self.y.plotY(1, self.countdata, self.dataY)
        # self.z.plotZ(1, self.countdata, self.dataZ)
        self.resetplot.setDisabled(True)

    def update_accel(self):
        self.startplot.setText("Done")
        # self.i +=1
        # self.countdata = np.append(self.countdata, [self.i*0.1])
        # self.dataX = np.append(self.dataX, [(valueX.value*2.5/4092 - 1.265)*9.81/0.041])
        # self.x.plotX(0, self.countdata, self.dataX)
        # self.dataY = np.append(self.dataY, [(valueY.value*2.5/4092 - 1.237)*9.81/0.045])
        # self.y.plotY(0, self.countdata, self.dataY)
        # self.dataZ = np.append(self.dataZ, [(valueZ.value*2.5/4092- 1.273)*9.81/0.049])
        # self.z.plotZ(0, self.countdata, self.dataZ)
        #status["SetDo"] = pl.pl1000SetDo(chandle, 1, 1)
        start = datetime.now()
        start = start.hour*3600000000 + start.minute*60000000 + start.second*1000000 + start.microsecond
        now = datetime.now()
        now = now.hour*3600000000 + now.minute*60000000 + now.second*1000000 + now.microsecond
        with open("config.json", "r") as read_file:
            time = json.load(read_file)
        while (now - start) < int(time["time"][0]["time"]):
            status["SetDo"] = pl.pl1000SetDo(chandle, 1, 0)
            now = datetime.now()
            now = now.hour*3600000000 + now.minute*60000000 + now.second*1000000 + now.microsecond
            self.countdataX, self.dataX = self.measure(self.countdataX, self.dataX, "PL1000_CHANNEL_9", chandle, start)
            self.countdataY, self.dataY = self.measure(self.countdataY, self.dataY, "PL1000_CHANNEL_10", chandle, start)
            self.countdataZ, self.dataZ = self.measure(self.countdataZ, self.dataZ, "PL1000_CHANNEL_11", chandle, start)
            self.countdataDCC, self.dataDCC = self.measure(self.countdataDCC, self.dataDCC, "PL1000_CHANNEL_1", chandle, start)
            status["SetDo"] = pl.pl1000SetDo(chandle, 0, 0)
            self.countdataDCV, self.dataDCV = self.measure(self.countdataDCV, self.dataDCV, "PL1000_CHANNEL_2", chandle, start)
            self.countdataACC1, self.dataACC1 = self.measure(self.countdataACC1, self.dataACC1, "PL1000_CHANNEL_3", chandle, start)
            self.countdataACV1, self.dataACV1 = self.measure(self.countdataACV1, self.dataACV1, "PL1000_CHANNEL_4", chandle, start)
            self.countdataACC2, self.dataACC2 = self.measure(self.countdataACC2, self.dataACC2, "PL1000_CHANNEL_5", chandle, start)
            status["SetDo"] = pl.pl1000SetDo(chandle, 1, 0)
            self.countdataACV2, self.dataACV2 = self.measure(self.countdataACV2, self.dataACV2, "PL1000_CHANNEL_6", chandle, start)
            self.countdataACC3, self.dataACC3 = self.measure(self.countdataACC3, self.dataACC3, "PL1000_CHANNEL_7", chandle, start)
            self.countdataACV3, self.dataACV3 = self.measure(self.countdataACV3, self.dataACV3, "PL1000_CHANNEL_8", chandle, start)
            status["SetDo"] = pl.pl1000SetDo(chandle, 0, 0)
        status["SetDo"] = pl.pl1000SetDo(chandle, 0, 0)
        status["SetDo"] = pl.pl1000SetDo(chandle, 0, 1)
        with open("config.json", "r") as read_file:
            config = json.load(read_file)
        self.plotX.plot(self.countdataX,self.dataX, pen=pg.mkPen('#5CDB95'))
        self.plotY.plot(self.countdataY,self.dataY, pen=pg.mkPen('#5CDB95'))
        self.plotZ.plot(self.countdataZ,self.dataZ, pen=pg.mkPen('#5CDB95'))
        self.plotDCV.plot(self.countdataDCV, (self.dataDCV/4092)*60, pen=pg.mkPen('#5CDB95'))
        self.plotDCC.plot(self.countdataDCC, ((self.dataDCC - int(config["DCcurrent"][0]["offset"]))/4092)*30, pen=pg.mkPen('#5CDB95'))
        self.plotACV.plot(self.countdataACV1, ((self.dataACV1 - int(config["ACvoltage"][0]["offset1"]))/4092)*60, pen=pg.mkPen('m'))
        self.plotACV.plot(self.countdataACV2, ((self.dataACV2 - int(config["ACvoltage"][0]["offset2"]))/4092)*60, pen=pg.mkPen('#5CDB95'))
        self.plotACV.plot(self.countdataACV3, ((self.dataACV3 - int(config["ACvoltage"][0]["offset3"]))/4092)*60, pen=pg.mkPen('#EDF5E1'))
        self.plotACC.plot(self.countdataACC1, ((self.dataACC1 - int(config["ACcurrent"][0]["offset1"]))/4092)*30, pen=pg.mkPen('m'))
        self.plotACC.plot(self.countdataACC2, ((self.dataACC2 - int(config["ACcurrent"][0]["offset2"]))/4092)*30, pen=pg.mkPen('#5CDB95'))
        self.plotACC.plot(self.countdataACC3, ((self.dataACC3 - int(config["ACcurrent"][0]["offset3"]))/4092)*30, pen=pg.mkPen('#EDF5E1'))

    def measure(self, countdataX, dataX, channel , chandle, start):
        value = ctypes.c_int16()
        status["getSingle"] = pl.pl1000GetSingle(chandle, pl.PL1000Inputs[channel], ctypes.byref(value))
        now = datetime.now()
        now = now.hour*3600000000 + now.minute*60000000 + now.second*1000000 + now.microsecond
        countdataX = np.append(countdataX, [(now - start)*0.000001])
        dataX = np.append(dataX, [(value.value)])
        assert_pico_ok(status["getSingle"])
        return [countdataX, dataX]

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
        qline1 = QLineEdit()
        layout.addRow(QLabel("offset:"), qline1)
        layout.addRow(QLabel("AC voltages"))
        qline2 = QLineEdit()
        layout.addRow(QLabel("offset AC1:"), qline2)
        qline3 = QLineEdit()
        layout.addRow(QLabel("offset AC2:"), qline3)
        qline4 = QLineEdit()
        layout.addRow(QLabel("offset AC3:"), qline4)
        layout.addRow(QLabel("AC currents"))
        qline5 = QLineEdit()
        layout.addRow(QLabel("offset AC1:"), qline5)
        qline6 = QLineEdit()
        layout.addRow(QLabel("offset AC2:"), qline6)
        qline7 = QLineEdit()
        layout.addRow(QLabel("offset AC3:"), qline7)
        layout.addRow(QLabel("Accelerometer"))
        qline8 = QLineEdit()
        layout.addRow(QLabel("X axis:"), qline8)
        qline9 = QLineEdit()
        layout.addRow(QLabel("Y axis:"), qline9)
        qline10 = QLineEdit()
        layout.addRow(QLabel("Z axis:"), qline10)
        layout.addRow(QLabel("Time of sampling"))
        qline11 = QLineEdit()
        layout.addRow(QLabel("Nbr of microseconds:"), qline11)
        layout.addRow(QPushButton("Cancel"), QPushButton("Save"))
        self.formGroupBox.setLayout(layout)

if __name__ == '__main__':
    sys_argv = sys.argv
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QColor(5, 56, 107))
    palette.setColor(QtGui.QPalette.WindowText, QColor(92, 219, 149))
    palette.setColor(QtGui.QPalette.Base, QColor(92, 219, 149))
    palette.setColor(QtGui.QPalette.AlternateBase, QColor(0,0,0))
    palette.setColor(QtGui.QPalette.ToolTipBase, Qt.white)
    palette.setColor(QtGui.QPalette.ToolTipText, QColor(0,0,0))
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