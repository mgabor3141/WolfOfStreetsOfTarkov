from ctypes import windll, create_unicode_buffer
from enum import Enum
from random import random
from time import sleep
from timeit import default_timer

import mss
import pyautogui
from PySide2.QtCore import QThread, Signal, Slot

from buyer import evaluate_listing
from constants import LINE_HEIGHT
from screenwatcher import ScreenWatcher

pyautogui.PAUSE = 0.1

PURCHASE_OFFSET = 1730, 185


class State(Enum):
    WAIT_FOR_REFRESH = 0
    WAIT_FOR_LISTINGS = 1
    WAIT_FOR_BUY_BUTTON = 2
    WAIT_FOR_BUY_RESULT = 3


class MarketBot(QThread):
    listings_signal = Signal(object)
    successful_buy_signal = Signal(object)
    fault_signal = Signal(object)  # TODO (eg. Item move error)

    def __init__(self, parentQWidget=None):
        super(MarketBot, self).__init__(parentQWidget)

        self.screenwatcher = None

        self.buying = False
        self.price = None
        self.state = State.WAIT_FOR_LISTINGS
        self.next_refresh = 0
        self.listings = None
        self.last_buy_number = None
        self.unavailable_listings = None

    @Slot(bool)
    def buying_changed(self, buying):
        self.buying = buying

    @Slot(bool)
    def price_changed(self, price):
        try:
            self.price = int(price)
        except:
            self.price = 0

    def run(self):
        with mss.mss() as sct:
            self.screenwatcher = ScreenWatcher(sct)

            while True:
                if not self.buying or not get_foreground_window_title() == "EscapeFromTarkov":
                    sleep(0.5)
                    continue

                if self.state is State.WAIT_FOR_REFRESH:
                    if self.next_refresh < default_timer():
                        self.refresh()
                        sleep(0.08)
                        self.next_refresh = default_timer() + self.refresh_interval()
                        self.state = State.WAIT_FOR_LISTINGS

                elif self.state is State.WAIT_FOR_LISTINGS:
                    self.listings = self.screenwatcher.find_listings()
                    if self.listings:
                        self.listings_signal.emit(self.listings)
                        self.unavailable_listings = set()
                        self.state = State.WAIT_FOR_BUY_BUTTON

                elif self.state is State.WAIT_FOR_BUY_BUTTON:
                    wait_more = False
                    buyable_items = self.screenwatcher.find_purchase_buttons() - self.unavailable_listings
                    for i in range(0, len(self.listings)):
                        if i not in self.unavailable_listings and evaluate_listing(self.listings[i], self.price):
                            wait_more = True
                            if i in buyable_items:
                                self.buy(i)
                                self.state = State.WAIT_FOR_BUY_RESULT
                                break
                    if not wait_more:
                        self.state = State.WAIT_FOR_REFRESH

                elif self.state is State.WAIT_FOR_BUY_RESULT:
                    if self.last_buy_number in self.screenwatcher.find_purchase_or_outofstock():
                        sleep(0.1)
                        error = self.screenwatcher.find_error_ok_button()
                        if error:
                            print("\tPurchase unsuccessful")
                            self.unavailable_listings.add(self.last_buy_number)
                            pyautogui.click(error)
                        else:
                            print("\tPurchase successful")
                            self.successful_buy_signal.emit(self.listings[self.last_buy_number])
                            new_listings = []
                            for i in range(0, len(self.listings)):
                                if i != self.last_buy_number:
                                    self.listings[i].coord -= LINE_HEIGHT
                                    new_listings.append(self.listings[i])
                            self.listings = new_listings
                        self.state = State.WAIT_FOR_BUY_BUTTON

    def refresh(self):
        # Todo: right click filter by item
        self.listings = None
        pyautogui.press('f5')

    def refresh_interval(self):
        # Todo intelligent backoff based on price
        return 3.1 + random()

    def buy(self, listing_no):
        self.last_buy_number = listing_no
        listing = self.listings[listing_no]
        print("Buying {}".format(listing))
        pyautogui.click(x=PURCHASE_OFFSET[0], y=PURCHASE_OFFSET[1] + listing.coord)
        pyautogui.press('y')
        pyautogui.moveTo(x=PURCHASE_OFFSET[0], y=120)


def get_foreground_window_title():
    hWnd = windll.user32.GetForegroundWindow()
    length = windll.user32.GetWindowTextLengthW(hWnd)
    buf = create_unicode_buffer(length + 1)
    windll.user32.GetWindowTextW(hWnd, buf, length + 1)

    return buf.value if buf.value else None