import sys
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *

from screenwatcher import ScreenWatcher


class QCustomMainWindow(QMainWindow):
    def __init__(self, *args):
        super(QCustomMainWindow, self).__init__(*args)

        self.setWindowTitle('WolfOfStreetsOfTarkov')
        self.text = QLabel("")
        self.setCentralWidget(self.text)
        self.screen_watcher = ScreenWatcher(self)

        def data_cb(progress):
            self.text.setText(progress)

        self.screen_watcher.progressLoad.connect(data_cb)

        self.screen_watcher.start()

    # def closeEvent(self, event):
    #     self.screen_watcher.cancel()
        # self.worker.signals.quit.emit()
        # self.worker.quit()
        # self.threadpool.waitForDone()


myQApplication = QApplication(sys.argv)
myQCustomMainWindow = QCustomMainWindow(None, Qt.WindowStaysOnTopHint)
myQCustomMainWindow.show()
myQApplication.exec_()
