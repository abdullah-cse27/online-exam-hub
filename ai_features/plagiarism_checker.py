# ===================================================
# FILE: ai_features/plagiarism_checker.py
# ===================================================

import difflib
import re


# ===================================================
# CLEAN CODE
# ===================================================

def normalize_code(code):

    # remove spaces
    code = code.strip()

    # remove comments
    code = re.sub(r"#.*", "", code)

    # remove extra whitespace
    code = re.sub(r"\s+", " ", code)

    return code


# ===================================================
# SIMILARITY CHECK
# ===================================================

def calculate_similarity(code1, code2):

    code1 = normalize_code(code1)
    code2 = normalize_code(code2)

    matcher = difflib.SequenceMatcher(None, code1, code2)

    return round(matcher.ratio() * 100, 2)


# ===================================================
# PLAGIARISM DETECTION
# ===================================================

def detect_plagiarism(student_code, reference_codes):

    """
    student_code = code submitted by student
    reference_codes = list of other codes
    """

    max_similarity = 0

    for ref in reference_codes:

        similarity = calculate_similarity(student_code, ref)

        if similarity > max_similarity:
            max_similarity = similarity

    return max_similarity


# ===================================================
# PLAGIARISM WARNING
# ===================================================

def plagiarism_warning(score):

    if score > 90:
        return "High plagiarism detected"

    elif score > 70:
        return "Moderate similarity detected"

    elif score > 50:
        return "Some similarity detected"

    else:
        return "Code appears original"


# ===================================================
# FINAL CHECK
# ===================================================

def check_code_plagiarism(student_code, previous_codes):

    similarity = detect_plagiarism(student_code, previous_codes)

    warning = plagiarism_warning(similarity)

    return {
        "similarity": similarity,
        "warning": warning
    }