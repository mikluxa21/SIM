import sys

from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5 import QtCore, QtTest
import os #Used in Testing Script
import pyqtgraph as pg
import numpy as np
from examples.test_ps5000a import pico_worker

FILE_NAME_PY = "Sim_Interface.py"
FILE_NAME_UI = "SIM_Interface_2.1.ui"

if not os.path.isfile(FILE_NAME_PY):
    if not os.path.isfile(FILE_NAME_UI):
        raise Exception("Not found .ui model")
    else:
        os.system(f"pyuic5 -o {FILE_NAME_PY} {FILE_NAME_UI}")
from Sim_Interface import Ui_MainWindow


class MyApplication(QMainWindow):
    def __init__(self):
        self.filename = ""
        super().__init__()
        # Create an instance of the UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.change_file)
        self.ui.actionOpen.triggered.connect(self.change_file)
        self.ui.actionDraw.triggered.connect(self.draw_run)

        #self.data = [np.random.randint(low=0, high=10, size=None, dtype=int)/10 for i in range(1000)]
        #self.i = 0
        self.ui.widget.setBackground("w")
        self.line = self.ui.widget.plot(
            name="Temperature Sensor",
            pen=pg.mkPen(color=(255, 0, 0)),
        )



    def change_file(self):
        self.filename, ok = QFileDialog.getOpenFileName(self,
                                                     "Выберите файл",
                                                     ".npy",
                                                     "Only Files(*.npy)")
        if ok:
            self.ui.lineEdit_15.setText(self.filename)

    def draw_run(self):
        self.thread = QtCore.QThread()
        self.thread.started.connect(self.draw_graphik)
        self.thread.start()

    def draw_graphik(self):
        while True:
            self.data = pico_worker.get_data()
            self.i = 0
            for i in self.data:
                print(i[0])
                for j in range(len(i) - 25):
                    self.line.setData(abs(i)[self.i:self.i+25])
                    self.i += 1

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApplication()
    window.show()
    sys.exit(app.exec_())