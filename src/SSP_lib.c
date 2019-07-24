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
// later:
// #include "SSP_lib.h"
#define CHUNK 5

// global
bool v = false;
uint64_t *f_max;
uint64_t *f_min;


typedef struct
{
    uint64_t number;
    uint64_t quantity;
} Num_q;


void _free_all()
// free all allocated stuff
{
    free(f_max);
    free(f_min);
}


void verbose(const char * restrict format, ...)
// show verbose message if v is activated
{
    if(!v) {return;}
    va_list args;
    va_start(args, format);
    vprintf(format, args);
    va_end(args);
    return;
}


uint64_t *accumulate_sum(uint64_t *arr, uint64_t arr_size)
// create accumulated sum array
{
    uint64_t *res = (uint64_t*)malloc(arr_size * sizeof(uint64_t));
    res[0] = arr[0];
    for (uint64_t i = 1; i < arr_size; i++)
    {
        res[i] = res[i - 1] + arr[i];
    }
    return res;
}


Num_q *count_elements(uint64_t *arr, uint64_t arr_size, uint64_t *q)
// count elements, create array of structs
{
    Num_q *res = (Num_q*)malloc(arr_size * sizeof(Num_q));
    uint64_t cur_val = arr[1];
    res[*q].number = cur_val;
    res[*q].quantity = 0;
    for (uint32_t i = 1; i < arr_size; i++)
    // go over elements
    // it is granted that they are arranged as:
    // x x x x y y y z z
    {   
        if (arr[i] < cur_val){
            // new elem
            cur_val = arr[i];  // now initiate next value
            *q = *q + 1;  // cannot do with *q++ by sime reason
            res[*q].number = cur_val;
            res[*q].quantity = 1;
        } else {
            // the same value, just increase the quantity
            res[*q].quantity++;
        }
    }
    // shrink array size
    size_t shrinked = sizeof(Num_q) * (*q + CHUNK);
    res = (Num_q*)realloc(res, shrinked);
    // terminate the sequence with 0
    *q = *q + 1;
    res[*q].number = 0;
    res[*q].quantity = 0;
    return res;
}


uint64_t *solve_SSP(uint64_t *in_arr, uint64_t arr_size, uint64_t sub_size,
                    uint64_t req_sum, bool _v)
// what we should call
{
    // allocate f_max and f_min
    size_t f_max_min_size = sizeof(uint64_t) * (arr_size + CHUNK);
    // the numbers were actually pre-sorted, so f_min is defined just for explicity
    f_max = (uint64_t*)malloc(f_max_min_size);
    f_min = (uint64_t*)malloc(f_max_min_size);
    f_max[0] = 0;
    f_min[0] = 0;
    for (uint64_t i = 0; i < arr_size; i++){f_min[i + 1] = in_arr[i];}
    for (uint64_t i = 1, j = arr_size; i < arr_size + 1; i++, j--){f_max[j] = f_min[i];}
    arr_size++;  // arrays were started from 0, so size +1
    v = _v;  // maybe there's a better solution to implement verbosity
    // now count the elements
    uint64_t elem_num = 0;
    Num_q *num_count = count_elements(f_max, arr_size, &elem_num);
    printf("Found %llu uniq elems\n", elem_num);
    // allocate the result and fill it
    uint64_t *answer = (uint64_t*)calloc(sub_size, sizeof(uint64_t));
    _free_all();
    return answer;
}
