import yfinance as yf

def get_stock_info(stockname):
    stock = yf.Ticker(stockname)
    price = '$' + '{:0.2f}'.format(stock.fast_info['last_price'])
    cap = '$' + '{:,}'.format(int(stock.fast_info['market_cap']))

    
    return '`{0:10}{1:15}{2:20}'.format('Ticker', 'Price', 'Market Cap') + '\n' \
            + '{0:10}{1:15}{2:20}`'.format(stockname, price, cap)

    
    
