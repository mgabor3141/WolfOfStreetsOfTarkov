import pyautogui

from listing import *
from constants import *

pyautogui.PAUSE = CLICK_TIME


def buy(listings, target_value, currencies=None):
    if currencies is None:
        currencies = {'rub'}

    # items_to_buy = 0

    for l in listings:
        if l.rub_value() is not None and l.rub_value() <= target_value and l.currency in currencies:
            # items_to_buy += 1
            buy_listing(l)
            return 1

    return 0
    # return items_to_buy


def buy_listing(listing: Listing):
    print("Buying listing: {}".format(listing))
    pyautogui.click(x=PURCHASE_OFFSET[0], y=PURCHASE_OFFSET[1] + listing.coord)
    # pyautogui.click(x=ALL_BUTTON[0], y=ALL_BUTTON[1])
    pyautogui.press('y')
    pyautogui.click(x=OK_BUTTON[0], y=OK_BUTTON[1])
