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
#include <signal.h>
#include "SSP_lib.h"
#define CHUNK 5


// global variables
bool v = false;
bool first_allocated = false;
uint64_t *f_max;
uint64_t *f_min;
uint64_t *f_max_a;
uint64_t *f_min_a;
uint64_t *first_path;
Num_q *num_count;
uint64_t uniq_num = 0;


// free all variables
void free_all()
{
    free(f_max);
    free(f_min);
    free(f_max_a);
    free(f_min_a);
    if (first_allocated){free(first_path);}
    free(num_count);
}


// show verbose message if v is activated
void verbose(const char * restrict format, ...)
{
    if(!v) {return;}
    va_list args;
    va_start(args, format);
    vprintf(format, args);
    va_end(args);
    return;
}


// keyboard interrupt handler
void sigint_handler(int sig_num)
{
    // actually doesn't work
    // but probably it's a right direction
    fprintf(stderr, "KeyboardInterrupt.");
    abort();
}


// create accumulated sum array
uint64_t *accumulate_sum(uint64_t *arr, uint64_t arr_size)
{
    uint64_t *res = (uint64_t*)malloc(arr_size * sizeof(uint64_t));
    res[0] = arr[0];
    for (uint64_t i = 1; i < arr_size; i++){res[i] = res[i - 1] + arr[i];}
    return res;
}


// count elements, create array of structs
Num_q *count_elements(uint64_t *arr, uint64_t arr_size, uint64_t *q)
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
            *q = *q + 1;  // cannot do with *q++ by some reason
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


// get subset sizes to check
Sz_out get_subset_sizes(uint64_t arr_len, uint64_t req_sum)
{
    Sz_out res;
    res.sub_sizes = (uint64_t*)calloc(arr_len, sizeof(uint64_t));
    res.sz_count = 0;
    res.ind_max = 0;
    res.ind_min = 0;
    bool found = false;
    uint64_t sub_size = 0;
    uint64_t sup = 0;
    uint64_t inf = 0;

    for (uint64_t i = 1; i < arr_len; i++)
    // try every possible size
    {
        sub_size = i;
        sup = f_max_a[i];
        inf = f_min_a[i];
        // printf("Ssize %llu inf %llu sup %llu X %llu\n", sub_size, inf, sup, req_sum);
        if (req_sum == sup){
            // need to return path to sup then
            res.ind_max = i + 1;
            return res;
        } else if (req_sum == inf){
            res.ind_min = i + 1;
            return res;
        } else if ((inf < req_sum) && (req_sum < sup)){
            // printf("Added %llu\n", sub_size);
            res.sub_sizes[res.sz_count] = sub_size;
            res.sz_count++;
            found = true;
        } else {
            if (found) {return res;}
        }
    }
    return res;
}


// add elements to the counter
void add_to_zero_counter(Num_q *counter, uint64_t *arr, uint64_t arr_size)
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


// create empty counter
Num_q *_get_zero_num_q()
{
    Num_q *res = (Num_q*)malloc(uniq_num * sizeof(Num_q));
    for (uint64_t i = 0; i < uniq_num; i++)
    {
        res[i].number = num_count[i].number;
        res[i].quantity = 0;
    }
    return res;
}


// check if current value still can be used
uint64_t check_current(Num_q *path, uint64_t cur_ind)
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


// compute array sum
uint64_t arr_sum(uint64_t *arr, uint64_t up_to)
{
    if (up_to == 0){return 0;}
    uint64_t res = 0;
    for (uint64_t i = 0; i < up_to; i++){res += arr[i];}
    return res;
}


// __int128_t just to avoid overflows, maybe an overkill
uint64_t _elem_search(__int128_t l, __int128_t r, uint64_t w)
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
    return uniq_num;
}


// get path for the subset size given
uint64_t *get_path(uint64_t sub_size, uint64_t *prev_path, uint64_t prev_p_len,
                   uint64_t _cur_val, uint64_t _cur_ind, 
                   uint64_t req_sum, uint64_t arr_size)
{
    // initiate values
    uint64_t *path = (uint64_t*)calloc(sub_size + CHUNK, sizeof(uint64_t));
    Num_q *path_count = _get_zero_num_q();
    uint64_t pos_left;  // don't change this
    uint64_t _l_f_arr_size = arr_size;  // to keep local
    uint64_t path_len = prev_p_len;
    uint64_t cur_val = _cur_val;
    uint64_t cur_ind = _cur_ind;
    uint64_t inter_val = 0;

    if (prev_path != NULL){
        // add existing part to answer
        for (uint64_t i = 0; i < prev_p_len; i++){path[i] = prev_path[i];}
        pos_left = sub_size - prev_p_len;
        // add exitsing values to counter
        add_to_zero_counter(path_count, prev_path, prev_p_len);
    } else {pos_left = sub_size;}

    uint64_t *_f_max = (uint64_t*)malloc(_l_f_arr_size * sizeof(uint64_t));
    for (uint64_t i = 0; i < _l_f_arr_size; i++){_f_max[i] = f_max[i];}

    // values I need insude
    uint64_t prev_sum = 0;
    int64_t delta = 0;  // might be negative!
    uint64_t sup = 0;
    uint64_t inf = 0;
    uint64_t points_left = 0;
    
    uint64_t delta_ind;
    uint64_t delta_spent;
    uint64_t delta_avail;

    // the main loop, trying to add the next element
    for (uint64_t i = 0; i < pos_left; i++)
    {   
        bool passed = false;
        prev_sum = arr_sum(path, path_len);
        cur_ind = check_current(path_count, cur_ind);
        cur_val = num_count[cur_ind].number;

        while (!passed)
        {
            // no values left
            if (cur_val == 0){
                free(_f_max);
                return path;
            }
            // get intermediate values
            inter_val = prev_sum + cur_val;
            delta = req_sum - inter_val;
            points_left = pos_left - (i + 1);
            sup = f_max_a[points_left];
            inf = f_min_a[points_left];
            // uint64_t to_inf = prev_sum - inf;
            // uint64_t to_inf_ind = _elem_search(0, (__int128_t)uniq_num, to_inf);
            // if (to_inf_ind != uniq_num)
            // we can fall down to fmin and that's it
            // {
            //     uint64_t to_inf_spent = path_count[to_inf_ind].quantity;
            //     uint64_t to_inf_avail= num_count[to_inf_ind].quantity;
                // printf("to_inf: %llu ind: %llu \n", to_inf, to_inf_ind);
                // printf("Used: %llu available: %llu\n", to_inf_spent, to_inf_avail);
                // if (to_inf_avail > to_inf_spent){printf("TODO THIS PART DINF EXISTS\n");}
            // }
            // need to be carefull -> comparing signed vs unsigned
            if ((delta > 0) && (uint64_t)delta > sup){
                // unreachable
                break;
            } else if ((delta < 0) || (uint64_t)delta < inf){
                // printf("Delta %lld inf %llu\n", delta, inf);
                cur_ind++;
                cur_val = num_count[cur_ind].number;
                continue;
            }
            // ok, value passed, let's add it
            passed = true;
            path[path_len] = cur_val;
            path_count[cur_ind].quantity++;
            path_len++;

            delta_ind = _elem_search(0, (__int128_t)uniq_num, (uint64_t)delta);
            delta_spent = path_count[delta_ind].quantity;
            delta_avail = num_count[delta_ind].quantity;
            // if 0 > not found actually
            // but I don't like conglomeration of if's
            if ((delta_avail > 0) && (delta_spent < delta_avail))
            // yes, it is available
            {
                verbose("Delta %lld is in the dataset\n", delta);
                path[path_len] = delta;
                return path;
            }
        }
    }
    return path;
}


// shared library entry point
uint64_t *solve_SSP(uint64_t *in_arr, uint64_t _arr_size,
                    uint64_t req_sum, bool _v, bool deep)
{
    // allocate f_max and f_min
    signal(SIGINT, sigint_handler);
    verbose("Entered shared library.\n");
    uint64_t arr_size = _arr_size;
    size_t f_max_min_size = sizeof(uint64_t) * (arr_size + CHUNK);
    uint64_t *dummy = (uint64_t*)calloc(CHUNK, sizeof(uint64_t));
    // the numbers were actually pre-sorted, so f_min is defined just for explicity
    f_max = (uint64_t*)malloc(f_max_min_size);
    f_min = (uint64_t*)malloc(f_max_min_size);
    f_max[0] = 0;
    f_min[0] = 0;
    for (uint64_t i = 0; i < arr_size; i++){f_min[i + 1] = in_arr[i];}
    for (uint64_t i = 1, j = arr_size; i < arr_size + 1; i++, j--){f_max[j] = f_min[i];}
    arr_size++;  // arrays were started from 0, so size +1
    f_max_a = accumulate_sum(f_max, arr_size);
    f_min_a = accumulate_sum(f_min, arr_size);
    v = _v;  // maybe there's a better solution to implement verbosity

    // now count the elements
    uniq_num = 0;
    num_count = count_elements(f_max, arr_size, &uniq_num);
    // for (uint64_t i = 0; i < uniq_num; i++){
    //     printf("%llu %llu | ", num_count[i].number, num_count[i].quantity);
    // }
    // printf("\n");
    verbose("# %llu unique numbers in the dataset\n", uniq_num);

    // get suitable subset sizes
    Sz_out s_sizes = get_subset_sizes(arr_size, req_sum);
    if (s_sizes.sz_count == 0){
        // weird but possible; return empty array
        return dummy;
    }
    verbose("Found %llu subset sizes\n", s_sizes.sz_count);
    // check if result was not on f_max or f_min
    if (s_sizes.ind_max != 0){
        // TODO: this scenario was not tested!
        // our answer is on f_max
        uint64_t *answer = (uint64_t*)calloc(s_sizes.sub_sizes[s_sizes.sz_count], sizeof(uint64_t));
        for (uint64_t i = 0; i <= s_sizes.ind_max; i++){answer[i] = f_max[i + 1];}
        free_all();
        return answer;
    } else if (s_sizes.ind_min != 0){
        // or on f_min
        uint64_t *answer = (uint64_t*)calloc(s_sizes.sub_sizes[s_sizes.sz_count], sizeof(uint64_t));
        for (uint64_t i = 0; i <= s_sizes.ind_min; i++){answer[i] = f_min[i + 1];}
        free_all();
        return answer;
    }

    // ok, let's find the answer then
    uint64_t sub_size = 0;
    uint64_t cur_ind = 0;
    uint64_t cur_val = num_count[cur_ind].number;

    for (uint64_t s_i = 0; s_i < s_sizes.sz_count; s_i++)
    // trying different subset sizes
    {
        sub_size = s_sizes.sub_sizes[s_i];
        cur_ind = 0;
        cur_val = num_count[cur_ind].number;

        
        uint64_t * first_path = get_path(sub_size, NULL, 0, cur_val, cur_ind,
                                         req_sum, arr_size);
        uint64_t path_sum = arr_sum(first_path, sub_size);
        if (path_sum == req_sum){
            free_all();
            return first_path;
        }
        // otherwise we will free first and then return
        first_allocated = true;
        verbose("First path doesn't fit\n");
        uint64_t p = 0;
        uint64_t pointed;
        uint64_t pointed_ind;
        uint64_t lower;
        uint64_t lower_ind;
        uint64_t *answer = (uint64_t*)calloc(sub_size + CHUNK, sizeof(uint64_t));
        for (uint64_t p_ = (sub_size - 1); p_ > 0; p_--)
        {
            p = p_ - 1;   // if >= then it is an infinite loop
            pointed = first_path[p];
            if (pointed == 0) {continue;}
            pointed_ind = _elem_search(0, (__int128_t)uniq_num, pointed);
            // todo: check if it is necessary
            // if deep = false, will not enter this
            bool possible = deep;
            while (possible)
            // decrease while decreseable  
            {
                lower_ind = pointed_ind + 1;
                lower = num_count[lower_ind].number;
                if (lower == 0) {possible = false; break;}
                verbose("# Changing %llu at pos. %llu to %llu\n", pointed, p, lower);
                if (lower == 0){possible = false; break;}
                uint64_t *try_path = (uint64_t*)calloc(sub_size + CHUNK, sizeof(uint64_t));
                for (uint64_t i = 0; i < p; i++){try_path[i] = first_path[i];}
                try_path[p] = lower;
                // try to get this path
                uint64_t *try_res = get_path(sub_size, try_path, p + 1, lower, lower_ind, 
                                             req_sum, arr_size);
                pointed = lower;
                pointed_ind = lower_ind;
                // do not forget!
                free(try_path);
                uint64_t try_res_sum = arr_sum(try_res, sub_size);
                if (try_res_sum == req_sum)
                // we've got an answer!
                {
                    verbose("# Found answer\n");
                    for (uint64_t i = 0; i < sub_size; i++){answer[i] = try_res[i];}
                    answer[sub_size] = 0;
                    free(try_res);
                    free(first_path);
                    first_allocated = false;
                    free_all();
                    return answer;
                }
                free(try_res);
            }

        }
        // allocating answer each time -> wasn't a bad idea?
        free(answer);
    }
    free_all();
    return dummy;
}
