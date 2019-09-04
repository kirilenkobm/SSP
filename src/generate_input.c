// Bogdan Kirilenko
// 2019, Dresden
// Generate input for CSP
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <ctype.h> 
#include <stdarg.h>
#include <limits.h>
#include <time.h>
#include <sys/types.h>
#include <sys/stat.h>
#ifdef _WIN32
#include <io.h>
#define F_OK 0
#elif __unix__
#include <unistd.h>
#elif __APPLE__
#include <unistd.h>
#endif

#define OPT_NUM 6
#define MAXCHAR 512

typedef struct
{
    uint64_t num_num;
    uint64_t max_num;
    uint64_t min_num;
    char *output_file;
} Input_data;

struct stat st = {0};


// show help and exit
void _show_usage_and_quit(char * executable)
{
    fprintf(stderr, "Usage: %s [num_num] [max_num] [min_num] [output_file]\n", executable);
    fprintf(stderr, "[num_num] - set S size\n");
    fprintf(stderr, "[max_num] - max number in the dataset\n");
    fprintf(stderr, "[min_num] - min number in the dataset\n");
    fprintf(stderr, "[output_file] - where to save, a file or stdout\n");
    exit(1);
}


// read input
void __read_input(Input_data *input_data, char **argv)
{
    input_data->num_num = (uint16_t)strtoul(argv[1], 0L, 10);
    input_data->max_num = (uint16_t)strtoul(argv[2], 0L, 10);
    input_data->min_num = (uint16_t)strtoul(argv[3], 0L, 10);
    input_data->output_file = (char*)malloc(MAXCHAR * sizeof(char));
    strcpy(input_data->output_file, argv[4]);
}

// enrty point
int main(int argc, char **argv)
{
    if (argc != 5){_show_usage_and_quit(argv[0]);}
    srand((uint32_t)time(NULL) + (uint32_t)**main);
    Input_data input_data;
    __read_input(&input_data, argv);

    uint64_t *arr = (uint64_t*)calloc(input_data.num_num, sizeof(uint64_t));
    for (uint64_t i = 0; i < input_data.num_num; ++i){
        arr[i] = (rand() % (input_data.max_num - input_data.min_num + 1)) + input_data.min_num;
    }
    // if we need to stdout -> just print it
    if (strcmp(input_data.output_file, "stdout") == 0){
        for (uint64_t i = 0; i < input_data.num_num; ++i){printf("%llu\n", arr[i]);}
        free(arr);
        return 0;
    }
    FILE *f;
    f = fopen(input_data.output_file, "w");
    for (uint64_t i = 0; i < input_data.num_num; ++i){
        fprintf(f, "%llu\n", arr[i]);
    }
    fclose(f);
    free(arr);
}