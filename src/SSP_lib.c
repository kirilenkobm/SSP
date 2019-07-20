/*
Copyright: Bogdan Kirilenko
Dresden, Germany, 2019
kirilenkobm@gmail.com
*/
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include "SSP_lib.h"
#define ALLOC_STEP 10
#define CHUNK 5


uint32_t *accumulate_sum(uint32_t *func, uint32_t f_len)
// just create accumulated sum array
{
    uint32_t *res = (uint32_t*)malloc(sizeof(uint32_t) * (f_len + CHUNK));
    uint32_t val = 0;
    for (uint32_t i = 0; i < f_len; i++){
        res[i] = val + func[i];
        val = res[i];
    }
    return res;
}


Elem_count *count_elems(uint32_t *arr, uint32_t arr_size)
// count each elem in the array
{
    // it must be a better solution than allocate a ton of memory
    // an then shrinking it down
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


uint32_t check_current(uint32_t current, Elem_count *path_count, Elem_count *overall_count)
// check if current value still can be used, decrease it or return 0 otherwise
// if all possible elements vere spent
{

}


uint32_t *get_first_path(Elem_count *counter, uint32_t uniq_num, uint32_t* f_max_a,
                         uint32_t *f_min_a, uint32_t target, uint32_t comb_size)
// get the first, base combination
{
    uint32_t *res = (uint32_t*)calloc(comb_size, sizeof(uint32_t));
    uint32_t current = counter[0].number;
    uint32_t pos_left = comb_size;
    uint32_t pos_used = 0;
    uint32_t prev_sum = 0;
    Elem_count *path_count = get_zero_path_count(counter, uniq_num);
    for (uint32_t i = 0; i < pos_left; i++)
    // add elems one-by-one
    {
        bool passed = false;
        prev_sum = part_sum(res, pos_used);
        current = check_current(current, path_count, counter);
    }
    return res;
}


uint32_t *solve_SSP(uint32_t *in_arr, uint32_t arr_size,
                    uint32_t sub_size, uint32_t req_sum)
// what we should call
{
    // just write sub_size -by- sub_size
    size_t ans_size = ALLOC_STEP * sub_size + CHUNK;
    uint32_t *answer = (uint32_t*)calloc(ans_size, sizeof(uint32_t));
    size_t f_max_min_size = sizeof(uint32_t) * (arr_size + CHUNK);
    uint32_t *f_max = (uint32_t*)malloc(f_max_min_size);
    uint32_t *f_min = (uint32_t*)malloc(f_max_min_size);
    // the numbers are actually pre-sorted
    // just for explicity
    for (uint32_t i = 0; i < arr_size; i++){f_min[i] = in_arr[i];}
    // f_max is just reversed f_min
    for (uint32_t i = 0, j = arr_size - 1; i < arr_size; i++, j--){
        f_max[j] = f_min[i];}
    // not get accumulated sums
    uint32_t *f_max_acc = accumulate_sum(f_max, arr_size);
    uint32_t *f_min_acc = accumulate_sum(f_min, arr_size);
    // count elems | there must be a better solution
    Elem_count *elem_counted = count_elems(f_max, arr_size);
    uint32_t uniq_num = 0;
    for (uint32_t i = 0; i < arr_size; i++){
        // if we reached zero -> the array is over
        if (elem_counted[i].number == 0){break;}
        uniq_num++;
    }
    printf("# there are %d uniq elems\n", uniq_num);
    // find the first maximal path
    // actually they might be merged into one func
    // like in the python implementation
    uint32_t *first_path = get_first_path(elem_counted, uniq_num, f_max_acc,
                                          f_min_acc, req_sum, sub_size);
    // then modify it

    // don't forget to clean memory up
    free(f_max);
    free(f_min);
    free(first_path);
    free(f_max_acc);
    free(f_min_acc);
    return answer;
}
