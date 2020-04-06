import cv2
import numpy as np

from resource_path import resource_path
from constants import LINE_HEIGHT
from listing import *

LISTINGS_TO_PROCESS = 5
LINE_TOP_PADDING = 20
LINE_TOP_PADDING_BUTTON = 29
MATCH_THRESHOLDS = {
    0: 0.7,
    1: 0.85,
    2: 0.85,
    3: 0.85,
    4: 0.85,
    5: 0.9,
    6: 0.9,
    7: 0.85,
    8: 0.85,
    9: 0.85,
    'rub': 0.85,
    'usd': 0.85,
    'eur': 0.85,
    'perpack': 0.85,
    'purchase': 0.85,
    'outofstock': 0.85,
    'ok': 0.85
}


class ScreenWatcher:
    def __init__(self, sct):
        self.debug = False
        self.sct = sct

        self.price_patterns = {}
        for i in range(0, 10):
            self.price_patterns[i] = cv2.imread(resource_path(f'patterns/{i}.png'), cv2.IMREAD_GRAYSCALE)

        for c in {'rub', 'eur', 'usd', 'perpack'}:
            self.price_patterns[c] = cv2.imread(resource_path(f'patterns/{c}.png'), cv2.IMREAD_GRAYSCALE)

        self.purchase_pattern = cv2.imread(resource_path('patterns/purchase.png'), cv2.IMREAD_GRAYSCALE)
        self.outofstock_pattern = cv2.imread(resource_path('patterns/outofstock.png'), cv2.IMREAD_GRAYSCALE)
        self.ok_pattern = cv2.imread(resource_path('patterns/ok.png'), cv2.IMREAD_GRAYSCALE)

    def find_listings(self):
        PRICE_REGION = {'top': 146, 'left': 1239, 'width': 205, 'height': LINE_HEIGHT * LISTINGS_TO_PROCESS}
        img = cv2.cvtColor(self.sct.grab(PRICE_REGION), cv2.COLOR_BGR2GRAY)

        raw_listings = {}
        line_offset = None

        for pattern in self.price_patterns:
            res = cv2.matchTemplate(img, self.price_patterns[pattern], cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= MATCH_THRESHOLDS[pattern])

            for pt in zip(*loc[::-1]):
                if line_offset is None:
                    line_offset = (pt[1] - LINE_TOP_PADDING) % LINE_HEIGHT

                x = pt[0]
                y = (pt[1] - line_offset) // LINE_HEIGHT

                raw_listings.setdefault(y, {})
                if all([abs(x - cx) > 5 for cx, val in raw_listings[y].items() if val == pattern]):
                    raw_listings[y][x] = pattern

        return [Listing(y * LINE_HEIGHT + line_offset, l) for y, l in sorted(raw_listings.items())]

    def find_purchase_buttons(self):
        BUTTON_REGION = {'top': 146, 'left': 1695, 'width': 120, 'height': LINE_HEIGHT * LISTINGS_TO_PROCESS}
        img = cv2.cvtColor(self.sct.grab(BUTTON_REGION), cv2.COLOR_BGR2GRAY)

        button_numbers = set()
        line_offset = None

        res = cv2.matchTemplate(img, self.purchase_pattern, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= MATCH_THRESHOLDS['purchase'])

        for pt in zip(*loc[::-1]):
            if line_offset is None:
                line_offset = (pt[1] - LINE_TOP_PADDING) % LINE_HEIGHT

            x = pt[0]
            y = (pt[1] - line_offset) // LINE_HEIGHT

            button_numbers.add(y)

        return button_numbers

    def find_purchase_or_outofstock(self):
        button_numbers = self.find_purchase_buttons()

        BUTTON_REGION = {'top': 146, 'left': 1695, 'width': 120, 'height': LINE_HEIGHT * LISTINGS_TO_PROCESS}
        img = cv2.cvtColor(self.sct.grab(BUTTON_REGION), cv2.COLOR_BGR2GRAY)

        line_offset = None

        res = cv2.matchTemplate(img, self.outofstock_pattern, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= MATCH_THRESHOLDS['outofstock'])

        for pt in zip(*loc[::-1]):
            if line_offset is None:
                line_offset = (pt[1] - LINE_TOP_PADDING) % LINE_HEIGHT

            x = pt[0]
            y = (pt[1] - line_offset) // LINE_HEIGHT

            button_numbers.add(y)

        return button_numbers

    def find_error_ok_button(self):
        OK_REGION = {'top': 549, 'left': 927, 'width': 67, 'height': 120}
        img = cv2.cvtColor(self.sct.grab(OK_REGION), cv2.COLOR_BGR2GRAY)

        res = cv2.matchTemplate(img, self.ok_pattern, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= MATCH_THRESHOLDS['ok'])
        coords = next(zip(*loc[::-1]), None)
        return (coords[0] + OK_REGION['left'], coords[1] + OK_REGION['top']) if coords else None
