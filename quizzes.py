QUIZZES = {
    "1": {
        "question": "What does owning a stock like Tesla (TSLA) mean?",
        "options": [
            "A: You own a small piece of the company and share in its success",
            "B: You owe Tesla money for their Cybertruck",
            "C: You get free Tesla cars as a perk",
            "D: You control Tesla’s decisions"
        ],
        "answer": "A"
    },
    "2": {
        "question": "Why should you diversify your investments, like splitting money between Nvidia (NVDA) and Walmart (WMT)?",
        "options": [
            "A: To focus all your money on one stock for bigger gains",
            "B: To reduce risk by spreading investments across different sectors",
            "C: To buy only the most expensive stocks",
            "D: To avoid paying taxes on profits"
        ],
        "answer": "B"
    },
    "3": {
        "question": "What can cause Microsoft (MSFT) stock to jump from $430 to $450 in a day?",
        "options": [
            "A: A big AI tool announcement increases demand",
            "B: The CEO’s favorite color changes",
            "C: The number of shareholders doubles overnight",
            "D: It rains in Seattle"
        ],
        "answer": "A"
    },
    "4": {
        "question": "If Coca-Cola (KO) pays a $0.48 quarterly dividend and you own 50 shares, how much do you earn per quarter?",
        "options": [
            "A: $4.80",
            "B: $24.00",
            "C: $48.00",
            "D: $0—dividends aren’t real money"
        ],
        "answer": "B"
    },
    "5": {
        "question": "What’s the first step to buy 2 shares of Starbucks (SBUX) at $95 each?",
        "options": [
            "A: Open a broker app like Robinhood and fund it with $190",
            "B: Call Starbucks HQ for permission",
            "C: Wait for a stock certificate in the mail",
            "D: Ask the bot to buy it with /simulator"
        ],
        "answer": "A"
    },
    "6": {
        "question": "You have $500 to start investing in 2025. Which is a smart beginner plan?",
        "options": [
            "A: Buy 2 Disney (DIS) at $110, 5 Ford (F) at $12, and 1 PepsiCo (PEP) at $175",
            "B: Put all $500 into one hyped AI stock for quick riches",
            "C: Wait until you have $5,000 to start investing",
            "D: Buy stocks with no research to diversify"
        ],
        "answer": "A"
    }
}

def get_quiz(quiz_num):
    return QUIZZES.get(quiz_num, None)