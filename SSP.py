#!/usr/bin/env python3
"""Solve subset sum problem."""
import argparse
import sys
import os
import platform
from collections import defaultdict
from collections import Counter
from datetime import datetime as dt
from math import log
import ctypes

__author__ = "Bogdan Kirilenko"
__email__ = "kirilenkobm@gmail.com"
__version__ = 0.1

# within the C library everything is uint64_t
UINT64_SIZE = 18446744073709551615


class SSP_lib:
    """Class to solve Subset Sum Problem in natural numbers.

    S - input multiset of numbers
    k - number of elements in the set
    X - sum of subset s in S
    """
    def __init__(self, in_file, req_sum, v=False, d=False, deep=False,
                 ext_v=False):
        """Initiate the class."""
        self.in_file = in_file
        self.X = req_sum
        self._verbose = v
        self._get_d = d
        self.answer = None
        self._deep = deep
        self._ext_v = ext_v
        self.__make_input_arr()
        self.f_min = self.S[:]
        self.f_min += self.f_min
        self.f_max = self.S[::-1]
        self.f_max += self.f_max
        self.elems_count = Counter()
        self._lib_calls = 0
        self._shifts_num = 0
        self._on_leaf = False

    @staticmethod
    def __do_nothing(*args):
        """Just do nothing.
        
        To mask methods if needed.
        """
        pass

    def __v(self, msg, end="\n"):
        """Print a verbose message."""
        sys.stderr.write(msg + end) if self._verbose else None

    def __make_input_arr(self):
        """Read input and check it."""
        in_is_stdin_stream = self.in_file == "stdin"
        f = open(self.in_file) if not in_is_stdin_stream else sys.stdin
        try:
            numbers = sorted([int(x.rstrip()) for x in f.readlines()])
        except ValueError:  # there was something non-numeric!
            sys.exit("Error: in input, numeric values expected.")
        finally:  # Q: will it work after sys.exit()?
            f.close()
        self.S = numbers
        # check for boundaries
        if any(x < 0 for x in numbers):
            sys.exit("Sorry, but for now works for non-negative"
                    " numbers only.")
        elif any(x > UINT64_SIZE for x in numbers):
            sys.exit("Sorry, but input number size is limited"
                    " to uint64_t capacity")
        # check limits
        tot_sum = sum(numbers)
        arr_len = len(numbers)
        min_elem = numbers[0]
        max_elem = numbers[-1]

        if self._get_d or self._verbose:
            # we were reqested to print dataset density
            dens = arr_len / log(max_elem, 2)
            print(f"# Dataset density is:\n# {dens}")
        if tot_sum > UINT64_SIZE:
            sys.exit(f"Error: overall input sum should not exceed "
                     "the uint64_t capacity, got {tot_sum}")
        elif self.X > tot_sum:
            sys.exit(f"Requested sum {self.X} > overall sum of the array {tot_sum}, abort")
        elif self.X < min_elem:
            sys.exit(f"Requested sum {self.X} < smallest element in the array {min_elem}, abort")
        elif self.X in numbers:
            print("Requested sum is in S")
            self.answer = [self.X]
            return

        self.k = len(numbers)
        self.__v(f"# /V: Input array of size {self.k}")
        self.__v(f"# /V: Array sum {tot_sum}")
        self.__v(f"# /V max_val: {max_elem}, min_val: {min_elem}")

    def __configure_solver_lib(self):
        """Find the lib and configure it."""
        lib_ext = "so" if platform.system != "Windows" else "dll"
        lib_path = os.path.join(os.path.dirname(__file__), "bin",
                                "SSP_lib.{}".format(lib_ext))
        if not os.path.isfile(lib_path):
            sys.exit("Please call make or win_make.bat first")
        self.lib = ctypes.cdll.LoadLibrary(lib_path)
        # convert everyting into C types
        self.lib.solve_SSP.argtypes = [ctypes.POINTER(ctypes.c_uint64),
                                       ctypes.c_uint64,
                                       ctypes.c_uint64,
                                       ctypes.c_bool,
                                       ctypes.c_bool]
        self.c_v = ctypes.c_bool(self._verbose)
        self.c_d = ctypes.c_bool(self._deep)
        self.lib.solve_SSP.restype = ctypes.POINTER(ctypes.c_uint64)

    def __call_solver_lib(self, arr, X, ext_v=False):
        """Call lib with the parameters given."""
        self._lib_calls += 1
        c_arr = (ctypes.c_uint64 * (len(arr) + 1))()
        c_arr[:-1] = arr
        c_arr_size = ctypes.c_uint64(len(arr))
        c_X = ctypes.c_uint64(X)
        # c_ext_v = ctypes.c_bool(ext_v)
        result = self.lib.solve_SSP(c_arr,
                                    c_arr_size,
                                    c_X,
                                    self.c_v,
                                    self.c_d)
        # get everything except 0; check the answer
        _answer = []
        for elem in result:
            _answer.append(elem) if elem != 0 else None
            if elem == 0:
                break
        if sum(_answer) != X:
            return None
        # answer is correct
        return _answer

    def solve_ssp(self):
        """Get answer."""
        if self.answer is not None:
            # answer already found
            self.__v("# /V: Answer is obvious")
            return self.answer
        # try naïve approach from 0
        self.__configure_solver_lib()
        naive_ans = self.__call_solver_lib(self.S, self.X, self._ext_v)
        self.answer = naive_ans
        return self.answer


def parse_args():
    """Parse and check args."""
    app = argparse.ArgumentParser()
    app.add_argument("input", help="Text file containing input numbers, or stdin stream, "
                                    "just write stdin for that")
    app.add_argument("requested_sum", type=int, help="Sum requested")
    app.add_argument("--subset_size", "-s", type=int, default=0,
                    help="Specify particular size of subset, look only for this")
    app.add_argument("--get_density", "--gd", action="store_true", dest="get_density",
                     help="Compute dataset density")
    app.add_argument("--deep", "-d", action="store_true", dest="deep",
                     help="Include deep target search, drastically increases "
                          "the runtime")
    app.add_argument("--verbose", "-v", action="store_true", dest="verbose",
                     help="Show verbose messages.")
    app.add_argument("--ext_out", "-e", action="store_true", dest="ext_out")
    if len(sys.argv) < 3:
        app.print_help()
        sys.exit()
    args = app.parse_args()
    if args.requested_sum < 0:
        sys.exit("Requested sum cannot be negative")
    return args


def shift_right(arr):
    """Shift accumulated sum."""
    start = arr[0]
    end = arr[-1]
    ans = [e - start for e in arr[1:]]
    ans.append(end)
    return ans


def accumulate_sum(lst):
    """Return accumulated sum list."""
    if len(lst) == 1:
        return lst
    accumulated_sum = [lst[0]]
    for i in range(1, len(lst)):
        accumulated_sum.append(accumulated_sum[i - 1] + lst[i])
    return accumulated_sum


def flatten(lst):
    """Flatten a list of lists into a list."""
    return [item for sublist in lst for item in sublist]


def eprint(msg, end="\n"):
    """Print for stderr."""
    sys.stderr.write(msg + end)


def main(input_file, requested_sum, v, dens, deep, ext_out):
    """Entry point."""
    t0 = dt.now()
    ssp = SSP_lib(input_file, requested_sum, v,
                  dens, deep, ext_out)
    answer = ssp.solve_ssp()
    ans_str = str(sorted(answer, reverse=True)) if answer else "None"
    if answer:
        assert sum(answer) == requested_sum
    print("# Answer is:\n{}".format(ans_str))
    if ext_out:
        print("# /E: Lib calls: {}".format(ssp._lib_calls))
        print("# /E: Commited shifts: {}".format(ssp._shifts_num))
        print("# /E: Elapsed time: {}".format(dt.now() - t0))
        print("# /E: Answer on leaf node: {}".format(ssp._on_leaf))


if __name__ == "__main__":
    args = parse_args()
    main(args.input, args.requested_sum,
         args.verbose, args.get_density,
         args.deep, args.ext_out)
