#!/usr/bin/env bash
# Just to check if everything works in one command
echo "Make..."
make clean
make
if [[ $? -ne 0 ]]; then
    echo "Make stage failed"
else 
    echo "Make successful"
fi

TEST_1=test_input/1.txt
TEST_2=test_input/2.txt
TEST_3=test_input/3.txt

SSP=./SSP.py
echo "TEST_1 10"
$SSP $TEST_1 10
if [[ $? -ne 0 ]]; then
    echo "Test1 failed"
else 
    echo "Test1 successful"
fi

echo "TEST_1 10 with -s == 4"
$SSP $TEST_1 10 -s 4
if [[ $? -ne 0 ]]; then
    echo "Test1 failed"
else 
    echo "Test1 successful"
fi
