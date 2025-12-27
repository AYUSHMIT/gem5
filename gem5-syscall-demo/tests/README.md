# Testing gem5 Syscall Demo

This directory contains tests for the syscall demo programs and tools.

## Structure

```
tests/
├── unit-tests/          # Unit tests for individual components
├── integration-tests/   # End-to-end tests
└── README.md           # This file
```

## Running Tests

### Quick Test

```bash
# From gem5-syscall-demo directory
./quickstart.sh
```

This will:
- Build all demo programs
- Run them natively to verify correctness
- Test visualization and analysis tools

### Individual Demo Tests

```bash
# Test hello-world demo
cd demos/01-hello-world
make test-native

# Test file-operations demo
cd demos/02-file-operations
make test-native

# Test process-management demo
cd demos/03-process-management
make test-native
```

### With gem5

```bash
# Requires gem5 to be built first
cd demos/01-hello-world
./run.sh

# With debug output
./run.sh --debug
```

## Test Categories

### 1. Unit Tests

Test individual syscall implementations:

- `test_open.c` - Test open() syscall
- `test_read_write.c` - Test I/O operations
- `test_mmap.c` - Test memory mapping
- `test_fork.c` - Test process creation

### 2. Integration Tests

Test complete workflows:

- File I/O pipeline (open → read/write → close)
- Process lifecycle (fork → exec → wait)
- Memory management (brk → allocations → munmap)

### 3. Regression Tests

Ensure changes don't break existing functionality:

- Compare output with known-good results
- Check syscall counts and patterns
- Verify performance characteristics

## CI/CD

GitHub Actions automatically runs tests on:
- Every push to demo directories
- Every pull request

See `.github/workflows/syscall-demo-ci.yml` for details.

## Writing Tests

### Test Program Template

```c
#include <stdio.h>
#include <assert.h>

int test_syscall() {
    // Setup
    int fd = open("/tmp/test.txt", O_CREAT | O_RDWR, 0644);
    assert(fd >= 0);
    
    // Test
    char buf[] = "test data";
    ssize_t n = write(fd, buf, sizeof(buf));
    assert(n == sizeof(buf));
    
    // Cleanup
    close(fd);
    unlink("/tmp/test.txt");
    
    return 0;
}

int main() {
    printf("Running test_syscall...\n");
    if (test_syscall() == 0) {
        printf("✓ PASSED\n");
        return 0;
    } else {
        printf("✗ FAILED\n");
        return 1;
    }
}
```

### Adding to CI

1. Create test program in appropriate directory
2. Add build rule to Makefile
3. Update `.github/workflows/syscall-demo-ci.yml`

## Test Checklist

Before submitting changes:

- [ ] All demos compile without warnings
- [ ] All demos run correctly natively
- [ ] Python tools pass --help check
- [ ] Documentation is updated
- [ ] No sensitive data in test files
- [ ] Tests clean up temporary files

## Known Issues

### gem5 SE Mode Limitations

Some tests may not work in SE mode:
- Complex multi-process scenarios
- execve() calls
- Advanced IPC mechanisms

For these, use Full-System mode or mark as expected failures.

## Coverage

To check test coverage:

```bash
python3 analysis/coverage-report.py --arch x86
```

This shows which syscalls are:
- ✓ Implemented and tested
- ⚠️ Implemented but not tested
- ✗ Not implemented

## Reporting Issues

If you find a bug:

1. Check if it's a known limitation
2. Create minimal reproduction case
3. File issue with:
   - gem5 version
   - System information
   - Steps to reproduce
   - Expected vs actual behavior

## Contributing Tests

We welcome test contributions! See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

Priority areas:
- Edge cases and error conditions
- Performance benchmarks
- Cross-architecture tests
- Stress tests

---

**Questions?** See the main [README](../README.md) or open an issue.
