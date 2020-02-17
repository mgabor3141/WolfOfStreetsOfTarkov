import random
import sys
from ctypes import windll, create_unicode_buffer

import pyautogui
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from pyqtkeybind import keybinder

from marketbot import MarketBot


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


class MarketBotMainWindow(QMainWindow):
    buying_signal = Signal(bool)

    def __init__(self, *args):
        super(MarketBotMainWindow, self).__init__(*args)
        # self.last_time = timeit.default_timer()
        self.setWindowTitle('WolfOfStreetsOfTarkov')
        self.setGeometry(1910, 700, 370, 200)

        self.buy_button = QPushButton("")
        self.buy_button.clicked.connect(self.toggle_buying)

        self.text = QLabel("")
        self.successful_buys_text = QLabel("")
        self.target_price = QLineEdit(self)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.buy_button)
        main_layout.addWidget(self.target_price)
        main_layout.addWidget(self.text)
        main_layout.addWidget(self.successful_buys_text)

        wrapper_widget = QWidget()
        wrapper_widget.setLayout(main_layout)
        self.setCentralWidget(wrapper_widget)

        self.marketbot = MarketBot(self)
        self.buying_signal.connect(self.marketbot.buying_changed)
        self.target_price.textChanged.connect(self.marketbot.price_changed)

        self.buying = False
        self.update_buy_state()
        self.target_price.setText("12000")

        def listing_cb(listings):
            self.text.setText(
                '\n'.join(["{} ({:.0f})".format(str(l), l.rub_value() if l.rub_value() is not None else -1)
                           for l in listings]))

        self.marketbot.listings_signal.connect(listing_cb)

        self.successful_buys = []

        def buy_cb(listing):
            self.successful_buys.append(listing)
            numbuys = len(self.successful_buys)
            self.successful_buys_text.setText(
                "Bought {} for {:.1f} rub avg".format(
                    numbuys, sum([l.rub_value() for l in self.successful_buys]) / numbuys))

        self.marketbot.successful_buy_signal.connect(buy_cb)
        self.marketbot.start()

    def update_buy_state(self):
        self.buying_signal.emit(self.buying)
        if self.buying:
            print("Buying active")
            self.buy_button.setText("Du not baj (Ctrl + Alt + B)")
        else:
            print("Buying not active")
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
    win = MarketBotMainWindow(None, Qt.WindowStaysOnTopHint)

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
