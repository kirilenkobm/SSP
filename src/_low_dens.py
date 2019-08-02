"""Temporary python replacement for low density cases."""
from itertools import islice


class SSP_low_density:
    """Class to solve SSP at low density."""
    def __init__(self, S, X):
        """Entry point."""
        self.S = sorted(S)
        self.k = len(S)
        self.X = X
        self.f_min = S.copy()
        self.f_max = self.f_min[::-1]
        self.f_min_a = accumulate_sum(self.f_min)
        self.f_max_a = accumulate_sum(self.f_max)
        self.answer = None
        self.__get_subset_sizes()

    def __get_subset_sizes(self):
        """Get possible subset sizes."""
        self.sub_sizes = []
        for i in range(self.k):
            sub_size = i
            sup = self.f_max_a[i]
            inf = self.f_min_a[i]
            if self.X == sup:
                self.answer = self.f_max[:i + 1]
                return
            elif self.X == inf:
                self.answer = self.f_min[:i + 1]
                return
            elif inf < self.X < sup:
                self.sub_sizes.append(sub_size)

    def __get_chain_ind(self, sub_size):
        """Get chain for analysys."""
        chain_ind = []
        for i in range(self.k - sub_size + 1):
            w_i = self.f_min[i: i + sub_size]
            w_i_sum = sum(w_i)
            if w_i_sum < self.X:
                chain_ind = list(range(i, i + sub_size))
            elif w_i_sum == self.X:
                self.answer = w_i
                return None
            else:
                break
        return chain_ind

    def get_answer(self):
        """Just return the answer."""
        if self.answer:
            return self.answer
        for sub_size in self.sub_sizes:
            chain_ind = self.__get_chain_ind(sub_size)
            if chain_ind is None:
                return self.answer
            


def accumulate_sum(lst):
    """Return accumulated sum list."""
    if len(lst) == 1:
        return lst
    accumulated_sum = [lst[0]]
    for i in range(1, len(lst)):
        accumulated_sum.append(accumulated_sum[i - 1] + lst[i])
    return accumulated_sum


def window(seq, n):
    """Sliding window over the seq."""
    it = iter(seq)
    result = tuple(islice(it, n))
    if len(result) == n:
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result


def mean(arr):
    """Just return mean value."""
    return sum(arr) / len(arr)
