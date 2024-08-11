import yfinance as yf
import pandas as pd
from flask import Flask, render_template

app = Flask(__name__)

# List of Nifty 100 stock tickers
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
        history = stock.history(period='1y')
        info = stock.info
        
        if history.empty:
            print(f"No historical data found for {stock_symbol}")
            return None
        
        current_price = round(history['Close'].iloc[-1], 2) if not history.empty else None
        
        # Fundamental metrics
        eps = info.get('epsTrailingTwelveMonths', None)
        forward_eps = info.get('forwardEps', None)
        pe_ratio = info.get('forwardPE', None)
        if eps is None and forward_eps is not None:
            eps = forward_eps
        if pe_ratio is None and eps is not None and eps != 0:
            pe_ratio = current_price / eps
        
        pb_ratio = info.get('priceToBook', None)
        dividend_yield = info.get('dividendYield', None) * 100 if info.get('dividendYield') else None
        
        # Technical indicators
        sma_50 = round(history['Close'].rolling(window=50).mean().iloc[-1], 2) if len(history) >= 50 else None
        sma_200 = round(history['Close'].rolling(window=200).mean().iloc[-1], 2) if len(history) >= 200 else None
        rsi = round(compute_rsi(history['Close']), 2) if not history.empty else None
        macd, macd_signal = (round(compute_macd(history['Close'])[0], 2), round(compute_macd(history['Close'])[1], 2)) if not history.empty else (None, None)
        bollinger_bands = (round(compute_bollinger_bands(history['Close'])[0], 2), round(compute_bollinger_bands(history['Close'])[1], 2)) if not history.empty else (None, None)
        
        data = {
            'Stock Name': stock_symbol,
            'Current Market Price': current_price,
            'P/E Ratio': round(pe_ratio, 2) if pe_ratio else None,
            'P/B Ratio': round(pb_ratio, 2) if pb_ratio else None,
            'Dividend Yield': round(dividend_yield, 2) if dividend_yield else None,
            'EPS': round(eps, 2) if eps else None,
            'SMA 50': sma_50,
            'SMA 200': sma_200,
            'RSI': rsi,
            'MACD': macd,
            'MACD Signal': macd_signal,
            'Bollinger Bands Upper': bollinger_bands[0],
            'Bollinger Bands Lower': bollinger_bands[1]
        }
        return data
    except Exception as e:
        print(f"Error fetching data for {stock_symbol}: {e}")
    return None

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(window=period, min_periods=1).mean()
    avg_loss = loss.rolling(window=period, min_periods=1).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def compute_macd(series):
    short_ema = series.ewm(span=12, adjust=False).mean()
    long_ema = series.ewm(span=26, adjust=False).mean()
    macd = short_ema - long_ema
    macd_signal = macd.ewm(span=9, adjust=False).mean()
    return macd.iloc[-1], macd_signal.iloc[-1]

def compute_bollinger_bands(series, window=20):
    sma = series.rolling(window=window).mean()
    std = series.rolling(window=window).std()
    upper_band = sma + (std * 2)
    lower_band = sma - (std * 2)
    return upper_band.iloc[-1], lower_band.iloc[-1]

def analyze_stocks(tickers):
    data = []
    for ticker in tickers:
        stock_data = fetch_stock_data(ticker)
        if stock_data:
            data.append(stock_data)
    
    df = pd.DataFrame(data)
    if df.empty:
        print("No data fetched")
        return pd.DataFrame()  # Return an empty DataFrame if no data is fetched

    # Scoring system (example weights)
    df['P/E Score'] = df['P/E Ratio'].rank(ascending=True)
    df['P/B Score'] = df['P/B Ratio'].rank(ascending=True)
    df['Dividend Score'] = df['Dividend Yield'].rank(ascending=False)
    df['EPS Score'] = df['EPS'].rank(ascending=False)
    df['SMA Score'] = (df['SMA 50'] / df['SMA 200']).rank(ascending=False)
    df['RSI Score'] = df['RSI'].rank(ascending=True)
    df['MACD Score'] = (df['MACD'] - df['MACD Signal']).rank(ascending=False)
    df['Bollinger Score'] = ((df['Current Market Price'] - df['Bollinger Bands Lower']) / 
                             (df['Bollinger Bands Upper'] - df['Bollinger Bands Lower'])).rank(ascending=False)

    # Combine scores to get the final score (example weights)
    df['Total Score'] = (0.2 * df['P/E Score'] +
                         0.2 * df['P/B Score'] +
                         0.1 * df['Dividend Score'] +
                         0.1 * df['EPS Score'] +
                         0.1 * df['SMA Score'] +
                         0.1 * df['RSI Score'] +
                         0.1 * df['MACD Score'] +
                         0.1 * df['Bollinger Score'])

    df['Total Score'] = df['Total Score'].round(2)
    
    # Sort by Total Score in descending order
    top_50_stocks = df.sort_values(by='Total Score', ascending=False).head(50)
    return top_50_stocks

@app.route('/')
def home():
    top_50_stocks = analyze_stocks(nifty_100_stocks)
    return render_template('best_50_stocks_to_buy.html', stocks=top_50_stocks)

if __name__ == '__main__':
    app.run(debug=True)
