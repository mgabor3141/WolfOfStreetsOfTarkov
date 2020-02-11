import sys
import time
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *


from screenwatcher import ScreenWatcher


class QCustomMainWindow(QMainWindow):
    def __init__(self):
        super(QCustomMainWindow, self).__init__()
        # Create action with QPushButton
        self.startQPushButton = QPushButton('START')
        self.startQPushButton.released.connect(self.startWork)
        self.setCentralWidget(self.startQPushButton)
        # Create QProgressDialog
        self.loadingQProgressDialog = QProgressDialog(self)
        self.loadingQProgressDialog.setLabelText('Loading')
        self.loadingQProgressDialog.setCancelButtonText('Cancel')
        self.loadingQProgressDialog.setWindowModality(Qt.WindowModal)

    def startWork(self):
        myQCustomThread = ScreenWatcher(self)

        def startLoadCallBack(numberOfprogress):
            self.loadingQProgressDialog.setMinimum(0)
            self.loadingQProgressDialog.setMaximum(numberOfprogress)
            self.loadingQProgressDialog.show()

        def progressLoadCallBack(progress):
            self.loadingQProgressDialog.setValue(progress)

        def statusLoadCallBack(flag):
            print
            'SUCCESSFUL' if flag else 'FAILED'

        myQCustomThread.startLoad.connect(startLoadCallBack)
        myQCustomThread.progressLoad.connect(progressLoadCallBack)
        myQCustomThread.statusLoad.connect(statusLoadCallBack)
        self.loadingQProgressDialog.canceled.connect(myQCustomThread.cancel)
        myQCustomThread.start()


myQApplication = QApplication(sys.argv)
myQCustomMainWindow = QCustomMainWindow()
myQCustomMainWindow.show()
sys.exit(myQApplication.exec_())
