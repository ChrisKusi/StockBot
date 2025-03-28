# StockBot

A Telegram bot designed to help beginners learn about stocks through interactive lessons, quizzes, and tools.

## Features
- **Lessons**: Step-by-step stock market lessons with real-life examples and YouTube links.
- **Quizzes**: Test your knowledge with quizzes tied to lessons.
- **Portfolio**: Track virtual stock holdings (resets on redeploy in free tier).
- **Simulator**: Practice buying/selling stocks with a virtual balance.
- **Analysis**: Get stock snapshots with market sentiment.
- **Charts**: View stock price trends (1W, 1M, 3M).
- **AI Chat**: Ask stock-related questions via Gemini AI.
- **Watchlist**: Monitor favorite stocks.
- **Daily Tips**: Subscribe for daily stock tips.

## Commands
- `/start` - Welcome message and dashboard.
- `/lesson <number>` - Start a lesson (e.g., `/lesson 1`).
- `/quiz <number>` - Take a quiz (e.g., `/quiz 1`).
- `/analyze <symbol>` - Analyze a stock (e.g., `/analyze AAPL`).
- `/add <symbol> <quantity>` - Add to portfolio (e.g., `/add AAPL 5`).
- `/portfolio` - View portfolio.
- `/simulator <buy/sell> <symbol> <quantity>` - Use simulator (e.g., `/simulator buy AAPL 2`).
- `/chat <question>` - Ask AI (e.g., `/chat What’s an ETF?`).
- `/chart <symbol>` - Get stock chart (e.g., `/chart AAPL`).
- Full list: `/help`.

## Deployment on Render
1. **Repository**: Push code to GitHub (`https://github.com/ChrisKusi/grokStockBot`).
2. **Render Setup**:
   - Create a Web Service on [Render](https://render.com).
   - Environment: Python 3.
   - Build Command: `pip install -r requirements.txt && python -m nltk.downloader -d ./nltk_data vader_lexicon`.
   - Start Command: `python main.py`.
   - Add environment variables (see below).
3. **Environment Variables**:

    - TELEGRAM_TOKEN=your_telegram_token
    - GEMINI_API_KEY=your_gemini_key
    - NEWS_API_KEY=your_news_api_key
    - ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
    - ADMIN_TELEGRAM_ID=your_telegram_id
    - PYTHONUNBUFFERED=1

4. **Notes**:
- Free tier: Database resets on redeploy (ephemeral filesystem).
- Polling keeps the bot alive.

## Local Setup
```bash
1. Clone the repo:
    git clone https://github.com/ChrisKusi/grokStockBot.git
    cd grokStockBot

2. Install dependencies:
    pip install -r requirements.txt

3. Create .env:
    TELEGRAM_TOKEN=your_telegram_token
    GEMINI_API_KEY=your_gemini_key
    NEWS_API_KEY=your_news_api_key
    ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
    ADMIN_TELEGRAM_ID=your_telegram_id

4. Run:
    python main.py
```

## Dependencies
    python-telegram-bot: Telegram API.
    python-dotenv: Load .env.
    google-generativeai: Gemini AI.
    yfinance: Stock data.
    requests: API calls.
    nltk: Sentiment analysis.
    matplotlib: Charts.
    forex-python: Currency conversion.
    ratelimit: API rate limiting.
    Files
    main.py: Core bot logic.
    lessons.py: Lesson content.
    quizzes.py: Quiz content.
    portfolio.py: Portfolio management.
    analysis.py: Stock analysis.

## Notes
   **Data Persistence:**  SQLite DB resets on Render free tier redeploy. Use a paid disk or external DB for persistence.

   **API Limits:** Monitor Gemini, Alpha Vantage, and News API usage.

## Author
Christian Kusi (@chriskusi)

**Built with ❤️ for educational purposes, not financial advice.**