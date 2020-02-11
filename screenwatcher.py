import time
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *


class ScreenWatcher(QThread):
    startLoad = Signal(int)
    progressLoad = Signal(int)
    statusLoad = Signal(bool)

    def __init__(self, parentQWidget=None):
        super(ScreenWatcher, self).__init__(parentQWidget)
        self.wasCanceled = False

    def run(self):
        # Simulate data load estimation
        numberOfprogress = 100
        self.startLoad.emit(numberOfprogress)
        for progress in range(numberOfprogress + 1):
            # Delay
            time.sleep(0.1)
            if not self.wasCanceled:
                self.progressLoad.emit(progress)
            else:
                break
        self.statusLoad.emit(True if progress == numberOfprogress else False)
        self.exit(0)

    def cancel(self):
        self.wasCanceled = True

        # import time
        #
        # import cv2
        # import mss
        # import numpy
        # import numpy as np
        #
        # LINE_HEIGHT = 75
        # LINE_TOP_PADDING = 20
        # MATCH_THRESHOLD = 0.85
        #
        # quit_flag = False
        #
        # def quit_fn():
        #     global quit_flag
        #     quit_flag = True
        #
        # def watch_screen(data_callback, quit_signal):
        #     quit_signal.connect(quit_fn)
        #
        #     patterns = {}
        #     for i in range(0, 10):
        #         patterns[i] = cv2.imread(r'patterns/{}.png'.format(i), 0)
        #
        #     for c in {'rub', 'eur', 'usd'}:
        #         patterns[c] = cv2.imread(r'patterns/{}.png'.format(c), 0)
        #
        #     # img_rgb = cv2.imread('market_cropped.png')
        #     # img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        #
        #     with mss.mss() as sct:
        #         monitor = {'top': 150, 'left': 1250, 'width': 200, 'height': 830}
        #
        #         while True:
        #             img_rgb = numpy.array(sct.grab(monitor))
        #             img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        #
        #             raw_listings = {}
        #             line_offset = None
        #
        #             for pattern in patterns:
        #                 res = cv2.matchTemplate(img_gray, patterns[pattern], cv2.TM_CCOEFF_NORMED)
        #                 loc = np.where(res >= MATCH_THRESHOLD)
        #
        #                 last_x = None
        #                 last_y = None
        #
        #                 for pt in zip(*loc[::-1]):
        #                     if line_offset is None:
        #                         line_offset = pt[1] % LINE_HEIGHT - LINE_TOP_PADDING
        #
        #                     x = pt[0]
        #                     y = (pt[1] + line_offset) // LINE_HEIGHT
        #
        #                     # Numbers have to be this far from each other to filter duplicates
        #                     if last_x is not None and last_y is not None and abs(x - last_x) < 6 and y - last_y == 0:
        #                         continue
        #
        #                     raw_listings.setdefault(y, {})[x] = pattern
        #                     cv2.putText(img_rgb, str(pattern), pt, cv2.FONT_HERSHEY_SIMPLEX, 1, (64, 128, 64))
        #
        #                     last_x = x
        #                     last_y = y
        #
        #             # print(raw_listings)
        #             sorted_listings = [p[1] for p in sorted(raw_listings.items())]
        #             listings = [[p[1] for p in sorted(listing.items())] for listing in sorted_listings]
        #             # print(sorted_listings)
        #             # print(listings)
        #             # print('\n'.join([r''.join([str(item) for item in listing]) for listing in listings]))
        #             data_callback.emit('\n'.join([r''.join([str(item) for item in listing]) for listing in listings]))
        #
        #             # cv2.imshow("Image", img_rgb)
        #
        #             # Press "q" to quit
        #             # cv2.waitKey(0)
        #             # if cv2.waitKey(25) & 0xFF == ord('q'):
        #             #     cv2.destroyAllWindows()
        #             #     break
        #
        #             time.sleep(0.05)