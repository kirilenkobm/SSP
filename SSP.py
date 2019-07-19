#!/usr/bin/env python3
"""Solve subset sum problem."""
import argparse
import sys
import os
import platform
from datetime import datetime as dt
import numpy as np
from numpy.ctypeslib import ndpointer
import ctypes

__author__ = "Bogdan Kirilenko"
__email__ = "kirilenkobm@gmail.com"
__version__ = 0.1

# actually, it will overflow on values like this
# arr sum should be limited to uint32_t max
UINT32_SIZE = 4294967295


def parse_args():
    """Parse and check args."""
    app = argparse.ArgumentParser()
    app.add_argument("input", help="Text file containing input numbers, "
                                   "or stdin stream, just write stdin "
                                   "for that")
    app.add_argument("subset_size", type=int, help="Subset size")
    app.add_argument("requested_sum", type=int, help="Sum requested")
    app.add_argument("--verbose", "-v", help="Show verbose messages")
    args = app.parse_args()
    if args.subset_size <= 1:
        sys.exit("Error! Requested subset size must be > 1")
    elif args.requested_sum < 0:
        sys.exit("Requested sum cannot be negative")
    if args.subset_size > args.requested_sum:
        sys.exit("Elem size is >= 1, sum cannot be < than subset size")
    return args


def make_input_arr(in_file):
    """Read input, check and convert to a numpy array."""
    in_is_stdin_stream = in_file == "stdin"
    f = open(in_file) if not in_is_stdin_stream else sys.stdin
    try:
        numbers = sorted([int(x.rstrip()) for x in f.readlines()])
    except ValueError:  # there was something non-numeric!
        sys.exit("Error: in input, numeric values expected.")
    f.close()
    # check for boundaries
    if any(x < 0 for x in numbers):
        sys.exit("Sorry, but for now works for non-negative"
                 " numbers only.")
    elif any(x > UINT32_SIZE for x in numbers):
        sys.exit("Sorry, but input nmber size is limited"
                 " to uint32_t max size")
    # ACTUALLY A PROBLEM
    if sum(numbers) > UINT32_SIZE:
        sys.exit("Overall array sum is too big, it will overflow")
    # ok, let's return this
    return numbers


def main():
    """Entry point."""
    args = parse_args()
    # read user input
    in_arr = make_input_arr(args.input)
    in_arr_len = len(in_arr)
    if args.subset_size >= in_arr_len:
        sys.exit("Subset size cannot be >= the set size")
    # then find shared lib
    lib_ext = "so" if platform.system != "Windows" else "dll"
    lib_path = os.path.join("bin", "SSP_lib.{}".format(lib_ext))
    if not os.path.isfile(lib_path):
        sys.exit("Please call make or win_make.bat first")
    lib = ctypes.cdll.LoadLibrary(lib_path)
    # convert everyting into C types
    lib.solve_SSP.argtypes = [ctypes.POINTER(ctypes.c_uint32),
                              ctypes.c_uint32,
                              ctypes.c_uint32,
                              ctypes.c_uint32]
    lib.solve_SSP.restype = ctypes.POINTER(ctypes.c_uint32)
    c_arr = (ctypes.c_uint32 * (in_arr_len + 1))()
    c_arr[:-1] = in_arr
    c_arr_size = ctypes.c_uint32(in_arr_len)
    c_sub_size = ctypes.c_uint32(args.subset_size)
    c_req_sum = ctypes.c_uint32(args.requested_sum)
    # get and parse the result
    # TODO: verbose messages in c param
    t0 = dt.now()
    result = lib.solve_SSP(c_arr,
                           c_arr_size,
                           c_sub_size,
                           c_req_sum)
    sys.stderr.write("Time spent (within shared lib): {}\n"
                     "".format(dt.now() - t0))
    ptr = 0
    if result[ptr] == 0:
        # if starts with 0 -> nothing found at all
        print("No results for:\n{}".format(vars(args)))
        sys.exit(0)
    # there are our results
    print("# The results are:")
    while result[ptr] != 0:
        up_to = ptr + args.subset_size
        result_line = [result[x] for x in range(ptr, up_to)]
        print(result_line)
        ptr = up_to
    

if __name__ == "__main__":
    main()
