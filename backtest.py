import mysql.connector
import pandas as pd

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "chiragsql@2002",
    "database": "stock_project"
}

def run_backtest(symbol, rsi_buy=30, rsi_sell=70, initial_capital=100000):
    """
    Strategy:
    - BUY when RSI < rsi_buy (oversold)
    - SELL when RSI > rsi_sell (overbought)
    - Start with initial_capital (in INR)
    """
    conn = mysql.connector.connect(**DB_CONFIG)
    query = """
        SELECT timestamp, price, rsi FROM stock_data
        WHERE symbol=%s
        ORDER BY id ASC
    """
    df = pd.read_sql(query, conn, params=(symbol,))
    conn.close()

    if df.empty or len(df) < 10:
        return None

    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # ---------- SIMULATE TRADES ----------
    capital = initial_capital
    shares = 0
    position = None  # 'long' or None
    trades = []

    for _, row in df.iterrows():
        price = row['price']
        rsi = row['rsi']
        ts = row['timestamp']

        # BUY signal
        if rsi < rsi_buy and position is None:
            shares = capital / price
            capital = 0
            position = 'long'
            trades.append({
                "type": "BUY",
                "timestamp": str(ts),
                "price": round(price, 2),
                "shares": round(shares, 4)
            })

        # SELL signal
        elif rsi > rsi_sell and position == 'long':
            capital = shares * price
            shares = 0
            position = None
            trades.append({
                "type": "SELL",
                "timestamp": str(ts),
                "price": round(price, 2),
                "capital": round(capital, 2)
            })

    # If still holding at end, sell at last price
    if position == 'long':
        final_price = df['price'].iloc[-1]
        capital = shares * final_price
        trades.append({
            "type": "SELL (End)",
            "timestamp": str(df['timestamp'].iloc[-1]),
            "price": round(final_price, 2),
            "capital": round(capital, 2)
        })

    # ---------- PERFORMANCE METRICS ----------
    total_profit = round(capital - initial_capital, 2)
    return_pct = round((total_profit / initial_capital) * 100, 2)

    # Count winning trades (buy-sell pairs)
    buy_prices = [t['price'] for t in trades if t['type'] == 'BUY']
    sell_prices = [t['price'] for t in trades if t['type'] in ('SELL', 'SELL (End)')]
    pairs = list(zip(buy_prices, sell_prices))
    winning_trades = sum(1 for b, s in pairs if s > b)
    total_pairs = len(pairs)
    win_rate = round((winning_trades / total_pairs) * 100, 2) if total_pairs > 0 else 0

    return {
        "symbol": symbol,
        "strategy": f"Buy RSI<{rsi_buy}, Sell RSI>{rsi_sell}",
        "initial_capital": f"₹{initial_capital:,}",
        "final_capital": f"₹{round(capital, 2):,}",
        "total_profit": f"₹{total_profit:,}",
        "return_pct": f"{return_pct}%",
        "total_trades": len(trades),
        "winning_trades": winning_trades,
        "win_rate": f"{win_rate}%",
        "trade_log": trades
    }
