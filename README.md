# 📈 Real-Time Stock Market Predictor

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.21-orange)
![Streamlit](https://img.shields.io/badge/Streamlit-1.56-red)
![MySQL](https://img.shields.io/badge/MySQL-8.0-blue)

A full-stack AI-powered stock market application for Indian NSE markets that combines **deep learning**, **NLP sentiment analysis**, and **algorithmic backtesting** into a single interactive dashboard.

---

## 🚀 Features

### 🤖 LSTM Neural Network Prediction
- 2-layer LSTM model built with TensorFlow/Keras
- Trained on real historical price data stored in MySQL
- Predicts the next price point with MinMaxScaler normalization
- Significantly more accurate than traditional linear regression

### 🧠 AI Combined Signal
- Fuses LSTM price prediction + News sentiment into one unified trading signal
- Outputs: Strong Buy / Weak Buy / Neutral / Weak Sell / Strong Sell
- Includes confidence level and explanation for every signal

### 📰 News Sentiment Analysis
- Fetches latest financial news via NewsAPI
- Analyzes headlines using TextBlob NLP
- Scores each article from -1 (negative) to +1 (positive)
- Visualizes sentiment as an interactive bar chart

### 📊 Interactive Dashboard
- Candlestick + Line chart toggle
- RSI indicator with overbought/oversold zones
- MA5 moving average overlay
- 4-tab organized layout: Market Overview · AI Predictions · News Sentiment · Backtesting Lab

### ⚙️ Strategy Backtesting Engine
- Simulates RSI-based buy/sell strategies on historical data
- Calculates real P&L, win rate, and return %
- Color-coded trade log with BUY/SELL markers on price chart
- Adjustable RSI thresholds and initial capital

### ⏰ Smart Scheduler
- Auto-fetches OHLC data every 30 seconds
- Only runs during NSE market hours (Mon–Fri, 9:15 AM – 3:30 PM IST)
- Calculates and stores RSI and MA5 automatically

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit, Plotly |
| Backend | FastAPI, Python |
| ML Model | TensorFlow, Keras (LSTM) |
| NLP | TextBlob, NewsAPI |
| Database | MySQL |
| Data Source | yfinance |
| Scheduler | APScheduler |
| Data Processing | Pandas, NumPy, Scikit-learn |

---

## 📁 Project Structure

    RealTimeStockMarketPredictor/
    ├── dashboard.py          → Streamlit frontend (4-tab dashboard)
    ├── main.py               → FastAPI REST backend
    ├── predict_model.py      → LSTM neural network model
    ├── sentiment.py          → News sentiment analysis
    ├── backtest.py           → Strategy backtesting engine
    ├── combined_signal.py    → LSTM + Sentiment fusion
    ├── scheduler.py          → Real-time data scheduler
    ├── db_setup.py           → MySQL database setup
    ├── requirements.txt      → Python dependencies
    ├── .env                  → Environment variables (not pushed)
    └── README.md             → Project documentation
---

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/diya019-git/RealTimeStockMarketPredictor.git
cd RealTimeStockMarketPredictor
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up MySQL database
```bash
python db_setup.py
```

### 4. Configure environment variables
Create a `.env` file:
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=stock_project
NEWS_API_KEY=your_newsapi_key

### 5. Start the data scheduler
```bash
python scheduler.py
```

### 6. Start the FastAPI backend
```bash
uvicorn main:app --reload
```

### 7. Launch the dashboard
```bash
streamlit run dashboard.py
```

---

## 🔗 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| GET | `/history` | Historical stock data |
| GET | `/predict` | LSTM price prediction + RSI |
| GET | `/real-time-price` | Live price via yfinance |
| GET | `/backtest` | RSI strategy backtesting |
| GET | `/sentiment` | News sentiment analysis |
| GET | `/combined-signal` | LSTM + Sentiment unified signal |

---

## 📈 Stocks Tracked

| Symbol | Company |
|---|---|
| RELIANCE.NS | Reliance Industries |
| TCS.NS | Tata Consultancy Services |
| INFY.NS | Infosys |
| HDFCBANK.NS | HDFC Bank |

---

## 🧠 How the LSTM Model Works

1. Fetches last 100 price points from MySQL
2. Normalizes data to [0,1] using MinMaxScaler
3. Creates sequences of 10 timesteps
4. Trains a 2-layer LSTM with Dropout regularization
5. Predicts the next price and inverse-transforms to original scale

---

## 📊 How the Combined Signal Works

| LSTM Direction | News Sentiment | Signal |
|---|---|---|
| UP | Bullish | 🟢 Strong Buy |
| UP | Neutral | 🟡 Weak Buy |
| UP | Bearish | 🟡 Conflicted |
| DOWN | Bearish | 🔴 Strong Sell |
| DOWN | Neutral | 🟡 Weak Sell |
| DOWN | Bullish | 🟡 Conflicted |

---

## 👨‍💻 Author

Built with ❤️ by Diya Gupta as a final year project demonstrating real-world applications of:
- Deep Learning (LSTM Neural Networks)
- Natural Language Processing (Sentiment Analysis)
- Financial Engineering (Technical Indicators + Backtesting)
- Full-Stack Development (FastAPI + Streamlit + MySQL)
