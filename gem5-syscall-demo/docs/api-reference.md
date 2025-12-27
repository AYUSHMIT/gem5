# 📚 gem5 Syscall Emulation API Reference

## Table of Contents

- [Core Classes](#core-classes)
- [Syscall Functions](#syscall-functions)
- [Helper Functions](#helper-functions)
- [Data Structures](#data-structures)
- [Debug Macros](#debug-macros)

---

## Core Classes

### Process Class

**File:** `src/sim/process.hh`

Main class representing a simulated user-space process.

#### Constructor

```cpp
Process(const ProcessParams &params,
        loader::ObjectFile *obj_file,
        loader::MemoryImage image);
```

**Parameters:**
- `params`: Configuration parameters
- `obj_file`: Loaded executable object
- `image`: Memory image from binary

#### Key Methods

##### getSyscallDesc()

```cpp
SyscallDesc* getSyscallDesc(int callnum);
```

Retrieves syscall descriptor for given syscall number.

**Parameters:**
- `callnum`: System call number (architecture-specific)

**Returns:** Pointer to `SyscallDesc` or `nullptr` if not found

**Example:**
```cpp
SyscallDesc *desc = process->getSyscallDesc(2);  // open on x86-64
if (desc) {
    return desc->doSyscall(tc);
}
```

##### allocFD()

```cpp
int allocFD(std::shared_ptr<FDEntry> fde);
```

Allocates a file descriptor for given FD entry.

**Parameters:**
- `fde`: Shared pointer to FD entry

**Returns:** Target file descriptor number

**Example:**
```cpp
auto fde = std::make_shared<FileFDEntry>(host_fd, flags, path);
int target_fd = process->allocFD(fde);
```

##### getFDEntry()

```cpp
std::shared_ptr<FDEntry> getFDEntry(int tgt_fd);
```

Retrieves FD entry for target file descriptor.

**Parameters:**
- `tgt_fd`: Target file descriptor

**Returns:** Shared pointer to FD entry or `nullptr`

**Example:**
```cpp
auto fde = process->getFDEntry(3);
if (fde) {
    fde->write(buffer, size);
}
```

##### allocateMem()

```cpp
void allocateMem(Addr vaddr, int64_t size, bool clobber = false);
```

Allocates memory in virtual address space.

**Parameters:**
- `vaddr`: Virtual address to allocate
- `size`: Size in bytes
- `clobber`: If true, overwrite existing mapping

**Example:**
```cpp
// Allocate 4KB at address 0x1000
process->allocateMem(0x1000, 4096);
```

---

### SyscallDesc Class

**File:** `src/sim/syscall_desc.hh`

Describes a single system call and its handler.

#### Constructor

```cpp
SyscallDesc(const char *name,
            SyscallReturn (*func)(SyscallDesc *, ThreadContext *),
            int flags = 0);
```

**Parameters:**
- `name`: Syscall name (e.g., "open")
- `func`: Handler function pointer
- `flags`: Optional flags (Unimplemented, WarnOnce, etc.)

#### Methods

##### doSyscall()

```cpp
SyscallReturn doSyscall(ThreadContext *tc);
```

Executes the syscall handler.

**Parameters:**
- `tc`: Thread context containing register state

**Returns:** `SyscallReturn` with result value

**Example:**
```cpp
SyscallReturn ret = desc->doSyscall(tc);
tc->setIntReg(ReturnReg, ret.encodedValue());
```

##### name()

```cpp
const char* name() const;
```

Returns the syscall name.

**Returns:** C-string with syscall name

---

### FDEntry Class

**File:** `src/sim/fd_entry.hh`

Base class for file descriptor entries.

#### Virtual Methods

##### read()

```cpp
virtual ssize_t read(uint8_t *buf, size_t len);
```

Read from file descriptor.

**Parameters:**
- `buf`: Buffer to read into
- `len`: Number of bytes to read

**Returns:** Number of bytes read, or -errno on error

##### write()

```cpp
virtual ssize_t write(const uint8_t *buf, size_t len);
```

Write to file descriptor.

**Parameters:**
- `buf`: Buffer to write from
- `len`: Number of bytes to write

**Returns:** Number of bytes written, or -errno on error

##### fstat()

```cpp
virtual int fstat(struct stat *buf);
```

Get file statistics.

**Parameters:**
- `buf`: Stat structure to fill

**Returns:** 0 on success, -errno on error

#### Derived Classes

- **FileFDEntry**: Regular files
- **PipeFDEntry**: Pipes
- **SocketFDEntry**: Sockets
- **DeviceFDEntry**: Special devices

---

### MemState Class

**File:** `src/sim/mem_state.hh`

Manages virtual memory state for a process.

#### Methods

##### setStackRegion()

```cpp
void setStackRegion(Addr base, Addr size);
```

Sets up stack region.

**Parameters:**
- `base`: Stack base address
- `size`: Stack size in bytes

##### extendBrk()

```cpp
Addr extendBrk(Addr new_brk);
```

Extends heap via brk syscall.

**Parameters:**
- `new_brk`: New break point address

**Returns:** New break point (may differ from requested)

**Example:**
```cpp
Addr new_brk = mem_state->extendBrk(old_brk + 4096);
```

##### mmap()

```cpp
Addr mmap(Addr start, uint64_t length, int prot, int flags);
```

Maps memory region.

**Parameters:**
- `start`: Desired start address (0 = let system choose)
- `length`: Length in bytes
- `prot`: Protection flags (PROT_READ, PROT_WRITE, etc.)
- `flags`: Mapping flags (MAP_PRIVATE, MAP_SHARED, etc.)

**Returns:** Start address of mapped region

##### munmap()

```cpp
void munmap(Addr start, uint64_t length);
```

Unmaps memory region.

**Parameters:**
- `start`: Start address
- `length`: Length in bytes

---

## Syscall Functions

### File I/O Syscalls

#### openFunc()

```cpp
template <class OS>
SyscallReturn openFunc(SyscallDesc *desc, ThreadContext *tc,
                       Addr pathname, int flags, mode_t mode);
```

Opens a file.

**Parameters:**
- `pathname`: Address of path string in guest memory
- `flags`: Open flags (O_RDONLY, O_WRONLY, etc.)
- `mode`: File permissions (for O_CREAT)

**Returns:** File descriptor or -errno

**Example implementation:**
```cpp
template <class OS>
SyscallReturn openFunc(SyscallDesc *desc, ThreadContext *tc) {
    // Extract arguments from registers
    Addr pathname_ptr = tc->readIntReg(ArgumentReg0);
    int flags = tc->readIntReg(ArgumentReg1);
    mode_t mode = tc->readIntReg(ArgumentReg2);
    
    // Read pathname from guest memory
    std::string path;
    if (!tc->getVirtProxy().tryReadString(path, pathname_ptr))
        return -EFAULT;
    
    // Apply path redirections
    path = process->checkPathRedirect(path);
    
    // Convert flags to host format
    int host_flags = OS::convertOpenFlags(flags);
    
    // Open on host
    int host_fd = ::open(path.c_str(), host_flags, mode);
    if (host_fd < 0)
        return -errno;
    
    // Create FD entry and allocate target FD
    auto fde = std::make_shared<FileFDEntry>(host_fd, flags, path);
    int target_fd = process->allocFD(fde);
    
    return target_fd;
}
```

#### readFunc()

```cpp
template <class OS>
SyscallReturn readFunc(SyscallDesc *desc, ThreadContext *tc,
                       int fd, Addr buf_ptr, size_t nbytes);
```

Reads from file descriptor.

**Parameters:**
- `fd`: Target file descriptor
- `buf_ptr`: Address of buffer in guest memory
- `nbytes`: Number of bytes to read

**Returns:** Number of bytes read or -errno

#### writeFunc()

```cpp
template <class OS>
SyscallReturn writeFunc(SyscallDesc *desc, ThreadContext *tc,
                        int fd, Addr buf_ptr, size_t nbytes);
```

Writes to file descriptor.

**Parameters:**
- `fd`: Target file descriptor
- `buf_ptr`: Address of buffer in guest memory
- `nbytes`: Number of bytes to write

**Returns:** Number of bytes written or -errno

#### closeFunc()

```cpp
template <class OS>
SyscallReturn closeFunc(SyscallDesc *desc, ThreadContext *tc,
                        int tgt_fd);
```

Closes file descriptor.

**Parameters:**
- `tgt_fd`: Target file descriptor to close

**Returns:** 0 on success, -errno on error

---

### Process Management Syscalls

#### forkFunc()

```cpp
template <class OS>
SyscallReturn forkFunc(SyscallDesc *desc, ThreadContext *tc);
```

Forks current process.

**Returns:** 
- Parent: child PID
- Child: 0

**Implementation notes:**
- Clones process object
- Duplicates memory state (COW)
- Clones FD table (shared)
- Allocates new thread context

#### cloneFunc()

```cpp
template <class OS>
SyscallReturn cloneFunc(SyscallDesc *desc, ThreadContext *tc,
                        int flags, Addr newStack, Addr ptidPtr,
                        Addr ctidPtr, Addr tlsPtr);
```

Creates new process or thread.

**Parameters:**
- `flags`: Clone flags (CLONE_VM, CLONE_THREAD, etc.)
- `newStack`: Stack pointer for child
- `ptidPtr`: Parent TID pointer
- `ctidPtr`: Child TID pointer  
- `tlsPtr`: Thread-local storage pointer

**Returns:** Thread ID or -errno

#### execveFunc()

```cpp
template <class OS>
SyscallReturn execveFunc(SyscallDesc *desc, ThreadContext *tc,
                         Addr filename, Addr argv, Addr envp);
```

Executes new program (not fully implemented in SE mode).

---

### Memory Management Syscalls

#### mmapFunc()

```cpp
template <class OS>
SyscallReturn mmapFunc(SyscallDesc *desc, ThreadContext *tc,
                       Addr start, size_t length, int prot,
                       int flags, int fd, off_t offset);
```

Maps memory region.

**Parameters:**
- `start`: Desired start address (0 = any)
- `length`: Size in bytes
- `prot`: Protection (PROT_READ|PROT_WRITE|PROT_EXEC)
- `flags`: Flags (MAP_PRIVATE|MAP_SHARED|MAP_ANONYMOUS)
- `fd`: File descriptor (for file-backed mappings)
- `offset`: Offset in file

**Returns:** Start address of mapping or -errno

#### munmapFunc()

```cpp
template <class OS>
SyscallReturn munmapFunc(SyscallDesc *desc, ThreadContext *tc,
                         Addr start, size_t length);
```

Unmaps memory region.

**Parameters:**
- `start`: Start address
- `length`: Size in bytes

**Returns:** 0 on success, -errno on error

#### brkFunc()

```cpp
template <class OS>
SyscallReturn brkFunc(SyscallDesc *desc, ThreadContext *tc,
                      Addr new_brk);
```

Changes program break (heap end).

**Parameters:**
- `new_brk`: New break point address

**Returns:** New break point address

---

## Helper Functions

### Memory Access Helpers

#### readString()

```cpp
bool SETranslatingPortProxy::readString(std::string &str, Addr addr,
                                        size_t maxlen = std::string::npos);
```

Reads null-terminated string from guest memory.

**Parameters:**
- `str`: Output string
- `addr`: Guest address
- `maxlen`: Maximum length

**Returns:** true on success

**Example:**
```cpp
std::string path;
if (!tc->getVirtProxy().readString(path, pathname_ptr)) {
    return -EFAULT;
}
```

#### readBlob()

```cpp
void SETranslatingPortProxy::readBlob(Addr addr, void *p, uint64_t size);
```

Reads binary data from guest memory.

**Parameters:**
- `addr`: Guest address
- `p`: Host buffer
- `size`: Number of bytes

#### writeBlob()

```cpp
void SETranslatingPortProxy::writeBlob(Addr addr, const void *p,
                                      uint64_t size);
```

Writes binary data to guest memory.

**Parameters:**
- `addr`: Guest address
- `p`: Host buffer
- `size`: Number of bytes

---

### Argument Extraction

#### getArg()

```cpp
template <typename T>
T getArg(ThreadContext *tc, int index);
```

Extracts syscall argument from register.

**Parameters:**
- `tc`: Thread context
- `index`: Argument index (0-5)

**Returns:** Argument value

**Example:**
```cpp
int fd = getArg<int>(tc, 0);
Addr buf_ptr = getArg<Addr>(tc, 1);
size_t len = getArg<size_t>(tc, 2);
```

---

## Data Structures

### SyscallReturn

**File:** `src/sim/syscall_return.hh`

Encapsulates syscall return value.

```cpp
class SyscallReturn {
  public:
    // Constructors
    SyscallReturn(int64_t value);
    SyscallReturn(int64_t value, bool success);
    
    // Methods
    int64_t value() const;
    bool successful() const;
    int64_t encodedValue() const;
};
```

**Usage:**
```cpp
// Success
return SyscallReturn(bytes_read);

// Error
return SyscallReturn(-ENOENT);

// Check result
SyscallReturn ret = syscall_func(tc);
if (ret.successful()) {
    // Handle success
}
```

### stat / stat64

File information structure (OS-dependent).

```cpp
struct stat {
    dev_t     st_dev;     // Device ID
    ino_t     st_ino;     // Inode number
    mode_t    st_mode;    // File mode
    nlink_t   st_nlink;   // Number of hard links
    uid_t     st_uid;     // User ID
    gid_t     st_gid;     // Group ID
    dev_t     st_rdev;    // Device ID (for special files)
    off_t     st_size;    // File size
    time_t    st_atime;   // Access time
    time_t    st_mtime;   // Modification time
    time_t    st_ctime;   // Status change time
};
```

---

## Debug Macros

### DPRINTF

```cpp
DPRINTF(FlagName, format, args...);
```

Conditional debug print (only when flag enabled).

**Example:**
```cpp
DPRINTF(Syscall, "open('%s', %#x) = %d\n", path.c_str(), flags, fd);
```

**Common flags:**
- `Syscall`: Basic syscall tracing
- `SyscallVerbose`: Detailed syscall info
- `SyscallAll`: All syscall-related output

### warn() / inform() / fatal()

```cpp
warn(format, args...);
inform(format, args...);
fatal(format, args...);
```

**Example:**
```cpp
warn("Syscall %s not fully implemented", name);
inform("Process %d exited with code %d", pid, status);
fatal("Cannot allocate memory at %#x", addr);
```

---

## Usage Examples

### Complete Syscall Implementation

```cpp
// Example: Custom syscall implementation
template <class OS>
SyscallReturn
myCustomSyscall(SyscallDesc *desc, ThreadContext *tc)
{
    // 1. Extract arguments
    int arg1 = tc->readIntReg(ArgumentReg0);
    Addr arg2 = tc->readIntReg(ArgumentReg1);
    
    // 2. Validate arguments
    if (arg1 < 0) {
        warn("Invalid argument: %d", arg1);
        return -EINVAL;
    }
    
    // 3. Access guest memory
    std::string str;
    if (!tc->getVirtProxy().tryReadString(str, arg2)) {
        return -EFAULT;
    }
    
    // 4. Perform operation
    int result = doSomething(arg1, str);
    
    // 5. Debug output
    DPRINTF(Syscall, "myCustomSyscall(%d, '%s') = %d\n",
            arg1, str.c_str(), result);
    
    // 6. Return result
    return SyscallReturn(result);
}
```

---

## Further Reading

- [Architecture Documentation](architecture.md)
- [Syscall Flow Guide](syscall-flow.md)
- [Tutorial](tutorial.md)
- [gem5 Doxygen](http://www.gem5.org/documentation/doxygen/)

---

**[⬆ back to top](#-gem5-syscall-emulation-api-reference)**
