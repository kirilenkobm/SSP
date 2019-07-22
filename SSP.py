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


class SSP:
    """Subset Sum Problem Solver."""
    def __init__(self, in_file, req_sum, subset_size=0, v=False):
        """Initiate the class."""
        self.in_file = in_file
        self.requested_sum = req_sum
        self._verbose = v
        self.subset_size = subset_size
        self.answer = None
        self.__make_input_arr()
        self.__get_subset_sizes()
        self.__configure_lib()
    
    @staticmethod
    def __do_nothing(*args):
        """Just do nothing."""
        pass

    def __v(self, msg):
        """Print a verbose message."""
        sys.stderr.write(msg + "\n") if self._verbose else None

    def __make_input_arr(self):
        """Read input and check it."""
        in_is_stdin_stream = self.in_file == "stdin"
        f = open(self.in_file) if not in_is_stdin_stream else sys.stdin
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
        tot_sum = sum(numbers)
        if tot_sum > UINT32_SIZE:
            sys.exit("Overall array sum is too big, it will overflow")
        elif self.requested_sum > tot_sum:
            sys.exit("Requested sum > overall sum of the array, abort")
        self.in_arr = numbers
        self.in_arr_len = len(numbers)
        self.__v("# Input array of size {}".format(self.in_arr_len))

    def __get_subset_sizes(self):
        """Get subset sizes to check."""
        f_min = self.in_arr.copy()
        f_max = self.in_arr[::-1]
        f_min_acc = self.accumulate_sum(f_min)
        f_max_acc = self.accumulate_sum(f_max)
        # find the first elem what's bigger
        subset_sizes = []
        # 1 is deleted, should be specially noted
        for sub_size in range(1, len(f_max_acc)):
            inf = f_min_acc[sub_size]
            sup = f_max_acc[sub_size]
            if self.requested_sum == inf:
                # the problem is actually solved
                # better to wrap in a class;
                # TODO: make it fancier
                self.answer = f_min[:sub_size + 1][::-1]
                self.__configure_lib = self.__do_nothing
            elif self.requested_sum == sup:
                self.answer = f_max[:sub_size + 1][::-1]
                self.__configure_lib = self.__do_nothing
            elif inf < self.requested_sum < sup:
                subset_sizes.append(sub_size + 1)
        self.subset_sizes = subset_sizes
        self.__v("# Will try {} subset sizes".format(len(subset_sizes)))

    def __configure_lib(self):
        """Find the lib and configure it."""
        lib_ext = "so" if platform.system != "Windows" else "dll"
        lib_path = os.path.join(os.path.dirname(__file__), "bin",
                                "SSP_lib.{}".format(lib_ext))
        if not os.path.isfile(lib_path):
            sys.exit("Please call make or win_make.bat first")
        self.lib = ctypes.cdll.LoadLibrary(lib_path)
        # convert everyting into C types
        self.lib.solve_SSP.argtypes = [ctypes.POINTER(ctypes.c_uint32),
                                       ctypes.c_uint32,
                                       ctypes.c_uint32,
                                       ctypes.c_uint32,
                                       ctypes.c_bool]
        self.lib.solve_SSP.restype = ctypes.POINTER(ctypes.c_uint32)

    @staticmethod
    def accumulate_sum(lst):
        """Just accumulate a sum of array."""
        """Return accumulated sum list."""
        if len(lst) == 1:
            return lst
        accumulated_sum = [lst[0]]
        for i in range(1, len(lst)):
            accumulated_sum.append(accumulated_sum[i - 1] + lst[i])
        return accumulated_sum

    @staticmethod
    def __make_single_size(req, available):
        """Check if requested elem len is possible."""
        if req < available[0] or req > available[-1]:
            print("# Impossible to find combination of length {}".format(req))
            print("# Please use one of these for this input:\n{}".format(str(available)))
            sys.exit("Abort")
        return [req]

    def __call_lib(self, subset_size):
        """Call lib with the parameters given."""
        self.__v("# Trying subset size: {}".format(subset_size))
        c_arr = (ctypes.c_uint32 * (self.in_arr_len + 1))()
        c_arr[:-1] = self.in_arr
        c_arr_size = ctypes.c_uint32(self.in_arr_len)
        c_sub_size = ctypes.c_uint32(subset_size)
        c_req_sum = ctypes.c_uint32(self.requested_sum)
        c_v = ctypes.c_bool(self._verbose)
        # get and parse the result
        result = self.lib.solve_SSP(c_arr,
                                    c_arr_size,
                                    c_sub_size,
                                    c_req_sum,
                                    c_v)
        _answer = [result[i] for i in range(subset_size)]
        # if starts with 0 -> nothing found at all
        if _answer[0] == 0 or sum(_answer) != self.requested_sum:
            msg_ = "No results for:\n IN FILE: {} REQ_SUM: {}" \
                  " SUBSET_SIZE: {}".format(self.in_file,
                                            self.requested_sum,
                                            subset_size)
            self.__v(msg_)
            del self.lib  # no need to stop iter:
            self.__configure_lib()
            return False
        self.__v("# Found result at subset size {}".format(subset_size))
        del self.lib
        self.answer = _answer
        return True  # signal to stop

    def solve_ssp(self):
        """Get answer."""
        if self.answer is not None:
            # already known
            return self.answer
        f_calls = 0
        if self.subset_size != 0:
            self.__v("# One subset size was specified: {}".format(args.subset_size))
            self.subset_sizes = self.__make_single_size(self.subset_size,
                                                        self.subset_sizes)
        for subset_size in self.subset_sizes:
            stop_iter = self.__call_lib(subset_size)
            f_calls += 1
            if stop_iter:  # stop, we found what we need
                break
        self.__v("# Shared lib called {} times".format(f_calls))
        return self.answer

def parse_args():
    """Parse and check args."""
    app = argparse.ArgumentParser()
    app.add_argument("input", help="Text file containing input numbers, or stdin stream, "
                                    "just write stdin for that")
    app.add_argument("requested_sum", type=int, help="Sum requested")
    app.add_argument("--subset_size", "-s", type=int, default=0,
                     help="Specify particular size of subset, look only for this")
    app.add_argument("--verbose", "-v", action="store_true", dest="verbose",
                     help="Shpw verbose messages.")
    if len(sys.argv) < 3:
        app.print_help()
        sys.exit()
    args = app.parse_args()
    if args.requested_sum < 0:
        sys.exit("Requested sum cannot be negative")
    return args


def main(input_file, requested_sum, subset_size, v):
    """Entry point."""
    ssp = SSP(input_file, requested_sum, subset_size, v)
    answer = ssp.solve_ssp()
    print("The answer is:\n{}".format(str(answer)))
    

if __name__ == "__main__":
    args = parse_args()
    main(args.input, args.requested_sum,
         args.subset_size, args.verbose)
