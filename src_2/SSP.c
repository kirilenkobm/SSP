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
#define LEAF_ALLOC 20
#define LEAD_ALLOC_STEP 20
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
    uint64_t max_allocated;
    uint64_t max_exists;
    uint64_t *min_shifts;
    uint64_t *min_indexes;
    uint64_t min_allocated;
    uint64_t min_exists;
} Leaf_node;


// global variables
In_data in_arr;
uint64_t f_size_ext;
In_data in_arr;
uint64_t *f_min_glob;
uint64_t *f_max_glob;
uint64_t *f_min_acc_glob;
uint64_t *f_max_acc_glob;
Leaf_node *Leaf;
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
        free(Leaf[i].max_indexes);
        free(Leaf[i].max_shifts);
        free(Leaf[i].min_indexes);
        free(Leaf[i].min_shifts);
    }
    free(Leaf);
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
    // also it will drop negative Xs
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
    if (X == 0){
        fprintf(stderr, "Error: X must be a positive number, not 0\n");
        exit(1);
    }
    return X;
}


// create accumulated sum array
uint64_t *accumulate_sum(uint64_t *arr, uint64_t arr_size, uint64_t shift)
{
    uint64_t *res = (uint64_t*)malloc(arr_size * sizeof(uint64_t));
    res[0] = arr[shift];
    for (uint64_t i = 1; i < arr_size; i++)
    {
        res[i] = res[i - 1] + arr[shift + i];
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


// true if element is in the array; rewrite in binary search
bool is_in(uint64_t *arr, uint64_t arr_size, uint64_t elem)
{
    for (uint64_t i = 0; i < arr_size; i++){
        if (arr[i] == elem){return true;}
    }
    return false;
}


// return trimmed array from shift to shift + size
uint64_t *trim_to(uint64_t *arr, uint64_t shift, uint64_t size)
{
    uint64_t *ans = (uint64_t*)malloc(size * sizeof(uint64_t));
    for (uint64_t i = shift, j = 0; i <= shift + size; i++, j++){
        ans[j] = arr[i];
    }
    return ans;
}


// the entry point
int main(int argc, char ** argv)
{
    // read and check input data
    if (argc != 3){usage(argv[0]);}
    in_arr = read_input(argv[1]);
    uint64_t X = read_target(argv[2]);
    fprintf(stderr, "# Array size: %llu; Target: %llu\n", in_arr.k, X);
    // exclude X in S
    bool X_in_S = is_in(in_arr.S, in_arr.k, X);
    if (X_in_S){
        free(in_arr.S);
        printf("X %llu is an element of S\n", X);
        exit(0);
    }

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
    return 0;
    uint64_t in_sum = arr_sum(in_arr.S, in_arr.k);
    leaf_size = in_sum + 1;
    fprintf(stderr, "# Array sum is %llu\n", in_sum);
    Leaf = (Leaf_node*)malloc(sizeof(Leaf_node) * leaf_size);

    // for (uint64_t i = 0; i < leaf_size; i++){
    //     Leaf[i].sum = i;
    //     Leaf[i].max_exists = 0;
    //     Leaf[i].min_exists = 0;
    //     Leaf[i].max_shifts = (uint64_t*)calloc(LEAF_ALLOC, sizeof(uint64_t));
    //     Leaf[i].max_indexes = (uint64_t*)calloc(LEAF_ALLOC, sizeof(uint64_t));
    //     Leaf[i].max_allocated = LEAF_ALLOC;
    //     Leaf[i].min_shifts = (uint64_t*)calloc(LEAF_ALLOC, sizeof(uint64_t));
    //     Leaf[i].min_indexes = (uint64_t*)calloc(LEAF_ALLOC, sizeof(uint64_t));
    //     Leaf[i].max_allocated = LEAF_ALLOC;

    // }
    // fill the leaf -> todo: move to another function
    uint64_t *f_min_acc = (uint64_t*)calloc(f_size_ext, sizeof(uint64_t));
    uint64_t *f_max_acc = (uint64_t*)calloc(f_size_ext, sizeof(uint64_t));
    uint64_t _s_max = 0;
    uint64_t _s_min = 0;

    for (uint64_t shift = 0; shift < in_arr.k; shift++){
        f_max_acc = accumulate_sum(f_max_glob, in_arr.k, shift);
        f_min_acc = accumulate_sum(f_min_glob, in_arr.k, shift);
        // add values to leaf
        for (uint64_t i = 0; i < in_arr.k; i++){
            _s_max = f_max_acc[i];
            _s_min = f_min_acc[i];
            // deal with max first
            uint64_t m_ind = Leaf[_s_max].max_exists;
            Leaf[_s_max].max_shifts[m_ind] = shift;
            Leaf[_s_max].max_indexes[m_ind] = i;
            Leaf[_s_max].max_exists++;
            // reallocate if it's too much
            if (Leaf[_s_max].max_exists > Leaf[_s_max].max_allocated - CHUNK)
            {
                Leaf[_s_max].max_allocated += LEAD_ALLOC_STEP;
                size_t new_size = Leaf[_s_max].max_allocated * sizeof(uint64_t);
                Leaf[_s_max].max_shifts = (uint64_t*)realloc(Leaf[_s_max].max_shifts, new_size);
                Leaf[_s_max].max_indexes = (uint64_t*)realloc(Leaf[_s_max].max_indexes, new_size);
            }
            // then the same for min
            m_ind = Leaf[_s_min].min_exists;
            Leaf[_s_min].min_shifts[m_ind] = shift;
            Leaf[_s_min].min_indexes[m_ind] = i;
            Leaf[_s_min].min_exists++;
            if (Leaf[_s_min].max_exists > Leaf[_s_min].min_allocated - CHUNK)
            {
                Leaf[_s_min].min_allocated += LEAD_ALLOC_STEP;
                size_t new_size = Leaf[_s_min].min_allocated * sizeof(uint64_t);
                Leaf[_s_min].min_shifts = (uint64_t*)realloc(Leaf[_s_min].min_shifts, new_size);
                Leaf[_s_min].min_indexes = (uint64_t*)realloc(Leaf[_s_min].min_indexes, new_size);
            }
        }
    }
    // don't need this anymore
    free(f_min_acc);
    free(f_max_acc);
    // if X is a trivial point; we already know the answer
    if (Leaf[X].max_exists > 0  || Leaf[X].min_exists > 0)
    {
        uint64_t* answer;
        if (Leaf[X].max_exists > 0){
            answer = trim_to(f_max_glob, Leaf[X].max_shifts[0], Leaf[X].max_indexes[0]);
        } else {
            answer = trim_to(f_min_glob, Leaf[X].min_shifts[0], Leaf[X].min_indexes[0]);
        }
        printf("The answer is:\n");
        for (uint64_t i = 0; i <= Leaf[X].max_indexes[0]; i++){
            printf("%llu\n", answer[i]);
        free_all();
        return 0;
        }
    }
    // we are not lucky, time to deal with complicated stuff
    printf("Complicated case\n");
    free_all();
    return 0;
}
