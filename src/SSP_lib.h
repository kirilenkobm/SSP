/*
Copyright: Bogdan Kirilenko
Dresden, Germany, 2019
kirilenkobm@gmail.com
*/
#ifndef SSP_LIB
#define SSP_LIB
#include <stdio.h>
#include <string.h>
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>

typedef struct{
    uint32_t number;
    uint32_t times;
} Elem_count;

void verbose(const char * restrict format, ...);

uint32_t *accumulate_sum(uint32_t *func, uint32_t f_len);

Elem_count *count_elems(uint32_t *arr, uint32_t arr_size);

Elem_count *get_zero_path_count(Elem_count *all_available, uint32_t all_size);

uint32_t part_sum(uint32_t *arr,uint32_t n);

uint32_t check_current(uint32_t current, uint32_t cur_index,
                       Elem_count *path_count, Elem_count *overall_count);

uint32_t *get_first_path(Elem_count *counter, uint32_t uniq_num, uint32_t* f_max_a,
                         uint32_t *f_min_a, uint32_t target,uint32_t comb_size,
                         uint32_t c_ind);

uint32_t *solve_SSP(uint32_t *in_arr, uint32_t arr_size, uint32_t sub_size,
                    uint32_t req_sum, bool _v);

#endif // !SSP_LIB
