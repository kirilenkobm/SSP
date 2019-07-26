"""Temporary Python replacement.

To be rewritten in C later.
"""
import sys
from collections import defaultdict
from collections import Counter
from src.SSP_naive import SSP_naive


class SSP_solver:
    """Solve SSP."""
    def __init__(self, in_arr, req_sum, sub_sizes):
        """Entry point."""
        self.in_arr = in_arr
        self.req_sum = req_sum
        self.sub_sizes = sub_sizes
        self.f_max_0 = sorted(in_arr, reverse=True)
        self.f_min_0 = sorted(in_arr)
        self.__make_f_arrs()
        self.__prepare_leaf()
    
    def __make_f_arrs(self):
        """Create a leaf."""
        self.f_max_N = []
        self.f_max_N.append(self.f_max_0)
        self.f_min_N = []
        self.f_min_N.append(self.f_min_0)
        self.f_max_A = []
        self.f_min_A = []
        for shift in range(1, len(self.f_max_0)):
            shifted_max = _shift(self.f_max_N[shift - 1])
            self.f_max_N.append(shifted_max)
            shifted_min = _shift(self.f_min_N[shift - 1])
            self.f_min_N.append(shifted_min)
        for i in range(len(self.f_max_N)):
            self.f_max_A.append(accumulate_sum([0] + self.f_max_N[i]))
            self.f_min_A.append(accumulate_sum([0] + self.f_min_N[i]))

    def __prepare_leaf(self):
        """Prepare all stuff to go."""
        self.sum_paths = defaultdict(list)
        for i in range(len(self.f_max_A)):
            path_id = i  # for f_min differently
            path = self.f_max_A[i]
            for s_ in path:
                self.sum_paths[s_].append(path_id)
            n_path_id = -1 * i if i != 0 else -1 * len(self.f_max_A)
            n_path = self.f_min_A[i]
            for s_ in n_path:
                self.sum_paths[s_].append(n_path_id)
        self.num_count = Counter(self.f_max_0)

    def __get_raw_paths(self, path_ids):
        """For a list of path ids return paths."""
        paths = []
        for path_id in path_ids:
            if path_id < 0:
                # negative path
                null_id = -1 * len(self.f_max_A)
                n_path_id = -1 * path_id if path_id != null_id else 0
                path_acc = self.f_min_A[n_path_id]
                req_sum_ind = path_acc.index(self.req_sum)
                paths.append(self.f_min_N[n_path_id][:req_sum_ind])
            else:  # positive id -> fmax derevative
                path_acc = self.f_max_A[path_id]
                req_sum_ind = path_acc.index(self.req_sum)
                paths.append(self.f_max_N[path_id][:req_sum_ind])
        return paths

    def get_answer(self):
        """Return the answer, if possible."""
        # try a naïve approach
        # naive_solver = SSP_naive(self.in_arr, self.req_sum)
        # for size in self.sub_sizes:
        #     naive_answer = naive_solver.get_answer(size)
        #     if not naive_answer:
        #         continue
        #     return naive_answer
        # naive approach didn't wotk
        # let's use the advanced one
        if self.req_sum in self.sum_paths.keys():
            # we already know the answer:
            path_ids = self.sum_paths[self.req_sum]
            return self.__get_raw_paths(path_ids)
        # not good, but terrible
        print("We are here")
        # find anchor points that fit
        path_delta = []
        for item in self.sum_paths.keys():
            if item > self.req_sum:
                continue
            delta = self.req_sum - item
            path_delta.append((item, delta))
        delta_sort = sorted((x for x in path_delta), key=lambda x: x[1])
        # go from one point to another
        elems_set = set(self.num_count.keys())
        for elem in delta_sort:
            s_1 = elem[0]
            path_id = sorted(self.sum_paths[s_1])
            path_a = self.f_max_A[path_id[-1]]
            s_1_ind = path_a.index(s_1)
            f_max_ = self.f_max_N[path_id[-1]][:s_1_ind]
            delta = elem[1]
            s_2_candidates = elems_set.difference(p for p in elems_set if p > delta)
            s_2_candidates = sorted(s_2_candidates.difference(f_max_))
            if sum(s_2_candidates) < delta:
                continue
            # let's put in in the naïve solver
            naive_solver = SSP_naive(s_2_candidates, delta)
            for s_size in range(3, len(s_2_candidates) - 1):
                naive_sol = naive_solver.get_answer(s_size)
                if not naive_sol:
                    continue
                ans = naive_sol + f_max_
                print(ans)
                print(sum(ans))
                print(Counter(ans).most_common(10))
                exit()
        return []

def _shift(seq):
    """Return 1-step shifted sequence."""
    sh_seq = []
    for i in range(1, len(seq)):
        sh_seq.append(seq[i])
    sh_seq.append(seq[0])
    return sh_seq


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


if __name__ == "__main__":
    pass
