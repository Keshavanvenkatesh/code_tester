import random
import string
import math
import time
from datetime import datetime
import matplotlib.pyplot as plt
import tkinter as tk
from klogging import *   # custom logger
import pickle 
import csv
import ast
from multiprocessing import Pool

###################################################################################################
# TYPE CHECKING + TESTCASE GENERATION
###################################################################################################

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
        # zip n (sub-ranges) with type structure
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

###################################################################################################
# RANDOM USAGE
###################################################################################################

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
        forbidden = ["bool", "int", "float", "str"]

        while True:
            sentence = "".join(random.choice(string.ascii_letters) for _ in range(length))
            # Check if any forbidden keyword appears as a substring
            if not any(word in sentence for word in forbidden):
                return sentence

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

###################################################################################################
# BENCHMARKING
###################################################################################################

def average_time(func, example, range_, iterations=10, type="random",
                 file_to_log="benchmark_logging.txt", max_size=1073741824):

    record_time = []
    total_time=[]

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
    mean_time=sum(record_time) / len(record_time) if record_time else None
    variance=0
    
    for i in record_time:
        variance+=(i-mean_time)**2
    mean_deviation=math.sqrt(variance/len(record_time))

    return {"Average time":sum(record_time) / len(record_time) if record_time else None,
"Mean deviation":mean_deviation,
"Minimum time":min(record_time),
"Max time":max(record_time),
"Total time":sum(total_time),
"Iterations":len(record_time)}

def benchmark(func, example, range_, iterations=10, type="random",
              file_to_log="benchmark_logging.txt", max_size=1073741824, multi_process=5):

    args_list = [
        (func, example, range_, iterations, type, file_to_log, max_size)
        for _ in range(multi_process)
    ]

    with Pool(processes=multi_process) as pool:
        results = pool.starmap(average_time, args_list)
    pretty_print(results)

def pretty_print(results):
    for i, result in enumerate(results):
        print(f"---------- Process {i+1} ----------")
        for key, value in result.items():
            print(f"{key}: {value}")
        print("-------------------------------")
        print()

###################################################################################################
# LOGGING INTERFACE
###################################################################################################

def show_error(file="", log_file="benchmark_logging.txt", write=False):
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

def show_info(file="", log_file="benchmark_logging.txt", write=False):
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

def show_warning(file="", log_file="benchmark_logging.txt", write=False):
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

def custom_test(func, input_=None, output_=None, file=None,
                file_to_log="benchmark_logging.txt", max_size=1073741824, file_type=None):

    benchmark_logger = logger("benchmark_logger", max_size, file_to_log=file_to_log)

    # ==================== Normal input/output lists ====================
    if file_type is None:
        if len(input_) != len(output_):
            raise ValueError("Input and output lengths do not match.")

        for i in range(len(input_)):
            start_time = time.time()
            return_val = func(*input_[i])
            end_time = time.time()
            exec_time = float(end_time - start_time)
            test_case = input_[i]

            if return_val == output_[i]:
                benchmark_logger.log_passed(
                    msg="Test case passed",
                    PREFIX=f"{i+1}.",
                    POSTFIX=f" >>> execution_time({exec_time})",
                    file_to_log=file_to_log,
                    function_name=func.__name__,
                    arguments=str(test_case),
                    return_value=return_val
                )
                print(f"Test case {i+1}: Passed")
            else:
                benchmark_logger.log_failed(
                    msg=f"Test case failed (expected {output_[i]})",
                    PREFIX=f"{i+1}.",
                    POSTFIX=f" >>> execution_time({exec_time})",
                    file_to_log=file_to_log,
                    function_name=func.__name__,
                    arguments=str(test_case),
                    return_value=return_val
                )
                print(f"Test case {i+1}: Failed")

    # ==================== CSV input ====================
    elif file_type == "csv":
        with open(file, mode="r") as csvfile:
            csvreader = csv.reader(csvfile)

            for i, line in enumerate(csvreader):
                if len(line) < 2:
                    benchmark_logger.log_warning(
                        msg="Incomplete line, skipping.",
                        PREFIX=f"{i+1}.",
                        POSTFIX=" >>> execution_time(none)",
                        file_to_log=file_to_log,
                        function_name=func.__name__,
                        arguments=str(line),
                        return_value=None
                    )
                    continue

                try:
                    test_case = ast.literal_eval(line[0])  
                    expected_output = ast.literal_eval(line[1])
                except Exception as e:
                    benchmark_logger.log_error(
                        msg=f"Parse error in CSV: {e}",
                        PREFIX=f"{i+1}.",
                        POSTFIX=" >>> execution_time(none)",
                        file_to_log=file_to_log,
                        function_name=func.__name__,
                        arguments=str(line),
                        return_value=None
                    )
                    continue

                start_time = time.time()
                return_val = func(*test_case) if isinstance(test_case, (list, tuple)) else func(test_case)
                end_time = time.time()
                exec_time = float(end_time - start_time)

                if return_val == expected_output:
                    benchmark_logger.log_passed(
                        msg="Test case passed",
                        PREFIX=f"{i+1}.",
                        POSTFIX=f" >>> execution_time({exec_time})",
                        file_to_log=file_to_log,
                        function_name=func.__name__,
                        arguments=str(test_case),
                        return_value=return_val
                    )
                else:
                    benchmark_logger.log_failed(
                        msg=f"Test case failed (expected {expected_output})",
                        PREFIX=f"{i+1}.",
                        POSTFIX=f" >>> execution_time({exec_time})",
                        file_to_log=file_to_log,
                        function_name=func.__name__,
                        arguments=str(test_case),
                        return_value=return_val
                    )

    # ==================== Binary input ====================
    elif file_type == "binary":
        with open(file, mode="rb") as binfile:
            i = 0
            while True:
                try:
                    data = pickle.load(binfile)   
                except EOFError:
                    break
                except Exception as e:
                    print(f"Error reading binary file: {e}")
                    break

                if not isinstance(data, (list, tuple)) or len(data) != 2:
                    benchmark_logger.log_error(
                        msg="Invalid format in binary file",
                        PREFIX=f"{i+1}.",
                        POSTFIX=" >>> execution_time(none)",
                        file_to_log=file_to_log,
                        function_name=func.__name__,
                        arguments=str(data),
                        return_value=None
                    )
                    continue

                test_case, expected_output = data
                start_time = time.time()
                return_val = func(*test_case) if isinstance(test_case, (list, tuple)) else func(test_case)
                end_time = time.time()
                exec_time = float(end_time - start_time)

                if return_val == expected_output:
                    benchmark_logger.log_passed(
                        msg="Test case passed",
                        PREFIX=f"{i+1}.",
                        POSTFIX=f" >>> execution_time({exec_time})",
                        file_to_log=file_to_log,
                        function_name=func.__name__,
                        arguments=str(test_case),
                        return_value=return_val
                    )
                else:
                    benchmark_logger.log_failed(
                        msg=f"Test case failed (expected {expected_output})",
                        PREFIX=f"{i+1}.",
                        POSTFIX=f" >>> execution_time({exec_time})",
                        file_to_log=file_to_log,
                        function_name=func.__name__,
                        arguments=str(test_case),
                        return_value=return_val
                    )
                i += 1
    else:
        raise ValueError("Invalid file_type. Use None, 'csv', or 'binary'.")
    
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