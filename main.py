import sys
from timeit import default_timer

from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from pyqtkeybind import keybinder
import pyqtgraph as pg

from marketbot import MarketBot


class MarketBotMainWindow(QMainWindow):
    buying_signal = pyqtSignal(bool)

    def __init__(self, *args):
        super(MarketBotMainWindow, self).__init__(*args)
        self.setWindowTitle('WolfOfStreetsOfTarkov')
        self.setGeometry(15, 560, 600, 500)

        self.main = uic.loadUi("main.ui")
        self.setCentralWidget(self.main)

        self.prices_scatter = pg.ScatterPlotItem(pen='w', symbol='o', size=1)
        self.bought_prices_scatter = pg.ScatterPlotItem(pen=(255, 64, 32, 255), symbol='o', size=1)
        self.target_price_line = pg.InfiniteLine(pen=(128, 128, 255, 64), angle=0, pos=1)
        self.main.chart.addItem(self.prices_scatter)
        self.main.chart.addItem(self.bought_prices_scatter)
        self.main.chart.addItem(self.target_price_line)

        self.marketbot = MarketBot(self)
        self.buying_signal.connect(self.marketbot.buying_changed)

        def price_changed(price):
            self.target_price_line.setValue(price)
        self.main.target_price.valueChanged.connect(self.marketbot.price_changed)
        self.main.target_price.valueChanged.connect(price_changed)
        self.main.target_price.setValue(0)

        self.buying = False
        self.set_buying()

        def listing_cb(listings):
            self.prices_scatter.addPoints([default_timer()], [listings[0].rub_value()])

        self.marketbot.listings_signal.connect(listing_cb)

        self.successful_buys = []

        def buy_cb(listing=None):
            if listing is not None:
                if self.main.buy_limit_enabled.isChecked():
                    limit = self.main.buy_limit.value() - 1
                    if limit == 0:
                        self.main.buy_limit_enabled.setChecked(False)
                        self.set_buying(False)
                    self.main.buy_limit.setValue(limit)

                if self.main.spend_limit_enabled.isChecked():
                    limit = self.main.spend_limit.value() - listing.total_value()
                    if limit <= 0:
                        self.main.spend_limit_enabled.setChecked(False)
                        self.set_buying(False)
                        limit = 0
                    self.main.spend_limit.setValue(limit)

                self.bought_prices_scatter.addPoints([default_timer()], [listing.rub_value()])
                self.successful_buys.append(listing)

            num_buys = len(self.successful_buys)
            self.main.total_label.setText(f"Bought: {num_buys}")
            self.main.avg_label.setText("Average Price: {:,.1f}".format(
                    sum([l.rub_value() for l in self.successful_buys]) / num_buys if num_buys else 0))
            self.main.spent_label.setText("Spent: {:,}".format(sum([l.total_value() for l in self.successful_buys])))
        self.marketbot.successful_buy_signal.connect(buy_cb)

        def reset_buys():
            self.successful_buys = []
            self.prices_scatter.clear()
            self.bought_prices_scatter.clear()
            buy_cb()
        self.main.reset_stats.clicked.connect(reset_buys)

        self.main.buy_button.clicked.connect(self.toggle_buying)

        self.marketbot.start()

    def set_buying(self, buying=None):
        if buying is not None:
            self.buying = buying
        self.buying_signal.emit(self.buying)
        if self.buying:
            print("Buying active")
            self.main.buy_button.setText("Stop buying (Ctrl + Alt + B)")
        else:
            print("Buying not active")
            self.main.buy_button.setText("Start buying (Ctrl + Alt + B)")

    def toggle_buying(self):
        self.set_buying(not self.buying)


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
