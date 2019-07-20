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
    app.add_argument("input", help="Text file containing input numbers, or stdin stream, "
                                    "just write stdin for that")
    app.add_argument("subset_size", type=int, help="Subset size, should not exceed the "
                                                   "input size. If set to 0, the program will "
                                                   "extract subsets of all possible sizes")
    # actually, 0 - not implemented yet!
    app.add_argument("requested_sum", type=int, help="Sum requested")
    # app.add_argument("--verbose", "-v", help="Show verbose messages")
    app.add_argument("--only", "-o", action="store_true", dest="only",
                     help="Halt right after the first sequence found. "
                          "In combination with sibset_size == 0 returns "
                          "only one combination of undefined size.")
    # actually returns only one result now, extensions are not implemented so far
    if len(sys.argv) < 3:
        app.print_help()
        sys.exit()
    args = app.parse_args()
    if args.subset_size <= 1 and args.subset_size != 0:
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


def call_lib(lib, only, subset_size, requested_sum, in_arr, in_arr_len, _in_file):
    """Call lib with the parameters given."""
    c_arr = (ctypes.c_uint32 * (in_arr_len + 1))()
    c_arr[:-1] = in_arr
    c_arr_size = ctypes.c_uint32(in_arr_len)
    c_sub_size = ctypes.c_uint32(subset_size)
    c_req_sum = ctypes.c_uint32(requested_sum)
    c_only = ctypes.c_bool(only)
    # get and parse the result
    # TODO: verbose messages in c param
    # t0 = dt.now()
    result = lib.solve_SSP(c_arr,
                           c_arr_size,
                           c_sub_size,
                           c_req_sum,
                           c_only)
    # sys.stderr.write("Time spent (within shared lib): {}\n"
    #                  "".format(dt.now() - t0))
    ptr = 0
    if result[ptr] == 0:
        # if starts with 0 -> nothing found at all
        print("# No results for:\n#IN_FILE: {}; REQ_SUM: {}; SUBSET_SIZE: {}".format(_in_file,
                                                                                     requested_sum,
                                                                                     subset_size))
        del lib  # no need to stop iter:
        return False
    # there are our results
    print("# The result(s) is/are:")
    while result[ptr] != 0:
        up_to = ptr + subset_size
        result_line = [result[x] for x in range(ptr, up_to)]
        print(result_line)
        ptr = up_to
    del lib
    # in case if we wanted one combination only,
    # it will halt the program
    return only
    

def main(input_file, subset_size_arg, requested_sum, only):
    """Entry point."""
    args = parse_args()
    # read user input
    in_arr = make_input_arr(input_file)
    in_arr_len = len(in_arr)
    if args.subset_size >= in_arr_len:
        sys.exit("Subset size cannot be >= the set size")
    # then find shared lib
    lib_ext = "so" if platform.system != "Windows" else "dll"
    lib_path = os.path.join(os.path.dirname(__file__), "bin",
                            "SSP_lib.{}".format(lib_ext))
    if not os.path.isfile(lib_path):
        sys.exit("Please call make or win_make.bat first")

    if subset_size_arg != 0:
        # we are interested only in one
        subset_sizes = [subset_size_arg]
    else:
        # we need to check all sizes
        # minimal elem size is 1
        # so comb size cannot be > than sum
        # combinations of size 1 are ignored
        # it's just a search in the array
        lo, hi = 2, requested_sum + 1
        subset_sizes = list(range(lo, hi))
        # call the library
    lib = ctypes.cdll.LoadLibrary(lib_path)
    # convert everyting into C types
    lib.solve_SSP.argtypes = [ctypes.POINTER(ctypes.c_uint32),
                              ctypes.c_uint32,
                              ctypes.c_uint32,
                              ctypes.c_uint32,
                              ctypes.c_bool]
    lib.solve_SSP.restype = ctypes.POINTER(ctypes.c_uint32)
    t0 = dt.now()
    f_calls = 0
    for subset_size in subset_sizes:
        stop_iter = call_lib(lib, only, subset_size, requested_sum, in_arr, in_arr_len, input_file)
        f_calls += 1
        if stop_iter:
            # we found what we've been looking for
            break
    elapsed = dt.now() - t0
    print("# Time spent within C libraries: {}".format(elapsed))
    print("# Func calls: {}".format(f_calls))

if __name__ == "__main__":
    args = parse_args()
    main(args.input, args.subset_size, args.requested_sum, args.only)
