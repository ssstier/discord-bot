import yfinance as yf


def format_currency(value: float, prefix: str = '$') -> str:
    return prefix + '{:,.2f}'.format(value)


def get_stock_info(stockname: str) -> str:
    stock = yf.Ticker(stockname)

    price = format_currency(stock.fast_info['last_price'])
    cap = format_currency(stock.fast_info['market_cap'])

    header = '`{:<10}{:<15}{:<20}'.format('Ticker', 'Price', 'Market Cap')
    stock_info = '{:<10}{:<15}{:<20}`'.format(stockname, price, cap)

    return header + '\n' + stock_info
