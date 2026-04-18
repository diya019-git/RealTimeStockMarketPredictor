from apscheduler.schedulers.background import BackgroundScheduler
import yfinance as yf
import time
import mysql.connector
from datetime import datetime

# MySQL connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="chiragsql@2002",
    database="stock_project"
)
cursor = conn.cursor()

# Stocks to track
stocks = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS"]

def fetch_stock():
    for symbol in stocks:
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period="1d", interval="1m")
            if data is None or data.empty:
                print("No data received for", symbol)
                continue

            # OHLC + Close
            latest = data.iloc[-1]
            latest_open  = float(latest['Open'])
            latest_high  = float(latest['High'])
            latest_low   = float(latest['Low'])
            latest_price = float(latest['Close'])  # Close = price

            close = data['Close']

            # Moving Average
            ma5 = float(close.tail(5).mean())

            # RSI Calculation
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            latest_rsi = float(rsi.iloc[-1])

            print(f"{symbol} | O:{latest_open:.2f} H:{latest_high:.2f} L:{latest_low:.2f} C:{latest_price:.2f} | RSI:{latest_rsi:.2f}")

            # Alerts
            if latest_rsi > 70:
                print(f"{symbol} 🚨 Overbought")
            elif latest_rsi < 30:
                print(f"{symbol} 🚨 Oversold")

            ts = datetime.now()
            cursor.execute(
                """
                INSERT INTO stock_data (symbol, timestamp, price, ma5, rsi, open, high, low)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (symbol, ts, latest_price, ma5, latest_rsi, latest_open, latest_high, latest_low)
            )
            conn.commit()
            print(f"{symbol} ✅ Inserted into DB")

        except Exception as e:
            print(f"Error fetching {symbol}: {e}")

# Scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(fetch_stock, 'interval', seconds=30)
scheduler.start()
print("Scheduler started...")

# Keep running
while True:
    time.sleep(1)