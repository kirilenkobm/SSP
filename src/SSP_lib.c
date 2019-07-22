/*
Copyright: Bogdan Kirilenko
Dresden, Germany, 2019
kirilenkobm@gmail.com
*/
#include <stdio.h>
#include <string.h>
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdarg.h>
#include "SSP_lib.h"
#define ALLOC_STEP 10
#define CHUNK 5

// global
uint32_t *f_max;
uint32_t *f_min;
uint32_t *f_max_acc;
uint32_t *f_min_acc;
uint32_t *answer;
bool v = false;


void verbose(const char * restrict format, ...) {
    if( !v )
        return;

    va_list args;
    va_start(args, format);
    vprintf(format, args);
    va_end(args);
    return;
}


uint32_t *accumulate_sum_s_z(uint32_t *func, uint32_t f_len)
// create accumulate sum array
// start with 0!
// TODO: wrong!
{
    uint32_t *res = (uint32_t*)malloc(sizeof(uint32_t) * (f_len + CHUNK));
    res[0] = 0;
    uint32_t val = 0;
    for (uint32_t i = 0; i < f_len; i++){
        res[i + 1] = val + func[i];
        val = res[i + 1];
    }
    return res;
}


Elem_count *count_elems(uint32_t *arr, uint32_t arr_size)
// count each elem in the array
{
    // it must be a better solution than allocate a ton of memory
    // an then shrinking it down | but...
    uint32_t uniq_count = 0;
    uint32_t cur_val = arr[0];
    Elem_count *res = (Elem_count*)malloc(arr_size * sizeof(Elem_count));
    res[uniq_count].number = cur_val;
    res[uniq_count].times = 0;

    for (uint32_t i = 0; i < arr_size; i++)
    {   
        if (arr[i] < cur_val){
            // new elem
            cur_val = arr[i];
            uniq_count++;
            res[uniq_count].number = cur_val;
            res[uniq_count].times = 1;
        } else {
            // arr is sorted, the same with arr[i] == cur_val
            res[uniq_count].times++;
        }
    }
    size_t shrinked = sizeof(Elem_count) * (uniq_count + CHUNK);
    res = (Elem_count*)realloc(res, shrinked);
    // terminate the sequence
    res[uniq_count + 1].number = 0;
    res[uniq_count + 1].times = 0;
    return res;
}


Elem_count *get_zero_path_count(Elem_count *all_available, uint32_t all_size)
// make zero counter
{   
    Elem_count *zero = (Elem_count*)malloc(all_size * sizeof(Elem_count));
    // then copy numbers but not the counts
    for (uint32_t i = 0; i < all_size; i++){
        zero[i].number = all_available[i].number;
        zero[i].times = 0;
    }
    return zero;
}


uint32_t part_sum(uint32_t *arr,uint32_t n)
// sum first n elems of array
{
    if (n == 0){return 0;}
    uint32_t sum = 0;
    for (uint32_t i = 0; i < n; i++){sum += arr[i];}
    return sum;
}


uint32_t check_current(uint32_t current, uint32_t cur_index,
                       Elem_count *path_count, Elem_count *overall_count)
// check if current value still can be used, decrease it or return 0 otherwise
// if all possible elements vere spent
{
    uint32_t used = path_count[cur_index].times;
    uint32_t available = overall_count[cur_index].times;
    assert(available >= used);
    if (available == used)
    {
        // we cannot use this elem -> this is over
        // if 0 -> all are over, so there is no way
        return overall_count[cur_index + 1].number;
    }
    // we still have this number
    return current;
}


uint32_t *get_first_path(Elem_count *counter, uint32_t uniq_num, uint32_t* f_max_a,
                         uint32_t *f_min_a, uint32_t target,uint32_t comb_size,
                         uint32_t current_index)
// get the first, base combination
{
    uint32_t *res = (uint32_t*)calloc(comb_size, sizeof(uint32_t));
    uint32_t current = counter[current_index].number;
    verbose("Trying to find a path of size %d\n", comb_size);
    uint32_t current_ = 0;  // I was too lazy for normal output
    uint32_t intermed_val = 0;  // to keep intermediate sum
    // uint32_t current_index = 0;  // to get next elem quickly
    int64_t delta = 0;  // between target and intermediate val
    uint32_t left_ = 0;  // intermediate left number
    uint32_t pos_left = comb_size;
    uint32_t pos_used = 0;
    uint32_t prev_sum = 0;
    uint32_t sup = 0;
    uint32_t inf = 0;
    Elem_count *path_count = get_zero_path_count(counter, uniq_num);
    for (uint32_t i = 0; i < pos_left; i++)
    // add elems one-by-one
    {
        bool passed = false;
        prev_sum = part_sum(res, pos_used);
        // printf("i %d prev sum %d\n", i, prev_sum);
        current_ = check_current(current, current_index,
                                 path_count, counter);
        if (current != current_){
            // change indexes
            current = current_;
            current_index++;
        }
        while (!passed)
        // select the suitable number
        {
            // if no current value (== 0)
            // then terminate execution
            if (current == 0){return res;}
            intermed_val = prev_sum + current;
            delta = (int64_t)target - (int64_t)intermed_val;
            left_ = comb_size - (i + 1);
            sup = f_max_a[left_];
            inf = f_min_a[left_];

            if (delta < 0){
                current_index++;
                current = counter[current_index].number;
                continue;
            } else if (delta > (int64_t)sup){
                // how it works?
                break;
            } else if (delta < (int64_t)inf){
                // get next size and repeat
                current_index++;
                current = counter[current_index].number;
                // printf("Switched cur to %d\n", current);
                continue;
            }
            // printf("AGAIN sup %d delta %lld inf %d\n", sup, delta, inf);
            // printf("CURRENT ADDED %d\n", current);
            // intermediate sum is in between, fine
            passed = true;
            res[pos_used] = current;
            path_count[current_index].times++;
            pos_used++;
        }
    }
    // just a check for correctness
    uint32_t act_sum = part_sum(res, pos_used);
    // maybe assert?
    if (act_sum != target){res[0] = 0;}
    return res;
}


void _free_all()
// free all allocated stuff
{
    free(f_max);
    free(f_min);
    free(f_max_acc);
    free(f_min_acc);
}


uint32_t *solve_SSP(uint32_t *in_arr, uint32_t arr_size, uint32_t sub_size,
                    uint32_t req_sum, bool _v)
// what we should call
{
    // just write sub_size -by- sub_size
    size_t f_max_min_size = sizeof(uint32_t) * (arr_size + CHUNK);
    f_max = (uint32_t*)malloc(f_max_min_size);
    f_min = (uint32_t*)malloc(f_max_min_size);
    v = _v;  // maybe there's a better solution

    // the numbers are actually pre-sorted
    // just for explicity
    for (uint32_t i = 0; i < arr_size; i++){f_min[i] = in_arr[i];}
    // f_max is just reversed f_min
    for (uint32_t i = 0, j = arr_size - 1; i < arr_size; i++, j--){
        f_max[j] = f_min[i];}
    // not get accumulated sums
    f_max_acc = accumulate_sum_s_z(f_max, arr_size);
    f_min_acc = accumulate_sum_s_z(f_min, arr_size);

    // count elems | there must be a better solution
    Elem_count *elem_counted = count_elems(f_max, arr_size);
    uint32_t uniq_num = 0;
    for (uint32_t i = 0; i < arr_size; i++){
        // if we reached zero -> the array is over
        if (elem_counted[i].number == 0){break;}
        uniq_num++;
    }
    verbose("# Found %d unique elems\n", uniq_num);

    for (uint32_t c_ind = 0; c_ind < uniq_num; c_ind++)
    // try different starting points
    {
        bool success = true;
        verbose("# Trying c_ind %d\n", c_ind);
        answer = get_first_path(elem_counted, uniq_num, f_max_acc,
                                    f_min_acc, req_sum, sub_size, c_ind);
        // if 0 in the array -> nothing found; negative result
        for (uint32_t s = 0; s < sub_size; s++){
           if (answer[s] == 0){success = false; break;}}
        // continue if there is nothing
        if (!success){continue;}
        printf("# Found result for c_ind %d\n", c_ind);
        // if we are here -> result was found
        break;
    }
    // we wanted to find an only one answer, so return it
    _free_all();
    return answer;
}
