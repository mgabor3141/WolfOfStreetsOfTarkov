from constants import *


class Listing:
    def __init__(self, coord, params_dict: dict):
        self.coord = coord

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

        self.locked = False

    def lock(self):
        self.locked = True

    def __repr__(self):
        if not self.valid:
            return '-'
        return "{:7d} {}{}{}".format(
            self.value,
            self.currency,
            ' p' if self.perpack else '',
            ' L' if self.locked else ''
        )
