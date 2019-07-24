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
#define CHUNK 5


// global
bool v = false;
uint64_t arr_size = 0;
uint64_t *f_max;
uint64_t *f_min;
uint64_t _f_arr_size;
uint64_t *first_path;
Num_q *num_count;
uint64_t _elem_num_max;

void _free_all()
// free all allocated stuff
{
    free(f_max);
    free(f_min);
    free(num_count);
    free(first_path);
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


// __int128_t just to avoid overflows, maybe an overkill
uint64_t _elem_search(__int128_t l, __int128_t r, uint64_t w)
// very dumb implementation in O(N)
// rewrite it better in log(N)
{
    if (r >= l)
    {
        __int128_t mid = l + (r - l) / 2;
        if (num_count[mid].number == w){
            return mid;
        } else if (num_count[mid].number < w){
            return _elem_search(l, mid - 1, w);
        } else {
            return _elem_search(mid + 1, r, w);
        }
    }
    // for (uint64_t i = 0; i < _elem_num_max; i++){
    //     if (num_count[i].number == w){return i;}
    // }
    return _elem_num_max;
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
    // the first element is 0 -> skip it
    // ititiate with the first element
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


Num_q *_get_zero_num_q(uint64_t elem_num)
// create empty counter
{
    Num_q *res = (Num_q*)malloc(elem_num * sizeof(Num_q));
    for (uint64_t i = 0; i < elem_num; i++)
    {
        res[i].number = num_count[i].number;
        res[i].quantity = 0;
    }
    return res;
}


void add_to_zero_counter(Num_q *counter, uint64_t *arr, uint64_t arr_size)
// add elements to the counter
{
    uint64_t counter_ind = 0;
    uint64_t arr_ind = 0;
    while (arr_ind < arr_size){
    // both are sorted
        assert(arr[arr_ind] <= counter[counter_ind].number);
        if (arr[arr_ind] == counter[counter_ind].number){
            counter[counter_ind].quantity++;
            arr_ind++;
        } else if (arr[arr_ind] < counter[counter_ind].number){
            counter_ind++;
        }
    }
}


uint64_t arr_sum(uint64_t *arr, uint64_t up_to)
// return array sum
{
    if (up_to == 0){return 0;}
    uint64_t res = 0;
    for (uint64_t i = 0; i < up_to; i++){res += arr[i];}
    return res;
}


uint64_t check_current(Num_q *path, uint64_t cur_ind)
// check if current value still can be used, decrease it or return 0 otherwise
// if all possible elements vere spent
{
    uint64_t used = path[cur_ind].quantity;
    uint64_t available = num_count[cur_ind].quantity;
    assert(available >= used);
    if (available == used)
    {
        // we cannot use this elem -> this is over
        // if 0 -> all are over, so there is no way
        cur_ind++;
        return cur_ind;
    }
    // we still have this number
    return cur_ind;
}


uint64_t *find_path(uint64_t sub_size, uint64_t *prev_path, uint64_t prev_p_len,
                    uint64_t _cur_val, uint64_t _cur_ind, uint64_t elem_num,
                    uint64_t req_sum)
// the core function -> finds a path
{
    // initiate values
    uint64_t *path = (uint64_t*)calloc(sub_size + CHUNK, sizeof(uint64_t));
    Num_q *path_count = _get_zero_num_q(elem_num);
    uint64_t pos_left;
    uint64_t path_len = prev_p_len;
    uint64_t cur_val = _cur_val;
    uint64_t cur_ind = _cur_ind;

    if (prev_path != NULL){
        // add existing part to answer
        for (uint64_t i = 0; i < prev_p_len; i++){path[i] = prev_path[i];}
        pos_left = sub_size - prev_p_len;
        // add exitsing values to counter
        add_to_zero_counter(path_count, prev_path, prev_p_len);
    } else {pos_left = sub_size;}


    // create local f_max and f_min
    uint64_t *f_max_a = accumulate_sum(f_max, arr_size);
    uint64_t *f_min_a = accumulate_sum(f_min, arr_size);
    uint64_t *_f_max = (uint64_t*)malloc(_f_arr_size * sizeof(uint64_t));
    for (uint64_t i = 0; i < _f_arr_size; i++){_f_max[i] = f_max[i];}
    // values I need insude
    uint64_t intermed_val = 0;
    uint64_t prev_sum = 0;
    int64_t delta = 0;  // might be negative!
    uint64_t sup = 0;
    uint64_t inf = 0;
    uint64_t points_left = 0;
    
    uint64_t delta_ind;
    uint64_t delta_spent;
    uint64_t delta_avail;

    for (uint64_t i = 0; i < pos_left; i++)
    // the main loop, trying to add the next element
    {
        bool passed = false;
        prev_sum = arr_sum(path, path_len);
        cur_ind = check_current(path_count, cur_ind);
        cur_val = num_count[cur_ind].number;

        while (!passed)
        // trying to add the current value
        {
            // no values left
            if (cur_val == 0){
                free(f_max_a);
                free(f_min_a);
                return path;
            }
            // get intermediate values
            intermed_val = prev_sum + cur_val;
            delta = req_sum - intermed_val;
            points_left = pos_left - (i + 1);
            sup = f_max_a[points_left];
            inf = f_min_a[points_left];

            // need to be carefull -> comparing signed vs unsigned
            if ((delta > 0) && (uint64_t)delta > sup){
                // unreachable
                break;
            } else if ((delta < 0) || (uint64_t)delta < inf){
                // get next value, skip iter
                cur_ind++;
                cur_val = num_count[cur_ind].number;
                continue;
            }
            // ok, value passed, let's add it
            passed = true;
            path[path_len] = cur_val;
            path_count[cur_ind].quantity++;
            path_len++;

            if (delta > 0)
            // we can also check if delta exists
            // if yes -> just add it to answer and return
            {
                delta_ind = _elem_search(0, (__int128_t)_elem_num_max, (uint64_t)delta);
                delta_spent = path_count[delta_ind].quantity;
                delta_avail = num_count[delta_ind].quantity;
                // if 0 > not found actually
                // but I don't like conglomeration of if's
                if ((delta_avail > 0) && (delta_spent < delta_avail))
                // yes, it is available
                {
                    path[path_len] = delta;
                    free(f_max_a);
                    free(f_min_a);
                    return path;
                }
            }
        }
    }
    free(f_max_a);
    free(f_min_a);
    return path;
}


uint64_t *solve_SSP(uint64_t *in_arr, uint64_t _arr_size, uint64_t sub_size,
                    uint64_t req_sum, bool _v)
// what we should call
{
    // allocate f_max and f_min
    arr_size = _arr_size;
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
    num_count = count_elements(f_max, arr_size, &elem_num);
    _elem_num_max = elem_num;

    // now find the first path
    uint64_t cur_ind = 0;
    uint64_t cur_val = num_count[cur_ind].number;
    uint64_t *answer = (uint64_t*)calloc(sub_size, sizeof(uint64_t));

    first_path = find_path(sub_size, NULL, 0, cur_val, cur_ind, elem_num, req_sum);
    // to output the array:
    // for (uint64_t i = 0; i < sub_size; i++){printf("%llu ", first_path[i]);}
    // printf("\n");

    uint64_t first_sum = arr_sum(first_path, sub_size);
    if (first_sum == req_sum)
    // the first answer is correct -> return it and that's it
    {
        for (uint64_t i = 0; i < sub_size; i++){answer[i] = first_path[i];}
        _free_all();
        return answer;
    }
    // we're here -> where the problems start
    uint64_t p = 0;
    uint64_t pointed;
    uint64_t pointed_ind;
    uint64_t lower;
    uint64_t lower_ind;

    for (uint64_t p_ = (sub_size - 1); p_ > 0; p_--)
    {   
        p = p_ - 1;   // if >= then it is an infinite loop
        pointed = first_path[p];
        pointed_ind = _elem_search(0, (__int128_t)_elem_num_max, pointed);
        bool possible = true;

        while (possible)
        // decrease while decreseable  
        {
            lower_ind = pointed_ind + 1;
            lower = num_count[lower_ind].number;
            if (lower == 0){possible = false; break;}
            uint64_t *try_path = (uint64_t*)calloc(sub_size + CHUNK, sizeof(uint64_t));
            for (uint64_t i = 0; i < p; i++){try_path[i] = first_path[i];}
            try_path[p] = lower;
            // try to get this path
            uint64_t *try_res = find_path(sub_size, try_path, p + 1, lower,
                                          lower_ind, elem_num, req_sum);
            pointed = lower;
            pointed_ind = lower_ind;
            // do not forget!
            free(try_path);
            uint64_t try_res_sum = arr_sum(try_res, sub_size);
            if (try_res_sum == req_sum)
            // we've got an answer!
            {
                for (uint64_t i = 0; i < sub_size; i++){answer[i] = try_res[i];}
                _free_all();
                free(try_res);
                return answer;
            }
        }
    }
    _free_all();
    return answer;
}
