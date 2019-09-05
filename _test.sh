#!/usr/bin/env bash
# Just to check if everything works in one command
echo "Make..."
make clean
make
if [[ $? -ne 0 ]]; then
    echo "Make stage failed"
    exit
else 
    echo "Make successful"
fi

TEST_1=test_input/1.txt
TEST_2=test_input/2.txt
TEST_3=test_input/3.txt
TEST_4=test_input/4.txt

SSP=./SSP.py
echo "### TEST_1"
echo "### Must return [8, 4] or equivalent"
$SSP $TEST_1 12
if [[ $? -ne 0 ]]; then
    echo "Test 1 failed"
    exit
else 
    echo "Test 1 successful"
fi

echo "### TEST_4"
echo "### Must return [902482, 54444, 12888, 10]"
$SSP $TEST_4 969824
if [[ $? -ne 0 ]]; then
    echo "Test 4 failed"
    exit
else 
    echo "Test 4 successful"
fi
