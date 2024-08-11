import yfinance as yf
import pandas as pd
from flask import Flask, render_template

app = Flask(__name__)

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
                'name': stock.info.get('shortName', stock_symbol),
                'open': round(history['Open'].iloc[0], 2),
                'dayHigh': round(history['High'].iloc[0], 2),
                'dayLow': round(history['Low'].iloc[0], 2),
                'close': round(history['Close'].iloc[0], 2),
                'pl_percent': round((history['Close'].iloc[0] - history['Open'].iloc[0]) / history['Open'].iloc[0] * 100, 2)
            }
            return data
    except Exception as e:
        print(f"Error fetching data for {stock_symbol}: {e}")
    return None     

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/top_gainers_and_losers')
def top_gainers_and_losers():
    data = []
    for stock in nifty_100_stocks:
        stock_data = fetch_stock_data(stock)
        if stock_data:
            data.append(stock_data)
        else:
            print(f"Failed to fetch data for {stock}")

    df = pd.DataFrame(data)
    if df.empty:
        print("No data fetched")
    else:
        print(df.head())

    top_gainers = df.nlargest(10, 'pl_percent')
    top_losers = df.nsmallest(10, 'pl_percent')
    
    return render_template('top_gainers_and_losers.html', top_gainers=top_gainers.to_dict(orient='records'), top_losers=top_losers.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)
