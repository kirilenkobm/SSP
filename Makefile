# Took this template from https://gist.github.com/xuhdev/1873316
# Makefile for shared library
CC = gcc
CFLAGS = -fPIC -Wall -Wextra -O2 -g
LDFLAGS = -shared
RM = rm -f
TARGET_LIB = bin/SSP_lib.so
RND_GEN = bin/generate_input

SRCS = src/SSP_lib.c
OBJS = $(SRCS:.c=.o)

.PHONY: all
all: ${TARGET_LIB}

$(TARGET_LIB): $(OBJS)
	$(CC) ${LDFLAGS} -o $@ $^

$(SRCS:.c=.d):%.d:%.c
	$(CC) $(CFLAGS) -MM $< >$@

include $(SRCS:.c=.d)

.PHONY: clean
clean:
	-${RM} ${OBJS} $(SRCS:.c)

.PHONY: rnd
rnd: $(RND_GEN)

$(RND_GEN): src/generate_input.c
	$(CC) $(CFLAGS) src/generate_input.c -o $(RND_GEN) $
