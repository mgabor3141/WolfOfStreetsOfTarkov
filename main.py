import sys

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import hotkey
from mainwindow import MarketBotMainWindow


def main():
    app = QApplication(sys.argv)
    win = MarketBotMainWindow(None, Qt.WindowStaysOnTopHint)

    hotkey.init_hotkey(win)

    win.show()
    app.exec_()


if __name__ == '__main__':
    main()
