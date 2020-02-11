import time

import cv2
import mss
import numpy as np
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'

mon = {'top': 10, 'left': 120, 'width': 40, 'height': 40}

with mss.mss() as sct:
    while True:
        # im = numpy.asarray(sct.grab(mon))
        # im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

        zero = cv2.imread(r'patterns/0.png', 0)
        w, h = zero.shape[::-1]

        img_rgb = cv2.imread('market_cropped.png')
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

        # ret, img_cv = cv2.threshold(img_cv, 130, 255, cv2.THRESH_TOZERO)
        # img_cv = cv2.bitwise_not(img_cv)

        res = cv2.matchTemplate(img_gray, zero, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        loc = np.where(res >= threshold)

        listings = {}

        for pt in zip(*loc[::-1]):
            print(pt)
            listings.setdefault(pt[1] // 70, {})[pt[0] // 5] = 0  # listing row height
            cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)

        print(listings)

        # text = pytesseract.image_to_string(img_cv)
        # print(text)

        # print(pytesseract.image_to_data(img_cv))

        cv2.imshow('Image', img_rgb)

        # Press "q" to quit
        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break

        # One screenshot per second
        time.sleep(1)
