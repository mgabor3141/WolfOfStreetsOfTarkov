import random
import sys
import timeit

import pyautogui
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from pyqtkeybind import keybinder
from ctypes import windll, create_unicode_buffer

from buyer import buy
from constants import *
from screenwatcher import ScreenWatcher


def get_foreground_window_title():
    hWnd = windll.user32.GetForegroundWindow()
    length = windll.user32.GetWindowTextLengthW(hWnd)
    buf = create_unicode_buffer(length + 1)
    windll.user32.GetWindowTextW(hWnd, buf, length + 1)

    return buf.value if buf.value else None


def refresh():
    if get_foreground_window_title() == "EscapeFromTarkov":
        pyautogui.press('f5')


def refresh_interval():
    return 3.1 + random.random()


class QCustomMainWindow(QMainWindow):
    def __init__(self, *args):
        super(QCustomMainWindow, self).__init__(*args)
        self.last_time = timeit.default_timer()

        self.setWindowTitle('WolfOfStreetsOfTarkov')
        self.setGeometry(100, 700, 370, 200)

        self.buy_button = QPushButton("")
        self.buy_button.clicked.connect(self.toggle_buying)

        self.text = QLabel("")
        self.frametime = QLabel("")
        self.target_price = QLineEdit(self)

        self.lo = QVBoxLayout()
        self.lo.addWidget(self.buy_button)
        self.lo.addWidget(self.target_price)
        self.lo.addWidget(self.text)
        self.lo.addWidget(self.frametime)

        self.widget = QWidget()
        self.widget.setLayout(self.lo)
        self.setCentralWidget(self.widget)

        self.screen_watcher = ScreenWatcher(self)

        self.buying = False
        self.update_buy_state()

        self.buying_until = 0
        self.refresh_interval = refresh_interval()

        def data_cb(data):
            if timeit.default_timer() < self.buying_until:
                return

            listings, frametime = data

            self.frametime.setText("Frame time: {:6.2f}ms".format(frametime))

            self.text.setText(
                '\n'.join(["{} ({:.0f})".format(str(l), l.rub_value() if l.rub_value() is not None else -1)
                           for l in listings]))

            if self.buying and self.target_price.text().isdigit() and get_foreground_window_title() == "EscapeFromTarkov":
                self.buying_until = timeit.default_timer() + CLICK_TIME * 5 * buy(listings, int(self.target_price.text()))

            if self.buying and timeit.default_timer() - self.last_time >= self.refresh_interval:
                refresh()
                self.last_time = timeit.default_timer()
                self.refresh_interval = refresh_interval()

        self.screen_watcher.listings_signal.connect(data_cb)

        self.screen_watcher.start()

    def update_buy_state(self):
        if self.buying:
            print("Buying")
            self.buy_button.setText("Du not baj (Ctrl + Alt + B)")
            refresh()
        else:
            print("No longer buying")
            self.buy_button.setText("Dubaj (Ctrl + Alt + B)")

    def toggle_buying(self):
        self.buying = not self.buying
        self.update_buy_state()


class WinEventFilter(QAbstractNativeEventFilter):
    def __init__(self, _keybinder):
        self.keybinder = _keybinder
        super().__init__()

    def nativeEventFilter(self, eventType, message):
        ret = self.keybinder.handler(eventType, message)
        return ret, 0


def main():
    app = QApplication(sys.argv)
    win = QCustomMainWindow(None, Qt.WindowStaysOnTopHint)

    keybinder.init()
    keybinder.register_hotkey(win.winId(), "Ctrl+Alt+B", win.toggle_buying)

    # Install a native event filter to receive events from the OS
    win_event_filter = WinEventFilter(keybinder)
    event_dispatcher = QAbstractEventDispatcher.instance()
    event_dispatcher.installNativeEventFilter(win_event_filter)

    win.show()
    app.exec_()


if __name__ == '__main__':
    main()
