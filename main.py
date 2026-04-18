import requests
from fastapi import FastAPI
import mysql.connector
from fastapi.middleware.cors import CORSMiddleware
from predict_model import predict_price

app = FastAPI()

# CORS (frontend dashboard ke liye)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Home API
@app.get("/")
def home():
    return {"message": "Stock API running"}

# Get historical data for selected stock
@app.get("/history")
def get_history(symbol: str = "RELIANCE.NS"):

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="chiragsql@2002",
        database="stock_project"
    )

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

@app.get("/real-time-price")
def get_real_time_price(symbol: str = "RELIANCE.NS"):
    url = f"https://api.example.com/stock/{symbol}/price"  # Replace with actual API URL
    response = requests.get(url)
    data = response.json()
    return {
        "symbol": symbol,
        "real_time_price": data['price']
    }

@app.get("/predict")
def predict(symbol: str = "RELIANCE.NS"):
    predicted = predict_price(symbol)
    rsi = calculate_rsi(symbol)  # Call the new RSI calculation function

    predicted = predict_price(symbol)

    return {
        "symbol": symbol,
        "predicted_price": predicted
    }

# Get latest data point for selected stock
@app.get("/latest")
def get_latest(symbol: str = "RELIANCE.NS"):

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="chiragsql@2002",
        database="stock_project"
    )

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
