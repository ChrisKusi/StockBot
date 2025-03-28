# quizzes.py
QUIZZES = {
    "1": {
        "question": "What does owning a stock mean?",
        "options": [
            "A: You own part of a company",
            "B: You owe the company money",
            "C: You get free products"
        ],
        "answer": "A"
    },
    "2": {
        "question": "Why should you diversify your investments?",
        "options": [
            "A: To put all your money in one stock",
            "B: To lower risk by spreading your money",
            "C: To buy more expensive stocks"
        ],
        "answer": "B"
    },
    "3": {
        "question": "What affects a stock’s price?",
        "options": [
            "A: Company performance and news",
            "B: The weather",
            "C: How many shares you own"
        ],
        "answer": "A"
    },
    "4": {
        "question": "What is a dividend?",
        "options": [
            "A: A loan you give the company",
            "B: A payment from company profits",
            "C: A fee for owning stock"
        ],
        "answer": "B"
    },
    "5": {
        "question": "What do you need to buy a stock?",
        "options": [
            "A: A broker and money",
            "B: A company’s permission",
            "C: A stock certificate in the mail"
        ],
        "answer": "A"
    }
}

def get_quiz(quiz_num):
    return QUIZZES.get(quiz_num, None)