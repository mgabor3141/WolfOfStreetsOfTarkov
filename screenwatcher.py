import timeit

import cv2
import mss
import numpy as np

from PySide2.QtCore import *


from listing import *


def find_listings(sct, patterns, locked_pattern):
    time_begin = timeit.default_timer()

    img_rgb = np.array(sct.grab(PRICE_REGION))
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

    img_locked = cv2.cvtColor(np.array(sct.grab(LOCKED_REGION)), cv2.COLOR_BGR2GRAY)

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
                # cv2.putText(img_rgb, str(pattern), pt, cv2.FONT_HERSHEY_SIMPLEX, 1, (64, 128, 64))

    listings = {y: Listing(y * LINE_HEIGHT + line_offset, l) for y, l in sorted(raw_listings.items())}

    res = cv2.matchTemplate(img_locked, locked_pattern, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= MATCH_THRESHOLDS['locked'])

    # cv2.imshow("Image", img_locked)
    # cv2.waitKey(1000)

    for pt in zip(*loc[::-1]):
        listings[(pt[1] - line_offset) // LINE_HEIGHT].lock()

    print("Frame time: {:6.2f}ms".format((timeit.default_timer() - time_begin) * 1000))
    return listings.values()


class ScreenWatcher(QThread):
    listings_signal = Signal(object)

    def __init__(self, parentQWidget=None):
        super(ScreenWatcher, self).__init__(parentQWidget)
        self.wasCanceled = False

        self.patterns = {}
        for i in range(0, 10):
            self.patterns[i] = cv2.imread(r'patterns/{}.png'.format(i), 0)

        for c in {'rub', 'eur', 'usd', 'perpack', 'locked'}:
            self.patterns[c] = cv2.imread(r'patterns/{}.png'.format(c), 0)

        self.locked = cv2.imread(r'patterns/locked.png', 0)

    def run(self):
        with mss.mss() as sct:
            while True:
                self.listings_signal.emit(find_listings(sct, self.patterns, self.locked))

                if self.wasCanceled:
                    break

    def cancel(self):
        self.wasCanceled = True
