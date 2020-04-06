from enum import Enum
from time import sleep

import cv2
import mss
import numpy as np
import pyautogui
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from scipy import ndimage

from resource_path import resource_path
from windowtitle import get_foreground_window_title


pyautogui.MINIMUM_DURATION = 0.04


class State(Enum):
    WORK = 0
    WAIT_FOR_SCROLL = 1


class CashStacker(QThread):
    progress = pyqtSignal(int)

    full_stack_pattern = cv2.imread(resource_path('patterns/roubles.png'), cv2.IMREAD_GRAYSCALE)
    stack_pattern = full_stack_pattern[:-14, ]

    def __init__(self, parentQWidget=None):
        super(CashStacker, self).__init__(parentQWidget)

    @pyqtSlot()
    def start(self):
        with mss.mss() as sct:
            state = State.WORK

            # while True:
            #     if state == State.WORK:
            while True:
                if not get_foreground_window_title() == "EscapeFromTarkov":
                    sleep(1)
                    continue

                img = cv2.cvtColor(np.array(sct.grab({'left': 0, 'top': 0, 'width': 1920, 'height': 1080})), cv2.COLOR_BGR2GRAY)
                match_stacks = cv2.matchTemplate(img, self.stack_pattern, cv2.TM_CCOEFF_NORMED)
                match_stacks[match_stacks < 0.85] = 0

                labeled, num_objects = ndimage.label(match_stacks)
                stack_pos = {(int(a), int(b)) for a, b in ndimage.center_of_mass(match_stacks, labeled, range(1, num_objects + 1))}

                match_full_stacks = cv2.matchTemplate(img, self.full_stack_pattern, cv2.TM_CCOEFF_NORMED)
                match_full_stacks[match_full_stacks < 0.98] = 0

                labeled, num_objects = ndimage.label(match_full_stacks)
                full_stack_pos = {(int(a), int(b)) for a, b in ndimage.center_of_mass(match_full_stacks, labeled, range(1, num_objects + 1))}

                positions = stack_pos - full_stack_pos

                # print(positions)

                if len(positions) < 2:
                    break

                mouse_down = False
                for p in positions:
                    pyautogui.moveTo(p[1] + 10, p[0] + 10)#, 0.05, pyautogui.easeOutQuad)
                    if not mouse_down:
                        pyautogui.mouseDown()
                        mouse_down = True
                    else:
                        pyautogui.mouseUp()
                        mouse_down = False

                if mouse_down:
                    pyautogui.mouseUp()


                # elif state == State.WAIT_FOR_SCROLL:
                #     pass
