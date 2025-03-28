# analysis.py
import yfinance as yf

def analyze_stock(symbol):
    stock = yf.Ticker(symbol)
    info = stock.info
    if "regularMarketPrice" not in info:
        return None
    hist = stock.history(period="1mo")
    sma = hist["Close"].rolling(window=10).mean().iloc[-1]
    return {
        "name": info.get("longName", symbol),
        "price": info["regularMarketPrice"],
        "sma": sma,
        "dividend": info.get("dividendYield", 0) * 100
    }