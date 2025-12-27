# Annotated gem5 Syscall Source Code

This directory contains heavily annotated excerpts from gem5's syscall emulation source code to help understand the implementation.

## Files

- `syscall_emul_annotated.cc` - Key syscall implementations with detailed comments
- `process_annotated.cc` - Process management code explained
- `fd_entry_annotated.cc` - File descriptor handling

## How to Read These Files

Each file contains:

1. **Original Code**: The actual gem5 source code
2. **Annotations**: Detailed line-by-line explanations
3. **Examples**: Usage examples and common patterns
4. **Gotchas**: Common pitfalls and edge cases

## Example: Annotated open() Implementation

```cpp
// File: syscall_emul_annotated.cc

/// This function implements the open() syscall for guest programs.
/// It demonstrates the complete flow from syscall invocation to
/// returning a file descriptor to the guest.
template <class OS>
SyscallReturn
openFunc(SyscallDesc *desc, ThreadContext *tc)
{
    // STEP 1: Extract arguments from guest registers
    // ================================================
    // In x86-64, syscall arguments are passed in:
    //   RDI = arg0 (pathname pointer)
    //   RSI = arg1 (flags)
    //   RDX = arg2 (mode)
    
    // Get pointer to pathname string in guest memory
    Addr pathname_ptr = tc->readIntReg(ArgumentReg0);  // RDI
    
    // Get flags (O_RDONLY, O_WRONLY, etc.)
    int tgt_flags = tc->readIntReg(ArgumentReg1);      // RSI
    
    // Get mode (permissions, only used with O_CREAT)
    mode_t mode = tc->readIntReg(ArgumentReg2);        // RDX
    
    // STEP 2: Read pathname from guest memory
    // =========================================
    // Guest memory is separate from host memory, so we need
    // to explicitly copy the string using the virtual memory proxy
    
    std::string pathname;
    SETranslatingPortProxy &proxy = tc->getVirtProxy();
    
    // tryReadString handles:
    // - Virtual to physical address translation
    // - Page boundary crossing
    // - Reading null-terminated string
    // Returns false if address is invalid
    if (!proxy.tryReadString(pathname, pathname_ptr)) {
        // EFAULT = Bad address
        return -EFAULT;
    }
    
    // STEP 3: Apply path redirections
    // =================================
    // gem5 can redirect certain paths for simulation purposes
    // Examples:
    //   /proc/cpuinfo -> simulated CPU info
    //   /sys/devices -> simulated device tree
    
    auto process = tc->getProcessPtr();
    pathname = process->checkPathRedirect(pathname);
    
    // STEP 4: Convert target OS flags to host OS flags
    // ==================================================
    // The guest may be running Linux, but host might be macOS
    // Flag values differ between operating systems!
    
    int host_flags = 0;
    
    // Access mode (mutually exclusive)
    if (tgt_flags & OS::TGT_O_RDONLY) host_flags |= O_RDONLY;
    if (tgt_flags & OS::TGT_O_WRONLY) host_flags |= O_WRONLY;
    if (tgt_flags & OS::TGT_O_RDWR)   host_flags |= O_RDWR;
    
    // File creation flags
    if (tgt_flags & OS::TGT_O_CREAT)  host_flags |= O_CREAT;
    if (tgt_flags & OS::TGT_O_EXCL)   host_flags |= O_EXCL;
    if (tgt_flags & OS::TGT_O_TRUNC)  host_flags |= O_TRUNC;
    if (tgt_flags & OS::TGT_O_APPEND) host_flags |= O_APPEND;
    
    // Convert mode (permissions)
    mode_t host_mode = OS::convertMode(mode);
    
    // STEP 5: Perform the actual open on the host
    // =============================================
    // Now we call the real open() syscall on the host OS
    
    int host_fd = ::open(pathname.c_str(), host_flags, host_mode);
    
    if (host_fd == -1) {
        // Open failed, return errno to guest
        // Important: Return NEGATIVE errno value
        return -errno;
    }
    
    // STEP 6: Create FD entry and allocate target FD
    // ================================================
    // We need to track this FD so we can translate between
    // target (guest) FD numbers and host FD numbers
    
    // Create an FD entry object that wraps the host FD
    auto fde = std::make_shared<FileFDEntry>(
        host_fd,        // Host file descriptor
        tgt_flags,      // Original flags for reference
        pathname,       // Path for debugging
        false           // Not a pipe
    );
    
    // Allocate a target FD number and associate with this entry
    // The FD allocator will choose the lowest available FD >= 3
    // (0, 1, 2 are reserved for stdin, stdout, stderr)
    int target_fd = process->fds->allocFD(fde);
    
    // STEP 7: Debug logging
    // ======================
    // This only outputs if Syscall debug flag is enabled
    
    DPRINTF(Syscall, 
            "open('%s', %#x, %#o) = %d (host_fd=%d)\n",
            pathname.c_str(), tgt_flags, mode, 
            target_fd, host_fd);
    
    // STEP 8: Return target FD to guest
    // ===================================
    // The guest program will receive this FD number
    // Future read/write calls will use this number
    
    return target_fd;
}

// USAGE EXAMPLE:
// ==============
// Guest program:
//     int fd = open("/tmp/file.txt", O_RDWR | O_CREAT, 0644);
//
// gem5 execution:
//     1. Guest calls syscall instruction
//     2. CPU traps, calls openFunc
//     3. openFunc reads args: ("/tmp/file.txt", 66, 420)
//     4. Calls host open() -> returns fd 42
//     5. Allocates target_fd 3
//     6. Guest receives fd 3
//     7. Future operations: read(3, ...) -> maps to host read(42, ...)

// COMMON PITFALLS:
// ===============
// 1. Forgetting to convert flags between target and host
// 2. Not handling EFAULT for invalid pointers
// 3. Leaking host FDs if target FD allocation fails
// 4. Path redirection causing unexpected behavior
```

## Cross-References

- See `src/sim/syscall_emul.hh` for full implementation
- See `src/sim/process.hh` for Process class details
- See `src/sim/fd_array.hh` for FD management
- See [API Reference](../docs/api-reference.md) for function documentation

## Learning Path

1. Start with simple syscalls (getpid, write)
2. Move to file I/O (open, read, write, close)
3. Study memory management (mmap, brk)
4. Advanced: process management (fork, clone)

## Contributing

If you find errors or want to add more annotated examples, please submit a PR!
