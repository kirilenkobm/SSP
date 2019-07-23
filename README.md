# Subset Sum problem

Each problem requires a solution, and 

## Usage

On Linux/MacOS:

```shell
git clone git@gitlab.com:kirilenkobm/ssp.git
cd ssp
make
./SSP.py test_input/3.txt 2 9
```

On windows:

```powershell
git clone git@gitlab.com:kirilenkobm/ssp.git
cd ssp
.\win_make.bat
python .\SSP.py test_input\3.txt 2 9
```

The answer for 3.txt should be [4, 5] and [3, 6]

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
