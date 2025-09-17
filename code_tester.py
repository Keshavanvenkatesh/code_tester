import random
import string
import math
import time
from datetime import datetime
import matplotlib.pyplot as plt
import tkinter as tk
from klogging import *   # custom logger
import os

# ==================== TYPE CHECKING + TESTCASE GENERATION ====================

def checktype(data):
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
    if i == "bool":
        return bool(random.randint(0, 1))
    elif i == "int":
        return random.randint(int("1" + ("0" * (n - 1))), int("9" * n))
    elif i == "float":
        return random.uniform(10 ** (n - 1), 10 ** n)
    elif i == "str":
        return "".join(random.choice(string.ascii_letters) for _ in range(n))
    elif isinstance(i, list):
        return [genereate_spefic_testcase_element(sub_n, j) for sub_n, j in zip(n, i)]
    elif isinstance(i, tuple):
        return tuple(genereate_spefic_testcase_element(sub_n, j) for sub_n, j in zip(n, i))
    elif isinstance(i, dict):
        return {k: genereate_spefic_testcase_element(n[k], v) for k, v in i.items()}


def generate_specific_testcase(example, range_):
    test_casetype = [checktype(i) for i in example]
    test_case = [
        genereate_spefic_testcase_element(range_[i], test_casetype[i])
        for i in range(len(test_casetype))
    ]
    return tuple(test_case)

# ==================== RANDOM TESTCASE GENERATION ====================

def genereate_random_testcase_element(i, range_):
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
    test_casetype = [checktype(i) for i in example]
    test_case = [genereate_random_testcase_element(test_casetype[i], range_[i]) for i in range(len(test_casetype))]
    return tuple(test_case)

# ==================== BENCHMARKING ====================

def average_time(func, example, range_, iterations=10, type="random",
                 file_to_log="benchmark_logging.txt", max_size=1073741824):

    record_time = []
    total_time = []

    benchmark_logger = logger("benchmark_logger", max_size, file_to_log=file_to_log)

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
            total_time.append(exec_time)

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

    mean_time = sum(record_time) / len(record_time) if record_time else None
    variance = sum((i - mean_time) ** 2 for i in record_time) if record_time else 0
    mean_deviation = math.sqrt(variance / len(record_time)) if record_time else None

    # Console Report
    print()
    print("----- BENCHMARKING REPORT -----")
    print(f"""Average time: {mean_time}
Mean deviation: {mean_deviation}
Minimum time: {min(record_time) if record_time else None}
Maximum time: {max(record_time) if record_time else None}
Total time: {sum(total_time)}
Iterations: {len(record_time)}""")
    print("-------------------------------")
    print()

    return {
        "Average time": mean_time,
        "Mean deviation": mean_deviation,
        "Minimum time": min(record_time) if record_time else None,
        "Max time": max(record_time) if record_time else None,
        "Total time": sum(total_time),
        "Iterations": len(record_time)
    }

# ==================== LOG VIEWING ====================

def show_error(file, log_file="benchmark_logging.txt", write=False):
    if write:
        if os.path.exists(log_file):
            with open(log_file, "r") as master_file, open(file, "w") as student_file:
                for line in master_file:
                    if "ERROR" in line:
                        student_file.write(line)
            print(f"Errors written to {file}")
        else:
            print("Log file does not exist.")
    else:
        logger.show_all_error(log_file)


def show_info(file, log_file="benchmark_logging.txt", write=False):
    if write:
        if os.path.exists(log_file):
            with open(log_file, "r") as master_file, open(file, "w") as student_file:
                for line in master_file:
                    if "INFO" in line:
                        student_file.write(line)
            print(f"Infos written to {file}")
        else:
            print("Log file does not exist.")
    else:
        logger.show_all_info(log_file)


def show_warning(file, log_file="benchmark_logging.txt", write=False):
    if write:
        if os.path.exists(log_file):
            with open(log_file, "r") as master_file, open(file, "w") as student_file:
                for line in master_file:
                    if "WARNING" in line:
                        student_file.write(line)
            print(f"Warnings written to {file}")
        else:
            print("Log file does not exist.")
    else:
        logger.show_all_warning(log_file)

# ==================== HELP ====================

def help():
    print(r"""
🔹 Benchmarking Toolkit 🔹
- Generate testcases (specific/random)
- Benchmark execution times
- Log execution results
- Review INFO, WARNING, ERROR logs
""")

# ==================== SAMPLE USAGE ====================

if __name__ == "__main__":
    def func_sort(lst):
        return sorted(lst)

    example = [[random.randint(0, 1000) for _ in range(500)]]
    ranges = [[3] * 500]   # 3-digit integers

    print("Benchmarking sort function...")
    average_time(func_sort, example, ranges, iterations=10, type="specific")

    show_info("benchmark_info.txt")
    show_error("benchmark_errors.txt")