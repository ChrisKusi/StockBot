QUIZZES = {
    "1": {
        "question": "What does owning a stock like Tesla (TSLA) mean?",
        "options": [
            "A: You own a small piece and share in its success",
            "B: You owe Tesla money for their Cybertruck",
            "C: You get free Tesla cars as a perk",
            "D: You control Tesla’s decisions"
        ],
        "answer": "A"
    },
    "2": {
        "question": "Why diversify, like splitting Nvidia and Walmart?",
        "options": [
            "A: To focus all money on one stock for big gains",
            "B: To reduce risk by spreading across sectors",
            "C: To buy only the most expensive stocks",
            "D: To avoid paying taxes on profits"
        ],
        "answer": "B"
    },
    "3": {
        "question": "What can make Microsoft (MSFT) jump $430 to $450?",
        "options": [
            "A: A big AI tool announcement increases demand",
            "B: The CEO’s favorite color changes",
            "C: Shareholders double overnight",
            "D: It rains in Seattle"
        ],
        "answer": "A"
    },
    "4": {
        "question": "Coca-Cola (KO) pays $0.48 dividend, 50 shares earns?",
        "options": [
            "A: $4.80",
            "B: $24.00",
            "C: $48.00",
            "D: $0—dividends aren’t real money"
        ],
        "answer": "B"
    },
    "5": {
        "question": "First step to buy 2 Starbucks (SBUX) at $95 each?",
        "options": [
            "A: Open a broker app like Robinhood with $190",
            "B: Call Starbucks HQ for permission",
            "C: Wait for a stock certificate in the mail",
            "D: Use /simulator to buy it in the bot"
        ],
        "answer": "A"
    },
    "6": {
        "question": "Smart $500 beginner plan for 2025?",
        "options": [
            "A: 2 Disney ($110), 5 Ford ($12), 1 PepsiCo ($175)",
            "B: All $500 in one hyped AI stock for quick riches",
            "C: Wait until you have $5,000 to invest",
            "D: Buy random stocks with no research"
        ],
        "answer": "A"
    }
}

def get_quiz(quiz_num):
    return QUIZZES.get(quiz_num, None)