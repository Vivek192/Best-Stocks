import yfinance as yf

def get_sector_data():
    sectors = {
        'Energy': ['HPCL.NS', 'IOC.NS', 'ONGC.NS', 'NTPC.NS', 'GAIL.NS'],
        'Financial': ['HDFC.NS', 'ICICIBANK.NS', 'KOTAKBANK.NS', 'SBI.NS', 'AXISBANK.NS'],
        'Pharmaceutical': ['SUNPHARMA.NS', 'DRREDDY.NS', 'CIPLA.NS', 'AUBANK.NS', 'LUPIN.NS'],
        'IT': ['TCS.NS', 'INFY.NS', 'WIPRO.NS', 'HCLTECH.NS', 'TECHM.NS'],
        'Telecom': ['BHARTIARTL.NS', 'RELIANCE.NS', 'INDUSINDBK.NS', 'MTNL.NS', 'VODAFONEIDEA.NS'],
        'Consumer Goods': ['HINDUNILVR.NS', 'ITC.NS', 'MARICO.NS', 'COLPAL.NS', 'DABUR.NS'],
        'Power': ['NTPC.NS', 'POWERGRID.NS', 'ADANIGREEN.NS', 'NHPC.NS', 'TATAPOWER.NS'],
        'Metals': ['TATASTEEL.NS', 'HINDALCO.NS', 'JSWSTEEL.NS', 'NMDC.NS', 'VEDL.NS'],
        'Automobiles': ['MARUTI.NS', 'TATAMOTORS.NS', 'M&M.NS', 'BAJAJAUTO.NS', 'TVSMOTOR.NS'],
        'Media': ['ZEEL.NS', 'PVR.NS', 'SUNTV.NS', 'NETWORK18.NS', 'INXMEDIA.NS'],
        'Real Estate': ['DLF.NS', 'OBEROIREALTY.NS', 'GODREJPROPERTIES.NS', 'BRIGADEENTP.NS', 'PHOENIXLTD.NS'],
        'FMCG': ['HUL.NS', 'DABUR.NS', 'MARICO.NS', 'COLPAL.NS', 'ITC.NS']
    }

    sector_data = {}
    for sector, stocks in sectors.items():
        sector_data[sector] = []
        for stock in stocks:
            try:
                ticker = yf.Ticker(stock)
                history = ticker.history(period='1d')
                
                if not history.empty:
                    # Calculate 1-day percentage change based on the difference between Open and Close prices
                    open_price = history['Open'].iloc[0]
                    close_price = history['Close'].iloc[0]
                    percent_change = round((close_price - open_price) / open_price * 100, 2)
                else:
                    percent_change = 'N/A'  # Handle cases where no data is available
                
                stock_info = {
                    'name': ticker.info.get('shortName', stock).replace('.NS', ''),
                    '1D_change': f"{percent_change}%",
                    'color': calculate_color(percent_change)
                }
                sector_data[sector].append(stock_info)
            except Exception as e:
                print(f"Error fetching data for {stock}: {e}")
                sector_data[sector].append({
                    'name': stock,
                    '1D_change': 'N/A',
                    'color': "gray"  # Default color for error cases
                })
    
    return sector_data

def calculate_color(change):
    try:
        change = float(change)
        if change > 5:
            return "darkgreen"
        elif change > 0:
            return f"rgb(0, {min(255, int((change / 5) * 255))}, 0)"
        elif change < -5:
            return "darkred"
        elif change < 0:
            return f"rgb({min(255, int((abs(change) / 5) * 255))}, 0, 0)"
        else:
            return "white"  # Neutral color for zero change
    except ValueError:
        return "gray"  # Default color for invalid data

# Test the function in your environment
sector_data = get_sector_data()
print(sector_data)
