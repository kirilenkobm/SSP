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

typedef struct
{
    uint64_t number;
    uint64_t quantity;
} Num_q;

void sigint_handler(int sig_num);

void _free_all();

void verbose(const char * restrict format, ...);

uint64_t _elem_search(__int128_t l, __int128_t r, uint64_t w);

uint64_t *accumulate_sum(uint64_t *arr, uint64_t arr_size);

Num_q *count_elements(uint64_t *arr, uint64_t arr_size, uint64_t *q);

Num_q *_get_zero_num_q(uint64_t elem_num);

void add_to_zero_counter(Num_q *counter, uint64_t *arr, uint64_t arr_size);

uint64_t arr_sum(uint64_t *arr, uint64_t up_to);

uint64_t check_current(Num_q *path, uint64_t cur_ind);

void redefine_f_max(uint64_t *_f_max, uint64_t *_f_arr_len, uint64_t cur_val);

uint64_t *find_path(uint64_t sub_size, uint64_t *prev_path, uint64_t prev_p_len,
                    uint64_t _cur_val, uint64_t _cur_ind, uint64_t elem_num,
                    uint64_t req_sum);

uint64_t *solve_SSP(uint64_t *in_arr, uint64_t _arr_size, uint64_t req_sum, bool _v);

#endif // !SSP_LIB
