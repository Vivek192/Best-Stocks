from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import stripe
from best_50_stocks_to_buy import analyze_stocks, nifty_100_stocks
from top_gainers_and_losers import fetch_stock_data
from all_stocks import get_all_stocks_data
from sectors import get_sector_data  # Import the function to get sector data

app = Flask(__name__)
app.secret_key = 'sk_test_51LY1QBSIqQO61hDB1N5xIHmXGhlBCe4vcJ3XUMod7MDiwTauydAjpETHWKh2iBdJiGkiQh8C3xwt0Ya2hBuPEFNi00kEhiboPC'  # Replace with a securely stored secret key

# Dummy user data
users = {
    'User1': '123456'
}

# Stripe configuration
stripe.api_key = 'sk_test_51LY1QBSIqQO61hDB1N5xIHmXGhlBCe4vcJ3XUMod7MDiwTauydAjpETHWKh2iBdJiGkiQh8C3xwt0Ya2hBuPEFNi00kEhiboPC'  # Replace with your securely stored Stripe secret key

@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if users.get(username) == password:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return 'Invalid credentials', 401  # You might want to render a template with an error message

    return render_template('login.html')

@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users:
            return 'Username already exists', 400  # You might want to render a template with an error message

        users[username] = password
        return redirect(url_for('login'))

    return render_template('sign_up.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/all_stocks')
def all_stocks():
    if 'username' in session:
        try:
            stocks_data = get_all_stocks_data()
            return render_template('all_stocks.html', stocks=stocks_data)
        except Exception as e:
            print(f"Error fetching all stocks data: {e}")
            return 'Error fetching data', 500  # You might want to render an error template

    return redirect(url_for('login'))

@app.route('/top_gainers_and_losers')
def top_gainers_and_losers():
    if 'username' in session:
        data = []
        for stock in nifty_100_stocks:
            try:
                stock_data = fetch_stock_data(stock)
                if stock_data:
                    data.append(stock_data)
                else:
                    print(f"Failed to fetch data for {stock}")
            except Exception as e:
                print(f"Error fetching stock data for {stock}: {e}")

        import pandas as pd
        df = pd.DataFrame(data)

        if df.empty:
            print("No data fetched")
            return 'No data available', 500  # You might want to render an error template

        top_gainers = df.nlargest(10, 'pl_percent')
        top_losers = df.nsmallest(10, 'pl_percent')

        return render_template('top_gainers_and_losers.html', 
                               top_gainers=top_gainers.to_dict(orient='records'), 
                               top_losers=top_losers.to_dict(orient='records'))
    return redirect(url_for('login'))

@app.route('/best_50_stocks_to_buy')
def best_50_stocks_to_buy():
    if 'username' in session:
        try:
            top_50_stocks = analyze_stocks(nifty_100_stocks)
            return render_template('best_50_stocks_to_buy.html', stocks=top_50_stocks.to_dict(orient='records'))
        except Exception as e:
            print(f"Error analyzing stocks: {e}")
            return 'Error analyzing stocks', 500  # You might want to render an error template
    return redirect(url_for('login'))

@app.route('/buy_and_sell_points')
def buy_and_sell_points():
    if 'username' in session:
        return render_template('buy_and_sell_points.html')
    return redirect(url_for('login'))

@app.route('/pay_here')
def pay_here():
    if 'username' in session:
        return render_template('pay_here.html')
    return redirect(url_for('login'))

@app.route('/sectors')
def sectors():
    if 'username' in session:
        try:
            sector_data = get_sector_data()
            return render_template('sectors.html', sectors=sector_data)
        except Exception as e:
            print(f"Error fetching sector data: {e}")
            return 'Error fetching sector data', 500  # You might want to render an error template
    return redirect(url_for('login'))

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'inr',
                        'product_data': {
                            'name': 'Subscription Service',
                        },
                        'unit_amount': 9900,  # 99 INR in paise
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=url_for('success', _external=True),
            cancel_url=url_for('cancel', _external=True),
        )
        return jsonify(id=checkout_session.id)
    except Exception as e:
        print(f"Error creating checkout session: {e}")
        return str(e), 500

@app.route('/success')
def success():
    return 'Payment Successful! Thank you for subscribing.'

@app.route('/cancel')
def cancel():
    return 'Payment Cancelled. Please try again.'

if __name__ == '__main__':
    app.run(debug=True)

