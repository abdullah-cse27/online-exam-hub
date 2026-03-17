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
# LIMIT RESOURCES
# ===================================================

def limit_resources():

    try:

        import resource

        resource.setrlimit(resource.RLIMIT_AS, (100 * 1024 * 1024, -1))
        resource.setrlimit(resource.RLIMIT_CPU, (2, 2))

    except:
        pass


# ===================================================
# RUN PYTHON CODE
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
# RUN C CODE
# ===================================================

def run_c_code(code, input_data=None):

    try:

        with tempfile.TemporaryDirectory() as tmpdir:

            c_file = os.path.join(tmpdir, "main.c")
            exe_file = os.path.join(tmpdir, "main")

            with open(c_file, "w") as f:
                f.write(code)

            compile_result = subprocess.run(
                ["gcc", c_file, "-o", exe_file],
                capture_output=True,
                text=True
            )

            if compile_result.stderr:
                return compile_result.stderr.strip()

            run_result = subprocess.run(
                [exe_file],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=3
            )

            if run_result.stderr:
                return run_result.stderr.strip()

            return run_result.stdout.strip()

    except Exception as e:

        return f"C Execution Error: {str(e)}"


# ===================================================
# RUN C++ CODE
# ===================================================

def run_cpp_code(code, input_data=None):

    try:

        with tempfile.TemporaryDirectory() as tmpdir:

            cpp_file = os.path.join(tmpdir, "main.cpp")
            exe_file = os.path.join(tmpdir, "main")

            with open(cpp_file, "w") as f:
                f.write(code)

            compile_result = subprocess.run(
                ["g++", cpp_file, "-o", exe_file],
                capture_output=True,
                text=True
            )

            if compile_result.stderr:
                return compile_result.stderr.strip()

            run_result = subprocess.run(
                [exe_file],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=3
            )

            if run_result.stderr:
                return run_result.stderr.strip()

            return run_result.stdout.strip()

    except Exception as e:

        return f"C++ Execution Error: {str(e)}"


# ===================================================
# UNIVERSAL RUNNER
# ===================================================

def run_code(language, code, input_data=None):

    language = language.lower()

    if language == "python":
        return run_python_code(code, input_data)

    elif language == "c":
        return run_c_code(code, input_data)

    elif language in ["cpp", "c++"]:
        return run_cpp_code(code, input_data)

    else:
        return "Unsupported language."


# ===================================================
# TEST CASE EVALUATION
# ===================================================

def evaluate_code(language, code, test_cases):

    results = []

    for case in test_cases:

        output = run_code(language, code, case["input"])

        passed = str(output).strip() == str(case["output"]).strip()

        results.append({
            "input": case["input"],
            "expected": case["output"],
            "output": output,
            "passed": passed
        })

    success = all(r["passed"] for r in results)

    return success, results