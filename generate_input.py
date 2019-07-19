#!/usr/bin/env python3
"""Generate input for subset sum problem."""
import argparse
import sys
import numpy as np

__author__ = "Bogdan Kirilenko"
__email__ = "kirilenkobm@gmail.com"
__version__ = 0.1

# lol
UINT32_SIZE = 4294967295

def parse_args():
    """Parse and check args."""
    app = argparse.ArgumentParser()
    app.add_argument("val_num", type=int, help="Output size, "
                     "should not exceed uint32_t max value")
    app.add_argument("output", help="Save to...")
    app.add_argument("--upp_bounder", "-u", type=int, default=100,
                     help="Max value, should not exceed uint32_max value;"
                     " default 1000")
    # TODO: add different types of distribution
    # TODO: maybe more complicated version that will
    # also show correct answers for further check
    args = app.parse_args()
    if args.val_num <= 1:
        sys.exit("val_num should be >= 2")
    elif args.val_num > UINT32_SIZE:
        sys.exit("Too huge val_num, max possible is {}"
                 "".format(UINT32_SIZE))
    if args.upp_bounder > UINT32_SIZE:
        sys.exit("Too high upper boundary, should not exceed {}"
                 "".format(UINT32_SIZE))
    return args
    

def main():
    """Entry point."""
    args = parse_args()
    sample = np.random.randint(1,
                               high=args.upp_bounder,
                               size=args.val_num,
                               dtype='l')
    out_std = args.output == "stdout"
    f = open(args.output, "r") if not out_std else sys.stdout
    f.write("\n".join([str(n) for n in sample]) + "\n")
    f.close() if not out_std else None

if __name__ == "__main__":
    main()
