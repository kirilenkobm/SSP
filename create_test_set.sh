#!/usr/bin/env bash
# remove previous stuff
./generate_input.py clean
samples_num=25
std=5000000
# generate commands:
for i in 100 1000 10000 100000 1000000 10000000
do
    echo "Generating N $i"
    i_10=$(($i/10))
    echo "./generate_input.py $i $((i/4)) $std $samples_num N_$i"
done
