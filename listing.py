MAX_GAP_BETWEEN_NUMBERS = 25


class Listing:
    def __init__(self, coord, params_dict: dict):
        self.coord = coord

        params = params_dict.values()
        number_pairs = [p for p in sorted(params_dict.items()) if isinstance(p[1], int)]

        self.valid = True

        self.perpack = "perpack" in params
        # self.purchasable = "purchase" in params

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

    def rub_value(self):
        if not self.valid:
            return None

        val = self.total_value()

        if self.perpack:
            if val % 2 == 0:
                val //= 2
            elif val % 3 == 0:
                val //= 3
            elif val % 5 == 0:
                val //= 5
            else:
                val /= 7

        return val

    def total_value(self):
        val = self.value
        if self.currency == 'usd':
            val *= 109  # 57 as far as sorting is concerned
        elif self.currency == 'eur':
            val *= 119

        return val

    def __repr__(self):
        if not self.valid:
            return '-'
        return "{:d} {}{}".format(
            self.value,
            self.currency,
            ' p' if self.perpack else ''
        )
