import streamlit as st
import mysql.connector
import pandas as pd
import plotly.graph_objects as go

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Stock Market AI Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>
    .stMetric {
        background-color: #1e2130;
        border-radius: 12px;
        padding: 15px;
        border: 1px solid #2d3250;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #1e2130;
        border-radius: 12px;
        padding: 5px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 8px;
        color: #aaaaaa;
        font-size: 15px;
        font-weight: 500;
        padding: 8px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2d3250 !important;
        color: #ffffff !important;
    }
    div[data-testid="stSidebarContent"] {
        background-color: #1e2130;
    }
</style>
""", unsafe_allow_html=True)

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
            ORDER BY id ASC LIMIT %s
        """
    else:
        query = """
            SELECT timestamp, price, ma5, rsi, open, high, low FROM stock_data
            WHERE symbol=%s ORDER BY id ASC LIMIT %s
        """
    df = pd.read_sql(query, conn, params=(symbol, limit))
    conn.close()
    return df

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("## 📈 Stock Market AI")
    st.markdown("---")
    symbol = st.selectbox(
        "🔍 Select Stock",
        ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS"]
    )
    limit = st.slider("📊 Data Points", min_value=20, max_value=300, value=100)
    st.markdown("---")
    st.markdown("**📅 NSE Market Hours**")
    st.caption("Mon–Fri: 9:15 AM – 3:30 PM IST")
    st.markdown("---")
    st.markdown("**🗂️ Pages**")
    st.caption("📊 Market Overview")
    st.caption("🤖 AI Predictions")
    st.caption("📰 News Sentiment")
    st.caption("⚙️ Backtesting Lab")

# ---------- HEADER ----------
st.markdown("# 📈 Real-Time Stock Market Dashboard")
st.markdown(f"Tracking **{symbol}** — Live prices · LSTM predictions · RSI signals · Sentiment analysis")
st.markdown("---")

# ---------- FETCH DATA ----------
df = get_history(symbol, limit)
df_ohlc = get_history(symbol, limit, ohlc_only=True)

if df.empty:
    st.error("No data found. Make sure the scheduler is running.")
    st.stop()

df['timestamp'] = pd.to_datetime(df['timestamp'])
if not df_ohlc.empty:
    df_ohlc['timestamp'] = pd.to_datetime(df_ohlc['timestamp'])

latest_price = df['price'].iloc[-1]
latest_rsi = df['rsi'].iloc[-1]
latest_ma5 = df['ma5'].iloc[-1]
price_change = df['price'].iloc[-1] - df['price'].iloc[-2]
price_change_pct = (price_change / df['price'].iloc[-2]) * 100

# ---------- GLOBAL METRICS ROW ----------
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("💰 Latest Price", f"₹{latest_price:.2f}",
          f"{price_change:+.2f} ({price_change_pct:+.2f}%)")
m2.metric("📊 MA5", f"₹{latest_ma5:.2f}")
m3.metric("📉 RSI", f"{latest_rsi:.2f}")
m4.metric("📈 Data Points", f"{len(df)}")
if latest_rsi > 70:
    m5.metric("🚦 Signal", "🔴 Overbought", "Consider Selling")
elif latest_rsi < 30:
    m5.metric("🚦 Signal", "🟢 Oversold", "Consider Buying")
else:
    m5.metric("🚦 Signal", "🟡 Neutral", "Hold")

st.markdown("---")

# ==================== TABS ====================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Market Overview",
    "🤖 AI Predictions",
    "📰 News Sentiment",
    "⚙️ Backtesting Lab"
])

# ==================== TAB 1: MARKET OVERVIEW ====================
with tab1:
    st.subheader(f"📊 Price Chart — {symbol}")
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
        height=420,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor='rgba(255,255,255,0.1)',
                   rangeslider=dict(visible=False)),
        yaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
        legend=dict(orientation='h', yanchor='bottom', y=1.02),
        margin=dict(l=0, r=0, t=10, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📉 RSI Indicator")
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df['timestamp'], y=df['rsi'],
        name='RSI', line=dict(color='#9b5de5', width=2),
        fill='tozeroy', fillcolor='rgba(155, 93, 229, 0.1)'
    ))
    fig2.add_hline(y=70, line_dash="dash", line_color="red",
                   annotation_text="Overbought (70)")
    fig2.add_hline(y=30, line_dash="dash", line_color="green",
                   annotation_text="Oversold (30)")
    fig2.update_layout(
        height=250,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.1)', range=[0, 100]),
        margin=dict(l=0, r=0, t=10, b=0)
    )
    st.plotly_chart(fig2, use_container_width=True)

    with st.expander("🗃️ View Raw Data"):
        st.dataframe(
            df.sort_values('timestamp', ascending=False),
            use_container_width=True
        )

# ==================== TAB 2: AI PREDICTIONS ====================
with tab2:

    # ---------- AI COMBINED SIGNAL ----------
    st.subheader("🧠 AI Combined Signal")
    st.caption("LSTM prediction + News sentiment → unified trading signal")

    if st.button("⚡ Generate Combined Signal", type="primary"):
        from combined_signal import get_combined_signal
        with st.spinner("Running LSTM + Sentiment analysis..."):
            result = get_combined_signal(symbol)

        if "error" in result:
            st.error(result["error"])
        else:
            signal = result["combined_signal"]
            if "Strong Buy" in signal:
                st.success(f"## {signal}")
            elif "Strong Sell" in signal:
                st.error(f"## {signal}")
            else:
                st.warning(f"## {signal}")

            st.markdown(f"**Confidence:** `{result['confidence']}` &nbsp;|&nbsp; _{result['explanation']}_")
            st.markdown("---")

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("💰 Current Price", f"₹{result['current_price']}")
            c2.metric("🤖 LSTM Prediction", f"₹{result['predicted_price']}",
                      delta=f"{result['price_change']:+.2f}")
            c3.metric("📈 Direction", result["price_direction"])
            c4.metric("📰 Sentiment", result["news_sentiment"].split(" ")[0])

    st.markdown("---")

    # ---------- LSTM PREDICTION ----------
    st.subheader("🔮 LSTM Price Prediction")
    st.caption("2-layer neural network trained on your historical data")

    info_col, btn_col = st.columns([3, 1])
    with info_col:
        st.markdown("""
        **Model Architecture:**
        LSTM Layer 1 (50 units + Dropout) → LSTM Layer 2 (50 units + Dropout) → Dense Output
        Optimizer: Adam | Loss: MSE | Trained fresh on each prediction
        """)
    with btn_col:
        predict_btn = st.button("🔮 Predict Next Price", type="primary", use_container_width=True)

    if predict_btn:
        from predict_model import predict_price
        with st.spinner("Training LSTM model... ~30 seconds"):
            predicted = predict_price(symbol)

        if predicted:
            diff = predicted - latest_price
            pct = (diff / latest_price) * 100

            p1, p2, p3 = st.columns(3)
            p1.metric("Current Price", f"₹{latest_price:.2f}")
            p2.metric("Predicted Price", f"₹{predicted:.2f}", delta=f"{diff:+.2f}")
            p3.metric("Expected Change", f"{pct:+.2f}%")

            next_time = df['timestamp'].iloc[-1] + pd.Timedelta(minutes=1)
            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(
                x=df['timestamp'], y=df['price'],
                name='Actual', line=dict(color='#00b4d8', width=2)
            ))
            fig3.add_trace(go.Scatter(
                x=[df['timestamp'].iloc[-1], next_time],
                y=[latest_price, predicted],
                name='Prediction',
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
            
# ==================== TAB 3: NEWS SENTIMENT ====================
with tab3:
    st.subheader("📰 News Sentiment Analysis")
    st.caption("NLP analysis of latest financial news using TextBlob sentiment scoring")

    if st.button("🔍 Analyze News Sentiment", type="primary"):
        from sentiment import get_sentiment
        with st.spinner("Fetching and analyzing news headlines..."):
            result = get_sentiment(symbol)

        if "error" in result:
            st.error(result["error"])
        else:
            s1, s2, s3 = st.columns(3)
            s1.metric("Overall Sentiment", result["overall_sentiment"])
            s2.metric("Avg Polarity", result["average_polarity"],
                      help="-1 = very negative, +1 = very positive")
            s3.metric("Articles Analyzed", result["total_articles_analyzed"])

            avg = result["average_polarity"]
            if avg > 0.1:
                st.success(f"💡 {result['recommendation']}")
            elif avg < -0.1:
                st.error(f"💡 {result['recommendation']}")
            else:
                st.warning(f"💡 {result['recommendation']}")

            st.markdown("---")

            articles = result["articles"]
            headlines = [a["headline"][:50] + "..." for a in articles]
            polarities = [a["polarity"] for a in articles]
            colors = ["#26a69a" if p > 0.1 else "#ef5350"
                      if p < -0.1 else "#888888" for p in polarities]

            fig_sent = go.Figure(go.Bar(
                x=polarities, y=headlines,
                orientation='h', marker_color=colors
            ))
            fig_sent.update_layout(
                height=420,
                title="Headline Sentiment Scores",
                xaxis_title="Polarity (-1 = Negative, +1 = Positive)",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(gridcolor='rgba(255,255,255,0.1)', range=[-1, 1]),
                yaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
                margin=dict(l=0, r=0, t=40, b=0)
            )
            st.plotly_chart(fig_sent, use_container_width=True)

            st.markdown("**📋 Article Details**")
            df_articles = pd.DataFrame(articles)[
                ["headline", "source", "published_at", "sentiment", "polarity"]
            ]
            st.dataframe(df_articles, use_container_width=True)

# ==================== TAB 4: BACKTESTING ====================
with tab4:
    st.subheader("⚙️ Strategy Backtester")
    st.caption("Simulate a RSI-based buy/sell strategy on your historical data")

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        bt_symbol = st.selectbox(
            "📈 Stock",
            ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS"],
            key="bt"
        )
    with col_b:
        rsi_buy = st.slider("🟢 Buy when RSI <", 20, 45, 30)
    with col_c:
        rsi_sell = st.slider("🔴 Sell when RSI >", 55, 80, 70)

    capital = st.number_input(
        "💰 Initial Capital (₹)",
        min_value=10000, max_value=1000000,
        value=100000, step=10000
    )

    if st.button("▶ Run Backtest", type="primary"):
        from backtest import run_backtest
        with st.spinner("Simulating trades..."):
            result = run_backtest(bt_symbol, rsi_buy, rsi_sell, int(capital))

        if result is None:
            st.error("Not enough data.")
        else:
            profit_val = float(result['total_profit'].replace('₹', '').replace(',', ''))

            if profit_val > 0:
                st.success(f"## ✅ Profitable — {result['return_pct']} return")
            elif profit_val < 0:
                st.error(f"## ❌ Unprofitable — {result['return_pct']} return")
            else:
                st.warning("## ⚠️ No trades executed — adjust RSI thresholds")

            st.markdown("---")
            r1, r2, r3, r4, r5 = st.columns(5)
            r1.metric("💰 Initial", result['initial_capital'])
            r2.metric("💵 Final", result['final_capital'])
            r3.metric("📈 Profit", result['total_profit'], delta=result['return_pct'])
            r4.metric("🏆 Win Rate", result['win_rate'])
            r5.metric("🔄 Trades", result['total_trades'])

            if result['trade_log']:
                st.markdown("---")
                st.markdown("**📋 Trade Log**")
                trade_df = pd.DataFrame(result['trade_log'])

                def highlight_trades(row):
                    if row['type'] == 'BUY':
                        return ['background-color: rgba(38,166,154,0.2)'] * len(row)
                    elif 'SELL' in str(row['type']):
                        return ['background-color: rgba(239,83,80,0.2)'] * len(row)
                    return [''] * len(row)

                st.dataframe(
                    trade_df.style.apply(highlight_trades, axis=1),
                    use_container_width=True
                )

                # Trade chart
                df_bt = get_history(bt_symbol, 300)
                if not df_bt.empty:
                    df_bt['timestamp'] = pd.to_datetime(df_bt['timestamp'])
                    fig_bt = go.Figure()
                    fig_bt.add_trace(go.Scatter(
                        x=df_bt['timestamp'], y=df_bt['price'],
                        name='Price', line=dict(color='#00b4d8', width=2)
                    ))
                    buys = [t for t in result['trade_log'] if t['type'] == 'BUY']
                    sells = [t for t in result['trade_log'] if 'SELL' in t['type']]
                    if buys:
                        fig_bt.add_trace(go.Scatter(
                            x=[b['timestamp'] for b in buys],
                            y=[b['price'] for b in buys],
                            name='BUY', mode='markers',
                            marker=dict(color='#26a69a', size=12,
                                        symbol='triangle-up')
                        ))
                    if sells:
                        fig_bt.add_trace(go.Scatter(
                            x=[s['timestamp'] for s in sells],
                            y=[s['price'] for s in sells],
                            name='SELL', mode='markers',
                            marker=dict(color='#ef5350', size=12,
                                        symbol='triangle-down')
                        ))
                    fig_bt.update_layout(
                        height=380,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
                        yaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
                        legend=dict(orientation='h', yanchor='bottom', y=1.02),
                        margin=dict(l=0, r=0, t=10, b=0)
                    )
                    st.plotly_chart(fig_bt, use_container_width=True)
            else:
                st.warning("No trades executed. Try widening the RSI thresholds.")