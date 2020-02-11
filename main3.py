from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *

import sys
import traceback

from screenwatcher import watch_screen


class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.

    Supported signals are:

    error
        `tuple` (exctype, value, traceback.format_exc() )

    data
        `object` data returned from processing, anything

    """
    error = Signal(tuple)
    data = Signal(object)
    quit = Signal(bool)


class Worker(QRunnable):
    """
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    """

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['data_callback'] = self.signals.data

    @Slot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(quit_signal=self.signals.quit, *self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        layout = QVBoxLayout()

        self.l = QLabel("WolfOfStreetsOfTarkov")
        self.d = QLabel("")
        # b = QPushButton("DANGER!")
        # b.pressed.connect(self.oh_no)

        layout.addWidget(self.l)
        layout.addWidget(self.d)

        w = QWidget()
        w.setLayout(layout)

        self.setCentralWidget(w)

        self.show()

        self.threadpool = QThreadPool()
        # print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

        self.worker = Worker(watch_screen)  # Any other args, kwargs are passed to the run function
        self.worker.signals.data.connect(self.data_fn)

        # Execute
        self.threadpool.start(self.worker)

    def data_fn(self, data):
        self.d.setText(data)

    def closeEvent(self, event):
        # self.worker.signals.quit.emit()
        self.worker.quit()
        self.threadpool.waitForDone()


app = QApplication([])
window = MainWindow(None, Qt.WindowStaysOnTopHint)
app.exec_()