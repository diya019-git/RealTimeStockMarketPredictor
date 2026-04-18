import mysql.connector
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

# ---------- DB CONFIG ----------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "chiragsql@2002",
    "database": "stock_project"
}

def get_prices_from_db(symbol):
    conn = mysql.connector.connect(**DB_CONFIG)
    query = """
    SELECT price FROM stock_data
    WHERE symbol=%s
    ORDER BY id ASC
    """
    df = pd.read_sql(query, conn, params=(symbol,))
    conn.close()
    return df

# ---------- RSI (unchanged) ----------
def calculate_rsi(symbol, period=14):
    df = get_prices_from_db(symbol)
    if len(df) < period:
        return None
    delta = df['price'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

# ---------- LSTM PREDICTION ----------
def predict_price(symbol, sequence_length=10):
    df = get_prices_from_db(symbol)

    # Need at least sequence_length + 1 rows to train
    if len(df) < sequence_length + 1:
        return None

    prices = df['price'].values.reshape(-1, 1)

    # Step 1: Scale prices to range [0, 1]
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_prices = scaler.fit_transform(prices)

    # Step 2: Build sequences
    X, y = [], []
    for i in range(sequence_length, len(scaled_prices)):
        X.append(scaled_prices[i - sequence_length:i, 0])
        y.append(scaled_prices[i, 0])

    X, y = np.array(X), np.array(y)

    # Step 3: Reshape X for LSTM input → (samples, timesteps, features)
    X = X.reshape((X.shape[0], X.shape[1], 1))

    # Step 4: Build LSTM model
    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=(sequence_length, 1)),
        Dropout(0.2),
        LSTM(50, return_sequences=False),
        Dropout(0.2),
        Dense(1)
    ])

    model.compile(optimizer='adam', loss='mean_squared_error')

    # Step 5: Train the model
    model.fit(X, y, epochs=10, batch_size=16, verbose=0)

    # Step 6: Predict next price
    last_sequence = scaled_prices[-sequence_length:].reshape(1, sequence_length, 1)
    predicted_scaled = model.predict(last_sequence, verbose=0)
    predicted_price = scaler.inverse_transform(predicted_scaled)

    return float(predicted_price[0][0])