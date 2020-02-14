def evaluate_listing(listing, target_value, currencies=None):
    if currencies is None:
        currencies = {'rub'}

    return listing.rub_value() is not None and listing.rub_value() <= target_value and listing.currency in currencies
