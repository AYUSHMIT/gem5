/*
 * Raw Syscall Demo - No libc dependencies
 * 
 * This version makes syscalls directly without using libc functions.
 * Useful for understanding the exact syscall interface.
 */

#include <unistd.h>
#include <sys/syscall.h>

// Direct syscall wrapper
long my_write(int fd, const void *buf, size_t count) {
    long ret;
    #ifdef __x86_64__
    __asm__ volatile (
        "syscall"
        : "=a" (ret)
        : "0" (SYS_write), "D" (fd), "S" (buf), "d" (count)
        : "rcx", "r11", "memory"
    );
    #else
    // Fallback to libc
    ret = write(fd, buf, count);
    #endif
    return ret;
}

void my_exit(int status) {
    #ifdef __x86_64__
    __asm__ volatile (
        "syscall"
        : 
        : "a" (SYS_exit), "D" (status)
        : "memory"
    );
    #else
    _exit(status);
    #endif
    __builtin_unreachable();
}

// Simple strlen implementation
size_t my_strlen(const char *s) {
    size_t len = 0;
    while (s[len])
        len++;
    return len;
}

int main() {
    const char *msg1 = "Hello from raw syscalls!\n";
    const char *msg2 = "This bypasses libc entirely.\n";
    const char *msg3 = "Syscall number on x86-64: write=1, exit=60\n";
    
    // Direct write syscalls
    my_write(1, msg1, my_strlen(msg1));
    my_write(1, msg2, my_strlen(msg2));
    my_write(1, msg3, my_strlen(msg3));
    
    // Direct exit syscall
    my_exit(0);
    
    return 0;  // Never reached
}
