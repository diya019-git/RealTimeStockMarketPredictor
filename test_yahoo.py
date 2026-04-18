import yfinance as yf
import time

while True:
    stock = yf.Ticker("RELIANCE.NS")
    data = stock.history(period="1d", interval="1m")

    latest_price = data['Close'].iloc[-1]

    print("Live price:", latest_price)

    time.sleep(30)   # 30 sec wait