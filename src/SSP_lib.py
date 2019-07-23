#!/usr/bin/env python3
"""Python implementation.

Temporary replacement.
To be rewritten in C.
"""
from collections import Counter


class SSP_lib:
    """Class to be replaced with C."""
    def __init__(self, in_arr, req_sum):
        """Init the class."""
        self.in_arr = in_arr
        self.req_sum = req_sum
        self.f_max = [0] + sorted(in_arr, reverse=True)
        self.f_min = [0] + sorted(in_arr)
        self.f_max_acc = self.__accumulate_sum(self.f_max)
        self.f_min_acc = self.__accumulate_sum(self.f_min)
        self.all_available = Counter(in_arr)
        self.all_numbers = sorted(set(self.f_max), reverse=True)

    @staticmethod
    def __accumulate_sum(lst):
        """Return accumulated sum list."""
        if len(lst) == 1:
            return lst
        accumulated_sum = [lst[0]]
        for i in range(1, len(lst)):
            accumulated_sum.append(accumulated_sum[i - 1] + lst[i])
        return accumulated_sum

    @staticmethod
    def flatten(lst):
        """Flatten a list of lists into a list."""
        return [item for sublist in lst for item in sublist]

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

    def __extend_path(self, subset_size, try_path, current, first=False):
        """Try to find another way."""
        path_count = Counter(try_path)
        path = try_path.copy()
        pos_left = subset_size - len(path)
        for i in range(pos_left):
            passed = False
            prev_sum = sum(path)
            current = self.__check_current(current, path_count)
            while not passed:
                if not current:
                    return None
                intermed_val = prev_sum + current
                delta = self.req_sum - intermed_val
                delta_in = delta in self.all_numbers
                # if delta in -> no need to continue

                if delta_in:
                    path.append(current)
                    path.append(delta)
                    return path

                points_left = pos_left - (i + 1)
                sup = self.f_max_acc[points_left]
                inf = self.f_min_acc[points_left]

                if delta > sup:
                    break
                elif delta < inf:
                    current = self.__get_next_size(current)
                    continue
                passed = True
                path.append(current)
                path_count[current] += 1
        if sum(path) != self.req_sum and not first:
            return None
        return path

    def get_answer(self, subset_size):
        """Try to get answer of the size given."""
        # find the first pathway
        start = self.all_numbers[0]
        first_path = self.__extend_path(subset_size, [], start, True)
        if sum(first_path) == self.req_sum:
            # the best case
            return first_path
        # the worst case
        for pointer in range(subset_size - 2, -1, -1):
            pointed = first_path[pointer]
            possible = True
            while possible:
                lower = self.__get_next_size(pointed)
                if not lower:
                    possible = False
                    break
                try_path = first_path[:pointer]
                try_path.append(lower)
                new_res = self.__extend_path(subset_size, try_path, lower)
                pointed = lower
                if not new_res:
                    continue
                return new_res
        return False

if __name__ == "__main__":
    pass
