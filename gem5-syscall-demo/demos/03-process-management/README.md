# Demo 03: Process Management

## Overview

This demo showcases process-related syscalls:
- `fork()` - Create child process
- `getpid()` - Get process ID
- `wait()` - Wait for child process
- `execve()` - Execute program (limited in SE mode)

## Files

- `fork_demo.c` - Basic fork demonstration
- `multiprocess.c` - Parent-child communication
- `process_tree.c` - Create process hierarchy
- `Makefile` - Build script

## Quick Start

```bash
make
# Note: gem5 SE mode has limited multi-process support
# Some features may not work as in full-system mode
```

## fork_demo.c

```c
#include <unistd.h>
#include <sys/wait.h>
#include <stdio.h>

int main() {
    printf("Parent process (PID: %d) starting\n", getpid());
    
    pid_t pid = fork();
    
    if (pid < 0) {
        perror("fork failed");
        return 1;
    } else if (pid == 0) {
        // Child process
        printf("Child process (PID: %d, Parent: %d)\n", 
               getpid(), getppid());
        return 0;
    } else {
        // Parent process
        printf("Parent created child with PID: %d\n", pid);
        wait(NULL);
        printf("Child exited\n");
        return 0;
    }
}
```

## Important Notes

⚠️ **gem5 SE Mode Limitations:**

gem5's Syscall Emulation mode has limited support for multi-process programs:

1. **fork()** - Basic support, but may not handle all cases
2. **execve()** - Not fully implemented
3. **Shared resources** - Limited simulation
4. **IPC** - Pipes and signals have partial support

For full multi-process simulation, use gem5's Full-System (FS) mode.

## What Works

✅ Basic `fork()` with simple child processes  
✅ `getpid()`, `getppid()` syscalls  
✅ `wait()` and `waitpid()` for process synchronization  
✅ Simple parent-child communication via pipes  

## What Doesn't Work

❌ Complex process hierarchies  
❌ `execve()` to run different programs  
❌ Advanced IPC (message queues, shared memory)  
❌ Process groups and sessions  

## Next Steps

- **Demo 04:** Threading with futex
- **Demo 05:** Networking with sockets
- For full process simulation, see gem5 FS mode documentation
