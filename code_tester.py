import random
import string
import time
from datetime import datetime
import matplotlib.pyplot as plt
import tkinter as tk
from klogging import *   # custom logger

###################################################################################################
# TYPE CHECKING + TESTCASE GENERATION
###################################################################################################

def checktype(data):
    """Recursively determine the type structure of given data."""
    if isinstance(data, bool):
        return "bool"
    elif isinstance(data, int):
        return "int"
    elif isinstance(data, float):
        return "float"
    elif isinstance(data, str):
        return "str"
    elif isinstance(data, list):
        return [checktype(i) for i in data]
    elif isinstance(data, tuple):
        return tuple(checktype(i) for i in data)
    elif isinstance(data, dict):
        return {k: checktype(v) for k, v in data.items()}


def genereate_spefic_testcase_element(n, i):
    """Generate one testcase element with fixed digit/length constraints."""
    if i == "bool":
        return bool(random.randint(0, 1))
    elif i == "int":
        return random.randint(int("1" + ("0" * (n - 1))), int("9" * n))
    elif i == "float":
        return random.uniform(10 ** (n - 1), 10 ** n)
    elif i == "str":
        return "".join(random.choice(string.ascii_letters) for _ in range(n))
    elif isinstance(i, list):
        return [genereate_spefic_testcase_element(n, j) for j in i]
    elif isinstance(i, tuple):
        return tuple(genereate_spefic_testcase_element(n, j) for j in i)
    elif isinstance(i, dict):
        return {k: genereate_spefic_testcase_element(n, v) for k, v in i.items()}


def generate_specific_testcase(example, range_):
    """Generate a testcase based on exact digit/length constraints."""
    test_casetype = [checktype(i) for i in example]
    test_case = [genereate_spefic_testcase_element(range_[i], test_casetype[i]) for i in range(len(test_casetype))]
    return tuple(test_case)


def genereate_random_testcase_element(i, range_):
    """Generate one testcase element within a random range."""
    if i == "bool":
        return bool(random.randint(0, 1))
    elif i == "int":
        digits = random.randint(*range_)
        return random.randint(10 ** (digits - 1), 10 ** digits - 1)
    elif i == "float":
        digits = random.randint(*range_)
        return random.uniform(10 ** (digits - 1), 10 ** digits)
    elif i == "str":
        length = random.randint(*range_)
        return "".join(random.choice(string.ascii_letters) for _ in range(length))
    elif isinstance(i, list):
        return [genereate_random_testcase_element(j, sub_range) for j, sub_range in zip(i, range_)]
    elif isinstance(i, tuple):
        return tuple(genereate_random_testcase_element(j, sub_range) for j, sub_range in zip(i, range_))
    elif isinstance(i, dict):
        return {k: genereate_random_testcase_element(v, range_[k]) for k, v in i.items()}


def generate_random_testcase(example, range_):
    """Generate a testcase with randomized digit/length constraints."""
    test_casetype = [checktype(i) for i in example]
    test_case = [genereate_random_testcase_element(test_casetype[i], range_[i]) for i in range(len(test_casetype))]
    return tuple(test_case)


###################################################################################################
# BENCHMARKING + LOGGING
###################################################################################################

def average_time(func, example, range_, iterations=10, type="random",
                 file_to_log="benchmark_logging.txt", max_size=1048576):
    """
    Benchmark execution time of a function across multiple runs.

    Logs details using custom klogging:
    - Function name
    - Arguments
    - Return value
    - Execution time
    - Success / Error
    """
    record_time = []

    benchmark_logger = logger("benchmark_logger", max_size=1073741824, file_to_log=file_to_log)

    for i in range(iterations):
        test_case = (generate_specific_testcase(example, range_) if type == "specific"
                     else generate_random_testcase(example, range_))

        return_val = None
        try:
            start_time = time.time()
            return_val = func(*test_case)
            end_time = time.time()

            exec_time = float(end_time - start_time)
            record_time.append(exec_time)

            benchmark_logger.log_info(
                msg="executed successfully",
                PREFIX=f"{i+1}.",
                POSTFIX=f" >>> execution_time({exec_time})",
                file_to_log=file_to_log,
                function_name=func.__name__,
                arguments=str(test_case),
                return_value=return_val
            )

        except Exception:
            benchmark_logger.log_error(
                msg="execution failed",
                PREFIX=f"{i+1}.",
                POSTFIX=" >>> execution_time(none)",
                file_to_log=file_to_log,
                function_name=func.__name__,
                arguments=str(test_case),
                return_value=return_val
            )

    return sum(record_time) / len(record_time) if record_time else None


###################################################################################################
# ERROR REVIEW + HELP
###################################################################################################

def show_error(write=False):
    """Show all logged errors from benchmark log."""
    if write:
        # Future: option to export error logs to a file
        pass
    else:
        logger.show_all_error(log_file="benchmark_logging.txt")


def help():
    """Display usage guide for testcase generator + benchmarking tool."""
    print(r"""
🔹 Benchmarking + Testcase Generator Help 🔹
Provides tools to:
- Generate random/specific testcases
- Benchmark execution time
- Log execution details
- Review error history

📌 Main Functions:
  checktype(data) → infer type structure
  generate_specific_testcase(example, range_)
  generate_random_testcase(example, range_)
  average_time(func, example, range_, iterations, type, file_to_log, max_size)
  show_error(write=False)

👉 Call help() anytime to show this guide.
""")


###################################################################################################
# SAMPLE USAGE
###################################################################################################

def func(a, b, c=[1, 2]):
    print(a / b)


if __name__ == "__main__":
    print(average_time(func, [1, 2, [1, 2]], [1, 1, 3, 3], 10, "specific"))
    show_error()
