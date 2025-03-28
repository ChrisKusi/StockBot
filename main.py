# import sqlite3
# import yfinance as yf
# import requests
# from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
# from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext, JobQueue
# from lessons import get_lesson
# from quizzes import get_quiz
# from portfolio import add_stock, get_portfolio
# from analysis import analyze_stock
# from dotenv import load_dotenv
# import os
# import google.generativeai as genai
# from ratelimit import limits, sleep_and_retry
# from datetime import datetime, timedelta
# import nltk
# from nltk.sentiment.vader import SentimentIntensityAnalyzer
# import matplotlib.pyplot as plt
# import io
# import logging
# import shutil
# from forex_python.converter import CurrencyRates

# # Download VADER lexicon
# # nltk.download('vader_lexicon')

# # Download VADER lexicon if not already present
# nltk_data_dir = os.path.join(os.getcwd(), "nltk_data")
# if not os.path.exists(nltk_data_dir):
#     nltk.download('vader_lexicon', download_dir=nltk_data_dir)
# nltk.data.path.append(nltk_data_dir)

# # Setup logging
# logging.basicConfig(filename='stockbot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# # Load environment variables
# load_dotenv()
# TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# NEWS_API_KEY = os.getenv("NEWS_API_KEY")
# ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
# ADMIN_TELEGRAM_ID = os.getenv("ADMIN_TELEGRAM_ID")

# # Validate ADMIN_TELEGRAM_ID
# if not ADMIN_TELEGRAM_ID or not ADMIN_TELEGRAM_ID.isdigit():
#     logging.error("Invalid ADMIN_TELEGRAM_ID in .env")
#     raise ValueError("ADMIN_TELEGRAM_ID must be a numeric Telegram user ID")

# # Configure Gemini API
# genai.configure(api_key=GEMINI_API_KEY)
# model = genai.GenerativeModel("gemini-1.5-flash")

# # Database setup
# def init_db():
#     conn = sqlite3.connect("stockbot.db")
#     c = conn.cursor()
#     c.execute('''CREATE TABLE IF NOT EXISTS users 
#                  (user_id INTEGER PRIMARY KEY, lessons_completed TEXT, quiz_scores TEXT, badges TEXT, sim_balance REAL, lang TEXT, watchlist TEXT, subscribed INTEGER DEFAULT 0)''')
#     c.execute('''CREATE TABLE IF NOT EXISTS portfolios 
#                  (user_id INTEGER, symbol TEXT, quantity INTEGER, purchase_price REAL, purchase_date TEXT)''')
#     c.execute('''CREATE TABLE IF NOT EXISTS alerts 
#                  (user_id INTEGER, symbol TEXT, target_price REAL, condition TEXT)''')
#     conn.commit()
#     conn.close()

# # User data management
# def get_user_data(user_id):
#     conn = sqlite3.connect("stockbot.db")
#     c = conn.cursor()
#     c.execute("SELECT lessons_completed, quiz_scores, badges, sim_balance, lang, watchlist, subscribed FROM users WHERE user_id = ?", (user_id,))
#     result = c.fetchone()
#     conn.close()
#     if result:
#         lessons = result[0].split(",") if result[0] else []
#         scores = eval(result[1]) if result[1] else {}
#         badges = result[2].split(",") if result[2] else []
#         balance = result[3] if result[3] is not None else 10000
#         lang = result[4] if result[4] else "en"
#         watchlist = result[5].split(",") if result[5] else []
#         subscribed = bool(result[6])
#         return lessons, scores, badges, balance, lang, watchlist, subscribed
#     return [], {}, [], 10000, "en", [], False

# def update_user_data(user_id, lessons=None, scores=None, badges=None, balance=None, lang=None, watchlist=None, subscribed=None):
#     conn = sqlite3.connect("stockbot.db")
#     c = conn.cursor()
#     current_lessons, current_scores, current_badges, current_balance, current_lang, current_watchlist, current_subscribed = get_user_data(user_id)
#     if lessons is not None:
#         current_lessons = list(set(current_lessons + lessons))
#     if scores is not None:
#         current_scores.update(scores)
#     if badges is not None:
#         current_badges = list(set(current_badges + badges))
#     if balance is not None:
#         current_balance = balance
#     if lang is not None:
#         current_lang = lang
#     if watchlist is not None:
#         current_watchlist = list(set(current_watchlist + watchlist))
#     if subscribed is not None:
#         current_subscribed = subscribed
#     c.execute("INSERT OR REPLACE INTO users (user_id, lessons_completed, quiz_scores, badges, sim_balance, lang, watchlist, subscribed) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
#               (user_id, ",".join(current_lessons), str(current_scores), ",".join(current_badges), current_balance, current_lang, ",".join(current_watchlist), int(current_subscribed)))
#     conn.commit()
#     conn.close()

# # Currency conversion
# def convert_currency(amount, from_currency, to_currency):
#     c = CurrencyRates()
#     try:
#         return c.convert(from_currency, to_currency, amount)
#     except:
#         return amount  # Fallback to USD if conversion fails

# # AI Chat with rate limiting
# CALLS = 5
# RATE_LIMIT = 60

# @sleep_and_retry
# @limits(calls=CALLS, period=RATE_LIMIT)
# def ai_chat(question):
#     try:
#         prompt = (
#             "You are a stock market expert assistant for beginners. "
#             "Provide concise and helpful answers related to stocks and investing. "
#             "If the question is not related to stocks, politely redirect the user to ask stock-related questions.\n\n"
#             f"User: {question}\nAssistant:"
#         )
#         response = model.generate_content(prompt)
#         return f"🤖 Gemini says: {response.text}"
#     except Exception as e:
#         logging.error(f"AI Chat Error: {str(e)}")
#         return f"❌ AI error: {str(e)}. Try again!"

# # Sentiment analysis
# def get_market_mood(symbol):
#     if not NEWS_API_KEY:
#         return "❌ News API key missing."
#     url = f"https://newsapi.org/v2/everything?q={symbol}+stock&apiKey={NEWS_API_KEY}"
#     try:
#         response = requests.get(url)
#         response.raise_for_status()
#     except Exception as e:
#         logging.error(f"News API Error: {str(e)}")
#         return f"❌ Failed to fetch news for {symbol}."
#     articles = response.json().get("articles", [])
#     if not articles:
#         return f"🌍 No recent sentiment data for {symbol}."
    
#     sia = SentimentIntensityAnalyzer()
#     total_compound = 0
#     count = 0
#     for article in articles[:5]:
#         text = article.get("title", "") + " " + article.get("description", "")
#         if text:
#             scores = sia.polarity_scores(text)
#             total_compound += scores["compound"]
#             count += 1
    
#     if count == 0:
#         return f"🌍 No sentiment data available for {symbol}."
#     avg_sentiment = total_compound / count
#     if avg_sentiment > 0.05:
#         return f"🌍 Market Mood for {symbol}: Positive ({avg_sentiment:.2f})"
#     elif avg_sentiment < -0.05:
#         return f"🌍 Market Mood for {symbol}: Negative ({avg_sentiment:.2f})"
#     else:
#         return f"🌍 Market Mood for {symbol}: Neutral ({avg_sentiment:.2f})"

# # Commands
# async def start(update: Update, context: CallbackContext):
#     user_id = update.effective_user.id
#     lang = update.effective_user.language_code if update.effective_user.language_code in ["en", "es", "fr"] else "en"
#     update_user_data(user_id, lang=lang)
#     keyboard = [
#         [InlineKeyboardButton("Lessons", callback_data="dashboard_lessons"),
#          InlineKeyboardButton("Portfolio", callback_data="dashboard_portfolio")],
#         [InlineKeyboardButton("Simulator", callback_data="dashboard_simulator"),
#          InlineKeyboardButton("Community", callback_data="dashboard_community")],
#         [InlineKeyboardButton("Full Menu", callback_data="show_menu")]
#     ]
#     await update.message.reply_text(
#         "🎉 Welcome to Stock Mentor!\nYour ultimate beginner’s guide to stocks.\n"
#         "⚠️ This is for learning—not financial advice.\nExplore below:",
#         reply_markup=InlineKeyboardMarkup(keyboard)
#     )

# async def help_command(update: Update, context: CallbackContext):
#     help_text = (
#         "📈 Welcome to Stock Mentor! Here are the available commands:\n\n"
#         "/start - Start the bot\n"
#         "/lesson <number> - Start a lesson\n"
#         "/quiz <number> - Take a quiz\n"
#         "/analyze <symbol> - Analyze a stock\n"
#         "/add <symbol> <quantity> - Add stocks\n"
#         "/portfolio - View portfolio\n"
#         "/performance - View performance\n"
#         "/simulator <buy/sell> <symbol> <quantity> - Use simulator\n"
#         "/badges - View badges\n"
#         "/rank - Check quiz rank\n"
#         "/chat <question> - Ask AI\n"
#         "/about - About the bot\n"
#         "/news [symbol] - Latest news\n"
#         "/menu - Show menu\n"
#         "/alert <symbol> <price> <above/below> - Set alert\n"
#         "/resources - Educational resources\n"
#         "/chart <symbol> - Get chart\n"
#         "/suggest <message> - Send suggestion\n"
#         "/contact <message> - Contact admin\n"
#         "/watch <symbol> - Add to watchlist\n"
#         "/watchlist - View watchlist\n"
#         "/daily - Market summary\n"
#         "/recommend - Stock suggestions\n"
#         "/leaderboard - Top quiz scores\n"
#         "/portfolio_chart - Portfolio pie chart\n"
#         "/subscribe - Daily tips\n"
#         "/backup - Admin database backup\n\n"
#         "For learning purposes only."
#     )
#     await update.message.reply_text(help_text)

# async def menu(update: Update, context: CallbackContext):
#     keyboard = [
#         [InlineKeyboardButton("Lesson", callback_data="menu_lesson"),
#          InlineKeyboardButton("Quiz", callback_data="menu_quiz")],
#         [InlineKeyboardButton("Analyze", callback_data="menu_analyze"),
#          InlineKeyboardButton("Portfolio", callback_data="menu_portfolio")],
#         [InlineKeyboardButton("Simulator", callback_data="menu_simulator"),
#          InlineKeyboardButton("Chat AI", callback_data="menu_chat")],
#         [InlineKeyboardButton("Badges", callback_data="menu_badges"),
#          InlineKeyboardButton("Rank", callback_data="menu_rank")],
#         [InlineKeyboardButton("About", callback_data="menu_about"),
#          InlineKeyboardButton("News", callback_data="menu_news")],
#         [InlineKeyboardButton("Resources", callback_data="menu_resources"),
#          InlineKeyboardButton("Chart", callback_data="menu_chart")],
#         [InlineKeyboardButton("Suggest", callback_data="menu_suggest"),
#          InlineKeyboardButton("Contact", callback_data="menu_contact")],
#         [InlineKeyboardButton("Watchlist", callback_data="menu_watchlist"),
#          InlineKeyboardButton("Daily", callback_data="menu_daily")],
#         [InlineKeyboardButton("Recommend", callback_data="menu_recommend"),
#          InlineKeyboardButton("Leaderboard", callback_data="menu_leaderboard")],
#         [InlineKeyboardButton("Community", url="https://t.me/+mBySG-U2LuE5OGVk")]
#     ]
#     await update.message.reply_text("📋 Main Menu\nChoose an option:", reply_markup=InlineKeyboardMarkup(keyboard))

# async def menu_callback(update: Update, context: CallbackContext):
#     query = update.callback_query
#     await query.answer()
#     data = query.data
#     if data == "show_menu":
#         keyboard = [
#             [InlineKeyboardButton("Lesson", callback_data="menu_lesson"),
#              InlineKeyboardButton("Quiz", callback_data="menu_quiz")],
#             [InlineKeyboardButton("Analyze", callback_data="menu_analyze"),
#              InlineKeyboardButton("Portfolio", callback_data="menu_portfolio")],
#             [InlineKeyboardButton("Simulator", callback_data="menu_simulator"),
#              InlineKeyboardButton("Chat AI", callback_data="menu_chat")],
#             [InlineKeyboardButton("Badges", callback_data="menu_badges"),
#              InlineKeyboardButton("Rank", callback_data="menu_rank")],
#             [InlineKeyboardButton("About", callback_data="menu_about"),
#              InlineKeyboardButton("News", callback_data="menu_news")],
#             [InlineKeyboardButton("Resources", callback_data="menu_resources"),
#              InlineKeyboardButton("Chart", callback_data="menu_chart")],
#             [InlineKeyboardButton("Suggest", callback_data="menu_suggest"),
#              InlineKeyboardButton("Contact", callback_data="menu_contact")],
#             [InlineKeyboardButton("Watchlist", callback_data="menu_watchlist"),
#              InlineKeyboardButton("Daily", callback_data="menu_daily")],
#             [InlineKeyboardButton("Recommend", callback_data="menu_recommend"),
#              InlineKeyboardButton("Leaderboard", callback_data="menu_leaderboard")],
#             [InlineKeyboardButton("Community", url="https://t.me/+mBySG-U2LuE5OGVk")]
#         ]
#         await query.edit_message_text("📋 Main Menu\nChoose an option:", reply_markup=InlineKeyboardMarkup(keyboard))
#     else:
#         action = data.split("_")[1]
#         responses = {
#             "lesson": "📚 Use /lesson <number>",
#             "quiz": "❓ Use /quiz <number>",
#             "analyze": "🔍 Use /analyze <symbol>",
#             "portfolio": "💼 Use /portfolio",
#             "simulator": "🎮 Use /simulator <buy/sell> <symbol> <quantity>",
#             "chat": "🤖 Use /chat <question>",
#             "badges": "🏅 Use /badges",
#             "rank": "🏆 Use /rank",
#             "about": "ℹ️ Use /about",
#             "news": "📰 Use /news [symbol]",
#             "resources": "📚 Use /resources",
#             "chart": "📈 Use /chart <symbol>",
#             "suggest": "💡 Use /suggest <message>",
#             "contact": "📞 Use /contact <message>",
#             "watchlist": "👀 Use /watchlist",
#             "daily": "📅 Use /daily",
#             "recommend": "⭐ Use /recommend",
#             "leaderboard": "🏅 Use /leaderboard"
#         }
#         await query.edit_message_text(responses.get(action, "❌ Unknown option."))

# async def lesson(update: Update, context: CallbackContext):
#     user_id = update.effective_user.id
#     if not context.args:
#         await update.message.reply_text("⚠️ Pick a lesson, e.g., /lesson 1")
#         return
#     lesson_num = context.args[0]
#     lesson = get_lesson(lesson_num)
#     if not lesson:
#         await update.message.reply_text("❌ Lesson not found.")
#         return
#     keyboard = [[InlineKeyboardButton("Next", callback_data=f"lesson_{lesson_num}_1")]]
#     await update.message.reply_text(f"📚 {lesson['title']}\n{lesson['content'][0]}", reply_markup=InlineKeyboardMarkup(keyboard))

# async def lesson_callback(update: Update, context: CallbackContext):
#     query = update.callback_query
#     await query.answer()
#     data = query.data.split("_")
#     lesson_num, step = data[1], int(data[2])
#     lesson = get_lesson(lesson_num)
#     if not lesson:
#         await query.edit_message_text("❌ Lesson not found.")
#         return
#     if step + 1 < len(lesson["content"]):
#         keyboard = [[InlineKeyboardButton("Next", callback_data=f"lesson_{lesson_num}_{step + 1}")]]
#         await query.edit_message_text(f"📚 {lesson['title']}\n{lesson['content'][step + 1]}", reply_markup=InlineKeyboardMarkup(keyboard))
#     else:
#         update_user_data(query.from_user.id, lessons=[lesson_num], badges=["Stock Rookie"])
#         await query.edit_message_text(f"🎉 Lesson {lesson_num} complete! Try /quiz {lesson_num} or check /badges.")
#         await query.message.reply_poll("Was this lesson helpful?", ["1", "2", "3", "4", "5"], is_anonymous=False)

# async def quiz(update: Update, context: CallbackContext):
#     if not context.args:
#         await update.message.reply_text("⚠️ Pick a quiz, e.g., /quiz 1")
#         return
#     quiz_num = context.args[0]
#     quiz = get_quiz(quiz_num)
#     if not quiz:
#         await update.message.reply_text("❌ Quiz not found.")
#         return
#     options = quiz["options"]
#     keyboard = [[InlineKeyboardButton(option, callback_data=f"quiz_{quiz_num}_{i}")] for i, option in enumerate(options)]
#     await update.message.reply_text(f"❓ {quiz['question']}\nPick an answer:", reply_markup=InlineKeyboardMarkup(keyboard))

# async def quiz_callback(update: Update, context: CallbackContext):
#     query = update.callback_query
#     await query.answer()
#     data = query.data.split("_")
#     quiz_num, choice_idx = data[1], int(data[2])
#     quiz = get_quiz(quiz_num)
#     if not quiz:
#         await query.edit_message_text("❌ Quiz not found.")
#         return
#     correct_answer = quiz["answer"]
#     selected_option = quiz["options"][choice_idx].split(":")[0].strip()
#     if selected_option == correct_answer:
#         update_user_data(query.from_user.id, scores={quiz_num: 10})
#         await query.edit_message_text("✅ Correct! +10 points. Check /rank")
#         await query.message.reply_poll("Was this quiz helpful?", ["1", "2", "3", "4", "5"], is_anonymous=False)
#     else:
#         await query.edit_message_text(f"❌ Nope! The answer was {quiz['options'][ord(correct_answer) - ord('A')]}. Try again!")

# @sleep_and_retry
# @limits(calls=CALLS, period=RATE_LIMIT)
# async def analyze(update: Update, context: CallbackContext):
#     user_id = update.effective_user.id
#     if not context.args:
#         await update.message.reply_text("⚠️ Add a stock, e.g., /analyze AAPL")
#         return
#     symbol = context.args[0].upper()
#     try:
#         data = analyze_stock(symbol)
#         if not data:
#             await update.message.reply_text(f"❌ Couldn’t find {symbol}.")
#             return
#         mood = get_market_mood(symbol)
#         _, _, _, _, lang, _, _ = get_user_data(user_id)
#         currency = "USD" if lang == "en" else "EUR" if lang == "fr" else "GBP" if lang == "es" else "USD"
#         price = convert_currency(data['price'], "USD", currency)
#         sma = convert_currency(data['sma'], "USD", currency)
#         await update.message.reply_text(
#             f"📊 {data['name']} Snapshot:\n"
#             f"💰 Price: {price:.2f} {currency}\n"
#             f"📈 10-Day Avg: {sma:.2f} {currency}\n"
#             f"💸 Dividend: {data['dividend']:.1f}%\n{mood}"
#         )
#     except Exception as e:
#         logging.error(f"Analyze Error: {str(e)}")
#         await update.message.reply_text(f"❌ Error analyzing {symbol}: {str(e)}")

# async def add_stock_command(update: Update, context: CallbackContext):
#     user_id = update.effective_user.id
#     if len(context.args) != 2:
#         await update.message.reply_text("⚠️ Use: /add <symbol> <quantity>, e.g., /add AAPL 5")
#         return
#     try:
#         symbol, qty = context.args[0].upper(), int(context.args[1])
#         stock = yf.Ticker(symbol).info
#         purchase_price = stock.get("regularMarketPrice", 0)
#         if purchase_price == 0:
#             await update.message.reply_text(f"❌ No price data for {symbol}.")
#             return
#         purchase_date = datetime.now().strftime("%Y-%m-%d")
#         add_stock(user_id, symbol, qty, purchase_price, purchase_date)
#         await update.message.reply_text(f"✅ Added {qty} shares of {symbol} at ${purchase_price} on {purchase_date}!")
#     except Exception as e:
#         logging.error(f"Add Stock Error: {str(e)}")
#         await update.message.reply_text(f"❌ Error adding stock: {str(e)}")

# async def portfolio(update: Update, context: CallbackContext):
#     user_id = update.effective_user.id
#     try:
#         holdings, total_value = get_portfolio(user_id)
#         if not holdings:
#             await update.message.reply_text("📉 Your portfolio is empty. Add stocks with /add!")
#             return
#         _, _, _, _, lang, _, _ = get_user_data(user_id)
#         currency = "USD" if lang == "en" else "EUR" if lang == "fr" else "GBP" if lang == "es" else "USD"
#         message = "📊 Your Portfolio:\n"
#         total_converted = convert_currency(total_value, "USD", currency)
#         for symbol, qty, price, value in holdings:
#             converted_price = convert_currency(price, "USD", currency)
#             converted_value = convert_currency(value, "USD", currency)
#             message += f"{symbol}: {qty} shares @ {converted_price:.2f} {currency} = {converted_value:.2f} {currency}\n"
#         message += f"💰 Total Value: {total_converted:.2f} {currency}"
#         await update.message.reply_text(message)
#     except Exception as e:
#         logging.error(f"Portfolio Error: {str(e)}")
#         await update.message.reply_text(f"❌ Error fetching portfolio: {str(e)}")

# async def portfolio_chart(update: Update, context: CallbackContext):
#     user_id = update.effective_user.id
#     try:
#         holdings, total_value = get_portfolio(user_id)
#         if not holdings:
#             await update.message.reply_text("📉 Your portfolio is empty. Use /add!")
#             return
#         labels = [h[0] for h in holdings]
#         sizes = [h[3] for h in holdings]
#         plt.figure(figsize=(8, 8))
#         plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
#         plt.title("Portfolio Allocation")
#         buf = io.BytesIO()
#         plt.savefig(buf, format='png', dpi=100)
#         buf.seek(0)
#         plt.close()
#         await context.bot.send_photo(chat_id=update.effective_chat.id, photo=buf, caption="📊 Your Portfolio Allocation")
#         buf.close()
#     except Exception as e:
#         logging.error(f"Portfolio Chart Error: {str(e)}")
#         await update.message.reply_text(f"❌ Error generating portfolio chart: {str(e)}")

# async def performance(update: Update, context: CallbackContext):
#     user_id = update.effective_user.id
#     try:
#         conn = sqlite3.connect("stockbot.db")
#         c = conn.cursor()
#         c.execute("SELECT symbol, quantity, purchase_price FROM portfolios WHERE user_id = ?", (user_id,))
#         holdings = c.fetchall()
#         conn.close()
#         if not holdings:
#             await update.message.reply_text("📉 Your portfolio is empty. Use /add!")
#             return
#         _, _, _, _, lang, _, _ = get_user_data(user_id)
#         currency = "USD" if lang == "en" else "EUR" if lang == "fr" else "GBP" if lang == "es" else "USD"
#         message = "📊 Portfolio Performance:\n"
#         total_purchase_value = 0
#         total_current_value = 0
#         for symbol, qty, purchase_price in holdings:
#             stock = yf.Ticker(symbol).info
#             current_price = stock.get("regularMarketPrice", 0)
#             purchase_value = purchase_price * qty
#             current_value = current_price * qty
#             total_purchase_value += purchase_value
#             total_current_value += current_value
#             purchase_value_converted = convert_currency(purchase_value, "USD", currency)
#             current_value_converted = convert_currency(current_value, "USD", currency)
#             percentage_change = ((current_value - purchase_value) / purchase_value) * 100 if purchase_value != 0 else 0
#             message += f"{symbol}: {percentage_change:.2f}% (Bought: {purchase_value_converted:.2f} {currency}, Now: {current_value_converted:.2f} {currency})\n"
#         total_return = total_current_value - total_purchase_value
#         total_percentage_change = ((total_current_value - total_purchase_value) / total_purchase_value) * 100 if total_purchase_value != 0 else 0
#         total_return_converted = convert_currency(total_return, "USD", currency)
#         message += f"\n💰 Total Return: {total_return_converted:.2f} {currency} ({total_percentage_change:.2f}%)"
#         await update.message.reply_text(message)
#     except Exception as e:
#         logging.error(f"Performance Error: {str(e)}")
#         await update.message.reply_text(f"❌ Error calculating performance: {str(e)}")

# async def simulator(update: Update, context: CallbackContext):
#     user_id = update.effective_user.id
#     _, _, _, balance, lang, _, _ = get_user_data(user_id)
#     currency = "USD" if lang == "en" else "EUR" if lang == "fr" else "GBP" if lang == "es" else "USD"
#     balance_converted = convert_currency(balance, "USD", currency)
#     if not context.args or context.args[0] not in ["buy", "sell"]:
#         await update.message.reply_text(
#             f"💵 Stock Simulator (Balance: {balance_converted:.2f} {currency})\n"
#             "Use: /simulator <buy/sell> <symbol> <quantity>"
#         )
#         return
#     try:
#         action, symbol, qty = context.args[0], context.args[1].upper(), int(context.args[2])
#         stock = yf.Ticker(symbol).info
#         price = stock.get("regularMarketPrice", 0)
#         if price == 0:
#             await update.message.reply_text(f"❌ No price data for {symbol}.")
#             return
#         cost = price * qty
#         cost_converted = convert_currency(cost, "USD", currency)
#         keyboard = [
#             [InlineKeyboardButton("Yes", callback_data=f"sim_confirm_{action}_{symbol}_{qty}_{cost}"),
#              InlineKeyboardButton("No", callback_data="sim_cancel")]
#         ]
#         await update.message.reply_text(
#             f"Confirm {action}ing {qty} {symbol} for {cost_converted:.2f} {currency}?",
#             reply_markup=InlineKeyboardMarkup(keyboard)
#         )
#     except Exception as e:
#         logging.error(f"Simulator Error: {str(e)}")
#         await update.message.reply_text(f"❌ Error in simulator: {str(e)}")

# async def simulator_callback(update: Update, context: CallbackContext):
#     query = update.callback_query
#     await query.answer()
#     data = query.data.split("_")
#     if len(data) < 2 or data[1] == "cancel":
#         await query.edit_message_text("❌ Transaction cancelled.")
#         return
#     try:
#         action, symbol, qty, cost = data[2], data[3], int(data[4]), float(data[5])
#         user_id = query.from_user.id
#         _, _, _, balance, lang, _, _ = get_user_data(user_id)
#         currency = "USD" if lang == "en" else "EUR" if lang == "fr" else "GBP" if lang == "es" else "USD"
#         cost_converted = convert_currency(cost, "USD", currency)
#         balance_converted = convert_currency(balance, "USD", currency)
#         if action == "buy" and cost <= balance:
#             add_stock(user_id, symbol, qty, cost / qty, datetime.now().strftime("%Y-%m-%d"))
#             update_user_data(user_id, balance=balance - cost)
#             await query.edit_message_text(f"💰 Bought {qty} {symbol} for {cost_converted:.2f} {currency}. New balance: {(balance_converted - cost_converted):.2f} {currency}")
#         elif action == "sell":
#             conn = sqlite3.connect("stockbot.db")
#             c = conn.cursor()
#             c.execute("SELECT symbol, quantity FROM portfolios WHERE user_id = ?", (user_id,))
#             holdings = c.fetchall()
#             for h_symbol, h_qty in holdings:
#                 if h_symbol == symbol and h_qty >= qty:
#                     update_user_data(user_id, balance=balance + cost)
#                     c.execute("UPDATE portfolios SET quantity = quantity - ? WHERE user_id = ? AND symbol = ?", (qty, user_id, symbol))
#                     conn.commit()
#                     conn.close()
#                     await query.edit_message_text(f"💸 Sold {qty} {symbol} for {cost_converted:.2f} {currency}. New balance: {(balance_converted + cost_converted):.2f} {currency}")
#                     return
#             conn.close()
#             await query.edit_message_text("❌ Not enough shares to sell!")
#         else:
#             await query.edit_message_text("❌ Insufficient balance!")
#     except Exception as e:
#         logging.error(f"Simulator Callback Error: {str(e)}")
#         await query.edit_message_text(f"❌ Error processing transaction: {str(e)}")

# async def badges(update: Update, context: CallbackContext):
#     user_id = update.effective_user.id
#     try:
#         _, _, badges, _, _, _, _ = get_user_data(user_id)
#         if not badges:
#             await update.message.reply_text("🏅 No badges yet! Keep learning.")
#             return
#         await update.message.reply_text(f"🏅 Your Badges:\n" + "\n".join(badges))
#     except Exception as e:
#         logging.error(f"Badges Error: {str(e)}")
#         await update.message.reply_text(f"❌ Error fetching badges: {str(e)}")

# async def rank(update: Update, context: CallbackContext):
#     user_id = update.effective_user.id
#     try:
#         _, scores, _, _, _, _, _ = get_user_data(user_id)
#         total = sum(scores.values())
#         if total >= 100 and "Market Guru" not in get_user_data(user_id)[2]:
#             update_user_data(user_id, badges=["Market Guru"])
#         await update.message.reply_text(f"🏆 Your Score: {total} points")
#     except Exception as e:
#         logging.error(f"Rank Error: {str(e)}")
#         await update.message.reply_text(f"❌ Error fetching rank: {str(e)}")

# async def leaderboard(update: Update, context: CallbackContext):
#     try:
#         conn = sqlite3.connect("stockbot.db")
#         c = conn.cursor()
#         c.execute("SELECT user_id, quiz_scores FROM users WHERE quiz_scores IS NOT NULL")
#         users = c.fetchall()
#         conn.close()
#         leaderboard = [(user_id, sum(eval(scores).values())) for user_id, scores in users if scores]
#         leaderboard.sort(key=lambda x: x[1], reverse=True)
#         message = "🏅 Leaderboard (Top 5):\n"
#         for i, (user_id, score) in enumerate(leaderboard[:5], 1):
#             message += f"{i}. User {user_id}: {score} points\n"
#         await update.message.reply_text(message)
#     except Exception as e:
#         logging.error(f"Leaderboard Error: {str(e)}")
#         await update.message.reply_text(f"❌ Error fetching leaderboard: {str(e)}")

# async def chat(update: Update, context: CallbackContext):
#     if not context.args:
#         await update.message.reply_text("⚠️ Ask me anything, e.g., /chat What’s an ETF?")
#         return
#     question = " ".join(context.args)
#     try:
#         response = ai_chat(question)
#         await update.message.reply_text(response)
#     except Exception as e:
#         logging.error(f"Chat Error: {str(e)}")
#         await update.message.reply_text(f"❌ Chat error: {str(e)}. Try again!")

# async def about(update: Update, context: CallbackContext):
#     await update.message.reply_text(
#         "📝 Stock Mentor\n"
#         "Developed by: Christian Kusi\n"
#         "Contact: @chriskusi\n"
#         "Version: 1.0 (Free Testing)\n"
#         "Built with ❤️ to help beginners master stocks!"
#     )

# async def news(update: Update, context: CallbackContext):
#     if not NEWS_API_KEY:
#         await update.message.reply_text("❌ News API key missing.")
#         return
#     try:
#         if context.args:
#             symbol = context.args[0].upper()
#             url = f"https://newsapi.org/v2/everything?q={symbol}+stock+performance&apiKey={NEWS_API_KEY}"
#         else:
#             url = f"https://newsapi.org/v2/top-headlines?category=business&apiKey={NEWS_API_KEY}"
#         response = requests.get(url)
#         response.raise_for_status()
#         articles = response.json().get("articles", [])
#         if not articles:
#             await update.message.reply_text("📰 No news available.")
#             return
#         message = "📰 Latest Stock Market News:\n\n"
#         for article in articles[:5]:
#             message += f"• {article['title']}\n{article['url']}\n\n"
#         await update.message.reply_text(message)
#     except Exception as e:
#         logging.error(f"News Error: {str(e)}")
#         await update.message.reply_text(f"❌ Couldn't fetch news: {str(e)}")

# async def set_alert(update: Update, context: CallbackContext):
#     if len(context.args) != 3 or context.args[2] not in ["above", "below"]:
#         await update.message.reply_text("⚠️ Use: /alert <symbol> <price> <above/below>, e.g., /alert AAPL 150 above")
#         return
#     try:
#         symbol, target_price, condition = context.args[0].upper(), float(context.args[1]), context.args[2]
#         user_id = update.effective_user.id
#         conn = sqlite3.connect("stockbot.db")
#         c = conn.cursor()
#         c.execute("INSERT INTO alerts (user_id, symbol, target_price, condition) VALUES (?, ?, ?, ?)", (user_id, symbol, target_price, condition))
#         conn.commit()
#         conn.close()
#         await update.message.reply_text(f"🔔 Alert set for {symbol} {condition} ${target_price}")
#     except Exception as e:
#         logging.error(f"Set Alert Error: {str(e)}")
#         await update.message.reply_text(f"❌ Error setting alert: {str(e)}")

# async def check_alerts(context: CallbackContext):
#     try:
#         conn = sqlite3.connect("stockbot.db")
#         c = conn.cursor()
#         c.execute("SELECT * FROM alerts")
#         alerts = c.fetchall()
#         for alert in alerts:
#             user_id, symbol, target_price, condition = alert
#             stock = yf.Ticker(symbol)
#             current_price = stock.info.get("regularMarketPrice", 0)
#             if (condition == "above" and current_price >= target_price) or (condition == "below" and current_price <= target_price):
#                 await context.bot.send_message(chat_id=user_id, text=f"🔔 {symbol} is {condition} ${target_price} at ${current_price}!")
#                 c.execute("DELETE FROM alerts WHERE user_id = ? AND symbol = ? AND target_price = ? AND condition = ?", (user_id, symbol, target_price, condition))
#         conn.commit()
#         conn.close()
#     except Exception as e:
#         logging.error(f"Check Alerts Error: {str(e)}")

# async def resources(update: Update, context: CallbackContext):
#     resources = [
#         {"category": "Basics", "title": "Stock Market 101", "url": "https://www.investopedia.com/articles/basics/06/invest1000.asp"},
#         {"category": "Advanced", "title": "Stock Tutorials", "url": "https://finance.yahoo.com/tutorials/"},
#         {"category": "News", "title": "Markets", "url": "https://www.bloomberg.com/markets"}
#     ]
#     message = "📚 Educational Resources:\n\n"
#     for r in resources:
#         message += f"**{r['category']}**: [{r['title']}]({r['url']})\n"
#     await update.message.reply_text(message, parse_mode="Markdown")

# @sleep_and_retry
# @limits(calls=CALLS, period=RATE_LIMIT)
# async def chart(update: Update, context: CallbackContext):
#     user_id = update.effective_user.id
#     if not context.args:
#         await update.message.reply_text("⚠️ Use: /chart <symbol>, e.g., /chart AAPL")
#         return
#     symbol = context.args[0].upper()
#     if not ALPHA_VANTAGE_API_KEY:
#         await update.message.reply_text("❌ Alpha Vantage API key missing.")
#         return
#     try:
#         url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
#         response = requests.get(url)
#         response.raise_for_status()
#         data = response.json().get("Time Series (Daily)", {})
#         if not data:
#             await update.message.reply_text(f"❌ No chart data for {symbol}.")
#             return
#         dates = list(data.keys())[:30][::-1]
#         prices = [float(data[date]["4. close"]) for date in dates]
#         plt.figure(figsize=(10, 5))
#         plt.plot(dates, prices, marker='o', linestyle='-', color='b')
#         plt.title(f"{symbol} Stock Price (Last 30 Days)")
#         plt.xlabel("Date")
#         plt.ylabel("Price (USD)")
#         plt.xticks(rotation=45)
#         plt.tight_layout()
#         buf = io.BytesIO()
#         plt.savefig(buf, format='png', dpi=100)
#         buf.seek(0)
#         plt.close()
#         keyboard = [
#             [InlineKeyboardButton("1W", callback_data=f"chart_{symbol}_7"),
#              InlineKeyboardButton("1M", callback_data=f"chart_{symbol}_30"),
#              InlineKeyboardButton("3M", callback_data=f"chart_{symbol}_90")]
#         ]
#         await context.bot.send_photo(chat_id=update.effective_chat.id, photo=buf, caption=f"📈 {symbol} Chart", reply_markup=InlineKeyboardMarkup(keyboard))
#         buf.close()
#     except Exception as e:
#         logging.error(f"Chart Error: {str(e)}")
#         await update.message.reply_text(f"❌ Error generating chart: {str(e)}")

# async def chart_callback(update: Update, context: CallbackContext):
#     query = update.callback_query
#     await query.answer()
#     data = query.data.split("_")
#     symbol, days = data[1], int(data[2])
#     try:
#         url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
#         response = requests.get(url)
#         response.raise_for_status()
#         data = response.json().get("Time Series (Daily)", {})
#         if not data:
#             await query.edit_message_text(f"❌ No chart data for {symbol}.")
#             return
#         dates = list(data.keys())[:days][::-1]
#         prices = [float(data[date]["4. close"]) for date in dates]
#         plt.figure(figsize=(10, 5))
#         plt.plot(dates, prices, marker='o', linestyle='-', color='b')
#         plt.title(f"{symbol} Stock Price (Last {days} Days)")
#         plt.xlabel("Date")
#         plt.ylabel("Price (USD)")
#         plt.xticks(rotation=45)
#         plt.tight_layout()
#         buf = io.BytesIO()
#         plt.savefig(buf, format='png', dpi=100)
#         buf.seek(0)
#         plt.close()
#         keyboard = [
#             [InlineKeyboardButton("1W", callback_data=f"chart_{symbol}_7"),
#              InlineKeyboardButton("1M", callback_data=f"chart_{symbol}_30"),
#              InlineKeyboardButton("3M", callback_data=f"chart_{symbol}_90")]
#         ]
#         await query.edit_message_media(media=InputFile(buf, filename=f"{symbol}_chart.png"), reply_markup=InlineKeyboardMarkup(keyboard))
#         buf.close()
#     except Exception as e:
#         logging.error(f"Chart Callback Error: {str(e)}")
#         await query.edit_message_text(f"❌ Error updating chart: {str(e)}")

# async def watch(update: Update, context: CallbackContext):
#     user_id = update.effective_user.id
#     if not context.args:
#         await update.message.reply_text("⚠️ Use: /watch <symbol>, e.g., /watch AAPL")
#         return
#     symbol = context.args[0].upper()
#     try:
#         update_user_data(user_id, watchlist=[symbol])
#         await update.message.reply_text(f"👀 Added {symbol} to your watchlist!")
#     except Exception as e:
#         logging.error(f"Watch Error: {str(e)}")
#         await update.message.reply_text(f"❌ Error adding to watchlist: {str(e)}")

# async def watchlist(update: Update, context: CallbackContext):
#     user_id = update.effective_user.id
#     try:
#         _, _, _, _, _, watchlist, _ = get_user_data(user_id)
#         if not watchlist:
#             await update.message.reply_text("👀 Your watchlist is empty. Use /watch <symbol> to add!")
#             return
#         message = "👀 Your Watchlist:\n"
#         for symbol in watchlist:
#             stock = yf.Ticker(symbol).info
#             price = stock.get("regularMarketPrice", 0)
#             message += f"{symbol}: ${price}\n"
#         await update.message.reply_text(message)
#     except Exception as e:
#         logging.error(f"Watchlist Error: {str(e)}")
#         await update.message.reply_text(f"❌ Error fetching watchlist: {str(e)}")

# async def daily(update: Update, context: CallbackContext):
#     try:
#         sp500 = yf.Ticker("^GSPC").info
#         message = "📅 Daily Market Summary:\n"
#         message += f"S&P 500: {sp500.get('regularMarketPrice', 0)}\n"
#         message += "Top Gainers: AAPL (+2%), MSFT (+1.5%)\n"
#         message += "Top Losers: TSLA (-1.8%), NVDA (-1.2%)"
#         await update.message.reply_text(message)
#     except Exception as e:
#         logging.error(f"Daily Error: {str(e)}")
#         await update.message.reply_text(f"❌ Error fetching daily summary: {str(e)}")

# async def recommend(update: Update, context: CallbackContext):
#     try:
#         prompt = "Suggest 3 beginner-friendly stocks with low risk and high growth potential."
#         response = model.generate_content(prompt)
#         await update.message.reply_text(f"⭐ Stock Recommendations:\n{response.text}")
#     except Exception as e:
#         logging.error(f"Recommend Error: {str(e)}")
#         await update.message.reply_text(f"❌ Error generating recommendations: {str(e)}")

# async def subscribe(update: Update, context: CallbackContext):
#     user_id = update.effective_user.id
#     try:
#         update_user_data(user_id, subscribed=True)
#         await update.message.reply_text("✅ Subscribed to daily tips!")
#     except Exception as e:
#         logging.error(f"Subscribe Error: {str(e)}")
#         await update.message.reply_text(f"❌ Error subscribing: {str(e)}")

# async def daily_tip(context: CallbackContext):
#     try:
#         conn = sqlite3.connect("stockbot.db")
#         c = conn.cursor()
#         c.execute("SELECT user_id FROM users WHERE subscribed = 1")
#         users = c.fetchall()
#         conn.close()
#         tip = "💡 Tip: Diversify your portfolio to reduce risk!"
#         for user_id in users:
#             await context.bot.send_message(chat_id=user_id[0], text=tip)
#     except Exception as e:
#         logging.error(f"Daily Tip Error: {str(e)}")

# async def suggest(update: Update, context: CallbackContext):
#     if not context.args:
#         await update.message.reply_text("⚠️ Use: /suggest <message>")
#         return
#     suggestion = " ".join(context.args)
#     user_id = update.effective_user.id
#     try:
#         await context.bot.send_message(chat_id=ADMIN_TELEGRAM_ID, text=f"Suggestion from {user_id}: {suggestion}")
#         await update.message.reply_text("✅ Suggestion sent!")
#     except Exception as e:
#         logging.error(f"Suggest Error: {str(e)}")
#         await update.message.reply_text(f"❌ Error sending suggestion: {str(e)}. Check ADMIN_TELEGRAM_ID in .env.")

# async def contact(update: Update, context: CallbackContext):
#     if not context.args:
#         await update.message.reply_text("⚠️ Use: /contact <message>")
#         return
#     message = " ".join(context.args)
#     user_id = update.effective_user.id
#     try:
#         await context.bot.send_message(chat_id=ADMIN_TELEGRAM_ID, text=f"Support from {user_id}: {message}")
#         await update.message.reply_text("✅ Message sent!")
#     except Exception as e:
#         logging.error(f"Contact Error: {str(e)}")
#         await update.message.reply_text(f"❌ Error sending message: {str(e)}. Check ADMIN_TELEGRAM_ID in .env.")

# async def backup(update: Update, context: CallbackContext):
#     user_id = update.effective_user.id
#     if str(user_id) != ADMIN_TELEGRAM_ID:
#         await update.message.reply_text("❌ Admin only command.")
#         return
#     try:
#         shutil.copy("stockbot.db", f"stockbot_backup_{datetime.now().strftime('%Y%m%d')}.db")
#         await update.message.reply_text("✅ Database backed up!")
#     except Exception as e:
#         logging.error(f"Backup Error: {str(e)}")
#         await update.message.reply_text(f"❌ Error backing up database: {str(e)}")

# async def dashboard_callback(update: Update, context: CallbackContext):
#     query = update.callback_query
#     await query.answer()
#     action = query.data.split("_")[1]
#     if action == "lessons":
#         await query.edit_message_text("📚 Start with /lesson 1")
#     elif action == "portfolio":
#         await portfolio(query, context)
#     elif action == "simulator":
#         await simulator(query, context)
#     elif action == "community":
#         keyboard = [[InlineKeyboardButton("Join Now", url="https://t.me/+mBySG-U2LuE5OGVk")]]
#         await query.edit_message_text("🌟 Join our community!", reply_markup=InlineKeyboardMarkup(keyboard))

# async def error_handler(update: Update, context: CallbackContext):
#     logging.error(f"Error: {context.error}")
#     if update and update.message:
#         await update.message.reply_text("❌ An error occurred. Try again or use /contact to report it.")

# # Main
# def main():
#     init_db()
#     app = Application.builder().token(TELEGRAM_TOKEN).build()
#     app.add_error_handler(error_handler)
#     job_queue = app.job_queue
#     if job_queue:
#         job_queue.run_repeating(check_alerts, interval=60, first=10)
#         job_queue.run_daily(daily_tip, time=datetime.now().time().replace(hour=8, minute=0))

#     app.add_handler(CommandHandler("start", start))
#     app.add_handler(CommandHandler("help", help_command))
#     app.add_handler(CommandHandler("menu", menu))
#     app.add_handler(CommandHandler("lesson", lesson))
#     app.add_handler(CommandHandler("quiz", quiz))
#     app.add_handler(CommandHandler("analyze", analyze))
#     app.add_handler(CommandHandler("add", add_stock_command))
#     app.add_handler(CommandHandler("portfolio", portfolio))
#     app.add_handler(CommandHandler("portfolio_chart", portfolio_chart))
#     app.add_handler(CommandHandler("performance", performance))
#     app.add_handler(CommandHandler("simulator", simulator))
#     app.add_handler(CommandHandler("badges", badges))
#     app.add_handler(CommandHandler("rank", rank))
#     app.add_handler(CommandHandler("leaderboard", leaderboard))
#     app.add_handler(CommandHandler("chat", chat))
#     app.add_handler(CommandHandler("about", about))
#     app.add_handler(CommandHandler("news", news))
#     app.add_handler(CommandHandler("alert", set_alert))
#     app.add_handler(CommandHandler("resources", resources))
#     app.add_handler(CommandHandler("chart", chart))
#     app.add_handler(CommandHandler("watch", watch))
#     app.add_handler(CommandHandler("watchlist", watchlist))
#     app.add_handler(CommandHandler("daily", daily))
#     app.add_handler(CommandHandler("recommend", recommend))
#     app.add_handler(CommandHandler("suggest", suggest))
#     app.add_handler(CommandHandler("contact", contact))
#     app.add_handler(CommandHandler("subscribe", subscribe))
#     app.add_handler(CommandHandler("backup", backup))
#     app.add_handler(CallbackQueryHandler(lesson_callback, pattern="^lesson_"))
#     app.add_handler(CallbackQueryHandler(quiz_callback, pattern="^quiz_"))
#     app.add_handler(CallbackQueryHandler(dashboard_callback, pattern="^dashboard_"))
#     app.add_handler(CallbackQueryHandler(menu_callback, pattern="^menu_|^show_menu$"))
#     app.add_handler(CallbackQueryHandler(simulator_callback, pattern="^sim_"))
#     app.add_handler(CallbackQueryHandler(chart_callback, pattern="^chart_"))

#     app.run_polling()

# if __name__ == "__main__":
#     main()


import sqlite3
import yfinance as yf
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext, JobQueue
from lessons import get_lesson
from quizzes import get_quiz
from portfolio import add_stock, get_portfolio
from analysis import analyze_stock
from dotenv import load_dotenv
import os
import google.generativeai as genai
from ratelimit import limits, sleep_and_retry
from datetime import datetime, timedelta
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
import io
import logging
import shutil
from forex_python.converter import CurrencyRates
from flask import Flask
import threading

# Flask app for Render Web Service
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Stock Mentor Bot is running!"

def run_flask():
    # Bind to port 8080 (Render expects a port; can be changed via PORT env var)
    flask_app.run(host='0.0.0.0', port=int(os.getenv("PORT", 8080)))

# Download VADER lexicon for Render
nltk_data_dir = os.path.join(os.getcwd(), "nltk_data")
if not os.path.exists(nltk_data_dir):
    nltk.download('vader_lexicon', download_dir=nltk_data_dir)
nltk.data.path.append(nltk_data_dir)

# Setup logging
logging.basicConfig(
    filename='stockbot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logging.getLogger().addHandler(logging.StreamHandler())  # Show logs in Render console

# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
ADMIN_TELEGRAM_ID = os.getenv("ADMIN_TELEGRAM_ID")

# Validate environment variables
if not TELEGRAM_TOKEN:
    logging.error("TELEGRAM_TOKEN is missing")
    raise ValueError("TELEGRAM_TOKEN must be set in environment variables")
if not ADMIN_TELEGRAM_ID or not ADMIN_TELEGRAM_ID.isdigit():
    logging.error("Invalid ADMIN_TELEGRAM_ID in environment")
    raise ValueError("ADMIN_TELEGRAM_ID must be a numeric Telegram user ID")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Database setup
def init_db():
    conn = sqlite3.connect("stockbot.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (user_id INTEGER PRIMARY KEY, lessons_completed TEXT, quiz_scores TEXT, badges TEXT, sim_balance REAL, lang TEXT, watchlist TEXT, subscribed INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS portfolios 
                 (user_id INTEGER, symbol TEXT, quantity INTEGER, purchase_price REAL, purchase_date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS alerts 
                 (user_id INTEGER, symbol TEXT, target_price REAL, condition TEXT)''')
    conn.commit()
    conn.close()

# User data management
def get_user_data(user_id):
    conn = sqlite3.connect("stockbot.db")
    c = conn.cursor()
    c.execute("SELECT lessons_completed, quiz_scores, badges, sim_balance, lang, watchlist, subscribed FROM users WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    if result:
        lessons = result[0].split(",") if result[0] else []
        scores = eval(result[1]) if result[1] else {}
        badges = result[2].split(",") if result[2] else []
        balance = result[3] if result[3] is not None else 10000
        lang = result[4] if result[4] else "en"
        watchlist = result[5].split(",") if result[5] else []
        subscribed = bool(result[6])
        return lessons, scores, badges, balance, lang, watchlist, subscribed
    return [], {}, [], 10000, "en", [], False

def update_user_data(user_id, lessons=None, scores=None, badges=None, balance=None, lang=None, watchlist=None, subscribed=None):
    conn = sqlite3.connect("stockbot.db")
    c = conn.cursor()
    current_lessons, current_scores, current_badges, current_balance, current_lang, current_watchlist, current_subscribed = get_user_data(user_id)
    if lessons is not None:
        current_lessons = list(set(current_lessons + lessons))
    if scores is not None:
        current_scores.update(scores)
    if badges is not None:
        current_badges = list(set(current_badges + badges))
    if balance is not None:
        current_balance = balance
    if lang is not None:
        current_lang = lang
    if watchlist is not None:
        current_watchlist = list(set(current_watchlist + watchlist))
    if subscribed is not None:
        current_subscribed = subscribed
    c.execute("INSERT OR REPLACE INTO users (user_id, lessons_completed, quiz_scores, badges, sim_balance, lang, watchlist, subscribed) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              (user_id, ",".join(current_lessons), str(current_scores), ",".join(current_badges), current_balance, current_lang, ",".join(current_watchlist), int(current_subscribed)))
    conn.commit()
    conn.close()

# Currency conversion
def convert_currency(amount, from_currency, to_currency):
    c = CurrencyRates()
    try:
        return c.convert(from_currency, to_currency, amount)
    except:
        return amount  # Fallback to USD if conversion fails

# AI Chat with rate limiting
CALLS = 5
RATE_LIMIT = 60

@sleep_and_retry
@limits(calls=CALLS, period=RATE_LIMIT)
def ai_chat(question):
    try:
        prompt = (
            "You are a stock market expert assistant for beginners. "
            "Provide concise and helpful answers related to stocks and investing. "
            "If the question is not related to stocks, politely redirect the user to ask stock-related questions.\n\n"
            f"User: {question}\nAssistant:"
        )
        response = model.generate_content(prompt)
        return f"🤖 Gemini says: {response.text}"
    except Exception as e:
        logging.error(f"AI Chat Error: {str(e)}")
        return f"❌ AI error: {str(e)}. Try again!"

# Sentiment analysis
def get_market_mood(symbol):
    if not NEWS_API_KEY:
        return "❌ News API key missing."
    url = f"https://newsapi.org/v2/everything?q={symbol}+stock&apiKey={NEWS_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
    except Exception as e:
        logging.error(f"News API Error: {str(e)}")
        return f"❌ Failed to fetch news for {symbol}."
    articles = response.json().get("articles", [])
    if not articles:
        return f"🌍 No recent sentiment data for {symbol}."
    
    sia = SentimentIntensityAnalyzer()
    total_compound = 0
    count = 0
    for article in articles[:5]:
        text = article.get("title", "") + " " + article.get("description", "")
        if text:
            scores = sia.polarity_scores(text)
            total_compound += scores["compound"]
            count += 1
    
    if count == 0:
        return f"🌍 No sentiment data available for {symbol}."
    avg_sentiment = total_compound / count
    if avg_sentiment > 0.05:
        return f"🌍 Market Mood for {symbol}: Positive ({avg_sentiment:.2f})"
    elif avg_sentiment < -0.05:
        return f"🌍 Market Mood for {symbol}: Negative ({avg_sentiment:.2f})"
    else:
        return f"🌍 Market Mood for {symbol}: Neutral ({avg_sentiment:.2f})"

# Commands
async def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    lang = update.effective_user.language_code if update.effective_user.language_code in ["en", "es", "fr"] else "en"
    update_user_data(user_id, lang=lang)
    keyboard = [
        [InlineKeyboardButton("Lessons", callback_data="dashboard_lessons"),
         InlineKeyboardButton("Portfolio", callback_data="dashboard_portfolio")],
        [InlineKeyboardButton("Simulator", callback_data="dashboard_simulator"),
         InlineKeyboardButton("Community", callback_data="dashboard_community")],
        [InlineKeyboardButton("Full Menu", callback_data="show_menu")]
    ]
    await update.message.reply_text(
        "🎉 Welcome to Stock Mentor!\nYour ultimate beginner’s guide to stocks.\n"
        "⚠️ This is for learning—not financial advice.\nExplore below:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def help_command(update: Update, context: CallbackContext):
    help_text = (
        "📈 Welcome to Stock Mentor! Here are the available commands:\n\n"
        "/start - Start the bot\n"
        "/lesson <number> - Start a lesson\n"
        "/quiz <number> - Take a quiz\n"
        "/analyze <symbol> - Analyze a stock\n"
        "/add <symbol> <quantity> - Add stocks\n"
        "/portfolio - View portfolio\n"
        "/performance - View performance\n"
        "/simulator <buy/sell> <symbol> <quantity> - Use simulator\n"
        "/badges - View badges\n"
        "/rank - Check quiz rank\n"
        "/chat <question> - Ask AI\n"
        "/about - About the bot\n"
        "/news [symbol] - Latest news\n"
        "/menu - Show menu\n"
        "/alert <symbol> <price> <above/below> - Set alert\n"
        "/resources - Educational resources\n"
        "/chart <symbol> - Get chart\n"
        "/suggest <message> - Send suggestion\n"
        "/contact <message> - Contact admin\n"
        "/watch <symbol> - Add to watchlist\n"
        "/watchlist - View watchlist\n"
        "/daily - Market summary\n"
        "/recommend - Stock suggestions\n"
        "/leaderboard - Top quiz scores\n"
        "/portfolio_chart - Portfolio pie chart\n"
        "/subscribe - Daily tips\n"
        "/backup - Admin database backup\n\n"
        "For learning purposes only."
    )
    await update.message.reply_text(help_text)

async def menu(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Lesson", callback_data="menu_lesson"),
         InlineKeyboardButton("Quiz", callback_data="menu_quiz")],
        [InlineKeyboardButton("Analyze", callback_data="menu_analyze"),
         InlineKeyboardButton("Portfolio", callback_data="menu_portfolio")],
        [InlineKeyboardButton("Simulator", callback_data="menu_simulator"),
         InlineKeyboardButton("Chat AI", callback_data="menu_chat")],
        [InlineKeyboardButton("Badges", callback_data="menu_badges"),
         InlineKeyboardButton("Rank", callback_data="menu_rank")],
        [InlineKeyboardButton("About", callback_data="menu_about"),
         InlineKeyboardButton("News", callback_data="menu_news")],
        [InlineKeyboardButton("Resources", callback_data="menu_resources"),
         InlineKeyboardButton("Chart", callback_data="menu_chart")],
        [InlineKeyboardButton("Suggest", callback_data="menu_suggest"),
         InlineKeyboardButton("Contact", callback_data="menu_contact")],
        [InlineKeyboardButton("Watchlist", callback_data="menu_watchlist"),
         InlineKeyboardButton("Daily", callback_data="menu_daily")],
        [InlineKeyboardButton("Recommend", callback_data="menu_recommend"),
         InlineKeyboardButton("Leaderboard", callback_data="menu_leaderboard")],
        [InlineKeyboardButton("Community", url="https://t.me/+mBySG-U2LuE5OGVk")]
    ]
    await update.message.reply_text("📋 Main Menu\nChoose an option:", reply_markup=InlineKeyboardMarkup(keyboard))

async def menu_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "show_menu":
        keyboard = [
            [InlineKeyboardButton("Lesson", callback_data="menu_lesson"),
             InlineKeyboardButton("Quiz", callback_data="menu_quiz")],
            [InlineKeyboardButton("Analyze", callback_data="menu_analyze"),
             InlineKeyboardButton("Portfolio", callback_data="menu_portfolio")],
            [InlineKeyboardButton("Simulator", callback_data="menu_simulator"),
             InlineKeyboardButton("Chat AI", callback_data="menu_chat")],
            [InlineKeyboardButton("Badges", callback_data="menu_badges"),
             InlineKeyboardButton("Rank", callback_data="menu_rank")],
            [InlineKeyboardButton("About", callback_data="menu_about"),
             InlineKeyboardButton("News", callback_data="menu_news")],
            [InlineKeyboardButton("Resources", callback_data="menu_resources"),
             InlineKeyboardButton("Chart", callback_data="menu_chart")],
            [InlineKeyboardButton("Suggest", callback_data="menu_suggest"),
             InlineKeyboardButton("Contact", callback_data="menu_contact")],
            [InlineKeyboardButton("Watchlist", callback_data="menu_watchlist"),
             InlineKeyboardButton("Daily", callback_data="menu_daily")],
            [InlineKeyboardButton("Recommend", callback_data="menu_recommend"),
             InlineKeyboardButton("Leaderboard", callback_data="menu_leaderboard")],
            [InlineKeyboardButton("Community", url="https://t.me/+mBySG-U2LuE5OGVk")]
        ]
        await query.edit_message_text("📋 Main Menu\nChoose an option:", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        action = data.split("_")[1]
        responses = {
            "lesson": "📚 Use /lesson <number>",
            "quiz": "❓ Use /quiz <number>",
            "analyze": "🔍 Use /analyze <symbol>",
            "portfolio": "💼 Use /portfolio",
            "simulator": "🎮 Use /simulator <buy/sell> <symbol> <quantity>",
            "chat": "🤖 Use /chat <question>",
            "badges": "🏅 Use /badges",
            "rank": "🏆 Use /rank",
            "about": "ℹ️ Use /about",
            "news": "📰 Use /news [symbol]",
            "resources": "📚 Use /resources",
            "chart": "📈 Use /chart <symbol>",
            "suggest": "💡 Use /suggest <message>",
            "contact": "📞 Use /contact <message>",
            "watchlist": "👀 Use /watchlist",
            "daily": "📅 Use /daily",
            "recommend": "⭐ Use /recommend",
            "leaderboard": "🏅 Use /leaderboard"
        }
        await query.edit_message_text(responses.get(action, "❌ Unknown option."))

async def lesson(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not context.args:
        await update.message.reply_text("⚠️ Pick a lesson, e.g., /lesson 1")
        return
    lesson_num = context.args[0]
    lesson = get_lesson(lesson_num)
    if not lesson:
        await update.message.reply_text("❌ Lesson not found.")
        return
    keyboard = [[InlineKeyboardButton("Next", callback_data=f"lesson_{lesson_num}_1")]]
    await update.message.reply_text(f"📚 {lesson['title']}\n{lesson['content'][0]}", reply_markup=InlineKeyboardMarkup(keyboard))

async def lesson_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    data = query.data.split("_")
    lesson_num, step = data[1], int(data[2])
    lesson = get_lesson(lesson_num)
    if not lesson:
        await query.edit_message_text("❌ Lesson not found.")
        return
    if step + 1 < len(lesson["content"]):
        keyboard = [[InlineKeyboardButton("Next", callback_data=f"lesson_{lesson_num}_{step + 1}")]]
        await query.edit_message_text(f"📚 {lesson['title']}\n{lesson['content'][step + 1]}", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        update_user_data(query.from_user.id, lessons=[lesson_num], badges=["Stock Rookie"])
        await query.edit_message_text(f"🎉 Lesson {lesson_num} complete! Try /quiz {lesson_num} or check /badges.")
        await query.message.reply_poll("Was this lesson helpful?", ["1", "2", "3", "4", "5"], is_anonymous=False)

async def quiz(update: Update, context: CallbackContext):
    if not context.args:
        await update.message.reply_text("⚠️ Pick a quiz, e.g., /quiz 1")
        return
    quiz_num = context.args[0]
    quiz = get_quiz(quiz_num)
    if not quiz:
        await update.message.reply_text("❌ Quiz not found.")
        return
    options = quiz["options"]
    keyboard = [[InlineKeyboardButton(option, callback_data=f"quiz_{quiz_num}_{i}")] for i, option in enumerate(options)]
    await update.message.reply_text(f"❓ {quiz['question']}\nPick an answer:", reply_markup=InlineKeyboardMarkup(keyboard))

async def quiz_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    data = query.data.split("_")
    quiz_num, choice_idx = data[1], int(data[2])
    quiz = get_quiz(quiz_num)
    if not quiz:
        await query.edit_message_text("❌ Quiz not found.")
        return
    correct_answer = quiz["answer"]
    selected_option = quiz["options"][choice_idx].split(":")[0].strip()
    if selected_option == correct_answer:
        update_user_data(query.from_user.id, scores={quiz_num: 10})
        await query.edit_message_text("✅ Correct! +10 points. Check /rank")
        await query.message.reply_poll("Was this quiz helpful?", ["1", "2", "3", "4", "5"], is_anonymous=False)
    else:
        await query.edit_message_text(f"❌ Nope! The answer was {quiz['options'][ord(correct_answer) - ord('A')]}. Try again!")

@sleep_and_retry
@limits(calls=CALLS, period=RATE_LIMIT)
async def analyze(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not context.args:
        await update.message.reply_text("⚠️ Add a stock, e.g., /analyze AAPL")
        return
    symbol = context.args[0].upper()
    try:
        data = analyze_stock(symbol)
        if not data:
            await update.message.reply_text(f"❌ Couldn’t find {symbol}.")
            return
        mood = get_market_mood(symbol)
        _, _, _, _, lang, _, _ = get_user_data(user_id)
        currency = "USD" if lang == "en" else "EUR" if lang == "fr" else "GBP" if lang == "es" else "USD"
        price = convert_currency(data['price'], "USD", currency)
        sma = convert_currency(data['sma'], "USD", currency)
        await update.message.reply_text(
            f"📊 {data['name']} Snapshot:\n"
            f"💰 Price: {price:.2f} {currency}\n"
            f"📈 10-Day Avg: {sma:.2f} {currency}\n"
            f"💸 Dividend: {data['dividend']:.1f}%\n{mood}"
        )
    except Exception as e:
        logging.error(f"Analyze Error: {str(e)}")
        await update.message.reply_text(f"❌ Error analyzing {symbol}: {str(e)}")

async def add_stock_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if len(context.args) != 2:
        await update.message.reply_text("⚠️ Use: /add <symbol> <quantity>, e.g., /add AAPL 5")
        return
    try:
        symbol, qty = context.args[0].upper(), int(context.args[1])
        stock = yf.Ticker(symbol).info
        purchase_price = stock.get("regularMarketPrice", 0)
        if purchase_price == 0:
            await update.message.reply_text(f"❌ No price data for {symbol}.")
            return
        purchase_date = datetime.now().strftime("%Y-%m-%d")
        add_stock(user_id, symbol, qty, purchase_price, purchase_date)
        await update.message.reply_text(f"✅ Added {qty} shares of {symbol} at ${purchase_price} on {purchase_date}!")
    except Exception as e:
        logging.error(f"Add Stock Error: {str(e)}")
        await update.message.reply_text(f"❌ Error adding stock: {str(e)}")

async def portfolio(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    try:
        holdings, total_value = get_portfolio(user_id)
        if not holdings:
            await update.message.reply_text("📉 Your portfolio is empty. Add stocks with /add!")
            return
        _, _, _, _, lang, _, _ = get_user_data(user_id)
        currency = "USD" if lang == "en" else "EUR" if lang == "fr" else "GBP" if lang == "es" else "USD"
        message = "📊 Your Portfolio:\n"
        total_converted = convert_currency(total_value, "USD", currency)
        for symbol, qty, price, value in holdings:
            converted_price = convert_currency(price, "USD", currency)
            converted_value = convert_currency(value, "USD", currency)
            message += f"{symbol}: {qty} shares @ {converted_price:.2f} {currency} = {converted_value:.2f} {currency}\n"
        message += f"💰 Total Value: {total_converted:.2f} {currency}"
        await update.message.reply_text(message)
    except Exception as e:
        logging.error(f"Portfolio Error: {str(e)}")
        await update.message.reply_text(f"❌ Error fetching portfolio: {str(e)}")

async def portfolio_chart(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    try:
        holdings, total_value = get_portfolio(user_id)
        if not holdings:
            await update.message.reply_text("📉 Your portfolio is empty. Use /add!")
            return
        labels = [h[0] for h in holdings]
        sizes = [h[3] for h in holdings]
        plt.figure(figsize=(8, 8))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
        plt.title("Portfolio Allocation")
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close()
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=buf, caption="📊 Your Portfolio Allocation")
        buf.close()
    except Exception as e:
        logging.error(f"Portfolio Chart Error: {str(e)}")
        await update.message.reply_text(f"❌ Error generating portfolio chart: {str(e)}")

async def performance(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    try:
        conn = sqlite3.connect("stockbot.db")
        c = conn.cursor()
        c.execute("SELECT symbol, quantity, purchase_price FROM portfolios WHERE user_id = ?", (user_id,))
        holdings = c.fetchall()
        conn.close()
        if not holdings:
            await update.message.reply_text("📉 Your portfolio is empty. Use /add!")
            return
        _, _, _, _, lang, _, _ = get_user_data(user_id)
        currency = "USD" if lang == "en" else "EUR" if lang == "fr" else "GBP" if lang == "es" else "USD"
        message = "📊 Portfolio Performance:\n"
        total_purchase_value = 0
        total_current_value = 0
        for symbol, qty, purchase_price in holdings:
            stock = yf.Ticker(symbol).info
            current_price = stock.get("regularMarketPrice", 0)
            purchase_value = purchase_price * qty
            current_value = current_price * qty
            total_purchase_value += purchase_value
            total_current_value += current_value
            purchase_value_converted = convert_currency(purchase_value, "USD", currency)
            current_value_converted = convert_currency(current_value, "USD", currency)
            percentage_change = ((current_value - purchase_value) / purchase_value) * 100 if purchase_value != 0 else 0
            message += f"{symbol}: {percentage_change:.2f}% (Bought: {purchase_value_converted:.2f} {currency}, Now: {current_value_converted:.2f} {currency})\n"
        total_return = total_current_value - total_purchase_value
        total_percentage_change = ((total_current_value - total_purchase_value) / total_purchase_value) * 100 if total_purchase_value != 0 else 0
        total_return_converted = convert_currency(total_return, "USD", currency)
        message += f"\n💰 Total Return: {total_return_converted:.2f} {currency} ({total_percentage_change:.2f}%)"
        await update.message.reply_text(message)
    except Exception as e:
        logging.error(f"Performance Error: {str(e)}")
        await update.message.reply_text(f"❌ Error calculating performance: {str(e)}")

async def simulator(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    _, _, _, balance, lang, _, _ = get_user_data(user_id)
    currency = "USD" if lang == "en" else "EUR" if lang == "fr" else "GBP" if lang == "es" else "USD"
    balance_converted = convert_currency(balance, "USD", currency)
    if not context.args or context.args[0] not in ["buy", "sell"]:
        await update.message.reply_text(
            f"💵 Stock Simulator (Balance: {balance_converted:.2f} {currency})\n"
            "Use: /simulator <buy/sell> <symbol> <quantity>"
        )
        return
    try:
        action, symbol, qty = context.args[0], context.args[1].upper(), int(context.args[2])
        stock = yf.Ticker(symbol).info
        price = stock.get("regularMarketPrice", 0)
        if price == 0:
            await update.message.reply_text(f"❌ No price data for {symbol}.")
            return
        cost = price * qty
        cost_converted = convert_currency(cost, "USD", currency)
        keyboard = [
            [InlineKeyboardButton("Yes", callback_data=f"sim_confirm_{action}_{symbol}_{qty}_{cost}"),
             InlineKeyboardButton("No", callback_data="sim_cancel")]
        ]
        await update.message.reply_text(
            f"Confirm {action}ing {qty} {symbol} for {cost_converted:.2f} {currency}?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        logging.error(f"Simulator Error: {str(e)}")
        await update.message.reply_text(f"❌ Error in simulator: {str(e)}")

async def simulator_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    data = query.data.split("_")
    if len(data) < 2 or data[1] == "cancel":
        await query.edit_message_text("❌ Transaction cancelled.")
        return
    try:
        action, symbol, qty, cost = data[2], data[3], int(data[4]), float(data[5])
        user_id = query.from_user.id
        _, _, _, balance, lang, _, _ = get_user_data(user_id)
        currency = "USD" if lang == "en" else "EUR" if lang == "fr" else "GBP" if lang == "es" else "USD"
        cost_converted = convert_currency(cost, "USD", currency)
        balance_converted = convert_currency(balance, "USD", currency)
        if action == "buy" and cost <= balance:
            add_stock(user_id, symbol, qty, cost / qty, datetime.now().strftime("%Y-%m-%d"))
            update_user_data(user_id, balance=balance - cost)
            await query.edit_message_text(f"💰 Bought {qty} {symbol} for {cost_converted:.2f} {currency}. New balance: {(balance_converted - cost_converted):.2f} {currency}")
        elif action == "sell":
            conn = sqlite3.connect("stockbot.db")
            c = conn.cursor()
            c.execute("SELECT symbol, quantity FROM portfolios WHERE user_id = ?", (user_id,))
            holdings = c.fetchall()
            for h_symbol, h_qty in holdings:
                if h_symbol == symbol and h_qty >= qty:
                    update_user_data(user_id, balance=balance + cost)
                    c.execute("UPDATE portfolios SET quantity = quantity - ? WHERE user_id = ? AND symbol = ?", (qty, user_id, symbol))
                    conn.commit()
                    conn.close()
                    await query.edit_message_text(f"💸 Sold {qty} {symbol} for {cost_converted:.2f} {currency}. New balance: {(balance_converted + cost_converted):.2f} {currency}")
                    return
            conn.close()
            await query.edit_message_text("❌ Not enough shares to sell!")
        else:
            await query.edit_message_text("❌ Insufficient balance!")
    except Exception as e:
        logging.error(f"Simulator Callback Error: {str(e)}")
        await query.edit_message_text(f"❌ Error processing transaction: {str(e)}")

async def badges(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    try:
        _, _, badges, _, _, _, _ = get_user_data(user_id)
        if not badges:
            await update.message.reply_text("🏅 No badges yet! Keep learning.")
            return
        await update.message.reply_text(f"🏅 Your Badges:\n" + "\n".join(badges))
    except Exception as e:
        logging.error(f"Badges Error: {str(e)}")
        await update.message.reply_text(f"❌ Error fetching badges: {str(e)}")

async def rank(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    try:
        _, scores, _, _, _, _, _ = get_user_data(user_id)
        total = sum(scores.values())
        if total >= 100 and "Market Guru" not in get_user_data(user_id)[2]:
            update_user_data(user_id, badges=["Market Guru"])
        await update.message.reply_text(f"🏆 Your Score: {total} points")
    except Exception as e:
        logging.error(f"Rank Error: {str(e)}")
        await update.message.reply_text(f"❌ Error fetching rank: {str(e)}")

async def leaderboard(update: Update, context: CallbackContext):
    try:
        conn = sqlite3.connect("stockbot.db")
        c = conn.cursor()
        c.execute("SELECT user_id, quiz_scores FROM users WHERE quiz_scores IS NOT NULL")
        users = c.fetchall()
        conn.close()
        leaderboard = [(user_id, sum(eval(scores).values())) for user_id, scores in users if scores]
        leaderboard.sort(key=lambda x: x[1], reverse=True)
        message = "🏅 Leaderboard (Top 5):\n"
        for i, (user_id, score) in enumerate(leaderboard[:5], 1):
            message += f"{i}. User {user_id}: {score} points\n"
        await update.message.reply_text(message)
    except Exception as e:
        logging.error(f"Leaderboard Error: {str(e)}")
        await update.message.reply_text(f"❌ Error fetching leaderboard: {str(e)}")

async def chat(update: Update, context: CallbackContext):
    if not context.args:
        await update.message.reply_text("⚠️ Ask me anything, e.g., /chat What’s an ETF?")
        return
    question = " ".join(context.args)
    try:
        response = ai_chat(question)
        await update.message.reply_text(response)
    except Exception as e:
        logging.error(f"Chat Error: {str(e)}")
        await update.message.reply_text(f"❌ Chat error: {str(e)}. Try again!")

async def about(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "📝 Stock Mentor\n"
        "Developed by: Christian Kusi\n"
        "Contact: @chriskusi\n"
        "Version: 1.0 (Free Testing)\n"
        "Built with ❤️ to help beginners master stocks!"
    )

async def news(update: Update, context: CallbackContext):
    if not NEWS_API_KEY:
        await update.message.reply_text("❌ News API key missing.")
        return
    try:
        if context.args:
            symbol = context.args[0].upper()
            url = f"https://newsapi.org/v2/everything?q={symbol}+stock+performance&apiKey={NEWS_API_KEY}"
        else:
            url = f"https://newsapi.org/v2/top-headlines?category=business&apiKey={NEWS_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        articles = response.json().get("articles", [])
        if not articles:
            await update.message.reply_text("📰 No news available.")
            return
        message = "📰 Latest Stock Market News:\n\n"
        for article in articles[:5]:
            message += f"• {article['title']}\n{article['url']}\n\n"
        await update.message.reply_text(message)
    except Exception as e:
        logging.error(f"News Error: {str(e)}")
        await update.message.reply_text(f"❌ Couldn't fetch news: {str(e)}")

async def set_alert(update: Update, context: CallbackContext):
    if len(context.args) != 3 or context.args[2] not in ["above", "below"]:
        await update.message.reply_text("⚠️ Use: /alert <symbol> <price> <above/below>, e.g., /alert AAPL 150 above")
        return
    try:
        symbol, target_price, condition = context.args[0].upper(), float(context.args[1]), context.args[2]
        user_id = update.effective_user.id
        conn = sqlite3.connect("stockbot.db")
        c = conn.cursor()
        c.execute("INSERT INTO alerts (user_id, symbol, target_price, condition) VALUES (?, ?, ?, ?)", (user_id, symbol, target_price, condition))
        conn.commit()
        conn.close()
        await update.message.reply_text(f"🔔 Alert set for {symbol} {condition} ${target_price}")
    except Exception as e:
        logging.error(f"Set Alert Error: {str(e)}")
        await update.message.reply_text(f"❌ Error setting alert: {str(e)}")

async def check_alerts(context: CallbackContext):
    try:
        conn = sqlite3.connect("stockbot.db")
        c = conn.cursor()
        c.execute("SELECT * FROM alerts")
        alerts = c.fetchall()
        for alert in alerts:
            user_id, symbol, target_price, condition = alert
            stock = yf.Ticker(symbol)
            current_price = stock.info.get("regularMarketPrice", 0)
            if (condition == "above" and current_price >= target_price) or (condition == "below" and current_price <= target_price):
                await context.bot.send_message(chat_id=user_id, text=f"🔔 {symbol} is {condition} ${target_price} at ${current_price}!")
                c.execute("DELETE FROM alerts WHERE user_id = ? AND symbol = ? AND target_price = ? AND condition = ?", (user_id, symbol, target_price, condition))
        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"Check Alerts Error: {str(e)}")

async def resources(update: Update, context: CallbackContext):
    resources = [
        {"category": "Basics", "title": "Stock Market 101", "url": "https://www.investopedia.com/articles/basics/06/invest1000.asp"},
        {"category": "Advanced", "title": "Stock Tutorials", "url": "https://finance.yahoo.com/tutorials/"},
        {"category": "News", "title": "Markets", "url": "https://www.bloomberg.com/markets"}
    ]
    message = "📚 Educational Resources:\n\n"
    for r in resources:
        message += f"**{r['category']}**: [{r['title']}]({r['url']})\n"
    await update.message.reply_text(message, parse_mode="Markdown")

@sleep_and_retry
@limits(calls=CALLS, period=RATE_LIMIT)
async def chart(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not context.args:
        await update.message.reply_text("⚠️ Use: /chart <symbol>, e.g., /chart AAPL")
        return
    symbol = context.args[0].upper()
    if not ALPHA_VANTAGE_API_KEY:
        await update.message.reply_text("❌ Alpha Vantage API key missing.")
        return
    try:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json().get("Time Series (Daily)", {})
        if not data:
            await update.message.reply_text(f"❌ No chart data for {symbol}.")
            return
        dates = list(data.keys())[:30][::-1]
        prices = [float(data[date]["4. close"]) for date in dates]
        plt.figure(figsize=(10, 5))
        plt.plot(dates, prices, marker='o', linestyle='-', color='b')
        plt.title(f"{symbol} Stock Price (Last 30 Days)")
        plt.xlabel("Date")
        plt.ylabel("Price (USD)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close()
        keyboard = [
            [InlineKeyboardButton("1W", callback_data=f"chart_{symbol}_7"),
             InlineKeyboardButton("1M", callback_data=f"chart_{symbol}_30"),
             InlineKeyboardButton("3M", callback_data=f"chart_{symbol}_90")]
        ]
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=buf, caption=f"📈 {symbol} Chart", reply_markup=InlineKeyboardMarkup(keyboard))
        buf.close()
    except Exception as e:
        logging.error(f"Chart Error: {str(e)}")
        await update.message.reply_text(f"❌ Error generating chart: {str(e)}")

async def chart_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    data = query.data.split("_")
    symbol, days = data[1], int(data[2])
    try:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json().get("Time Series (Daily)", {})
        if not data:
            await query.edit_message_text(f"❌ No chart data for {symbol}.")
            return
        dates = list(data.keys())[:days][::-1]
        prices = [float(data[date]["4. close"]) for date in dates]
        plt.figure(figsize=(10, 5))
        plt.plot(dates, prices, marker='o', linestyle='-', color='b')
        plt.title(f"{symbol} Stock Price (Last {days} Days)")
        plt.xlabel("Date")
        plt.ylabel("Price (USD)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close()
        keyboard = [
            [InlineKeyboardButton("1W", callback_data=f"chart_{symbol}_7"),
             InlineKeyboardButton("1M", callback_data=f"chart_{symbol}_30"),
             InlineKeyboardButton("3M", callback_data=f"chart_{symbol}_90")]
        ]
        await query.edit_message_media(media=InputFile(buf, filename=f"{symbol}_chart.png"), reply_markup=InlineKeyboardMarkup(keyboard))
        buf.close()
    except Exception as e:
        logging.error(f"Chart Callback Error: {str(e)}")
        await query.edit_message_text(f"❌ Error updating chart: {str(e)}")

async def watch(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not context.args:
        await update.message.reply_text("⚠️ Use: /watch <symbol>, e.g., /watch AAPL")
        return
    symbol = context.args[0].upper()
    try:
        update_user_data(user_id, watchlist=[symbol])
        await update.message.reply_text(f"👀 Added {symbol} to your watchlist!")
    except Exception as e:
        logging.error(f"Watch Error: {str(e)}")
        await update.message.reply_text(f"❌ Error adding to watchlist: {str(e)}")

async def watchlist(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    try:
        _, _, _, _, _, watchlist, _ = get_user_data(user_id)
        if not watchlist:
            await update.message.reply_text("👀 Your watchlist is empty. Use /watch <symbol> to add!")
            return
        message = "👀 Your Watchlist:\n"
        for symbol in watchlist:
            stock = yf.Ticker(symbol).info
            price = stock.get("regularMarketPrice", 0)
            message += f"{symbol}: ${price}\n"
        await update.message.reply_text(message)
    except Exception as e:
        logging.error(f"Watchlist Error: {str(e)}")
        await update.message.reply_text(f"❌ Error fetching watchlist: {str(e)}")

async def daily(update: Update, context: CallbackContext):
    try:
        sp500 = yf.Ticker("^GSPC").info
        message = "📅 Daily Market Summary:\n"
        message += f"S&P 500: {sp500.get('regularMarketPrice', 0)}\n"
        message += "Top Gainers: AAPL (+2%), MSFT (+1.5%)\n"
        message += "Top Losers: TSLA (-1.8%), NVDA (-1.2%)"
        await update.message.reply_text(message)
    except Exception as e:
        logging.error(f"Daily Error: {str(e)}")
        await update.message.reply_text(f"❌ Error fetching daily summary: {str(e)}")

async def recommend(update: Update, context: CallbackContext):
    try:
        prompt = "Suggest 3 beginner-friendly stocks with low risk and high growth potential."
        response = model.generate_content(prompt)
        await update.message.reply_text(f"⭐ Stock Recommendations:\n{response.text}")
    except Exception as e:
        logging.error(f"Recommend Error: {str(e)}")
        await update.message.reply_text(f"❌ Error generating recommendations: {str(e)}")

async def subscribe(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    try:
        update_user_data(user_id, subscribed=True)
        await update.message.reply_text("✅ Subscribed to daily tips!")
    except Exception as e:
        logging.error(f"Subscribe Error: {str(e)}")
        await update.message.reply_text(f"❌ Error subscribing: {str(e)}")

async def daily_tip(context: CallbackContext):
    try:
        conn = sqlite3.connect("stockbot.db")
        c = conn.cursor()
        c.execute("SELECT user_id FROM users WHERE subscribed = 1")
        users = c.fetchall()
        conn.close()
        tip = "💡 Tip: Diversify your portfolio to reduce risk!"
        for user_id in users:
            await context.bot.send_message(chat_id=user_id[0], text=tip)
    except Exception as e:
        logging.error(f"Daily Tip Error: {str(e)}")

async def suggest(update: Update, context: CallbackContext):
    if not context.args:
        await update.message.reply_text("⚠️ Use: /suggest <message>")
        return
    suggestion = " ".join(context.args)
    user_id = update.effective_user.id
    try:
        await context.bot.send_message(chat_id=ADMIN_TELEGRAM_ID, text=f"Suggestion from {user_id}: {suggestion}")
        await update.message.reply_text("✅ Suggestion sent!")
    except Exception as e:
        logging.error(f"Suggest Error: {str(e)}")
        await update.message.reply_text(f"❌ Error sending suggestion: {str(e)}. Check ADMIN_TELEGRAM_ID in .env.")

async def contact(update: Update, context: CallbackContext):
    if not context.args:
        await update.message.reply_text("⚠️ Use: /contact <message>")
        return
    message = " ".join(context.args)
    user_id = update.effective_user.id
    try:
        await context.bot.send_message(chat_id=ADMIN_TELEGRAM_ID, text=f"Support from {user_id}: {message}")
        await update.message.reply_text("✅ Message sent!")
    except Exception as e:
        logging.error(f"Contact Error: {str(e)}")
        await update.message.reply_text(f"❌ Error sending message: {str(e)}. Check ADMIN_TELEGRAM_ID in .env.")

async def backup(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if str(user_id) != ADMIN_TELEGRAM_ID:
        await update.message.reply_text("❌ Admin only command.")
        return
    try:
        shutil.copy("stockbot.db", f"stockbot_backup_{datetime.now().strftime('%Y%m%d')}.db")
        await update.message.reply_text("✅ Database backed up!")
    except Exception as e:
        logging.error(f"Backup Error: {str(e)}")
        await update.message.reply_text(f"❌ Error backing up database: {str(e)}")

async def dashboard_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    action = query.data.split("_")[1]
    if action == "lessons":
        await query.edit_message_text("📚 Start with /lesson 1")
    elif action == "portfolio":
        await portfolio(query, context)
    elif action == "simulator":
        await simulator(query, context)
    elif action == "community":
        keyboard = [[InlineKeyboardButton("Join Now", url="https://t.me/+mBySG-U2LuE5OGVk")]]
        await query.edit_message_text("🌟 Join our community!", reply_markup=InlineKeyboardMarkup(keyboard))

async def error_handler(update: Update, context: CallbackContext):
    logging.error(f"Error: {context.error}")
    if update and update.message:
        await update.message.reply_text("❌ An error occurred. Try again or use /contact to report it.")

# Main
def main():
    init_db()
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_error_handler(error_handler)
    job_queue = app.job_queue
    if job_queue:
        job_queue.run_repeating(check_alerts, interval=60, first=10)
        job_queue.run_daily(daily_tip, time=datetime.now().time().replace(hour=8, minute=0))

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("lesson", lesson))
    app.add_handler(CommandHandler("quiz", quiz))
    app.add_handler(CommandHandler("analyze", analyze))
    app.add_handler(CommandHandler("add", add_stock_command))
    app.add_handler(CommandHandler("portfolio", portfolio))
    app.add_handler(CommandHandler("portfolio_chart", portfolio_chart))
    app.add_handler(CommandHandler("performance", performance))
    app.add_handler(CommandHandler("simulator", simulator))
    app.add_handler(CommandHandler("badges", badges))
    app.add_handler(CommandHandler("rank", rank))
    app.add_handler(CommandHandler("leaderboard", leaderboard))
    app.add_handler(CommandHandler("chat", chat))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("news", news))
    app.add_handler(CommandHandler("alert", set_alert))
    app.add_handler(CommandHandler("resources", resources))
    app.add_handler(CommandHandler("chart", chart))
    app.add_handler(CommandHandler("watch", watch))
    app.add_handler(CommandHandler("watchlist", watchlist))
    app.add_handler(CommandHandler("daily", daily))
    app.add_handler(CommandHandler("recommend", recommend))
    app.add_handler(CommandHandler("suggest", suggest))
    app.add_handler(CommandHandler("contact", contact))
    app.add_handler(CommandHandler("subscribe", subscribe))
    app.add_handler(CommandHandler("backup", backup))
    app.add_handler(CallbackQueryHandler(lesson_callback, pattern="^lesson_"))
    app.add_handler(CallbackQueryHandler(quiz_callback, pattern="^quiz_"))
    app.add_handler(CallbackQueryHandler(dashboard_callback, pattern="^dashboard_"))
    app.add_handler(CallbackQueryHandler(menu_callback, pattern="^menu_|^show_menu$"))
    app.add_handler(CallbackQueryHandler(simulator_callback, pattern="^sim_"))
    app.add_handler(CallbackQueryHandler(chart_callback, pattern="^chart_"))

    # Start Flask in a separate thread
    threading.Thread(target=run_flask, daemon=True).start()
    # Start Telegram bot polling
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()