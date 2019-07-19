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
        if (arr[i] > cur_val){
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
    res = (Elem_count*)realloc(res, sizeof(Elem_count) * (uniq_count + CHUNK));
    // terminate the sequence
    res[uniq_count + 1].number = 0;
    res[uniq_count + 1].times = 0;
    return res;
}

uint32_t *solve_SSP(uint32_t *in_arr, uint32_t arr_size, uint32_t sub_size, uint32_t req_sum)
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
    // don't need this anymore
    free(f_max);
    free(f_min);
    // count elems
    Elem_count *elem_counted = count_elems(in_arr, arr_size);
    uint32_t uniq_elems = 0;
    for (uint32_t i = 0; i < arr_size; i++){
        if (elem_counted[i].number == 0){
            // meaning that it's done
            break;
        }
        uniq_elems++;
    }

    // todo: the core part
    // find the first maximal path
    // then modify it

    // don't forget to clean memory up
    free(f_max_acc);
    free(f_min_acc);
    return answer;
}
