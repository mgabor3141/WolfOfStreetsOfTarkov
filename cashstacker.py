from time import sleep

import cv2
import pyautogui
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot

from screensearch import screen_search
from resource_path import resource_path
from screenshotter import ScreenShotter
from windowtitle import get_foreground_window_title


class CashStacker(QThread):
    progress = pyqtSignal(int)

    full_stack_pattern = cv2.imread(resource_path('patterns/roubles.png'), cv2.IMREAD_GRAYSCALE)
    stack_pattern = full_stack_pattern[:-14, ]

    def __init__(self, parentQWidget=None):
        super(CashStacker, self).__init__(parentQWidget)

    @pyqtSlot()
    def start(self):
        with ScreenShotter() as sct:
            while True:
                if not get_foreground_window_title() == "EscapeFromTarkov":
                    sleep(1)
                    continue

                OFFSET = 1265, 77
                screen = sct.grab({'left': OFFSET[0], 'top': OFFSET[1], 'width': 636, 'height': 862})
                stack_pos = screen_search(screen, self.stack_pattern, 0.85)
                full_stack_pos = screen_search(screen, self.full_stack_pattern, 0.98)

                positions = stack_pos - full_stack_pos

                if len(positions) < 2:
                    break

                mouse_down = False
                for p in positions:
                    pyautogui.moveTo(p[0] + OFFSET[0] + 10, p[1] + OFFSET[1] + 10)
                    if not mouse_down:
                        pyautogui.mouseDown()
                        mouse_down = True
                    else:
                        pyautogui.mouseUp()
                        mouse_down = False

                if mouse_down:
                    pyautogui.mouseUp()
