/*
Copyright: Bogdan Kirilenko
Dresden, Germany, 2019
kirilenkobm@gmail.com
*/
#ifndef SSP_LIB
#define SSP_LIB
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>

typedef struct{
    uint32_t number;
    uint32_t times;
} Elem_count;

uint32_t *accumulate_sum(uint32_t *func, uint32_t f_len);

Elem_count *count_elems(uint32_t *arr, uint32_t arr_size);

uint32_t *solve_SSP(uint32_t *in_arr, uint32_t arr_size, uint32_t sub_size, uint32_t req_sum);

#endif // !SSP_LIB