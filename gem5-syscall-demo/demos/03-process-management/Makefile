# Makefile for Process Management Demo

CC = gcc
CFLAGS = -Wall -O2 -static
TARGETS = fork_demo

all: $(TARGETS)

fork_demo: fork_demo.c
	$(CC) $(CFLAGS) -o fork_demo fork_demo.c

clean:
	rm -f $(TARGETS)

test-native: $(TARGETS)
	@echo "=== Testing fork_demo ==="
	./fork_demo

.PHONY: all clean test-native
