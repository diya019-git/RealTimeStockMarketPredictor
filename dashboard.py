import streamlit as st
import mysql.connector
import pandas as pd
import plotly.graph_objects as go
from predict_model import predict_price, calculate_rsi

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Stock Market Dashboard",
    page_icon="📈",
    layout="wide"
)

# ---------- DB CONFIG ----------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "chiragsql@2002",
    "database": "stock_project"
}

def get_history(symbol, limit=100, ohlc_only=False):
    conn = mysql.connector.connect(**DB_CONFIG)
    if ohlc_only:
        query = """
            SELECT timestamp, price, ma5, rsi, open, high, low FROM stock_data
            WHERE symbol=%s AND open IS NOT NULL
            ORDER BY id ASC
            LIMIT %s
        """
    else:
        query = """
            SELECT timestamp, price, ma5, rsi, open, high, low FROM stock_data
            WHERE symbol=%s
            ORDER BY id ASC
            LIMIT %s
        """
    df = pd.read_sql(query, conn, params=(symbol, limit))
    conn.close()
    return df

# ---------- HEADER ----------
st.title("📈 Real-Time Stock Market Dashboard")
st.markdown("Live prices · LSTM predictions · RSI signals")

st.divider()

# ---------- COMBINED SIGNAL (HERO SECTION) ----------
st.subheader("🧠 AI Combined Signal")
st.caption("Combines LSTM price prediction + News sentiment into one unified signal")

sig_symbol = st.selectbox(
    "Stock for Combined Signal",
    ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS"],
    key="sig"
)

if st.button("⚡ Generate Combined Signal"):
    from combined_signal import get_combined_signal
    with st.spinner("Running LSTM + Sentiment analysis..."):
        result = get_combined_signal(sig_symbol)

    if "error" in result:
        st.error(result["error"])
    else:
        # Big signal display
        signal = result["combined_signal"]
        confidence = result["confidence"]

        if "Strong Buy" in signal:
            st.success(f"## {signal}")
        elif "Strong Sell" in signal:
            st.error(f"## {signal}")
        else:
            st.warning(f"## {signal}")

        st.markdown(f"**Confidence:** {confidence} &nbsp;&nbsp; | &nbsp;&nbsp; {result['explanation']}")

        st.divider()

        # Metrics grid
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Current Price", f"₹{result['current_price']}")
        c2.metric("LSTM Prediction", f"₹{result['predicted_price']}",
                  delta=f"{result['price_change']:+.2f}")
        c3.metric("Price Direction", result["price_direction"])
        c4.metric("News Sentiment", result["news_sentiment"].split(" ")[0])
        c5.metric("RSI", result["rsi"] if result["rsi"] else "N/A")

st.divider()

# ---------- STOCK SELECTOR ----------
col1, col2 = st.columns([2, 1])
with col1:
    symbol = st.selectbox(
        "Select Stock",
        ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS"]
    )
with col2:
    limit = st.slider("Data points", min_value=20, max_value=200, value=100)

# ---------- FETCH DATA ----------
df = get_history(symbol, limit)
df_ohlc = get_history(symbol, limit, ohlc_only=True)

if df.empty:
    st.error("No data found for this symbol.")
    st.stop()

df['timestamp'] = pd.to_datetime(df['timestamp'])

# ---------- METRICS ROW ----------
latest_price = df['price'].iloc[-1]
latest_rsi = df['rsi'].iloc[-1]
latest_ma5 = df['ma5'].iloc[-1]
price_change = df['price'].iloc[-1] - df['price'].iloc[-2]
price_change_pct = (price_change / df['price'].iloc[-2]) * 100

m1, m2, m3, m4 = st.columns(4)
m1.metric("Latest Price", f"₹{latest_price:.2f}", f"{price_change:+.2f} ({price_change_pct:+.2f}%)")
m2.metric("MA5", f"₹{latest_ma5:.2f}")
m3.metric("RSI", f"{latest_rsi:.2f}")

# RSI Signal
if latest_rsi > 70:
    m4.metric("Signal", "🔴 Overbought", "Consider Selling")
elif latest_rsi < 30:
    m4.metric("Signal", "🟢 Oversold", "Consider Buying")
else:
    m4.metric("Signal", "🟡 Neutral", "Hold")

st.divider()

# ---------- PRICE CHART ----------
st.subheader(f"📊 Price Chart — {symbol}")

# Chart type toggle
chart_type = st.radio("Chart Type", ["Candlestick", "Line"], horizontal=True)

fig = go.Figure()

if chart_type == "Candlestick" and not df_ohlc.empty:
    fig.add_trace(go.Candlestick(
        x=df_ohlc['timestamp'],
        open=df_ohlc['open'],
        high=df_ohlc['high'],
        low=df_ohlc['low'],
        close=df_ohlc['price'],
        name='OHLC',
        increasing_line_color='#26a69a',
        decreasing_line_color='#ef5350'
    ))
    fig.add_trace(go.Scatter(
        x=df_ohlc['timestamp'], y=df_ohlc['ma5'],
        name='MA5', line=dict(color='#f77f00', width=1.5, dash='dash')
    ))
else:
    fig.add_trace(go.Scatter(
        x=df['timestamp'], y=df['price'],
        name='Price', line=dict(color='#00b4d8', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=df['timestamp'], y=df['ma5'],
        name='MA5', line=dict(color='#f77f00', width=1.5, dash='dash')
    ))

fig.update_layout(
    height=400,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(gridcolor='rgba(255,255,255,0.1)', rangeslider=dict(visible=False)),
    yaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
    legend=dict(orientation='h', yanchor='bottom', y=1.02),
    margin=dict(l=0, r=0, t=10, b=0)
)

st.plotly_chart(fig, use_container_width=True)

# ---------- RSI CHART ----------
st.subheader("📉 RSI Indicator")
fig2 = go.Figure()

fig2.add_trace(go.Scatter(
    x=df['timestamp'], y=df['rsi'],
    name='RSI', line=dict(color='#9b5de5', width=2), fill='tozeroy',
    fillcolor='rgba(155, 93, 229, 0.1)'
))

fig2.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought (70)")
fig2.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold (30)")

fig2.update_layout(
    height=250,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
    yaxis=dict(gridcolor='rgba(255,255,255,0.1)', range=[0, 100]),
    margin=dict(l=0, r=0, t=10, b=0)
)

st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ---------- LSTM PREDICTION ----------
st.subheader("🤖 LSTM Price Prediction")
st.caption("Click the button to run the neural network prediction (takes ~30 seconds)")

if st.button("🔮 Predict Next Price"):
    with st.spinner("Training LSTM model on your data..."):
        predicted = predict_price(symbol)
        rsi_val = calculate_rsi(symbol)

    if predicted:
        diff = predicted - latest_price
        st.success(f"**Predicted Next Price: ₹{predicted:.2f}** ({diff:+.2f} from current)")

        # Show prediction on chart
        next_time = df['timestamp'].iloc[-1] + pd.Timedelta(minutes=1)
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=df['timestamp'], y=df['price'],
            name='Actual Price', line=dict(color='#00b4d8', width=2)
        ))
        fig3.add_trace(go.Scatter(
            x=[df['timestamp'].iloc[-1], next_time],
            y=[latest_price, predicted],
            name='LSTM Prediction',
            line=dict(color='#ff006e', width=2, dash='dot'),
            mode='lines+markers',
            marker=dict(size=10)
        ))
        fig3.update_layout(
            height=350,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            margin=dict(l=0, r=0, t=10, b=0)
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.error("Not enough data to predict.")

st.divider()

# ---------- RAW DATA ----------
with st.expander("🗃️ View Raw Data"):
    st.dataframe(df.sort_values('timestamp', ascending=False), use_container_width=True)

st.divider()

# ---------- BACKTESTING ----------
st.subheader("⚙️ Strategy Backtester")
st.caption("Simulate a RSI-based buy/sell strategy on historical data")

col_a, col_b, col_c = st.columns(3)
with col_a:
    bt_symbol = st.selectbox("Stock", ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS"], key="bt")
with col_b:
    rsi_buy = st.slider("Buy when RSI <", 20, 40, 30)
with col_c:
    rsi_sell = st.slider("Sell when RSI >", 60, 80, 70)

capital = st.number_input("Initial Capital (₹)", min_value=10000, max_value=1000000, value=100000, step=10000)

if st.button("▶ Run Backtest"):
    from backtest import run_backtest
    with st.spinner("Running backtest..."):
        result = run_backtest(bt_symbol, rsi_buy, rsi_sell, int(capital))

    if result is None:
        st.error("Not enough data.")
    else:
        # Metrics
        r1, r2, r3, r4 = st.columns(4)
        profit_val = float(result['total_profit'].replace('₹','').replace(',',''))
        r1.metric("Final Capital", result['final_capital'])
        r2.metric("Total Profit", result['total_profit'], delta=result['return_pct'])
        r3.metric("Win Rate", result['win_rate'])
        r4.metric("Total Trades", result['total_trades'])

        # Trade log
        st.markdown("**📋 Trade Log**")
        trade_df = pd.DataFrame(result['trade_log'])
        st.dataframe(trade_df, use_container_width=True)

st.divider()

# ---------- SENTIMENT ANALYSIS ----------
st.subheader("📰 News Sentiment Analysis")
st.caption("Analyzes latest financial news headlines using NLP")

sent_symbol = st.selectbox(
    "Stock for Sentiment",
    ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS"],
    key="sent"
)

if st.button("🔍 Analyze News Sentiment"):
    from sentiment import get_sentiment
    with st.spinner("Fetching and analyzing news..."):
        result = get_sentiment(sent_symbol)

    if "error" in result:
        st.error(result["error"])
    else:
        # Overall metrics
        s1, s2, s3 = st.columns(3)
        s1.metric("Overall Sentiment", result["overall_sentiment"])
        s2.metric("Avg Polarity", result["average_polarity"],
                  help="-1 = very negative, +1 = very positive")
        s3.metric("Articles Analyzed", result["total_articles_analyzed"])

        # Recommendation box
        avg = result["average_polarity"]
        if avg > 0.1:
            st.success(f"💡 {result['recommendation']}")
        elif avg < -0.1:
            st.error(f"💡 {result['recommendation']}")
        else:
            st.warning(f"💡 {result['recommendation']}")

        # Polarity bar chart
        import plotly.graph_objects as go
        articles = result["articles"]
        headlines = [a["headline"][:40] + "..." for a in articles]
        polarities = [a["polarity"] for a in articles]
        colors = ["green" if p > 0.1 else "red" if p < -0.1 else "gray" for p in polarities]

        fig_sent = go.Figure(go.Bar(
            x=polarities,
            y=headlines,
            orientation='h',
            marker_color=colors
        ))
        fig_sent.update_layout(
            height=400,
            title="Headline Sentiment Scores",
            xaxis_title="Polarity (-1 = Negative, +1 = Positive)",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)', range=[-1, 1]),
            margin=dict(l=0, r=0, t=40, b=0)
        )
        st.plotly_chart(fig_sent, use_container_width=True)

        # Article table
        st.markdown("**📋 Article Details**")
        import pandas as pd
        df_articles = pd.DataFrame(articles)[
            ["headline", "source", "published_at", "sentiment", "polarity"]
        ]
        st.dataframe(df_articles, use_container_width=True)