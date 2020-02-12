import sys
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *

from screenwatcher import ScreenWatcher


class QCustomMainWindow(QMainWindow):
    def __init__(self, *args):
        super(QCustomMainWindow, self).__init__(*args)

        self.setWindowTitle('WolfOfStreetsOfTarkov')
        self.setGeometry(200, 500, 370, 450)

        self.buy_button = QPushButton("Dubaj")
        # self.buy_button.clicked.connect()
        self.text = QLabel("")

        self.lo = QVBoxLayout()
        self.lo.addWidget(self.buy_button)
        self.lo.addWidget(self.text)

        self.widget = QWidget()
        self.widget.setLayout(self.lo)
        self.setCentralWidget(self.widget)

        self.screen_watcher = ScreenWatcher(self)

        def data_cb(listings):
            self.text.setText('\n'.join([str(l) for l in listings]))
        self.screen_watcher.listings_signal.connect(data_cb)

        self.screen_watcher.start()

    # def closeEvent(self, event):
    #     self.screen_watcher.cancel()
        # self.worker.signals.quit.emit()
        # self.worker.quit()
        # self.threadpool.waitForDone()


app = QApplication(sys.argv)
win = QCustomMainWindow(None, Qt.WindowStaysOnTopHint)
win.show()
app.exec_()
