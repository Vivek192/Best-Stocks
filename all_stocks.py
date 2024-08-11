import yfinance as yf

nifty_100_stocks = [
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'HINDUNILVR.NS',
    'HDFC.NS', 'ICICIBANK.NS', 'KOTAKBANK.NS', 'SBIN.NS', 'BAJFINANCE.NS',
    'BHARTIARTL.NS', 'ITC.NS', 'LT.NS', 'ASIANPAINT.NS', 'AXISBANK.NS',
    'MARUTI.NS', 'DMART.NS', 'SUNPHARMA.NS', 'NESTLEIND.NS', 'TITAN.NS',
    'WIPRO.NS', 'ULTRACEMCO.NS', 'TATASTEEL.NS', 'POWERGRID.NS', 'ADANIGREEN.NS',
    'HCLTECH.NS', 'BAJAJFINSV.NS', 'ONGC.NS', 'NTPC.NS', 'SBILIFE.NS',
    'ADANIPORTS.NS', 'TATAMOTORS.NS', 'GRASIM.NS', 'INDUSINDBK.NS', 'BAJAJ-AUTO.NS',
    'DIVISLAB.NS', 'TECHM.NS', 'HINDALCO.NS', 'ADANIENT.NS', 'DRREDDY.NS',
    'M&M.NS', 'BRITANNIA.NS', 'HEROMOTOCO.NS', 'APOLLOHOSP.NS', 'VEDL.NS',
    'CIPLA.NS', 'SBICARD.NS', 'JSWSTEEL.NS', 'BPCL.NS', 'HDFCLIFE.NS',
    'EICHERMOT.NS', 'SHREECEM.NS', 'GODREJCP.NS', 'IOC.NS', 'GAIL.NS',
    'ICICIPRULI.NS', 'SIEMENS.NS', 'TORNTPHARM.NS', 'BOSCHLTD.NS', 'COLPAL.NS',
    'LUPIN.NS', 'MCDOWELL-N.NS', 'PIDILITIND.NS', 'DABUR.NS', 'MARICO.NS',
    'AMBUJACEM.NS', 'ACC.NS', 'ICICIGI.NS', 'HAVELLS.NS', 'PGHH.NS',
    'AUROPHARMA.NS', 'BERGEPAINT.NS', 'BANKBARODA.NS', 'PNB.NS', 'NAUKRI.NS',
    'ALKEM.NS', 'SRTRANSFIN.NS', 'PEL.NS', 'BANDHANBNK.NS', 'JUBLFOOD.NS',
    'BIOCON.NS', 'DLF.NS', 'MOTHERSON.NS', 'YESBANK.NS', 'MFSL.NS',
    'INDIGO.NS', 'INDUSTOWER.NS', 'LALPATHLAB.NS', 'HINDPETRO.NS', 'TRENT.NS',
    'BHEL.NS', 'IDEA.NS', 'NMDC.NS', 'TATACOMM.NS', 'BAJAJHLDNG.NS'
]

def fetch_stock_data(stock_symbol):
    try:
        stock = yf.Ticker(stock_symbol)
        history = stock.history(period='1d')
        if not history.empty:
            data = {
                'symbol': stock_symbol,
                'name': stock.info.get('shortName', stock_symbol).replace('.NS', ''),
                'current_price': round(stock.history(period='1d')['Close'].iloc[-1], 2),  # Current Market Price (CMP)
                '1D_change': round((history['Close'].iloc[0] - history['Open'].iloc[0]) / history['Open'].iloc[0] * 100, 2),
                'volume': int(history['Volume'].iloc[0])
            }
            
            # Fetch additional periods
            for period, label in [('5d', '1W_change'), ('1mo', '1M_change'), ('6mo', '6M_change'), ('1y', '1Y_change')]:
                history_period = stock.history(period=period)
                if not history_period.empty:
                    data[label] = round((history_period['Close'].iloc[-1] - history_period['Open'].iloc[0]) / history_period['Open'].iloc[0] * 100, 2)
                else:
                    data[label] = None
                    
            return data
    except Exception as e:
        print(f"Error fetching data for {stock_symbol}: {e}")
    return None

def get_all_stocks_data():
    data = []
    for stock in nifty_100_stocks:
        stock_data = fetch_stock_data(stock)
        if stock_data:
            data.append(stock_data)
        else:
            print(f"Failed to fetch data for {stock}")
    return data