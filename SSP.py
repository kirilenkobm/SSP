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
# TODO: re-write in C, completely


def parse_args():
    """Parse and check args."""
    app = argparse.ArgumentParser()
    app.add_argument("input", help="Text file containing input numbers, or stdin stream, "
                                    "just write stdin for that")
    # actually, 0 - not implemented yet!
    app.add_argument("requested_sum", type=int, help="Sum requested")
    app.add_argument("--subset_size", "-s", type=int, default=0,
                     help="Specify particular size of subset, look only for this")
    # app.add_argument("--verbose", "-v", help="Show verbose messages")
    if len(sys.argv) < 3:
        app.print_help()
        sys.exit()
    args = app.parse_args()
    if args.requested_sum < 0:
        sys.exit("Requested sum cannot be negative")
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


def accumulate_sum(lst):
    """Just accumulate a sum of array."""
    """Return accumulated sum list."""
    if len(lst) == 1:
        return lst
    accumulated_sum = [lst[0]]
    for i in range(1, len(lst)):
        accumulated_sum.append(accumulated_sum[i - 1] + lst[i])
    return accumulated_sum


def get_subset_sizes(in_arr, req_sum):
    """Get subset sizes to check."""
    # TODO: maybe also transfer to C func?
    f_min = in_arr.copy()
    f_max = in_arr[::-1]
    f_min_acc = accumulate_sum(f_min)
    f_max_acc = accumulate_sum(f_max)
    # find the first elem what's bigger
    subset_sizes = []
    # 1 is deleted, should be specially noted
    for sub_size in range(1, len(f_max_acc)):
        inf = f_min_acc[sub_size]
        sup = f_max_acc[sub_size]
        if req_sum == inf:
            # the problem is actually solved
            # better to wrap in a class;
            # TODO: make it fancier
            print("# Sum lies on f_min, the answer is:\n{}" \
                  "".format(f_min[:sub_size + 1]))
            exit()
        elif req_sum == sup:
            print("# Answer lies of f_max, the aswer is:\n{}" \
                  "".format(f_max[:sub_size + 1]))
            exit()
        elif inf < req_sum < sup:
            subset_sizes.append(sub_size + 1)
    return subset_sizes


def _make_single_size(req, available):
    """Check if requested elem len is possible."""
    if req < available[0] or req > available[-1]:
        print("# Impossible to find combination of length {}".format(req))
        print("# Please use one of these for this input:\n{}".format(str(available)))
        sys.exit("Abort")
    return [req]


def call_lib(lib, subset_size, requested_sum, in_arr, in_arr_len, _in_file):
    """Call lib with the parameters given."""
    c_arr = (ctypes.c_uint32 * (in_arr_len + 1))()
    c_arr[:-1] = in_arr
    c_arr_size = ctypes.c_uint32(in_arr_len)
    c_sub_size = ctypes.c_uint32(subset_size)
    c_req_sum = ctypes.c_uint32(requested_sum)
    # get and parse the result
    # TODO: verbose messages in c param
    # t0 = dt.now()
    result = lib.solve_SSP(c_arr,
                           c_arr_size,
                           c_sub_size,
                           c_req_sum)
    # sys.stderr.write("Time spent (within shared lib): {}\n"
    #                  "".format(dt.now() - t0))
    if result[0] == 0:
        # if starts with 0 -> nothing found at all
        # TODO: should be printer in the versbose mode only:
        print("# No results for:\n# IN_FILE: {}; REQ_SUM: "\
              "{}; SUBSET_SIZE: {}".format(_in_file,
                                           requested_sum,
                                           subset_size))
        del lib  # no need to stop iter:
        return False
    # there are our results
    answer = [result[i] for i in range(subset_size)]
    if sum(answer) != requested_sum:
        return False
    print("# The result(s) is/are:")
    print(answer)
    del lib
    # in case if we wanted one combination only,
    # it will halt the program
    return True


def main(input_file, requested_sum):
    """Entry point."""
    args = parse_args()
    # read user input
    in_arr = make_input_arr(input_file)
    in_arr_len = len(in_arr)
    # then find shared lib
    lib_ext = "so" if platform.system != "Windows" else "dll"
    lib_path = os.path.join(os.path.dirname(__file__), "bin",
                            "SSP_lib.{}".format(lib_ext))
    if not os.path.isfile(lib_path):
        sys.exit("Please call make or win_make.bat first")
    subset_sizes = get_subset_sizes(in_arr, requested_sum)
    lib = ctypes.cdll.LoadLibrary(lib_path)
    # convert everyting into C types
    lib.solve_SSP.argtypes = [ctypes.POINTER(ctypes.c_uint32),
                              ctypes.c_uint32,
                              ctypes.c_uint32,
                              ctypes.c_uint32]
    lib.solve_SSP.restype = ctypes.POINTER(ctypes.c_uint32)
    t0 = dt.now()
    f_calls = 0
    if args.subset_size:
        subset_sizes = _make_single_size(args.subset_size, subset_sizes)
    for subset_size in subset_sizes:
        stop_iter = call_lib(lib, subset_size, requested_sum, in_arr, in_arr_len, input_file)
        f_calls += 1
        if stop_iter:
            # we found what we've been looking for
            break
    elapsed = dt.now() - t0
    print("# Time spent within C libraries: {}".format(elapsed))
    print("# Func calls: {}".format(f_calls))

if __name__ == "__main__":
    args = parse_args()
    main(args.input, args.requested_sum)
