import hashlib
import os
import time

# ============================
# FILE PATHS
# ============================

DATA_FOLDER = "Data"

USERS_FILE = os.path.join(DATA_FOLDER, "users.txt")
QUESTIONS_FILE = os.path.join(DATA_FOLDER, "questions.txt")
RESULTS_FILE = os.path.join(DATA_FOLDER, "results.txt")
ATTEMPTS_FILE = os.path.join(DATA_FOLDER, "attempts.txt")
LOGIN_ATTEMPTS_FILE = os.path.join(DATA_FOLDER, "login_attempts.txt")


# ============================
# UTILITIES
# ============================

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def ensure_files_exist():

    os.makedirs(DATA_FOLDER, exist_ok=True)

    files = [
        USERS_FILE,
        QUESTIONS_FILE,
        RESULTS_FILE,
        ATTEMPTS_FILE,
        LOGIN_ATTEMPTS_FILE
    ]

    for path in files:
        if not os.path.exists(path):
            open(path, "a", encoding="utf-8").close()


def read_file(path):

    ensure_files_exist()

    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines() if line.strip()]


def write_file(path, lines):

    ensure_files_exist()

    with open(path, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")


# ============================
# USER FUNCTIONS
# ============================

def get_user_by_roll(roll):

    for line in read_file(USERS_FILE):

        parts = line.split("|")

        if len(parts) < 4:
            continue

        user_roll, email, password, role = parts[:4]

        if user_roll == roll:

            return {
                "roll": user_roll,
                "email": email,
                "password": password,
                "role": role
            }

    return None


def get_all_users():

    users = []

    for line in read_file(USERS_FILE):

        parts = line.split("|")

        if len(parts) >= 4:
            users.append(parts)

    return users


def create_empty_user(roll, role="student"):

    ensure_files_exist()

    with open(USERS_FILE, "a", encoding="utf-8") as f:

        timestamp = str(int(time.time()))

        f.write(f"{roll}|||{role}|{timestamp}\n")


def update_user(roll, email=None, password=None):

    users = read_file(USERS_FILE)

    updated = []

    for line in users:

        parts = line.split("|")

        if len(parts) < 4:
            continue

        user_roll, user_email, user_pass, user_role = parts[:4]

        if user_roll == roll:

            if email is not None:
                user_email = email

            if password is not None:
                user_pass = hash_password(password)

        updated.append(f"{user_roll}|{user_email}|{user_pass}|{user_role}")

    write_file(USERS_FILE, updated)


def validate_user(roll, password):

    user = get_user_by_roll(roll)

    if not user:
        return False

    hashed = hash_password(password)

    return user["password"] == hashed


# ============================
# QUESTION FUNCTIONS
# ============================

def get_all_questions():

    questions = []

    for line in read_file(QUESTIONS_FILE):

        parts = line.split("|")

        if len(parts) >= 7:
            questions.append(parts)

    return questions


def add_question(question_line):

    parts = question_line.split("|")

    if len(parts) < 7:
        print("Invalid question format skipped")
        return

    with open(QUESTIONS_FILE, "a", encoding="utf-8") as f:
        f.write(question_line + "\n")


def save_all_questions(question_list):

    formatted = ["|".join(q) for q in question_list if len(q) >= 7]

    write_file(QUESTIONS_FILE, formatted)


def get_questions_by_subject(subject):

    return [q for q in get_all_questions() if q[0] == subject]


def get_coding_questions(subject):

    return [q for q in get_all_questions() if q[0] == subject and q[3] == "code"]


def get_mcq_questions(subject):

    return [q for q in get_all_questions() if q[0] == subject and q[3] == "mcq"]


def get_all_subjects():

    qs = get_all_questions()

    subjects = {q[0] for q in qs if len(q) > 0}

    return sorted(subjects)


def get_latest_subject():

    qs = get_all_questions()

    if not qs:
        return None

    return qs[-1][0]


def count_questions():

    return len(get_all_questions())


# ============================
# RESULT FUNCTIONS
# ============================

def save_result(student_id, subject, score, total, percentage, grade):

    ensure_files_exist()

    timestamp = str(int(time.time()))

    with open(RESULTS_FILE, "a", encoding="utf-8") as f:

        f.write(
            f"{student_id}|{subject}|{score}|{total}|{percentage}|{grade}|{timestamp}\n"
        )


def get_all_results():

    results = []

    for line in read_file(RESULTS_FILE):

        parts = line.split("|")

        if len(parts) >= 7:
            results.append(parts)

    return results


def get_result(student_id):

    results = get_all_results()

    filtered = [r for r in results if r[0] == student_id]

    return filtered[-1] if filtered else None


def get_leaderboard():

    results = get_all_results()

    best_scores = {}

    for r in results:

        try:

            student = r[0]
            percent = float(r[4])

            if student not in best_scores or percent > best_scores[student]:
                best_scores[student] = percent

        except:
            continue

    leaderboard = list(best_scores.items())

    leaderboard.sort(key=lambda x: x[1], reverse=True)

    return leaderboard[:10]


def count_results():

    return len(get_all_results())


# ============================
# ATTEMPT FUNCTIONS
# ============================

def get_attempts(roll, subject):

    for line in read_file(ATTEMPTS_FILE):

        parts = line.split("|")

        if len(parts) != 3:
            continue

        r, sub, attempts = parts

        if r == roll and sub == subject:

            return int(attempts)

    return 0


def increase_attempt(roll, subject):

    lines = read_file(ATTEMPTS_FILE)

    updated = []

    found = False

    for line in lines:

        parts = line.split("|")

        if len(parts) != 3:
            continue

        r, sub, att = parts

        if r == roll and sub == subject:

            att = str(int(att) + 1)

            found = True

        updated.append(f"{r}|{sub}|{att}")

    if not found:

        updated.append(f"{roll}|{subject}|1")

    write_file(ATTEMPTS_FILE, updated)


# ============================
# LOGIN ATTEMPTS
# ============================

def record_failed_login(roll):

    attempts = read_file(LOGIN_ATTEMPTS_FILE)

    updated = []

    found = False

    for line in attempts:

        r, count = line.split("|")

        if r == roll:
            count = str(int(count) + 1)
            found = True

        updated.append(f"{r}|{count}")

    if not found:
        updated.append(f"{roll}|1")

    write_file(LOGIN_ATTEMPTS_FILE, updated)


def get_failed_attempts(roll):

    for line in read_file(LOGIN_ATTEMPTS_FILE):

        r, count = line.split("|")

        if r == roll:
            return int(count)

    return 0


def reset_failed_attempts(roll):

    attempts = read_file(LOGIN_ATTEMPTS_FILE)

    updated = [line for line in attempts if not line.startswith(roll + "|")]

    write_file(LOGIN_ATTEMPTS_FILE, updated)


# ============================
# SYSTEM STATS
# ============================

def total_users():
    return len(get_all_users())


def total_questions():
    return count_questions()


def total_results():
    return count_results()