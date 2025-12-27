/*
 * Comprehensive File Operations Demo
 */

#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>

#define TEST_FILE "/tmp/gem5_test.txt"

void demo_write() {
    printf("=== Demo: Writing to file ===\n");
    
    int fd = open(TEST_FILE, O_CREAT | O_WRONLY | O_TRUNC, 0644);
    if (fd < 0) {
        perror("open");
        return;
    }
    
    printf("Opened file for writing (fd=%d)\n", fd);
    
    const char *messages[] = {
        "Line 1: Hello from gem5!\n",
        "Line 2: This is a test file.\n",
        "Line 3: Demonstrating file I/O syscalls.\n"
    };
    
    for (int i = 0; i < 3; i++) {
        ssize_t n = write(fd, messages[i], strlen(messages[i]));
        if (n < 0) {
            perror("write");
            close(fd);
            return;
        }
        printf("Wrote %zd bytes: %s", n, messages[i]);
    }
    
    close(fd);
    printf("File closed.\n\n");
}

void demo_read() {
    printf("=== Demo: Reading from file ===\n");
    
    int fd = open(TEST_FILE, O_RDONLY);
    if (fd < 0) {
        perror("open");
        return;
    }
    
    printf("Opened file for reading (fd=%d)\n", fd);
    
    char buffer[256];
    ssize_t n = read(fd, buffer, sizeof(buffer) - 1);
    
    if (n < 0) {
        perror("read");
        close(fd);
        return;
    }
    
    buffer[n] = '\0';
    printf("Read %zd bytes:\n%s", n, buffer);
    
    close(fd);
    printf("File closed.\n\n");
}

void demo_stat() {
    printf("=== Demo: File statistics ===\n");
    
    struct stat st;
    
    if (stat(TEST_FILE, &st) < 0) {
        perror("stat");
        return;
    }
    
    printf("File: %s\n", TEST_FILE);
    printf("  Size: %ld bytes\n", st.st_size);
    printf("  Mode: 0%o\n", st.st_mode & 0777);
    printf("  Links: %ld\n", st.st_nlink);
    printf("  Inode: %ld\n", st.st_ino);
    printf("  Device: %ld\n", st.st_dev);
    printf("\n");
}

void demo_append() {
    printf("=== Demo: Appending to file ===\n");
    
    int fd = open(TEST_FILE, O_WRONLY | O_APPEND);
    if (fd < 0) {
        perror("open");
        return;
    }
    
    const char *msg = "Line 4: Appended line.\n";
    ssize_t n = write(fd, msg, strlen(msg));
    printf("Appended %zd bytes\n", n);
    
    close(fd);
    printf("\n");
}

void demo_seek() {
    printf("=== Demo: Seeking in file ===\n");
    
    int fd = open(TEST_FILE, O_RDONLY);
    if (fd < 0) {
        perror("open");
        return;
    }
    
    // Seek to offset 10
    off_t offset = lseek(fd, 10, SEEK_SET);
    printf("Seeked to offset %ld\n", offset);
    
    // Read 20 bytes
    char buffer[21];
    ssize_t n = read(fd, buffer, 20);
    if (n > 0) {
        buffer[n] = '\0';
        printf("Read after seek: '%s'\n", buffer);
    }
    
    // Seek to end
    offset = lseek(fd, 0, SEEK_END);
    printf("File size (seek to end): %ld bytes\n", offset);
    
    close(fd);
    printf("\n");
}

void demo_error_handling() {
    printf("=== Demo: Error handling ===\n");
    
    // Try to open non-existent file
    int fd = open("/nonexistent/file.txt", O_RDONLY);
    if (fd < 0) {
        printf("Expected error: %s\n", strerror(errno));
    }
    
    // Try to read from invalid FD
    char buffer[10];
    ssize_t n = read(999, buffer, 10);
    if (n < 0) {
        printf("Expected error on invalid FD: %s\n", strerror(errno));
    }
    
    printf("\n");
}

void cleanup() {
    printf("=== Cleanup ===\n");
    if (unlink(TEST_FILE) == 0) {
        printf("Test file deleted.\n");
    } else {
        printf("Could not delete test file (may not exist).\n");
    }
}

int main() {
    printf("gem5 File Operations Demo\n");
    printf("==========================\n\n");
    
    demo_write();
    demo_read();
    demo_stat();
    demo_append();
    demo_seek();
    demo_error_handling();
    cleanup();
    
    printf("All demos complete!\n");
    return 0;
}
