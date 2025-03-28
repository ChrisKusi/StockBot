# lessons.py
LESSONS = {
    "1": {
        "title": "What is a Stock?",
        "content": [
            "📚 A stock is a tiny piece of a company you can own. When you buy a stock, you become a shareholder, meaning you have a stake in the company’s success.",
            "💡 Real-Life Example: If you buy 1 Apple (AAPL) stock at $150, you own a small part of Apple. If Apple releases a hit iPhone and the stock rises to $180, your share is now worth more!",
            "🎥 Learn More: Check out this beginner-friendly video: [What Are Stocks?](https://youtu.be/dGBpjtrAIW8?si=tntpkNgTm_1zKx_k) by Bamboo."
        ]
    },
    "2": {
        "title": "Why Diversify?",
        "content": [
            "📚 Diversification means spreading your money across different stocks or industries to lower risk. If one stock drops, others might still do well.",
            "💡 Real-Life Example: Imagine you invest all your $1,000 in a single tech company like Tesla. If electric car sales slump, you could lose a lot. But if you split it between Tesla, Walmart, and a healthcare company, a dip in one might be offset by gains in others.",
            "🎥 Learn More: Watch [Why Diversification Matters](https://www.youtube.com/watch?v=7KjedG8rBig) by The Plain Bagel for a simple explanation."
        ]
    },
    "3": {
        "title": "How to Read a Stock Price",
        "content": [
            "📚 A stock price shows what people are willing to pay for a share right now. It’s influenced by company performance, news, and market trends.",
            "💡 Real-Life Example: On March 27, 2025, let’s say Microsoft (MSFT) is at $420. If they announce a big AI breakthrough, the price might jump to $450 as more people buy.",
            "🎥 Learn More: See [How to Read Stock Quotes](https://www.youtube.com/watch?v=0wpxEvR7vC0) by TD Ameritrade to understand stock tickers and prices."
        ]
    },
    "4": {
        "title": "What Are Dividends?",
        "content": [
            "📚 Dividends are payments companies make to shareholders from their profits, usually quarterly. It’s like a reward for owning the stock.",
            "💡 Real-Life Example: Coca-Cola (KO) might pay $0.46 per share every 3 months. If you own 100 shares, you’d get $46 in cash, even if the stock price doesn’t move!",
            "🎥 Learn More: Watch [Understanding Dividends](https://www.youtube.com/watch?v=f5j9v9rV6hk) by Khan Academy for a clear breakdown."
        ]
    },
    "5": {
        "title": "Buying Your First Stock",
        "content": [
            "📚 Buying a stock means picking a company, deciding how many shares, and using a broker (like Robinhood or Fidelity) to place the order.",
            "💡 Real-Life Example: Want to buy Nike (NKE)? Check its price (say, $100), decide on 5 shares ($500 total), and use an app to buy. Watch it grow as Nike sells more sneakers!",
            "🎥 Learn More: Follow [How to Buy a Stock](https://www.youtube.com/watch?v=9E4O27a7eD8) by Andrei Jikh for a step-by-step guide."
        ]
    }
}

def get_lesson(lesson_num):
    return LESSONS.get(lesson_num, None)