from yahoo_finance import Share


def get_quote(symbol):
    share = Share(symbol)

    if not share.get_price():
        return {}

    change_f = float(share.get_change())
    change_str = '+%.02f' % change_f if change_f >= 0 else '%.02f' % change_f

    change_percent_f = change_f / float(share.get_open()) * 100
    change_percent = '+%.02f' % change_percent_f if change_percent_f >= 0 else '%.02f' % change_percent_f

    return {
        'price': share.get_price(),
        'change': change_str,
        'change_percent': change_percent,
        'open_price': share.get_open(),
        'market_cap': share.get_market_cap(),
        'year_low': share.get_year_low(),
        'year_high': share.get_year_high(),
        'day_low': share.get_days_low(),
        'day_high': share.get_days_high(),
        'volume': share.get_volume(),
        'pe_ratio': share.get_price_earnings_ratio() or '-'
    }
