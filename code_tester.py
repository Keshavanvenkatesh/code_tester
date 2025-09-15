#######################################################################################################################################
# def decorator(func):
#     def wrapper(*args,**kwargs):
#         print("before func")
#         func(*args,**kwargs)
#         print("after func")
#     return wrapper

# @decorator
# def main(person):
#     print(f"hello {person}")
# main("keshavan")
######################################################################################################################################

import random
import string
import time
from datetime import datetime # so you can use time.time()
import matplotlib.pyplot as plt # for plotting
import tkinter as tk            # standard shorthand for tkinter
from klogging import *          # your custom logger

def checktype(data):                # this will check the types of the given data and it goes something like this working together with generate specific testcase
                                    #   data=[1,"hi",[2,"sanjana"]] -> [23213,"hello",[1323,"keshavan"]] this is later deferesensed for the function to use and benchmark perfomance
        if isinstance(data,bool):
            return("bool")
        
        elif isinstance(data,int):
            return "int"
        
        elif isinstance(data,float):
            return("float")
        
        elif isinstance(data,str):
            return("str")
             
        elif isinstance(data,list):
            temp=[]
            for i in data:
                temp.append(checktype(i))
            return temp
        
        elif isinstance(data,tuple):
            temp=[]
            for i in data:
                temp.append(checktype(i))
            return tuple(temp)
        
        elif isinstance(data,dict):
            return {k: checktype(v) for k,v in data.items()}

def genereate_spefic_testcase_element(n,i):

    if i=="bool":
        return (bool(random.randint(0,1)))
    
    elif i=="int":
        return (random.randint(int("0"+("0"*(n-1))),int("9"*n)))
    
    elif i=="float":
        return random.uniform(10**(n-1), 10**n)

    elif i == "str":
        # check for special char and num and generate specific characters
        temp_str=""
        for i in range(n):
            temp_str+=random.choice(list(string.ascii_letters))
        return temp_str
    
    elif isinstance(i,list):
        temp=[]
        for j in i:
            temp.append(genereate_spefic_testcase_element(n,j))
        return temp
    
    elif isinstance(i,tuple):
        temp=[]
        for j in i:
            temp.append(genereate_spefic_testcase_element(n,j))
        return tuple(temp)
    
    elif isinstance(i,dict):
        return {k: genereate_spefic_testcase_element(n,v) for k,v in i.items()}

def generate_specific_testcase(example,range_):
    test_casetype=[]
    test_case=[]
    for i in example:
        test_casetype.append(checktype(i))

    for i in range(len(test_casetype)):
        test_case.append(genereate_spefic_testcase_element(range_[i],test_casetype[i]))
    return(tuple(test_case))

def genereate_random_testcase_element(i,range_):

    if i=="bool":
        return (bool(random.randint(0,1)))
    
    elif i=="int":
        digits=random.randint(*range_)                    
        return (random.randint(10**(digits-1),10**digits-1))
    
    elif i=="float":
        digits=random.randint(*range_)
        return random.uniform(10**(digits-1),10**digits)
    
    elif i=="str":
        length=random.randint(*range_)
        temp_str=""
        for _ in range(length):
            temp_str+=random.choice(list(string.ascii_letters))
        return temp_str
     
    elif isinstance(i,list):
        temp=[]
        for j,sub_range in zip(i,range_):           
            temp.append(genereate_random_testcase_element(j,sub_range))
        return temp
    
    elif isinstance(i,tuple):
        temp=[]
        for j,sub_range in zip(i,range_):
            temp.append(genereate_random_testcase_element(j,sub_range))
        return tuple(temp)
    
    elif isinstance(i,dict):
        return {k:genereate_random_testcase_element(v,range_[k]) for k,v in i.items()}

def generate_random_testcase(example,range_):
    test_casetype=[]
    test_case=[]

    for i in example:
        test_casetype.append(checktype(i))

    for i in range(len(test_casetype)):
        test_case.append(genereate_random_testcase_element(test_casetype[i],range_[i]))
    return(tuple(test_case))

#####################################################################################################################

def average_time(func,example,range_,iterations=10,type="random",file_to_log="benchmark_logging.txt", max_size = 1048576):

    record_time=[]
    if type=="specific":

        benchmark_logger = logger("benchmark_logger",max_size=1073741824, file_to_log=file_to_log)

        for i in range(iterations):
            test_case=generate_specific_testcase(example,range_)
            return_val=None

            try:
                start_time=time.time()
                return_val=func(*test_case)
                end_time=time.time()

                excution_time=float(end_time-start_time)
                record_time.append(excution_time)

                benchmark_logger.log_info(msg="executed successfully",
                                          PREFIX=str(i+1)+".",
                                          POSTFIX=f" >>>time of excution({excution_time})",
                                          file_to_log="benchmark_logging.txt",
                                          function_name=func.__name__,
                                          arguments=str(test_case),
                                          return_value=return_val)
            except:
                benchmark_logger.log_error(msg="execution failed",
                                           PREFIX=str(i+1)+".",
                                           POSTFIX=" >>>time of excution(none)",
                                           file_to_log="benchmark_logging.txt",
                                          function_name=func.__name__,
                                          arguments=str(test_case),
                                          return_value=return_val)

        return sum(record_time)/len(record_time)

    elif type=="random":
        benchmark_logger = logger("benchmark_logger",max_size=1073741824, file_to_log=file_to_log)

        for i in range(iterations):
            test_case=generate_random_testcase(example,range_)      # range is a nested list of range of each element

            try:
                start_time=time.time()
                return_val=func(*test_case)
                end_time=time.time()

                excution_time=float(end_time-start_time)
                record_time.append(excution_time)

                benchmark_logger.log_info(msg="executed successfully",
                                          PREFIX=str(i+1)+".",
                                          POSTFIX=f" >>>time of excution({excution_time})",
                                          file_to_log="benchmark_logging.txt",
                                          function_name=func.__name__,
                                          arguments=str(test_case),
                                          return_value=return_val)
                
            except:
                benchmark_logger.log_error(msg="execution failed",
                                           PREFIX=str(i+1)+".",
                                           POSTFIX=" >>>time of excution(none)",
                                           file_to_log="benchmark_logging.txt",
                                          function_name=func.__name__,
                                          arguments=str(test_case),
                                          return_value=return_val)
                
def show_error(write=False):
    if write:
        pass
    else:
        logger.show_all_error(log_file="benchmark_logging.txt")

###############################################################################################

# example_testcase=["hi",1,["a",1]]
# print(generate_specific_testcase(example_testcase))

# def func(a,b,c=[1,2]):
#     print(a,b,c)
# func(*generate_specific_testcase([True,"hi",[1,2]]))

def func(a,b,c=[1,2]):
    print(a/b)

print(average_time(func,[1,2,[1,2]],[1,1,3,3],100,"specific"))
show_error()