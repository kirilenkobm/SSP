#!/usr/bin/env bash
# remove previous stuff
eval rm -rf performance/test_*
gen="./bin/generate_input"

repl_num=20
lo=5
range=100
props_range=2
props=(0.25 0.50 0.75)

echo "generating dataset with max num 10000"

hi=100000000

for step in `seq 1 $((range))`
do
    arr_size=$((step * 100))

    for n_ in `seq 0 $props_range`
    do
        prop="${props[$n_]}"
        ans=$(expr $prop*$arr_size | bc)
        ans_int=${ans%%.*}
        d_name="performance/test_${arr_size}_${ans_int}_${hi}"
        echo "Generating $d_name dataset"
        mkdir $d_name
        for r_num in `seq 0 $repl_num`
        do
            fname="${d_name}/${r_num}.txt"
            cmd="$gen $arr_size $hi $lo $ans $fname"
            eval $cmd
        done
    done
done

