import pyautogui

from listing import *

pyautogui.PAUSE = 0


def buy(listings, target_value, currencies=None):
    if currencies is None:
        currencies = {'rub'}

    for l in listings:
        if l.rub_value() is not None and l.rub_value() <= target_value and l.currency in currencies:
            buy_listing(l)


def buy_listing(listing: Listing):
    print("Buying listing: {}".format(listing))
    pyautogui.click(x=PURCHASE_OFFSET[0], y=PURCHASE_OFFSET[1] + listing.coord)
    # pyautogui.click(x=ALL_BUTTON[0], y=ALL_BUTTON[1])
    pyautogui.press('y')
    pyautogui.click(x=OK_BUTTON[0], y=OK_BUTTON[1])
