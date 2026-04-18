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

            close = data['Close']

            latest_price = close.iloc[-1]

            # Moving Average
            ma5 = close.tail(5).mean()

            # RSI Calculation
            delta = close.diff()

            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()

            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))

            latest_rsi = rsi.iloc[-1]

            print(symbol, "| Price:", latest_price, "| MA5:", ma5, "| RSI:", latest_rsi)

            # Alerts
            if latest_rsi > 70:
                print(symbol, "🚨 Overbought")

            elif latest_rsi < 30:
                print(symbol, "🚨 Oversold")

            ts = datetime.now()

            cursor.execute(
                """
                INSERT INTO stock_data (symbol, timestamp, price, ma5, rsi)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (symbol, ts, float(latest_price), float(ma5), float(latest_rsi))
            )

            conn.commit()

            print(symbol, "Inserted into DB")

        except Exception as e:

            print("Error fetching", symbol, e)


# Scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(fetch_stock, 'interval', seconds=30)
scheduler.start()

print("Scheduler started...")

# Keep running
while True:
    time.sleep(1)