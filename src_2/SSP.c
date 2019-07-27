/*
The entry point.

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
#include <stdio.h>
#include <unistd.h>
#include <ctype.h>
#include <limits.h>

#define MAXCHAR 22
#define ALLOC 100
#define ALLOC_STEP 100
#define LEAF_ALLOC 10
#define LEAD_ALLOC_STEP 10
#define CHUNK 5


typedef struct
{
    uint64_t *S;  // in_array
    uint64_t k;  // arr_size
} In_data;


typedef struct
{
    uint64_t sum;
    uint64_t *max_shifts;
    uint64_t *max_indexes;
    uint64_t *min_shifts;
    uint64_t *min_indexes;
    uint64_t exists;  // how many times it exists
} Leaf_node;


// global variables
uint64_t f_size_ext;
In_data in_arr;
uint64_t *f_min_glob;
uint64_t *f_max_glob;
uint64_t *f_min_acc_glob;
uint64_t *f_max_acc_glob;
Leaf_node *glob_list;
uint64_t leaf_size;


// print usage guids and quit
void usage(char *exe)
{
    // todo: add verbosity mode!
    fprintf(stderr, "Usage: %s [input file] [target]\n\n", exe);
    fprintf(stderr, "Input file: a file contatining input numbers \n");
    fprintf(stderr, "or stdin stream with numbers\n");
    fprintf(stderr, "Target: sum of subset to be found\n");
    exit(0);
}


// free everything
void free_all()
{
    free(in_arr.S);
    free(f_min_glob);
    free(f_max_glob);
    for (uint64_t i = 0; i < leaf_size; i++)
    {
        free(glob_list[i].max_indexes);
        free(glob_list[i].max_shifts);
        free(glob_list[i].min_indexes);
        free(glob_list[i].min_shifts);
    }
    free(glob_list);
}


// compare uints for sort
int uint64_comp(const void* a, const void* b)
{
     uint64_t _a = * ( (uint64_t*) a );
     uint64_t _b = * ( (uint64_t*) b );
     if (_a == _b) return 0;
     else if (_a < _b ) return -1;
     else return 1;
}


// read input file
In_data read_input(char *in_file)
{
    In_data ans;
    ans.S = (uint64_t*)malloc(ALLOC_STEP * sizeof(uint64_t));
    FILE *input;
    if (strcmp(in_file, "stdin") == 0) {
        input = stdin;  // if stdin --> ok
    } else if (access(in_file, F_OK) != -1) {
        // not stdin; check that file exists
        input = fopen(in_file, "r");
    } else {
        fprintf(stderr, "Sorry, but %s doesn't exist or unavailable\n", in_file);
        exit(1);
    }

    uint64_t arr_size = 0;
    uint64_t allocated = ALLOC;
    char buff[MAXCHAR];
    while (fgets(buff, MAXCHAR, input) != NULL)
    {
        char *c;
        for (c = buff; *c ; c++) {
            if (*c == 10){break;}  // if line terminates -> skip check
            if (!isdigit(*c)){
                // request each character to be numeric
                fprintf(stderr, "\nSorry, but input expected to have only numeric values\n");
                fprintf(stderr, "Unfortunately, there are non-numeric characters\n");
                fprintf(stderr, "At the line: %llu\n", arr_size + 1);
                fprintf(stderr, "Exit 2\n");
                exit(1);
            }
        }
        uint64_t val = strtoul(buff, 0L, 10);
        ans.S[arr_size] = val;
        arr_size++;
        if (arr_size > allocated - CHUNK){
            // reallocate memory then
            allocated += ALLOC_STEP;
            ans.S = (uint64_t*)realloc(ans.S, allocated * sizeof(uint64_t));
        }
        if (allocated > UINT64_MAX){
            fprintf(stderr, "Sorry, but your input is very long.\n");
            fprintf(stderr, "It is limited to %llu", UINT64_MAX);
            exit(2);
        }
    }
    qsort(ans.S, arr_size, sizeof(uint64_t), uint64_comp);
    ans.k = arr_size;
    return ans;
}

// read target
uint64_t read_target(char *X_arg)
{
    uint64_t X;
    char *c;
    for (c = X_arg; *c; c++){
        if (!isdigit(*c)){
            // non-numeric
            fprintf(stderr, "\nSorry, but target argument expected to numeric\n");
            fprintf(stderr, "got %s\n", X_arg);
            exit(1);
        }
        // everything's OK
        X = strtoul(X_arg, 0L, 10);
    }
    return X;
}


// create accumulated sum array
uint64_t *accumulate_sum(uint64_t *arr, uint64_t arr_size, uint64_t shift)
{
    uint64_t *res = (uint64_t*)malloc(arr_size * sizeof(uint64_t));
    res[0] = arr[shift];
    for (uint64_t i = shift + 1; i < arr_size + shift; i++)
    {
        res[i] = res[i - 1] + arr[i];
    }
    return res;
}


// compute array sum
uint64_t arr_sum(uint64_t *arr, uint64_t arr_size)
{
    uint64_t sum = 0;
    for (uint64_t i = 0; i < arr_size; i++){
        sum += arr[i];
        if (sum >= UINT64_MAX){
            fprintf(stderr, "Sorry, but sadly this program cannot handle arrays,\n");
            fprintf(stderr, "sum of which is > UINT64_MAX, thank you for your\n");
            fprintf(stderr, "understanding. Exit.\n");
            exit(3);
        }
    }
    return sum;
}


// the entry point
int main(int argc, char ** argv)
{
    // read and check input data
    if (argc != 3){usage(argv[0]);}
    In_data in_arr = read_input(argv[1]);
    uint64_t X = read_target(argv[2]);
    fprintf(stderr, "# Array size: %llu; Target: %llu\n", in_arr.k, X);

    // define fmax and fmin
    f_size_ext = in_arr.k * 2;
    // must be 1 2 3 4 5 1 2 3 4
    f_min_glob = (uint64_t*)calloc(f_size_ext, sizeof(uint64_t));
    f_max_glob = (uint64_t*)calloc(f_size_ext, sizeof(uint64_t));
    uint16_t i_num = 1;
    for (uint64_t i = 0; i < in_arr.k; i++)
    {
        f_min_glob[i] = in_arr.S[i];
        f_min_glob[i + in_arr.k] = in_arr.S[i];
        f_max_glob[in_arr.k - i_num] = in_arr.S[i];
        f_max_glob[(in_arr.k * 2) - i_num] = in_arr.S[i];
        i_num++;
    }
    
    // create the leaf
    uint64_t in_sum = arr_sum(in_arr.S, in_arr.k);
    leaf_size = in_sum + 1;
    fprintf(stderr, "# Array sum is %llu\n", in_sum);
    glob_list = (Leaf_node*)malloc(sizeof(Leaf_node) * leaf_size);
    for (uint64_t i = 0; i < leaf_size; i++){
        glob_list[i].sum = i;
        glob_list[i].exists = 0;
        glob_list[i].max_shifts = (uint64_t*)calloc(LEAF_ALLOC, sizeof(uint64_t));
        glob_list[i].max_indexes = (uint64_t*)calloc(LEAF_ALLOC, sizeof(uint64_t));
        glob_list[i].min_shifts = (uint64_t*)calloc(LEAF_ALLOC, sizeof(uint64_t));
        glob_list[i].min_indexes = (uint64_t*)calloc(LEAF_ALLOC, sizeof(uint64_t));
    }

    // fill the leaf


    free_all();
    return 0;
}
