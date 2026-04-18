from predict_model import predict_price, calculate_rsi
from sentiment import get_sentiment
import math

def get_combined_signal(symbol):
    # ---------- LSTM PREDICTION ----------
    current_price = None
    predicted_price = predict_price(symbol)

    # Get current price from DB
    from predict_model import get_prices_from_db
    df = get_prices_from_db(symbol)
    if df.empty or predicted_price is None:
        return {"error": "Not enough data"}

    current_price = float(df['price'].iloc[-1])
    price_diff = round(predicted_price - current_price, 2)
    price_direction = "UP" if predicted_price > current_price else "DOWN"

    # ---------- RSI ----------
    rsi = calculate_rsi(symbol)
    rsi = round(float(rsi), 2) if rsi is not None and not math.isnan(float(rsi)) else None

    if rsi:
        if rsi > 70:
            rsi_signal = "Overbought"
        elif rsi < 30:
            rsi_signal = "Oversold"
        else:
            rsi_signal = "Neutral"
    else:
        rsi_signal = "Unknown"

    # ---------- SENTIMENT ----------
    sent_result = get_sentiment(symbol)
    avg_polarity = sent_result.get("average_polarity", 0)
    overall_sentiment = sent_result.get("overall_sentiment", "Neutral 🟡")

    if avg_polarity > 0.1:
        sentiment_direction = "Bullish"
    elif avg_polarity < -0.1:
        sentiment_direction = "Bearish"
    else:
        sentiment_direction = "Neutral"

    # ---------- COMBINED SIGNAL LOGIC ----------
    if price_direction == "UP" and sentiment_direction == "Bullish":
        signal = "🟢 Strong Buy"
        explanation = "LSTM predicts price rise AND news sentiment is positive. High confidence."
        confidence = "High"

    elif price_direction == "UP" and sentiment_direction == "Neutral":
        signal = "🟡 Weak Buy"
        explanation = "LSTM predicts price rise but news sentiment is mixed. Proceed with caution."
        confidence = "Medium"

    elif price_direction == "UP" and sentiment_direction == "Bearish":
        signal = "🟡 Conflicted"
        explanation = "LSTM predicts rise but news sentiment is negative. Signals contradict each other."
        confidence = "Low"

    elif price_direction == "DOWN" and sentiment_direction == "Bearish":
        signal = "🔴 Strong Sell"
        explanation = "LSTM predicts price drop AND news sentiment is negative. High confidence."
        confidence = "High"

    elif price_direction == "DOWN" and sentiment_direction == "Neutral":
        signal = "🟡 Weak Sell"
        explanation = "LSTM predicts price drop but news sentiment is mixed. Monitor closely."
        confidence = "Medium"

    elif price_direction == "DOWN" and sentiment_direction == "Bullish":
        signal = "🟡 Conflicted"
        explanation = "LSTM predicts drop but news sentiment is positive. Signals contradict each other."
        confidence = "Low"

    else:
        signal = "🟡 Neutral"
        explanation = "No strong signal detected."
        confidence = "Low"

    return {
        "symbol": symbol,
        "current_price": round(current_price, 2),
        "predicted_price": round(predicted_price, 2),
        "price_change": price_diff,
        "price_direction": price_direction,
        "rsi": rsi,
        "rsi_signal": rsi_signal,
        "news_sentiment": overall_sentiment,
        "avg_polarity": avg_polarity,
        "combined_signal": signal,
        "confidence": confidence,
        "explanation": explanation
    }