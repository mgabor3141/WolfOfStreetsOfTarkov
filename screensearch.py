import cv2
from scipy import ndimage


def screen_search(screenshot, pattern, threshold):
    img = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    match = cv2.matchTemplate(img, pattern, cv2.TM_CCOEFF_NORMED)
    match[match < threshold] = 0
    labeled, num_objects = ndimage.label(match)
    return {(int(b), int(a)) for a, b in ndimage.center_of_mass(match, labeled, range(1, num_objects + 1))}
