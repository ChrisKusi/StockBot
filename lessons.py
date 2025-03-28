LESSONS = {
    "1": {
        "title": "What is a Stock? The Basics of Ownership",
        "content": [
            "📚 A stock represents a small piece of a company you can own. Buying a stock makes you a shareholder, giving you a stake in the company’s profits and growth.",
            "💡 Real-Life Example (March 2025): Imagine buying 1 share of Tesla (TSLA) at $250. If Tesla’s new Cybertruck boosts its stock to $300, your share gains $50 in value! You can sell it for a profit or hold it for more growth.",
            "🌍 Why It Matters: Companies like Apple or Amazon use shareholder money to innovate—think iPhones or Prime delivery. Your investment helps them grow while potentially earning you money.",
            "🎮 Try It: Use /simulator buy TSLA 1 to practice buying a stock in the bot’s simulator!",
            "🎥 Learn More: Watch [What Are Stocks?](https://youtu.be/dGBpjtrAIW8?si=tntpkNgTm_1zKx_k) by Bamboo for a quick visual explanation."
        ]
    },
    "2": {
        "title": "Why Diversify? Spreading Risk Like a Pro",
        "content": [
            "📚 Diversification means investing in different stocks or sectors (tech, healthcare, retail) to reduce risk. If one fails, others can balance it out.",
            "💡 Real-Life Example (March 2025): Say you put $1,000 all in Nvidia (NVDA) at $120/share. If AI chip demand drops, you might lose 20% ($200). But if you split $500 into NVDA and $500 into Walmart (WMT) at $75/share, a tech slump might be offset by steady retail gains.",
            "🌍 Market Context: In 2025, tech stocks are volatile due to AI hype, while consumer goods (e.g., PepsiCo) stay stable. Mixing them protects you.",
            "🎮 Try It: Use /add NVDA 4 and /add WMT 6 in your portfolio to simulate diversification, then check /portfolio!",
            "🎥 Learn More: [Why Diversification Matters](https://www.youtube.com/watch?v=7KjedG8rBig) by The Plain Bagel explains it simply."
        ]
    },
    "3": {
        "title": "How to Read a Stock Price: Decoding the Numbers",
        "content": [
            "📚 A stock price reflects what buyers pay for a share, driven by company news, earnings, and market trends. It’s your first clue to a stock’s health.",
            "💡 Real-Life Example (March 28, 2025): Microsoft (MSFT) is at $430. They just launched an AI tool, pushing the price up $10 today. Use /analyze MSFT to see its latest price and trends!",
            "🌍 Key Terms: Look at ‘52-week high/low’ (yearly range) and ‘volume’ (shares traded). High volume on a price jump signals strong interest.",
            "🎮 Try It: Pick a stock like AAPL and run /chart AAPL to see its 30-day price trend. Notice how news affects it!",
            "🎥 Learn More: [How to Read Stock Quotes](https://www.youtube.com/watch?v=0wpxEvR7vC0) by TD Ameritrade breaks down tickers and data."
        ]
    },
    "4": {
        "title": "What Are Dividends? Earning Passive Income",
        "content": [
            "📚 Dividends are cash payments from a company’s profits to shareholders, often paid quarterly. They’re a bonus for holding a stock.",
            "💡 Real-Life Example (March 2025): Coca-Cola (KO) pays $0.48/share quarterly. If you own 50 shares ($3,000 at $60/share), you’d get $24 every 3 months—$96/year—without selling!",
            "🌍 Dividend Stocks Today: In 2025, stable firms like KO or Johnson & Johnson (JNJ) offer 2-3% yields, great for beginners seeking income.",
            "🎮 Try It: Use /simulator buy KO 10 to ‘buy’ Coca-Cola shares and imagine that $4.80 quarterly payout!",
            "🎥 Learn More: [Understanding Dividends](https://www.youtube.com/watch?v=f5j9v9rV6hk) by Khan Academy simplifies this concept."
        ]
    },
    "5": {
        "title": "Buying Your First Stock: A Step-by-Step Guide",
        "content": [
            "📚 Ready to invest? Here’s how: 1) Pick a stock, 2) Check its price and trends, 3) Decide how much to buy, 4) Use a broker app, 5) Track it.",
            "💡 Real-Life Example (March 2025): Let’s buy Starbucks (SBUX). It’s $95/share today after a strong earnings report. You have $200, so you buy 2 shares via Robinhood. Use /analyze SBUX to check its stats!",
            "🌍 2025 Starter Tip: Start small—stocks like Ford (F) at $12 or Etsy (ETSY) at $50 are affordable. Avoid hype stocks (e.g., meme coins) until you’re confident.",
            "🎮 Try It: Simulate your first buy with /simulator buy SBUX 2, then track it with /portfolio!",
            "🎥 Learn More: [How to Buy a Stock](https://www.youtube.com/watch?v=9E4O27a7eD8) by Andrei Jikh walks you through the process."
        ]
    },
    "6": {
        "title": "Your Investing Roadmap: Start Smart in 2025",
        "content": [
            "📚 You’ve learned the basics—now let’s plan! Steps: 1) Set a goal (e.g., $1,000 growth), 2) Budget (start with $100?), 3) Research 3-5 stocks, 4) Diversify, 5) Monitor weekly.",
            "💡 Real-Life Plan (March 2025): With $500, buy 2 shares of Disney (DIS) at $110, 5 shares of Ford (F) at $12, and 1 share of PepsiCo (PEP) at $175. Total: $455. Use /add DIS 2, /add F 5, /add PEP 1 to test this!",
            "🌍 Why Now? In 2025, markets are rebounding—tech is hot (AI boom), and value stocks (e.g., Ford) are steady. Start small, learn fast.",
            "🎮 Next Steps: Build your portfolio with /portfolio, set an alert with /alert DIS 120 above, and chat with /chat 'What’s a good stock for beginners?'",
            "🎥 Learn More: [Investing for Beginners](https://www.youtube.com/watch?v=ULZmntZeetc) by Marko - WhiteBoard Finance ties it all together."
        ]
    }
}

def get_lesson(lesson_num):
    return LESSONS.get(lesson_num, None)