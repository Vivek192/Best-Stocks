from flask import Flask, render_template, request
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
import json

app = Flask(__name__)

def calculate_rsi(df, window=14):
    delta = df['Close'].diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def process_stock_data(stock_symbol, start_date, end_date):
    df = yf.download(stock_symbol, start=start_date, end=end_date)

    # Calculate EMAs
    df['12D_EMA'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['26D_EMA'] = df['Close'].ewm(span=26, adjust=False).mean()

    # Determine buy and sell points
    df['Buy_Signal'] = (df['12D_EMA'] > df['26D_EMA']) & (df['12D_EMA'].shift(1) <= df['26D_EMA'].shift(1))
    df['Sell_Signal'] = (df['12D_EMA'] < df['26D_EMA']) & (df['12D_EMA'].shift(1) >= df['26D_EMA'].shift(1))

    # Calculate RSI
    df['RSI'] = calculate_rsi(df)

    # Create the Plotly figure
    fig = go.Figure()

    # Add EMAs and buy/sell signals
    fig.add_trace(go.Scatter(x=df.index, y=df['12D_EMA'], mode='lines', name='12-Day EMA', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df.index, y=df['26D_EMA'], mode='lines', name='26-Day EMA', line=dict(color='red')))
    fig.add_trace(go.Scatter(x=df.loc[df['Buy_Signal']].index, y=df.loc[df['Buy_Signal'], '12D_EMA'], mode='markers', name='Buy Signal', marker=dict(symbol='triangle-up', color='green', size=10)))
    fig.add_trace(go.Scatter(x=df.loc[df['Sell_Signal']].index, y=df.loc[df['Sell_Signal'], '12D_EMA'], mode='markers', name='Sell Signal', marker=dict(symbol='triangle-down', color='red', size=10)))
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], mode='lines', name='RSI', line=dict(color='cyan')))

    fig.update_layout(
        title=f'Buy & Sell Points for {stock_symbol}',
        xaxis_title='Date',
        yaxis_title='Price (INR)',
        legend_title='Legend',
        template='plotly_dark',
        xaxis_rangeslider_visible=False
    )

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

@app.route('/buy_and_sell_points', methods=['GET', 'POST'])
def buy_and_sell_points():
    if request.method == 'POST':
        stock_symbol = request.form['stock_symbol']
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        graph_json = process_stock_data(stock_symbol, start_date, end_date)

        return render_template('buy_and_sell_points.html', graph_json=graph_json)

    return render_template('buy_and_sell_points.html')

if __name__ == '__main__':
    app.run(debug=True)
