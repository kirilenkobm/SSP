#!/usr/bin/env python3
"""Generate inputs and answers."""
import argparse
import os
import sys
import subprocess
import numpy as np
from datetime import datetime as dt
import scipy.stats as ss

PERF_DIR = os.path.join(os.path.dirname(__file__), "performance")
INPUTS_DIR = os.path.join(PERF_DIR, "inputs")
ANSWERS_DIR = os.path.join(PERF_DIR, "answers")
os.mkdir(INPUTS_DIR) if not os.path.isdir(INPUTS_DIR) else None
os.mkdir(ANSWERS_DIR) if not os.path.isdir(ANSWERS_DIR) else None
# some constants
# input array size borders
N_min = 1
N_max = 4294967296


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
    app.add_argument("--uniform", "-u", action="store_true", dest="uniform",
                     help="Create uniformly distributed set.")
    app.add_argument("--versbose", "-v", action="store_true", dest="versbose",
                     help="Show verbose messages")
    if len(sys.argv) < 5:
        app.print_help()
        sys.exit()
    args = app.parse_args()
    if args.N < N_min or args.N > N_max:
        sys.exit("Error: N is out of [{} {}]".format(N_min, N_max))
    elif args.n < 2 or args.n >= args.N:
        sys.exit("Error: n (lowercase) must be in "
                 "[{} {}]".format(2, args.N - 1))
    elif args.std_scale < 1:
        sys.exit("std scale expected to be >= 1")
    return args


def eprint(msg, end="\n"):
    """Print to stderr."""
    sys.stderr.write(msg + end)


def main():
    """Entry point."""
    t0 = dt.now()
    args = parse_args()
    for s in range(args.samples):
        # TODO: also try uniform distribution, make an option
        eprint("# Sample {} / {} in progress".format(s + 1, args.samples))
        if not args.uniform:
            rnd_sample = np.random.normal(scale=args.std_scale, size=args.N)
            rnd_sample_int = [int(x) + 1 for x in abs(np.round(rnd_sample))]
        else:
            low = args.std_scale / 100
            high = args.std_scale
            rnd_sample = np.random.uniform(low=low, high=high, size=args.N)
            rnd_sample_int = [int(x) + 1 for x in abs(np.round(rnd_sample))]
        eprint("# Got random numbers")
        sum_forms = sorted(rnd_sample_int[:args.n], reverse=True)
        ans_sum = sum(sum_forms)
        filename = "{}_{}".format(s, args.name_templ)
        in_path = os.path.join(INPUTS_DIR, filename)
        ans_path = os.path.join(ANSWERS_DIR, filename)
        _distr = "Norm" if not args.uniform else "Uni"
        eprint("# Saving the results...")
        with open(ans_path, "w") as f:
            f.write("{}\n".format(str(sum_forms)))
            f.write("Sum = {}\n".format(ans_sum))
            f.write("Sum_len = {}\n".format(len(sum_forms)))
            f.write("Distr = {}\n".format(_distr))
        in_str = [str(n) for n in rnd_sample_int]
        with open(in_path, "w") as f:
            f.write("\n".join(in_str) + "\n")
    eprint("The set was generated in {}".format(dt.now() - t0))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "clean":
        subprocess.call("rm {}/* ".format(INPUTS_DIR), shell=True)
        subprocess.call("rm {}/* ".format(ANSWERS_DIR), shell=True)
        sys.exit("Cleaned")
    main()
