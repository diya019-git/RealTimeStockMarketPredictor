import requests
from textblob import TextBlob
from datetime import datetime, timedelta

NEWS_API_KEY = "7394dd10e60441c9b4a30d21e9584389"

SYMBOL_TO_NAME = {
    "RELIANCE.NS": "Reliance Industries",
    "TCS.NS": "Tata Consultancy Services",
    "INFY.NS": "Infosys",
    "HDFCBANK.NS": "HDFC Bank"
}

def get_sentiment(symbol, num_articles=10):
    company_name = SYMBOL_TO_NAME.get(symbol, symbol)

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": company_name,
        "apiKey": NEWS_API_KEY,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": num_articles,
        "from": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data.get("status") != "ok" or not data.get("articles"):
        return {
            "symbol": symbol,
            "company": company_name,
            "error": "No news found",
            "articles": []
        }

    articles = []
    total_polarity = 0

    for article in data["articles"]:
        headline = article.get("title", "")
        description = article.get("description", "") or ""

        text = headline + " " + description
        blob = TextBlob(text)
        polarity = round(blob.sentiment.polarity, 4)
        subjectivity = round(blob.sentiment.subjectivity, 4)

        if polarity > 0.1:
            sentiment_label = "Positive 🟢"
        elif polarity < -0.1:
            sentiment_label = "Negative 🔴"
        else:
            sentiment_label = "Neutral 🟡"

        total_polarity += polarity

        articles.append({
            "headline": headline,
            "source": article.get("source", {}).get("name", "Unknown"),
            "published_at": article.get("publishedAt", "")[:10],
            "url": article.get("url", ""),
            "polarity": polarity,
            "subjectivity": subjectivity,
            "sentiment": sentiment_label
        })

    avg_polarity = round(total_polarity / len(articles), 4)

    if avg_polarity > 0.1:
        overall = "Bullish 🟢"
        recommendation = "Positive news sentiment — may support price rise"
    elif avg_polarity < -0.1:
        overall = "Bearish 🔴"
        recommendation = "Negative news sentiment — may pressure price down"
    else:
        overall = "Neutral 🟡"
        recommendation = "Mixed sentiment — no strong directional signal"

    return {
        "symbol": symbol,
        "company": company_name,
        "overall_sentiment": overall,
        "average_polarity": avg_polarity,
        "recommendation": recommendation,
        "total_articles_analyzed": len(articles),
        "articles": articles
    }