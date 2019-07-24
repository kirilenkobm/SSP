# Subset Sum problem

Each problem requires a solution. And the subset sum problem is not an exception.
Here, you can find an algorithm that effectively solves this problem in natural numbers.

## A formal definition of the subset sum problem

- A set of positive integers S is given

- Also given a target X

- Find a subset s ∈ S such as:

```math
\sum_{i=0}^n s_n = X
```

## Usage

### On Linux/MacOS

```shell
git clone git@gitlab.com:kirilenkobm/ssp.git
cd ssp
make
./SSP.py test_input/3.txt 15
```

### On Windows

```powershell
git clone git@gitlab.com:kirilenkobm/ssp.git
cd ssp
.\win_make.bat
python .\SSP.py test_input\3.txt 15
```

The answer for 3.txt should be [8, 3, 3, 1]

Inputs may be generated with generate_input.py

## Contents

- SSP.py - the main script to solve SSP.

- _test.sh and _test.bat - make shared lib and run SSP.py - just in one command

- generate_input.py - script to generate input set, and answers.

- create_test_set.sh - a wrapper around generate_input.py

- perf_tests.ipynb - notebook containing performance and precision tests

## Implementation details and limitations

The main part of the software is implemented in both Python and C.
C code is designed to be compiled as a shared library.
In turn, Python script is wrapped around the shared library, taking care of argument parsing and verification of input.
Actually, the compiled library might be simply used individually, apart from the python script.

The limitations are:

- all input numbers must be positive integers, zeros are allowed but don't make any sense in the context of problem

- number of input elements should not exceed the uint64_t maximal capacity (which is equal to 18446744073709551615)

- each input number also should not exceed the uint64_t capacity

- the most regrettable restriction - input array sum also should not exceed the uint64_t capacity due to the algorithm design

Master script SSP.py and C code don't require any external libraries.
Libraries required to call "generate_input.py" and "perf_tests.ipynb", are listed in the requirements.txt file.

## Explanation

Algorithm explained in detail at:

https://arxiv.org/blalba

## Performance measurements

Complexity in the worst case:

```math
O(N^4)
```

To be done
