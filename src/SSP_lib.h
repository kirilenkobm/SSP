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


typedef struct
{
    uint64_t *sub_sizes;
    uint64_t sz_count;
    uint64_t ind_max;
    uint64_t ind_min;
} Sz_out;


// free all variables
void free_all();

// show verbose message if v is activated
void verbose(const char * restrict format, ...);

// keyboard interrupt handler
void sigint_handler(int sig_num);

// create accumulated sum array
__uint128_t *accumulate_sum(__uint128_t *arr, uint64_t arr_size);

// count elements, create array of structs
Num_q *count_elements(__uint128_t *arr, uint64_t arr_size, uint64_t *q);

// get subset sizes to check
Sz_out get_subset_sizes(uint64_t arr_len, uint64_t req_sum);

// add elements to the counter
void add_to_zero_counter(Num_q *counter, uint64_t *arr, uint64_t arr_size);

// create empty counter
Num_q *_get_zero_num_q();

// check if current value still can be used
uint64_t check_current(Num_q *path, uint64_t cur_ind);

// compute array sum
uint64_t arr_sum(uint64_t *arr, uint64_t up_to);

// __int128_t just to avoid overflows, maybe an overkill
uint64_t _elem_search(__int128_t l, __int128_t r, uint64_t w);

// get path for the subset size given
uint64_t *get_path(uint64_t sub_size, uint64_t *prev_path, uint64_t prev_p_len,
                   uint64_t _cur_val, uint64_t _cur_ind, 
                   uint64_t req_sum, uint64_t arr_size);

// shared library entry point
uint64_t *solve_SSP(uint64_t *in_arr, uint64_t _arr_size,
                    uint64_t req_sum, bool _v, bool deep);

#endif // !SSP_LIB
