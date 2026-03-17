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
    "from os",
    "from sys",
    "open(",
    "eval(",
    "exec(",
    "__import__",
    "os.remove",
    "os.system",
    "shutil",
    "socket",
    "threading",
    "multiprocessing"
]


# ===================================================
# SECURITY CHECK
# ===================================================

def is_safe(code):

    code_lower = code.lower()

    for keyword in BLOCKED_KEYWORDS:

        if keyword in code_lower:
            return False, f"Restricted keyword detected: {keyword}"

    return True, ""


# ===================================================
# LIMIT RESOURCES (Linux/Mac)
# ===================================================

def limit_resources():

    try:

        import resource

        # limit memory to 100MB
        resource.setrlimit(resource.RLIMIT_AS, (100 * 1024 * 1024, -1))

        # limit CPU time
        resource.setrlimit(resource.RLIMIT_CPU, (2, 2))

    except:
        pass


# ===================================================
# RUN CODE
# ===================================================

def run_python_code(code, input_data=None):

    safe, message = is_safe(code)

    if not safe:
        return f"Security Error: {message}"

    tmp_file = None

    try:

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8"
        ) as tmp:

            tmp.write(code)
            tmp_file = tmp.name


        result = subprocess.run(
            [sys.executable, tmp_file],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=3,
            preexec_fn=limit_resources if os.name != "nt" else None
        )


        # stderr
        if result.stderr:
            return result.stderr.strip()

        output = result.stdout.strip()

        if output == "":
            return "No output."

        return output


    except subprocess.TimeoutExpired:

        return "Execution timed out (possible infinite loop)."


    except Exception as e:

        return f"Execution Error: {str(e)}"


    finally:

        try:
            if tmp_file and os.path.exists(tmp_file):
                os.remove(tmp_file)
        except:
            pass


# ===================================================
# TEST CASE EVALUATION
# ===================================================

def evaluate_code(code, test_cases):

    """
    test_cases format:
    [
        {"input": "2 3", "output": "5"},
        {"input": "5 7", "output": "12"}
    ]
    """

    results = []

    for case in test_cases:

        output = run_python_code(code, case["input"])

        passed = str(output).strip() == str(case["output"]).strip()

        results.append({
            "input": case["input"],
            "expected": case["output"],
            "output": output,
            "passed": passed
        })

    success = all(r["passed"] for r in results)

    return success, results