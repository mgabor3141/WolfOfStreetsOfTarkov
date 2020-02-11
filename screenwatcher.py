import timeit

import cv2
import mss
import numpy as np

from PySide2.QtCore import *


LINE_HEIGHT = 75
LINE_TOP_PADDING = 20
MATCH_THRESHOLD = 0.85
REGION = {'top': 150, 'left': 1250, 'width': 200, 'height': 830}


def find_listings(sct, patterns):
    time_begin = timeit.default_timer()

    img_rgb = np.array(sct.grab(REGION))
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

    raw_listings = {}
    line_offset = None

    for pattern in patterns:
        res = cv2.matchTemplate(img_gray, patterns[pattern], cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= MATCH_THRESHOLD)

        last_x = None
        last_y = None

        for pt in zip(*loc[::-1]):
            if line_offset is None:
                line_offset = pt[1] % LINE_HEIGHT - LINE_TOP_PADDING

            x = pt[0]
            y = (pt[1] + line_offset) // LINE_HEIGHT

            # Numbers have to be this far from each other to filter duplicates
            if last_x is not None and last_y is not None and abs(x - last_x) < 6 and y - last_y == 0:
                continue

            raw_listings.setdefault(y, {})[x] = pattern
            cv2.putText(img_rgb, str(pattern), pt, cv2.FONT_HERSHEY_SIMPLEX, 1, (64, 128, 64))

            last_x = x
            last_y = y

    sorted_listings = [p[1] for p in sorted(raw_listings.items())]
    listings = [[p[1] for p in sorted(listing.items())] for listing in sorted_listings]

    cv2.imshow("Image", img_rgb)

    print("Frame time: {:>6}ms".format(round((timeit.default_timer() - time_begin) * 1000, 2)))
    return listings


class ScreenWatcher(QThread):
    startLoad = Signal(int)
    progressLoad = Signal(object)
    statusLoad = Signal(bool)

    def __init__(self, parentQWidget=None):
        super(ScreenWatcher, self).__init__(parentQWidget)
        self.wasCanceled = False

    def run(self):
        patterns = {}
        for i in range(0, 10):
            patterns[i] = cv2.imread(r'patterns/{}.png'.format(i), 0)

        for c in {'rub', 'eur', 'usd'}:
            patterns[c] = cv2.imread(r'patterns/{}.png'.format(c), 0)

        with mss.mss() as sct:
            while True:
                self.progressLoad.emit(
                    '\n'.join([r''.join([str(item) for item in listing]) for listing in find_listings(sct, patterns)]))

                if self.wasCanceled:
                    break

    def cancel(self):
        self.wasCanceled = True
