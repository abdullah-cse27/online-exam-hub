# ===================================================
# FILE: ai_features/question_generator.py (UPGRADED)
# ===================================================

import random

# ===================================================
# NORMALIZE SUBJECT
# ===================================================

def normalize_subject(subject):
    return subject.strip().lower()


# ===================================================
# MCQ QUESTION BANK
# ===================================================

MCQ_TEMPLATES = {

    "python": [

        {
            "question": "What is the output of print(2 ** 3)?",
            "options": ["5", "6", "8", "9"],
            "answer": "C",
            "difficulty": "Easy",
            "topic": "operators"
        },

        {
            "question": "Which data type is immutable in Python?",
            "options": ["List", "Dictionary", "Tuple", "Set"],
            "answer": "C",
            "difficulty": "Medium",
            "topic": "data types"
        },

        {
            "question": "Which keyword is used to define a function?",
            "options": ["func", "define", "def", "lambda"],
            "answer": "C",
            "difficulty": "Easy",
            "topic": "functions"
        },

        {
            "question": "Which loop is used when iterations are known?",
            "options": ["while", "for", "do while", "loop"],
            "answer": "B",
            "difficulty": "Medium",
            "topic": "loops"
        }
    ],

    "c": [

        {
            "question": "Which symbol terminates a statement in C?",
            "options": [";", ":", ".", ","],
            "answer": "A",
            "difficulty": "Easy",
            "topic": "syntax"
        },

        {
            "question": "Which function prints output in C?",
            "options": ["print()", "echo()", "printf()", "cout"],
            "answer": "C",
            "difficulty": "Easy",
            "topic": "io"
        },

        {
            "question": "Which data type stores characters in C?",
            "options": ["int", "char", "float", "double"],
            "answer": "B",
            "difficulty": "Medium",
            "topic": "data types"
        }
    ],

    "dsa": [

        {
            "question": "Which data structure follows LIFO?",
            "options": ["Queue", "Stack", "Tree", "Array"],
            "answer": "B",
            "difficulty": "Easy",
            "topic": "stack"
        },

        {
            "question": "Time complexity of binary search?",
            "options": ["O(n)", "O(log n)", "O(n log n)", "O(1)"],
            "answer": "B",
            "difficulty": "Medium",
            "topic": "searching"
        }
    ]
}


# ===================================================
# CODING QUESTION BANK
# ===================================================

CODING_TEMPLATES = {

    "python": [

        {
            "question": "Write a program to print sum of two numbers.",
            "input": "5 6",
            "output": "11",
            "difficulty": "Easy",
            "topic": "basic"
        },

        {
            "question": "Check if number is even.",
            "input": "4",
            "output": "Even",
            "difficulty": "Easy",
            "topic": "conditions"
        }
    ],

    "c": [

        {
            "question": "Write a C program to add two numbers.",
            "input": "5 3",
            "output": "8",
            "difficulty": "Easy",
            "topic": "basic"
        },

        {
            "question": "Check if number is positive.",
            "input": "5",
            "output": "Positive",
            "difficulty": "Easy",
            "topic": "conditions"
        }
    ]
}


# ===================================================
# GENERATE MCQ
# ===================================================

def generate_mcq(subject):

    subject = normalize_subject(subject)

    if subject not in MCQ_TEMPLATES:
        return None

    q = random.choice(MCQ_TEMPLATES[subject])

    return {
        "subject": subject,
        "topic": q["topic"],
        "difficulty": q["difficulty"],
        "question": q["question"],
        "A": q["options"][0],
        "B": q["options"][1],
        "C": q["options"][2],
        "D": q["options"][3],
        "correct": q["answer"]
    }


# ===================================================
# GENERATE CODING QUESTION
# ===================================================

def generate_coding_question(subject):

    subject = normalize_subject(subject)

    if subject not in CODING_TEMPLATES:
        return None

    q = random.choice(CODING_TEMPLATES[subject])

    return {
        "subject": subject,
        "topic": q["topic"],
        "difficulty": q["difficulty"],
        "question": q["question"],
        "sample_input": q["input"],
        "expected_output": q["output"]
    }


# ===================================================
# FORMAT FOR DATABASE
# ===================================================

def format_mcq_for_db(q):
    return f"{q['subject']}|{q['topic']}|{q['difficulty']}|mcq|{q['question']}|{q['A']}|{q['B']}|{q['C']}|{q['D']}|{q['correct']}"


def format_code_for_db(q):
    return f"{q['subject']}|{q['topic']}|{q['difficulty']}|code|{q['question']}|{q['sample_input']}|{q['expected_output']}"


# ===================================================
# GENERATE MULTIPLE QUESTIONS
# ===================================================

def generate_questions(subject, mcq_count=5, coding_count=2):

    subject = normalize_subject(subject)

    questions = []

    for _ in range(mcq_count):
        q = generate_mcq(subject)
        if q:
            questions.append(format_mcq_for_db(q))

    for _ in range(coding_count):
        q = generate_coding_question(subject)
        if q:
            questions.append(format_code_for_db(q))

    random.shuffle(questions)

    return questions