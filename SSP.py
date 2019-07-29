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


class Kirilenko_lib:
    """Class to solve Subset Sum Problem in natural numbers.

    S - input multiset of numbers
    k - number of elements in the set
    X - sum of subset s in S
    """
    def __init__(self, in_file, req_sum, v=False, d=False, deep=False, naive=False):
        """Initiate the class."""
        self.in_file = in_file
        self.X = req_sum
        self._verbose = v
        self._get_d = d
        self.answer = None
        self._deep = deep
        self._naive = naive
        self.__make_input_arr()
        self.f_min = self.S[:]
        self.f_min += self.f_min
        self.f_max = self.S[::-1]
        self.f_max += self.f_max
        self.elems_count = Counter()

    @staticmethod
    def __do_nothing(*args):
        """Just do nothing."""
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

        if self._get_d:
            # we were reqested to print dataset density
            dens = arr_len / log(max_elem, 2)
            print("# Dataset density is:\n# {}".format(dens))
        if tot_sum > UINT64_SIZE:
            sys.exit("Error: overall input sum should not exceed "
                     "the uint64_t capacity, got {}".format(tot_sum))
        elif self.X > tot_sum:
            sys.exit("Requested sum {} > overall sum of the array {}, "
                     "abort".format(self.X, tot_sum))
        elif self.X < min_elem:
            sys.exit("Requested sum {} < smallest element in the array {}, "
                     "abort".format(self.X, min_elem))
        elif self.X in numbers:
            print("Requested sum is in S")
            self.answer = [self.X]
            return
        self.S = numbers
        self.k = len(numbers)
        self.__v("# Input array of size {}".format(self.k))

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

    def __call_solver_lib(self, arr, X):
        """Call lib with the parameters given."""
        c_arr = (ctypes.c_uint64 * (len(arr) + 1))()
        c_arr[:-1] = arr
        c_arr_size = ctypes.c_uint64(len(arr))
        c_X = ctypes.c_uint64(X)
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
            self.__v("# Answer is obvious")
            return self.answer
        # try naïve approach from 0
        self.__configure_solver_lib()
        naive_ans = self.__call_solver_lib(self.S, self.X) if self._naive else None
        self.__v("# Trying naïve approach first...") if self._naive else None
        if naive_ans:
            self.__v("# Naïve approach returned the answer")
            self.answer = naive_ans
            return self.answer
        # ok, try going over the list
        self.elems_count = Counter(self.S)
        f_max_acc = accumulate_sum(self.f_max)
        f_max_len = len(f_max_acc)
        already_checked = set()

        for shift in range(self.k):
            self.__v("# Trying shift {}".format(shift))
            for i, node in enumerate(f_max_acc[::-1]):
                if node in already_checked:
                    print("SKIPPED {}".format(node))
                    continue
                already_checked.add(node)
                ind = f_max_len - i
                self.__v("# shift {} index {}".format(shift, ind))
                delta = self.X - node
                # ways_to_node = self.__retrieve_node(self.leaf[node])
                way_to_node = self.f_max[shift: shift + ind]
                way_count = Counter(way_to_node)
                s_2_co = self.elems_count - way_count
                s_2 = sorted(flatten([k for _ in range(v)] for k, v in s_2_co.items()))
                if sum(s_2) < delta:
                    # unreachable
                    continue
                sol = self.__call_solver_lib(s_2, delta)
                if not sol:
                    continue
                self.answer = sol + list(way_to_node)
                return self.answer
            f_max_acc = shift_right(f_max_acc)


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
    app.add_argument("--verbose", "-v", action="store_true", dest="verbose",
                     help="Shpw verbose messages.")
    app.add_argument("--deep", "-d", action="store_true", dest="deep",
                     help="Include deep target search, drastically increases "
                          "the runtime")
    app.add_argument("--naive", "-n", action="store_true", dest="naive",
                     help="Try to find result without the lead")
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


def main(input_file, requested_sum, v, dens, deep, naive):
    """Entry point."""
    ssp = Kirilenko_lib(input_file, requested_sum, v, dens, deep, naive)
    answer = ssp.solve_ssp()
    ans_str = str(sorted(answer, reverse=True)) if answer else "None"
    assert sum(answer) == requested_sum
    print("# Answer with sum {}:\n{}".format(sum(answer), ans_str))


if __name__ == "__main__":
    args = parse_args()
    main(args.input, args.requested_sum,
         args.verbose, args.get_density,
         args.deep, args.naive)
