#!/usr/bin/env python3
"""Python implementation.

Temporary replacement.
IS DEPRECATED.
To be rewritten in C.
"""
from collections import Counter

__author__ = "Bogdan Kirilenko"
__email__ = "kirilenkobm@gmail.com"
__version__ = 0.1


class SSP_naive:
    """Naïve SSP solver."""
    def __init__(self, in_arr, req_sum):
        """Init the class."""
        self.in_arr = in_arr
        self.req_sum = req_sum
        self.f_max = [0] + sorted(in_arr, reverse=True)
        self.f_min = [0] + sorted(in_arr)
        self.f_max_acc = accumulate_sum(self.f_max)
        self.f_min_acc = accumulate_sum(self.f_min)
        self.all_available = Counter(in_arr)
        self.all_numbers = sorted(set(self.f_max), reverse=True)

    def __get_next_size(self, current_size):
        """Get the next lesser size."""
        for item in self.all_numbers:
            # the list is sorted, so the first lesser
            # is what we are looking for
            if item < current_size:
                return item
        return None

    def __check_current(self, current, counter):
        """Check if the current value is legit."""
        # TODO: re-implement in C
        used = counter[current]
        available = self.all_available[current]
        if available == used:
            # we used too many Ns, they are not available anymore
            return self.__get_next_size(current)
        # it's ok, we still have it
        if available < used:
            # should never happen, just in case
            err_msg = "Error! Size_path grabbed more {}'s ({}) "\
                      "that are available ({})!"\
                      "".format(current, used, available)
            raise OverflowError(err_msg)
        return current

    @staticmethod
    def __redefine_f_max(f_max, elem):
        """Redefine fmax considering already added elements."""
        elem_ind = f_max.index(elem)
        trimmed_f_mac = f_max[elem_ind + 1:]
        upd_f_max = [0] + trimmed_f_mac
        return upd_f_max

    def _find_path(self, subset_size, try_path, current, first=False):
        """Try to find another way."""
        path_count = Counter(try_path)
        path = try_path.copy()
        pos_left = subset_size - len(path)
        f_max_ = self.f_max.copy()
        f_max_a_ = self.f_max_acc.copy()
        f_min_a_ = self.f_min_acc.copy()
        for i in range(pos_left):
            passed = False
            prev_sum = sum(path)
            current = self.__check_current(current, path_count)
            while not passed:
                if not current:
                    return None if not first else path
                intermed_val = prev_sum + current
                delta = self.req_sum - intermed_val
                points_left = pos_left - (i + 1)
                sup = f_max_a_[points_left]
                inf = f_min_a_[points_left]
                if delta > sup:
                    break
                elif delta < inf:
                    current = self.__get_next_size(current)
                    continue
                passed = True
                path.append(current)
                path_count[current] += 1

                # if delta is available number -> add this
                if delta in self.all_numbers:
                    delta_avail = self.all_available[delta] - path_count[delta]
                    if delta_avail > 0:
                        path.append(delta)
                        return path
        if sum(path) != self.req_sum and not first:
            return None
        return path

    def get_answer(self, subset_size):
        """Try to get answer of the size given."""
        # find the first pathway
        start = self.all_numbers[0]
        first_path = self._find_path(subset_size, [], start, True)
        if sum(first_path) == self.req_sum:
            # the best case
            return first_path
        if not first_path:
            return False
        # the worst case
        for pointer in range(subset_size - 2, -1, -1):
            if pointer >= len(first_path):
                continue
            pointed = first_path[pointer]
            possible = True
            # trying to find path decreasing
            # the pointed value
            while possible:
                lower = self.__get_next_size(pointed)
                if not lower:
                    possible = False
                    break
                try_path = first_path[:pointer]
                try_path.append(lower)
                new_res = self._find_path(subset_size, try_path, lower)
                pointed = lower
                if not new_res:
                    continue
                return new_res
        # unfortunately, nothing was found
        return False


def flatten(lst):
    """Flatten a list of lists into a list."""
    return [item for sublist in lst for item in sublist]


def accumulate_sum(lst):
    """Return accumulated sum list."""
    if len(lst) == 1:
        return lst
    accumulated_sum = [lst[0]]
    for i in range(1, len(lst)):
        accumulated_sum.append(accumulated_sum[i - 1] + lst[i])
    return accumulated_sum


if __name__ == "__main__":
    pass
