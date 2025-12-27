# Makefile for Hello World Demo

CC = gcc
CFLAGS = -Wall -O2 -static
TARGETS = hello hello_raw

all: $(TARGETS)

hello: hello.c
	$(CC) $(CFLAGS) -o hello hello.c

hello_raw: hello_raw.c
	$(CC) $(CFLAGS) -o hello_raw hello_raw.c

clean:
	rm -f $(TARGETS)

test-native: $(TARGETS)
	@echo "=== Testing hello natively ==="
	./hello
	@echo ""
	@echo "=== Testing hello_raw natively ==="
	./hello_raw

.PHONY: all clean test-native
