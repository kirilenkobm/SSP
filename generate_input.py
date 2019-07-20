#!/usr/bin/env python3
"""Generate inputs and answers."""
import argparse
import os
import sys
import numpy as np

PERF_DIR = os.path.join(os.path.dirname(__file__), "performance")
INPUTS_DIR = os.path.join(PERF_DIR, "inputs")
ANSWERS_DIR = os.path.join(PERF_DIR, "answers")
os.mkdir(INPUTS_DIR) if not os.path.isdir(INPUTS_DIR) else None
os.mkdir(ANSWERS_DIR) if not os.path.isdir(ANSWERS_DIR) else None
N_LO = 10
N_HI = 1000000
FRACT_LO = 0.01
FRACT_HI = 0.95
VAL_LO = 1
VAL_HI = 10000
S_PROP_LO = 0.01
S_PROP_HI = 5
SAMPLES_MAX = 100
DISTR = ["normal", "uniform", "logistic"]


def parse_args():
    """Parse and check args."""
    app = argparse.ArgumentParser()
    app.add_argument("N", type=int, help="Dataset size, from 10 to 1M")
    app.add_argument("fract", type=float, help="Fraction of N that forms answer"
                                               "from 0.01 to 0.95")
    # app.add_argument("distr", type=str, help="Distribution_type, supported:\n"
    #                                          "normal, uniform, logistic")
    app.add_argument("s_prop", type=float, help="Answer sum must be S_PROP * MAX_VAL"
                                                "More or less, from 0.01 to 5")
    app.add_argument("samples", type=int, help="Num of samples to generate, up to 100")
    app.add_argument("name_templ", help="How to call the outputs?")
    args = app.parse_args()
    if args.N < N_LO or args.N > N_HI:
        sys.exit("N is out of borders: [{} {}]".format(N_LO, N_HI))
    if args.fract < FRACT_LO or args.fract > FRACT_HI:
        sys.exit("Fract is out of borders: [{} {}]".format(FRACT_LO, FRACT_HI))
    # if args.distr not in DISTR:
    #     sys.exit("Supported distributions are:\n{}".format(DISTR))
    if args.s_prop < S_PROP_LO or args.s_prop > S_PROP_HI:
        sys.exit("S_prop is out of [{} {}]".format(S_PROP_LO, S_PROP_HI))
    if args.samples < 1 or args.samples > SAMPLES_MAX:
        sys.exit("Samples num requested is out of [{} {}]".format(1, SAMPLES_MAX))
    return args


def gen_ans_base(ans_sum, ans_num):
    """Just create an array for further changes."""
    average = ans_sum // ans_num
    return [average for _ in range(ans_num)]

def mut_base(arr):
    """Mutate answer array preserving the sum."""
    arr_len = len(arr)
    minuses = np.random.randint(0, arr[0], arr_len)
    overall_minus = sum(minuses)
    # overall plus must be equal to overall minus!
    minused_arr = np.array(arr) - minuses
    # now we need somehow add plused values
    pluses_uncorrected_arr = np.random.randint(0, 10 * arr[0], arr_len)
    pluses_corr = []
    plused = 0
    for plus_ in pluses_uncorrected_arr:
        plused_inter = plused + plus_
        if plused_inter < overall_minus:
            pluses_corr.append(plus_)
            plused = plused_inter
            continue
        delta = plused_inter - overall_minus
        last_elem = plus_ - delta
        if last_elem == 0:
            break
        pluses_corr.append(last_elem)
        break
    # and add these pluses to a random subset
    ind_to_plus = np.random.choice(minused_arr, len(pluses_corr), replace=False)
    for i, ind in enumerate(ind_to_plus):
        minused_arr[ind] += pluses_corr[i]
    return minused_arr


def main():
    """Entry point."""
    args = parse_args()
    # form answer and the rest separately
    # in fact, we need the answer only to make sure,
    # that it exists in princible, not necessary created by us
    N_ans = int(args.N * args.fract)
    N_rest = args.N - N_ans
    ans_sum = int(args.s_prop * VAL_HI)
    if ans_sum < N_ans:
        sys.exit("Ans sum is {} and N ans {} which is impossible".format(N_ans, ans_sum))
    ans_base_sample = gen_ans_base(ans_sum, N_ans)
    for s in range(args.samples):
        s_ans_base = ans_base_sample.copy()
        ans_partition = mut_base(s_ans_base)
        answer = sorted(ans_partition, reverse=True)
        rest = np.random.choice(range(int(1.5 * max(answer))), N_rest, replace=True)
        overall = list(answer)
        overall.extend(rest)
        inp_ = [str(x) for x in overall]
        in_file = os.path.join(INPUTS_DIR, "{}_{}".format(s, args.name_templ))
        ans_file = os.path.join(ANSWERS_DIR, "{}_{}".format(s, args.name_templ))
        with open(in_file, "w") as f:
            f.write("\n".join(inp_) + "\n")
        with open(ans_file, "w") as f:
            f.write(str(answer) + "\n")
            f.write("# sum = {}\n".format(ans_sum))
            f.write("# num = {}\n".format(N_ans))

if __name__ == "__main__":
    main()
