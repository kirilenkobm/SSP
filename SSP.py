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
from src.SSP_naive import SSP_naive

__author__ = "Bogdan Kirilenko"
__email__ = "kirilenkobm@gmail.com"
__version__ = 0.1

# within the C library everything is uint64_t
UINT64_SIZE = 18446744073709551615


class Leaf_node:
    """Mini-class to hold leaf nodes."""
    def __init__(self):
        """Initiate the node."""
        self.value = 0
        self.max_coords = set()
        self.min_coords = set()

    def __repr__(self):
        """How to represent it."""
        s = "Sum {} | Max coords: {} | Min_coords: {}"
        return s.format(self.value, str(self.max_coords), str(self.min_coords))

    def retrieve(self, f_max, f_min, one=False):
        """Return subset under this node."""
        answer = []
        for elem in self.max_coords:
            slice_ = tuple(sorted(f_max[elem[0]: elem[0] + elem[1]]))
            answer.append(slice_)
            if one:
                return answer[0]
        for elem in self.min_coords:
            slice_ = tuple(sorted(f_min[elem[0]: elem[0] + elem[1]]))
            answer.append(slice_)
            if one:
                return answer[0]
        return set(answer)


class Kirilenko_lib:
    """Class to solve Subset Sum Problem in natural numbers.

    S - input multiset of numbers
    k - number of elements in the set
    X - sum of subset s in S
    """
    def __init__(self, in_file, req_sum, v=False, d=False):
        """Initiate the class."""
        self.in_file = in_file
        self.X = req_sum
        self._verbose = v
        self._get_d = d
        self.answer = None
        self.__make_input_arr()
        self.__make_leaf()
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

    def __configure_lib(self):
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
                                       ctypes.c_bool]
        self.c_v = ctypes.c_bool(self._verbose)
        self.lib.solve_SSP.restype = ctypes.POINTER(ctypes.c_uint64)

    @staticmethod
    def __empty_node(v):
        """Make empty node."""
        return {"sum": v, "max_coords": set(), "min_coords": set()}

    def __retrieve_node(self, node, once=False):
        """Get paths to the node."""
        answer = []
        for elem in node:
            shift = elem[0]
            ind = elem[1]
            dir_ = elem[2]
            if dir_:
                slice_ = tuple(sorted(self.f_max[elem[0]: elem[0] + elem[1]]))
            else:
                slice_ = tuple(sorted(self.f_min[elem[0]: elem[0] + elem[1]]))
            answer.append(slice_)
            if once:
                return answer[0]
        return set(answer)    

    def __make_leaf(self):
        """Create leaf structure.
        
        Seems like to be rewritten in C.
        """
        # self.leaf = defaultdict(Leaf_node)
        # self.leaf = {}
        self.leaf = defaultdict(list)
        self.f_min = self.S[:]
        f_min_acc = accumulate_sum(self.f_min)
        for i, _sum in enumerate(f_min_acc):
            self.leaf[_sum].append((0, i + 1, False))
            if _sum > self.X:
                break

        self.f_min += self.f_min
        self.f_max = self.S[::-1]
        f_max_acc = accumulate_sum(self.f_max)
        for i, _sum in enumerate(f_max_acc):
            if _sum > self.X:
                break
            self.leaf[_sum].append((0, i + 1, True))

        self.f_max += self.f_max
        for shift in range(1, self.k):
            # tt = dt.now()
            f_max_acc = shift_right(f_max_acc)
            f_min_acc = shift_right(f_min_acc)
            # print("Acc: {}".format(dt.now() - tt))
            for i, _sum in enumerate(f_max_acc):
                if _sum > self.X:
                    break
                self.leaf[_sum].append((shift, i + 1, True))
            # tt = dt.now()
            for i, _sum in enumerate(f_min_acc):
                self.leaf[_sum].append((shift, i + 1, False))
                if _sum > self.X:
                    break
            # print("Add: {}".format(dt.now() - tt))
        if self.X in self.leaf.keys():
            # exclude X in S
            self.answer = self.__retrieve_node(self.leaf[self.X], once=True)

    def __call_lib(self, arr, X):
        """Call lib with the parameters given."""
        c_arr = (ctypes.c_uint64 * (len(arr) + 1))()
        c_arr[:-1] = arr
        c_arr_size = ctypes.c_uint64(len(arr))
        c_X = ctypes.c_uint64(X)
        result = self.lib.solve_SSP(c_arr,
                                    c_arr_size,
                                    c_X,
                                    self.c_v)
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
            return self.answer
        # try naïve approach from 0
        self.__configure_lib()
        naive_ans = self.__call_lib(self.S, self.X)
        if naive_ans:
            return naive_ans
        # ok, try going over the list
        all_nodes_ = list(self.leaf.keys())
        # delete nodes that are > X (== not exist)
        for node in all_nodes_:
            if node < self.X:
                continue
            del self.leaf[node]
        del all_nodes_

        self.elems_count = Counter(self.S)
        all_nodes = sorted(self.leaf.keys(), reverse=True)
        for node in all_nodes:
            delta = self.X - node
            ways_to_node = self.__retrieve_node(self.leaf[node])
            for way in ways_to_node:
                way_count = Counter(way)
                s_2_co = self.elems_count - way_count
                s_2 = sorted(flatten([k for _ in range(v)] for k, v in s_2_co.items()))
                if sum(s_2) < delta:
                    # unreachable
                    continue
                sol = self.__call_lib(s_2, delta)
                if not sol:
                    continue
                answer = sol + list(way)
                return answer

def parse_args():
    """Parse and check args."""
    app = argparse.ArgumentParser()
    app.add_argument("input", help="Text file containing input numbers, or stdin stream, "
                                    "just write stdin for that")
    app.add_argument("requested_sum", type=int, help="Sum requested")
    app.add_argument("--subset_size", "-s", type=int, default=0,
                    help="Specify particular size of subset, look only for this")
    app.add_argument("--get_density", "-d", action="store_true", dest="get_density",
                     help="Compute dataset density")
    app.add_argument("--verbose", "-v", action="store_true", dest="verbose",
                     help="Shpw verbose messages.")
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
    del arr[0]
    for i in range(len(arr)):
        arr[i] -= start
    arr.append(end)
    return arr


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


def main(input_file, requested_sum, v, d):
    """Entry point."""
    ssp = Kirilenko_lib(input_file, requested_sum, v, d)
    answer = ssp.solve_ssp()
    ans_str = str(sorted(answer, reverse=True)) if answer else "None"
    print("Subset with sum {}:\n{}".format(sum(answer), ans_str))


if __name__ == "__main__":
    args = parse_args()
    main(args.input, args.requested_sum,
         args.verbose, args.get_density)
