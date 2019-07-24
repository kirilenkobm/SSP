# Subset Sum problem

Each problem requires a solution.

A formal definition of the subset sum problem is:

```math
A set of integers S is given

Also given a target X

Find a subset s ∈ S such as \sum_{i=0}^n s_n = X

```

## Usage

On Linux/MacOS:

```shell
git clone git@gitlab.com:kirilenkobm/ssp.git
cd ssp
make
./SSP.py test_input/3.txt 2 15
```

On Windows:

```powershell
git clone git@gitlab.com:kirilenkobm/ssp.git
cd ssp
.\win_make.bat
python .\SSP.py test_input\3.txt 2 15
```

The answer for 3.txt should be [8, 3, 3, 1]

Inputs may be generated with generate_input.py

## Contents

- SSP.py - the main script to solve SSP.

- _test.sh and _test.bat - make shared lib and run SSP.py - just to do it in one command

- generate_input.py - script to generate input set, and answers.

- create_test_set.sh - a wrapper around generate_input.py

- perf_tests.ipynb - notebook containing performance and precision tests

## Explanation

Algorithm explained in detail at:

https://arxiv.org/blalba

## Performance measurements

Complexity in the worst case:

```math
O(N^4)
```

To be done
