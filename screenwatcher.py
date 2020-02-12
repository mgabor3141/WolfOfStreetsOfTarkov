import timeit

import cv2
import mss
import numpy as np

from PySide2.QtCore import *


from listing import *


def find_listings(sct, patterns):
    time_begin = timeit.default_timer()

    img_rgb = np.array(sct.grab(SCREEN_REGION))
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

    img_price = img_gray[:, :200]
    img_purchase = img_gray[:, -129:]

    raw_listings = {}
    line_offset = None

    for pattern in patterns:
        if pattern == 'purchase':
            img = img_purchase
        else:
            img = img_price

        res = cv2.matchTemplate(img, patterns[pattern], cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= MATCH_THRESHOLDS[pattern])

        for pt in zip(*loc[::-1]):
            if line_offset is None:
                line_offset = (pt[1] - LINE_TOP_PADDING) % LINE_HEIGHT

            x = pt[0]
            y = (pt[1] - line_offset) // LINE_HEIGHT

            raw_listings.setdefault(y, {})
            if all([abs(x - cx) > 5 for cx, val in raw_listings[y].items() if val == pattern]):
                raw_listings[y][x] = pattern
                # cv2.putText(img, str(pattern), pt, cv2.FONT_HERSHEY_SIMPLEX, 1, (64, 128, 64))

    listings = {y: Listing(y * LINE_HEIGHT + line_offset, l) for y, l in sorted(raw_listings.items())}

    # cv2.imshow("Image", img_price)
    # cv2.waitKey(1)

    return listings.values(), (timeit.default_timer() - time_begin) * 1000


class ScreenWatcher(QThread):
    listings_signal = Signal(object)

    def __init__(self, parentQWidget=None):
        super(ScreenWatcher, self).__init__(parentQWidget)
        self.wasCanceled = False

        self.patterns = {}
        for i in range(0, 10):
            self.patterns[i] = cv2.imread(r'patterns/{}.png'.format(i), 0)

        for c in {'rub', 'eur', 'usd', 'perpack', 'purchase'}:
            self.patterns[c] = cv2.imread(r'patterns/{}.png'.format(c), 0)

    def run(self):
        with mss.mss() as sct:
            while True:
                self.listings_signal.emit(find_listings(sct, self.patterns))

                if self.wasCanceled:
                    break

    def cancel(self):
        self.wasCanceled = True
