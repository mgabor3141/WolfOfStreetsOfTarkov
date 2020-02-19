import random
import sys
from ctypes import windll, create_unicode_buffer
from timeit import default_timer

import pyautogui
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from pyqtkeybind import keybinder
import pyqtgraph as pg

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
    buying_signal = pyqtSignal(bool)

    def __init__(self, *args):
        super(MarketBotMainWindow, self).__init__(*args)
        self.setWindowTitle('WolfOfStreetsOfTarkov')
        self.setGeometry(100, 600, 600, 500)

        self.main = uic.loadUi("main.ui")
        self.setCentralWidget(self.main)

        self.prices_scatter = pg.ScatterPlotItem(pen='w', symbol='o', size=1)
        self.bought_prices_scatter = pg.ScatterPlotItem(pen='r', symbol='o', size=1)
        self.main.chart.addItem(self.prices_scatter)
        self.main.chart.addItem(self.bought_prices_scatter)

        self.marketbot = MarketBot(self)
        self.buying_signal.connect(self.marketbot.buying_changed)
        self.main.target_price.valueChanged.connect(self.marketbot.price_changed)

        self.buying = False
        self.update_buy_state()

        def listing_cb(listings):
            self.prices_scatter.addPoints([default_timer()], [listings[0].rub_value()])

        self.marketbot.listings_signal.connect(listing_cb)

        self.successful_buys = []

        def buy_cb(listing):
            if self.main.limit_enabled.isChecked():
                limit = self.main.buy_limit.value() - 1
                if limit == 0:
                    self.buying = False
                    self.update_buy_state()
                self.main.buy_limit.setValue(limit)

            self.bought_prices_scatter.addPoints([default_timer()], [listing.rub_value()])
            self.successful_buys.append(listing)
            num_buys = len(self.successful_buys)
            self.main.total_label.setText("Bought: {}".format(num_buys))
            self.main.avg_label.setText("Average Price: {:.1f}".format(sum([l.rub_value() for l in self.successful_buys]) / num_buys))
        self.marketbot.successful_buy_signal.connect(buy_cb)

        def reset_buys():
            self.successful_buys = []
            self.prices_scatter.clear()
            self.bought_prices_scatter.clear()
        self.main.reset_stats.clicked.connect(reset_buys)

        self.main.buy_button.clicked.connect(self.toggle_buying)

        self.marketbot.start()

    def update_buy_state(self):
        self.buying_signal.emit(self.buying)
        if self.buying:
            print("Buying active")
            self.main.buy_button.setText("Stop buying (Ctrl + Alt + B)")
        else:
            print("Buying not active")
            self.main.buy_button.setText("Start buying (Ctrl + Alt + B)")

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
