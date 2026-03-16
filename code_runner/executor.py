# ===================================================
# FILE: code_runner/executor.py
# ===================================================

import subprocess
import tempfile
import sys
import os


# ===================================================
# BLOCKED KEYWORDS (Security)
# ===================================================

BLOCKED_KEYWORDS = [
    "import os",
    "import sys",
    "import subprocess",
    "open(",
    "eval(",
    "exec(",
    "__import__",
    "os.remove",
    "os.system",
    "shutil",
    "socket"
]


# ===================================================
# SECURITY CHECK
# ===================================================

def is_safe(code):

    code_lower = code.lower()

    for keyword in BLOCKED_KEYWORDS:

        if keyword in code_lower:
            return False, f"Use of restricted keyword detected: {keyword}"

    return True, ""


# ===================================================
# RUN CODE
# ===================================================

def run_python_code(code):

    safe, message = is_safe(code)

    if not safe:
        return f"Security Error: {message}"

    tmp_file = None

    try:

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False
        ) as tmp:

            tmp.write(code)
            tmp_file = tmp.name


        result = subprocess.run(
            [sys.executable, tmp_file],
            capture_output=True,
            text=True,
            timeout=3
        )

        if result.stderr:
            return result.stderr.strip()

        if result.stdout.strip() == "":
            return "No output."

        return result.stdout.strip()


    except subprocess.TimeoutExpired:

        return "Execution timed out (possible infinite loop)."


    except Exception as e:

        return str(e)


    finally:

        # Clean temporary file
        try:
            if tmp_file and os.path.exists(tmp_file):
                os.remove(tmp_file)
        except:
            pass