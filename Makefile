# Took this template from https://gist.github.com/xuhdev/1873316
# Makefile for shared library
CC = gcc
CFLAGS = -fPIC -Wall -Wextra -O2 -g
# CFLAGS = -Wall -Wextra -O2 -g
LDFLAGS = -shared
RM = rm -f
TARGET_LIB = bin/SSP_lib.so
# TARGET = bin/SSP

SRCS = src/SSP_lib.c
OBJS = $(SRCS:.c=.o)

.PHONY: all
all: ${TARGET_LIB}
# all: ${TARGET}

$(TARGET_LIB): $(OBJS)
# $(TARGET): $(OBJS)
	$(CC) ${LDFLAGS} -o $@ $^
	# $(CC) -o $@ $^

$(SRCS:.c=.d):%.d:%.c
	$(CC) $(CFLAGS) -MM $< >$@

include $(SRCS:.c=.d)

.PHONY: clean
clean:
	-${RM} ${OBJS} $(SRCS:.c)
