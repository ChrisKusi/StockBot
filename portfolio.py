# portfolio.py
import sqlite3
import yfinance as yf
from datetime import datetime

def add_stock(user_id, symbol, quantity, purchase_price=None, purchase_date=None):
    conn = sqlite3.connect("stockbot.db")
    c = conn.cursor()
    if purchase_price is None:
        stock = yf.Ticker(symbol).info
        purchase_price = stock.get("regularMarketPrice", 0)
    if purchase_date is None:
        purchase_date = datetime.now().strftime("%Y-%m-%d")
    c.execute("INSERT INTO portfolios (user_id, symbol, quantity, purchase_price, purchase_date) VALUES (?, ?, ?, ?, ?)", 
              (user_id, symbol, quantity, purchase_price, purchase_date))
    conn.commit()
    conn.close()

def get_portfolio(user_id):
    conn = sqlite3.connect("stockbot.db")
    c = conn.cursor()
    c.execute("SELECT symbol, quantity, purchase_price FROM portfolios WHERE user_id = ?", (user_id,))
    holdings = c.fetchall()
    conn.close()
    total_value = 0
    details = []
    for symbol, qty, purchase_price in holdings:
        stock = yf.Ticker(symbol).info
        current_price = stock.get("regularMarketPrice", 0)
        value = current_price * qty
        total_value += value
        details.append((symbol, qty, current_price, value))
    return details, total_value