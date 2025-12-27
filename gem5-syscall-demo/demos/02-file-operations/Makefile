# Makefile for File Operations Demo

CC = gcc
CFLAGS = -Wall -O2 -static
TARGETS = fileops dirops

all: $(TARGETS)

fileops: fileops.c
	$(CC) $(CFLAGS) -o fileops fileops.c

dirops: dirops.c
	$(CC) $(CFLAGS) -o dirops dirops.c

clean:
	rm -f $(TARGETS)
	rm -f /tmp/gem5_test.txt
	rm -rf /tmp/gem5_testdir

test-native: $(TARGETS)
	@echo "=== Testing fileops ==="
	./fileops
	@echo ""
	@echo "=== Testing dirops ==="
	./dirops

.PHONY: all clean test-native
