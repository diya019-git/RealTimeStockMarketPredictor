import streamlit as st
import mysql.connector
import pandas as pd
import plotly.graph_objects as go
import os
from dotenv import load_dotenv

load_dotenv()

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Stock Market AI Dashboard",
    page_icon="📈",
    layout="wide"
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
</style>
""", unsafe_allow_html=True)

# ---------- DB CONFIG ----------
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "sql12.freesqldatabase.com"),
    "user": os.getenv("DB_USER", "sql12824704"),
    "password": os.getenv("DB_PASSWORD", "B9Bt85gVs2"),
    "database": os.getenv("DB_NAME", "sql12824704"),
    "port": int(os.getenv("DB_PORT", "3306"))
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

# ---------- HEADER ----------
st.markdown("# 📈 Real-Time Stock Market Dashboard")
st.markdown("Live prices · RSI signals · News sentiment · Strategy backtesting")
st.markdown("---")

# ---------- CONTROLS ROW ----------
ctrl1, ctrl2, ctrl3 = st.columns([2, 2, 1])
with ctrl1:
    symbol = st.selectbox(
        "🔍 Select Stock",
        ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS"]
    )
with ctrl2:
    limit = st.slider("📊 Data Points", min_value=20, max_value=300, value=100)
with ctrl3:
    st.markdown("**📅 Market Hours**")
    st.caption("Mon–Fri 9:15AM–3:30PM IST")

st.markdown("---")

# ---------- FETCH DATA ----------
df = get_history(symbol, limit)
df_ohlc = get_history(symbol, limit, ohlc_only=True)

if df.empty:
    st.error("No data found.")
    st.stop()

df['timestamp'] = pd.to_datetime(df['timestamp'])
if not df_ohlc.empty:
    df_ohlc['timestamp'] = pd.to_datetime(df_ohlc['timestamp'])

latest_price = df['price'].iloc[-1]
latest_rsi = df['rsi'].iloc[-1]
latest_ma5 = df['ma5'].iloc[-1]
price_change = df['price'].iloc[-1] - df['price'].iloc[-2]
price_change_pct = (price_change / df['price'].iloc[-2]) * 100

# ---------- METRICS ROW ----------
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
tab1, tab2, tab3 = st.tabs([
    "📊 Market Overview",
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

# ==================== TAB 2: NEWS SENTIMENT ====================
with tab2:
    st.subheader("📰 News Sentiment Analysis")
    st.caption("NLP analysis of latest financial news using TextBlob")

    if st.button("🔍 Analyze News Sentiment", type="primary"):
        from sentiment import get_sentiment
        with st.spinner("Fetching and analyzing news headlines..."):
            result = get_sentiment(symbol)

        if "error" in result:
            st.error(result["error"])
        else:
            s1, s2, s3 = st.columns(3)
            s1.metric("Overall Sentiment", result["overall_sentiment"])
            s2.metric("Avg Polarity", result["average_polarity"])
            s3.metric("Articles Analyzed", result["total_articles_analyzed"])

            avg = result["average_polarity"]
            if avg > 0.1:
                st.success(f"💡 {result['recommendation']}")
            elif avg < -0.1:
                st.error(f"💡 {result['recommendation']}")
            else:
                st.warning(f"💡 {result['recommendation']}")

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

# ==================== TAB 3: BACKTESTING ====================
with tab3:
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
            else:
                st.warning("No trades executed. Try widening the RSI thresholds.")