import requests
from fastapi import FastAPI
import mysql.connector
from fastapi.middleware.cors import CORSMiddleware
from predict_model import predict_price, calculate_rsi
from backtest import run_backtest
from sentiment import get_sentiment
from combined_signal import get_combined_signal

app = FastAPI()

# CORS (frontend dashboard ke liye)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB CONFIG
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "chiragsql@2002",
    "database": "stock_project"
}

# Home API
@app.get("/")
def home():
    return {"message": "Stock API running with LSTM predictions"}

# Get historical data for selected stock
@app.get("/history")
def get_history(symbol: str = "RELIANCE.NS"):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT * FROM stock_data
        WHERE symbol=%s
        ORDER BY id DESC
        LIMIT 50
        """,
        (symbol,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows

# Real-time price (yfinance fallback since example.com won't work)
@app.get("/real-time-price")
def get_real_time_price(symbol: str = "RELIANCE.NS"):
    import yfinance as yf
    ticker = yf.Ticker(symbol)
    data = ticker.history(period="1d")
    if data.empty:
        return {"error": "Could not fetch price"}
    price = round(float(data['Close'].iloc[-1]), 2)
    return {
        "symbol": symbol,
        "real_time_price": price
    }

# LSTM Predict + RSI
@app.get("/predict")
def predict(symbol: str = "RELIANCE.NS"):
    predicted = predict_price(symbol)
    rsi = calculate_rsi(symbol)

    # RSI signal interpretation
    if rsi is None:
        rsi_signal = "Not enough data"
    elif rsi > 70:
        rsi_signal = "Overbought - Consider Selling"
    elif rsi < 30:
        rsi_signal = "Oversold - Consider Buying"
    else:
        rsi_signal = "Neutral"

    return {
        "symbol": symbol,
        "predicted_price": round(predicted, 2) if predicted else None,
        "rsi": round(float(rsi), 2) if rsi is not None else None,
        "rsi_signal": rsi_signal
    }

# Get latest data point for selected stock
@app.get("/latest")
def get_latest(symbol: str = "RELIANCE.NS"):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT * FROM stock_data
        WHERE symbol=%s
        ORDER BY id DESC
        LIMIT 1
        """,
        (symbol,)
    )
    row = cursor.fetchone()
    conn.close()
    return row

@app.get("/backtest")
def backtest(symbol: str = "INFY.NS", rsi_buy: int = 30, rsi_sell: int = 70, capital: int = 100000):
    result = run_backtest(symbol, rsi_buy, rsi_sell, capital)
    if result is None:
        return {"error": "Not enough data to backtest"}
    return result

@app.get("/sentiment")
def sentiment(symbol: str = "INFY.NS"):
    result = get_sentiment(symbol)
    return result

@app.get("/combined-signal")
def combined_signal(symbol: str = "INFY.NS"):
    result = get_combined_signal(symbol)
    return result