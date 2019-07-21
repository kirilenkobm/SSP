#!/usr/bin/env bash
# remove previous stuff
./generate_input.py clean
samples_num=50
std=500
# generate commands:
for i in 100 1000 10000 100000
do
    echo "Generating N $i"
    i_10=$(($i/10))
    ./generate_input.py $i $((i/10)) $samples_num $std N_$i
done
