import cv2
import mss
import numpy as np
import pyautogui


class ScreenShotter:
    sct = None
    debug = False

    def __enter__(self):
        if self.sct is not None:
            raise Exception

        self.sct = mss.mss().__enter__()
        return self

    def __exit__(self, *args):
        self.sct.__exit__(*args)

    def grab(self, region):
        # adjust resolution if screen is not 1920 wide
        region['left'] += (pyautogui.size()[0] - 1920) // 2

        # noinspection PyTypeChecker
        shot = np.array(self.sct.grab(region))

        if self.debug:
            cv2.imshow(f"Debug {region['top']}-{region['left']}-{region['width']}-{region['height']}", shot)
            cv2.waitKey(1)

        return shot
