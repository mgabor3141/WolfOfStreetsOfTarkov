import timeit

import cv2
import mss
import numpy as np

from PySide2.QtCore import *


from constants import *


class Listing:
    def __init__(self, params_dict: dict):
        params = params_dict.values()
        number_pairs = [p for p in sorted(params_dict.items()) if isinstance(p[1], int)]

        self.valid = True

        # self.peritem = "peritem" in params
        self.perpack = "perpack" in params

        # if self.perpack == self.peritem:
        #     self.valid = False

        self.currency = None
        for c in {"rub", "eur", "usd"}:
            if c in params:
                self.currency = c

        if self.currency is None:
            self.valid = False

        self.value = 0

        last_x = None

        for i in range(0, len(number_pairs)):
            x, v = number_pairs[-1 - i]

            if last_x is not None and last_x - x > MAX_GAP_BETWEEN_NUMBERS:
                self.valid = False
                self.value = None
                print("Gap too large: {}".format(last_x - x))
                break

            self.value += v * 10 ** i
            last_x = x

        if self.value == 0:
            self.valid = False

    def __repr__(self):
        if not self.valid:
            return '-'
        return "{:7d} {}{}".format(self.value, self.currency, ' p' if self.perpack else '')


def find_listings(sct, patterns):
    time_begin = timeit.default_timer()

    img_rgb = np.array(sct.grab(PRICE_REGION))
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

    raw_listings = {}
    line_offset = None

    for pattern in patterns:
        res = cv2.matchTemplate(img_gray, patterns[pattern], cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= MATCH_THRESHOLDS[pattern])

        for pt in zip(*loc[::-1]):
            if line_offset is None:
                line_offset = (pt[1] - LINE_TOP_PADDING) % LINE_HEIGHT

            x = pt[0]
            y = (pt[1] - line_offset) // LINE_HEIGHT

            raw_listings.setdefault(y, {})
            if all([abs(x - cx) > 5 for cx, val in raw_listings[y].items() if val == pattern]):
                raw_listings[y][x] = pattern
                cv2.putText(img_rgb, str(pattern), pt, cv2.FONT_HERSHEY_SIMPLEX, 1, (64, 128, 64))

    sorted_listings = [p[1] for p in sorted(raw_listings.items())]
    listings = [Listing(l) for l in sorted_listings]
    # listings = [[p[1] for p in sorted(listing.items())] for listing in sorted_listings]

    cv2.imshow("Image", img_rgb)
    cv2.waitKey(1)

    print("Frame time: {:6.2f}ms".format((timeit.default_timer() - time_begin) * 1000, 2))
    return listings


class ScreenWatcher(QThread):
    progressLoad = Signal(object)

    def __init__(self, parentQWidget=None):
        super(ScreenWatcher, self).__init__(parentQWidget)
        self.wasCanceled = False

    def run(self):
        patterns = {}
        for i in range(0, 10):
            patterns[i] = cv2.imread(r'patterns/{}.png'.format(i), 0)

        for c in {'rub', 'eur', 'usd', 'perpack'}:
            patterns[c] = cv2.imread(r'patterns/{}.png'.format(c), 0)

        with mss.mss() as sct:
            while True:
                self.progressLoad.emit(find_listings(sct, patterns))

                if self.wasCanceled:
                    break

    def cancel(self):
        self.wasCanceled = True
