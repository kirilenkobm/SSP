#!/usr/bin/env python3
"""Generate inputs and answers."""
import argparse
import os
import sys
import subprocess
import numpy as np
import scipy.stats as ss

PERF_DIR = os.path.join(os.path.dirname(__file__), "performance")
INPUTS_DIR = os.path.join(PERF_DIR, "inputs")
ANSWERS_DIR = os.path.join(PERF_DIR, "answers")
os.mkdir(INPUTS_DIR) if not os.path.isdir(INPUTS_DIR) else None
os.mkdir(ANSWERS_DIR) if not os.path.isdir(ANSWERS_DIR) else None
# some constants
# input array size borders
N_min = 1
N_max = 1000000
# number borders
I_min = 1
I_max = 100000


def parse_args():
    """Parse and check args."""
    app = argparse.ArgumentParser()
    app.add_argument("N", type=int, help="Input sample size. Also you can "
                                         "call with 'clean' as the fitst "
                                         "argument to delete all previously "
                                         "generated inputs.")
    app.add_argument("n", type=int, help="Take n first elems to get sum "
                                         "that really exists")
    app.add_argument("std_scale", type=int)
    app.add_argument("samples", type=int, help="Num of samples")
    app.add_argument("name_templ", help="Template for output filename")
    args = app.parse_args()
    if args.N < N_min or args.N > N_max:
        sys.exit("Error: N is out of [{} {}]".format(N_min, N_max))
    elif args.n < 2 or args.n >= args.N:
        sys.exit("Error: n (lowercase) must be in "
                 "[{} {}]".format(2, args.N - 1))
    elif args.std_scale < 1:
        sys.exit("std scale expected to be >= 1")
    return args

def main():
    """Entry point."""
    args = parse_args()
    for s in range(args.samples):
        rnd_sample = np.random.normal(scale=args.std_scale, size=args.N)
        rnd_sample_int = [int(x) + 1 for x in abs(np.round(rnd_sample))]
        sum_forms = sorted(rnd_sample_int[:args.n], reverse=True)
        ans_sum = sum(sum_forms)
        filename = "{}_{}".format(s, args.name_templ)
        in_path = os.path.join(INPUTS_DIR, filename)
        ans_path = os.path.join(ANSWERS_DIR, filename)
        with open(ans_path, "w") as f:
            f.write("{}\n".format(str(sum_forms)))
            f.write("Sum = {}\n".format(ans_sum))
            f.write("Sum_len = {}\n".format(len(sum_forms)))
        in_str = [str(n) for n in rnd_sample_int]
        with open(in_path, "w") as f:
            f.write("\n".join(in_str) + "\n")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "clean":
        subprocess.call("rm {}/* ".format(INPUTS_DIR), shell=True)
        subprocess.call("rm {}/* ".format(ANSWERS_DIR), shell=True)
        sys.exit("Cleaned")
    main()
